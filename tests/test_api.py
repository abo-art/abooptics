import os
import base64
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "static")

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "MediaPipe" in data["model"]
    assert data["catalog_count"] >= 9

def test_get_catalog():
    res = client.get("/api/catalog")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 9
    assert len(data["frames"]) >= 9

def test_worn_frame_evaluation_scenario():
    """
    Тестирует новый сценарий (Real-Time Evaluation):
    Клиент в квадратных очках -> ИИ оценивает посадку и возвращает вердикт стилиста + топ-3 альтернативы
    """
    img_path = os.path.join(STATIC_DIR, "demo_faces", "wearing_square.jpg")
    with open(img_path, "rb") as f:
        res = client.post("/api/analyze?frame_shape=square", files={"file": ("wearing_square.jpg", f, "image/jpeg")})
    
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["face_detected"] is True
    
    # 1. Оценка надетой оправы
    worn = data.get("worn_frame_evaluation")
    assert worn is not None
    assert worn["has_glasses"] is True
    assert "Квадратная" in worn["detected_shape_name_ru"]
    assert worn["compatibility_score"] > 0
    assert len(worn["verdict_quote_ru"]) > 15
    assert worn["fit_metrics"]["width_status"] in ["Идеально", "Широковата", "Узковата"]
    
    # 2. Топ-5 альтернатив смарт-очков Meta
    alts = data.get("top_alternatives")
    assert len(alts) == 5
    for alt in alts:
        assert alt["match_score"] >= 88
        assert len(alt["why_better_ru"]) > 10
        assert alt["shape"] != "square" # Альтернативы исключают текущую неудачную форму
        assert len(alt["material"]) > 3
        assert len(alt["dimensions"]) > 3
        assert "Meta" in alt["brand"]

def test_worn_frame_evaluation_base64():
    """Проверка работы с data-URI схемой (data:image/jpeg;base64,...)"""
    img_path = os.path.join(STATIC_DIR, "demo_faces", "wearing_round.jpg")
    with open(img_path, "rb") as f:
        b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")
    
    res = client.post("/api/analyze", json={"image_base64": b64, "frame_shape": "round"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["face_detected"] is True
    assert len(data["top_alternatives"]) == 5

def test_worn_frame_evaluation_pure_base64():
    """Проверка работы с чистой base64 строкой (без префикса)"""
    img_path = os.path.join(STATIC_DIR, "demo_faces", "wearing_round.jpg")
    with open(img_path, "rb") as f:
        pure_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    res = client.post("/api/analyze", json={"image_base64": pure_b64, "frame_shape": "round"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["face_detected"] is True
    assert len(data["top_alternatives"]) == 5

def test_worn_frame_evaluation_base64_with_whitespace_and_newlines():
    """Проверка устойчивости к пробелам, переводам строк и data-URI схеме"""
    img_path = os.path.join(STATIC_DIR, "demo_faces", "wearing_round.jpg")
    with open(img_path, "rb") as f:
        raw_b64 = base64.b64encode(f.read()).decode("utf-8")
    # Добавляем префикс, переводы строк и пробелы
    formatted_b64 = f"data:image/jpeg;base64, \n {raw_b64[:100]} \r\n {raw_b64[100:]} \n "
    
    res = client.post("/api/analyze", json={"image_base64": formatted_b64, "frame_shape": "round"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["face_detected"] is True

def test_analyze_invalid_base64_rejected():
    """Проверка отклонения некорректного формата/паттерна base64"""
    # 1. Недопустимые символы
    res = client.post("/api/analyze", json={"image_base64": "data:image/jpeg;base64,@@@invalid_base64!!!"})
    assert res.status_code in [400, 422]

    # 2. Пустая строка
    res2 = client.post("/api/analyze", json={"image_base64": ""})
    assert res2.status_code in [400, 422]

    # 3. Неверная схема
    res3 = client.post("/api/analyze", json={"image_base64": "data:text/plain;base64,hello"})
    assert res3.status_code in [400, 422]


def test_branding_and_pwa_assets():
    # 1. Favicon
    res = client.get("/favicon.ico")
    assert res.status_code == 200
    assert "image" in res.headers.get("content-type", "")

    # 2. Manifest PWA
    res = client.get("/manifest.json")
    assert res.status_code == 200
    m_data = res.json()
    assert "abooptika" in m_data["name"]
    assert m_data["theme_color"] == "#0C2662"
    assert len(m_data["icons"]) >= 2

    # 3. Apple Touch Icon
    res = client.get("/apple-touch-icon.png")
    assert res.status_code == 200
    assert "image/png" in res.headers.get("content-type", "")

    # 4. Brand Logo
    res = client.get("/static/images/brand/logo.png")
    assert res.status_code == 200
    assert "image/png" in res.headers.get("content-type", "")

def test_camera_motion_alignment_transform():
    # Проверка, что для фронтальной камеры задана ориентация 1:1 с движениями пользователя (scaleX(-1))
    index_res = client.get("/")
    assert index_res.status_code == 200
    assert "scaleX(-1)" in index_res.text
    assert "btn-toggle-mirror" in index_res.text

    css_res = client.get("/static/css/custom.css")
    assert css_res.status_code == 200
    assert "scaleX(-1)" in css_res.text

def test_meta_smart_glasses_catalog_structure():
    """Тест исчерпывающей структуры каталога смарт-очков Meta (25 отдельных моделей)"""
    from app.services.catalog_service import CatalogService
    frames = CatalogService.get_all_frames()
    assert len(frames) == 25, f"Expected 25 frames, got {len(frames)}"

    # Проверка поколений
    generations = {f["generation"] for f in frames}
    assert any("Gen 1" in g for g in generations)
    assert any("Gen 2" in g for g in generations)
    assert any("Gen 3" in g for g in generations)

    # Проверка силуэтов
    shapes = {f["shape"] for f in frames}
    assert "wayfarer" in shapes
    assert "panto" in shapes
    assert "cat_eye" in shapes
    assert "aviator" in shapes
    assert "geometric" in shapes

    # Проверка обязательных моделей по ТЗ
    names = [f["name"] for f in frames]
    assert any("Fury" in n for n in names), "Meta Fury missing"
    assert any("Adventurer" in n and "LISA" in n for n in names), "Adventurer LISA missing"
    assert any("Adventurer" in n for n in names), "Adventurer missing"
    assert any("Capri" in n and "LISA" in n for n in names), "Capri LISA missing"
    assert any("Capri" in n for n in names), "Capri missing"
    assert any("Nova" in n for n in names), "Nova missing"
    assert any("Clubmaster" in n and "Audio" in n for n in names), "Clubmaster Audio missing"
    assert any("Burbank" in n and "Audio" in n for n in names), "Burbank Audio missing"
    assert any("Zena" in n for n in names), "Zena missing"
    assert any("HSTN" in n for n in names), "Oakley HSTN missing"
    assert any("Vanguard" in n for n in names), "Oakley Vanguard missing"
    assert any("Wayfarer" in n for n in names), "Wayfarer missing"
    assert any("Headliner" in n for n in names), "Headliner missing"
    assert any("Skyler" in n for n in names), "Skyler missing"
    assert any("Aviator" in n for n in names), "Aviator missing"
    assert any("Orion" in n for n in names), "Orion Display missing"

    # Проверка технических атрибутов
    for frame in frames:
        assert len(frame["frame_id"]) > 3
        assert "dimensions" in frame and len(frame["dimensions"]) >= 7
        assert "camera" in frame and len(frame["camera"]) > 3
        assert "display" in frame and len(frame["display"]) > 3
        assert "audio" in frame and len(frame["audio"]) > 3
        assert frame["price"] > 50000
        assert frame["currency"] == "₸"
        assert len(frame["in_stock_salons"]) >= 1

def test_meta_catalog_profiles_endpoint():
    """Тест эндпоинта 5 ключевых геометрических профилей Meta Smart Glasses"""
    res = client.get("/api/catalog/profiles")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 5
    profiles = data["profiles"]
    assert len(profiles) == 5

    profile_ids = [p.get("profile_id") or p.get("id") for p in profiles]
    assert "profile-wayfarer" in profile_ids
    assert "profile-aviator" in profile_ids
    assert "profile-round-headliner" in profile_ids
    assert "profile-cateye-skyler" in profile_ids
    assert "profile-shield-display" in profile_ids

    for p in profiles:
        assert len(p["name_ru"]) > 5
        assert len(p["description_ru"]) > 10
        assert "size_grid" in p
        grid = p["size_grid"]
        assert len(grid) >= 1
        for item in grid:
            assert "lens_width_mm" in item
            assert "bridge_width_mm" in item
            assert "temple_length_mm" in item
            assert "fit_type" in item
        assert len(p.get("supported_shapes", [])) >= 1

def test_ai_optometrist_evaluation_fields():
    """Проверка экспертного заключения ИИ-оптометриста Gemini (мостик, дужки, % совместимости)"""
    img_path = os.path.join(STATIC_DIR, "demo_faces", "wearing_square.jpg")
    with open(img_path, "rb") as f:
        res = client.post("/api/analyze?frame_shape=square", files={"file": ("wearing_square.jpg", f, "image/jpeg")})
    
    assert res.status_code == 200
    data = res.json()
    worn = data.get("worn_frame_evaluation")
    assert worn is not None

    # Поля ИИ-оптометриста
    assert "bridge_nuance_ru" in worn
    assert len(worn["bridge_nuance_ru"]) > 10
    assert "мостик" in worn["bridge_nuance_ru"].lower() or "переносиц" in worn["bridge_nuance_ru"].lower() or "посадк" in worn["bridge_nuance_ru"].lower()

    assert "temple_nuance_ru" in worn
    assert len(worn["temple_nuance_ru"]) > 10
    assert "заушник" in worn["temple_nuance_ru"].lower() or "височ" in worn["temple_nuance_ru"].lower() or "дужк" in worn["temple_nuance_ru"].lower()

    assert "is_ai_powered" in worn
    assert isinstance(worn["is_ai_powered"], bool)
    assert "ai_model_name" in worn

    # Топ-5 альтернатив содержат привязку к профилям
    alts = data.get("top_alternatives", [])
    assert len(alts) == 5
    for alt in alts:
        assert "profile_id" in alt
        assert alt["profile_id"] in [
            "profile-wayfarer",
            "profile-aviator",
            "profile-round-headliner",
            "profile-cateye-skyler",
            "profile-shield-display"
        ]

def test_bare_face_detection_no_glasses():
    """
    Тестирует переключение интерфейса в режим «Подбор идеальной оправы / Рекомендации»
    при отсутствии очков на лице (первичное сканирование геометрии лица).
    """
    img_path = os.path.join(STATIC_DIR, "demo_faces", "oval_face.jpg")
    with open(img_path, "rb") as f:
        res = client.post("/api/analyze?frame_shape=none", files={"file": ("oval_face.jpg", f, "image/jpeg")})
    
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["face_detected"] is True
    
    # 1. Проверка флага и режима подбора
    worn = data.get("worn_frame_evaluation")
    assert worn is not None
    assert worn["has_glasses"] is False
    assert worn["detected_shape"] == "none"
    assert "не надета" in worn["detected_shape_name_ru"].lower()
    assert worn["match_badge"] == "Первичный биометрический подбор"
    assert worn["compatibility_score"] == 98
    assert len(worn["verdict_quote_ru"]) > 15
    quote_lower = worn["verdict_quote_ru"].lower()
    assert any(term in quote_lower for term in ["aboooptika", "оправ", "биометрическ", "лиц", "пропорци"])
    
    # 2. Метрики посадки переключены на рекомендации
    assert worn["fit_metrics"]["width_status"] == "Подбор размера"
    assert worn["fit_metrics"]["pupil_status"] == "Оптическая ось"
    assert worn["fit_metrics"]["eyebrow_status"] == "Линия бровей"
    
    # 3. Рекомендованные альтернативы (топ-5 моделей Meta)
    alts = data.get("top_alternatives", [])
    assert len(alts) == 5
    for alt in alts:
        assert alt["match_score"] >= 80
        assert len(alt["why_better_ru"]) > 10

def test_clean_branding_and_no_smart_meta_lab():
    """
    Проверка чистоты бренда AbooOptika:
    Ни в HTML, ни в ответах API нет плашек «Smart Meta Lab» и «Gemini 3.5 Flash Lite».
    """
    # 1. Главная страница
    res_html = client.get("/")
    assert res_html.status_code == 200
    assert "Smart Meta Lab" not in res_html.text
    assert "Gemini 3.5" not in res_html.text
    assert "Flash Lite" not in res_html.text
    assert "AbooOptika" in res_html.text
    
    # 2. Ответ анализа
    img_path = os.path.join(STATIC_DIR, "demo_faces", "wearing_square.jpg")
    with open(img_path, "rb") as f:
        res_api = client.post("/api/analyze?frame_shape=square", files={"file": ("wearing_square.jpg", f, "image/jpeg")})
    assert res_api.status_code == 200
    api_text = res_api.text
    assert "Smart Meta Lab" not in api_text
    assert "Gemini 3.5" not in api_text
    assert "Flash Lite" not in api_text
    
    data = res_api.json()
    worn = data.get("worn_frame_evaluation", {})
    assert worn.get("ai_model_name") == "AbooOptika AI Optometrist"

def test_security_env_exclusion():
    """Проверка безопасности: .env в .gitignore, наличие .env.example, ключ загружается безопасно"""
    gitignore_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".gitignore")
    assert os.path.exists(gitignore_path)
    with open(gitignore_path, "r", encoding="utf-8") as f:
        git_content = f.read()
    assert ".env" in git_content

    example_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.example")
    assert os.path.exists(example_path)
    with open(example_path, "r", encoding="utf-8") as f:
        example_content = f.read()
    assert "GEMINI_API_KEY" in example_content
    # .env.example не должен содержать реальный ключ
    assert "AQ.Ab8RN6L" not in example_content

def test_ai_chat_endpoint_basic():
    """Тест интерактивного эндпоинта ИИ-консультанта AbooOptika (POST /api/chat)"""
    payload = {
        "messages": [
            {"role": "user", "content": "Расскажи про смарт-очки Meta LISA Edition и Fury"}
        ]
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["reply"]) > 20
    reply_low = data["reply"].lower()
    assert any(term in reply_low for term in ["lisa", "fury", "meta", "aboooptika", "adventurer", "capri"])
    assert isinstance(data.get("suggested_prompts"), list)
    assert len(data["suggested_prompts"]) >= 1

def test_ai_chat_endpoint_with_biometric_context():
    """Тест ИИ-консультанта с учетом биометрического контекста сканирования лица"""
    payload = {
        "messages": [
            {"role": "user", "content": "Какие смарт-очки лучше всего выбрать для меня?"}
        ],
        "client_context": {
            "face_shape_ru": "Квадратное лицо",
            "metrics": {
                "height_to_width_ratio": 1.25,
                "jaw_to_cheek_ratio": 0.92,
                "chin_sharpness_deg": 170
            },
            "worn_frame": {
                "has_glasses": False,
                "detected_shape_name_ru": "Оправа не надета"
            },
            "top_recommendations": ["Meta Nova", "Ray-Ban Meta Headliner", "Meta Adventurer"]
        }
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["reply"]) > 30
    reply_low = data["reply"].lower()
    # Ответ должен содержать экспертную оптическую рекомендацию
    assert any(term in reply_low for term in ["лиц", "квадрат", "оправ", "headliner", "nova", "adventurer", "meta", "aboooptika"])

def test_ai_chat_widget_in_frontend():
    """Тест наличия виджета ИИ-чата и стилей Apple HIG на главной странице"""
    res = client.get("/")
    assert res.status_code == 200
    html = res.text
    assert "chat-widget-container" in html
    assert "btn-toggle-chat" in html
    assert "chat-panel" in html
    assert "chat-messages" in html
    assert "chat-chips-bar" in html
    assert "chat-input" in html
    assert "AbooOptika AI" in html

    # Проверка стилей в custom.css
    css_res = client.get("/static/css/custom.css")
    assert css_res.status_code == 200
    assert "chat-glass" in css_res.text
    assert "chat-bubble-ai" in css_res.text
    assert "chat-trigger-btn" in css_res.text

    # Проверка наличия и доступности официального аватара ИИ-консультанта
    assert "ai-avatar.png" in html
    avatar_res = client.get("/static/images/brand/ai-avatar.png")
    assert avatar_res.status_code == 200
    assert "image/png" in avatar_res.headers.get("content-type", "")

    # Проверка мобильного позиционирования виджета (поднятие над системной панелью)
    assert "chat-widget-container" in css_res.text
    assert "84px" in css_res.text
    assert "safe-area-inset-bottom" in css_res.text

def test_ai_chat_open_scope_streetwear_and_offtopic():
    """Проверка директивы Open Scope: консультация по streetwear-стилю и ответ на отвлеченные вопросы"""
    # 1. Streetwear / стиль
    payload_style = {
        "messages": [
            {"role": "user", "content": "Посоветуй крутой streetwear-аутфит с оверсайз худи под очки Meta Fury"}
        ]
    }
    res = client.post("/api/chat", json=payload_style)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    reply = data["reply"].lower()
    # Консультант дает развернутый ответ по стилю и аутфиту
    assert any(w in reply for w in ["streetwear", "аутфит", "худи", "fury", "стил", "лук", "кроссовк", "карго"])
    assert len(data["reply"]) > 50

    # 2. Бытовой / отвлеченный вопрос (Open Scope: не отказывает и отвечает остроумно от AbooOptika)
    payload_offtopic = {
        "messages": [
            {"role": "user", "content": "Как сегодня одеться для прогулки по городу?"}
        ]
    }
    res_off = client.post("/api/chat", json=payload_offtopic)
    assert res_off.status_code == 200
    data_off = res_off.json()
    assert data_off["success"] is True
    assert len(data_off["reply"]) > 40
    assert "aboooptika" in data_off["reply"].lower()

def test_ai_chat_anti_loop_and_continuous_dialog_history():
    """Проверка директив Anti-Loop и Dynamic Context: сохранение истории диалога и исключение сброса на дефолтное приветствие"""
    from app.services.chat_service import ChatService
    from app.models.face_analysis import ChatMessage

    # 1. Форматирование истории: очистка, удаление изолированного системного приветствия, чередование
    raw_history = [
        ChatMessage(role="assistant", content="Здравствуйте! Я стилист AbooOptika."),
        ChatMessage(role="user", content="Меня зовут Алибек, я ищу очки для спорта."),
        ChatMessage(role="assistant", content="Отлично, Алибек! Рекомендую Oakley Vanguard."),
        ChatMessage(role="user", content="Какая цена у этой модели в тенге?")
    ]
    gemini_contents = ChatService._format_gemini_contents(raw_history)
    assert gemini_contents[0]["role"] == "user"
    assert "Алибек" in gemini_contents[0]["parts"][0]["text"]
    assert len(gemini_contents) == 3
    assert gemini_contents[1]["role"] == "model"
    assert gemini_contents[2]["role"] == "user"

    # 2. Непрерывность диалога: второй ход не должен сбрасываться на шаблонное дефолтное приветствие
    payload_multiturn = {
        "messages": [
            {"role": "assistant", "content": "Здравствуйте! Я персональный ИИ-стилист AbooOptika."},
            {"role": "user", "content": "Меня зовут Алибек, порекомендуй спортивную модель очков."},
            {"role": "assistant", "content": "Очень приятно, Алибек! Рассмотрите Oakley Vanguard или Meta Fury."},
            {"role": "user", "content": "Напомни, как меня зовут, и какая цена у Vanguard?"}
        ]
    }
    res = client.post("/api/chat", json=payload_multiturn)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    reply = data["reply"]
    # Не сбрасывается на дефолтное первое приветствие
    assert "Я ваш персональный ИИ-консультант по всей коллекции смарт-очков Meta 2025 года.\n\nУ нас представлены все 25" not in reply
    assert len(reply) > 30

def test_ai_chat_rayban_meta_gen3_direct_answer_after_greeting():
    """
    Тест конкретного сценария из ТЗ:
    При отправке вопроса 'расскажи мне про рейбан мета ген 3' сразу после первичного
    приветствия виджета ИИ обязан ответить конкретно про модель Gen 3 / Zena,
    НЕ присылая дефолтное приветствие с общим описанием 25 моделей.
    """
    payload = {
        "messages": [
            {
                "role": "assistant",
                "content": "Здравствуйте! Я персональный ИИ-стилист и эксперт AbooOptika.\n\nЯ знаю все 25 моделей смарт-очков Meta...\nЧем я могу помочь вам прямо сейчас?"
            },
            {
                "role": "user",
                "content": "расскажи мне про рейбан мета ген 3"
            }
        ]
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    reply = data["reply"]

    # Проверка изоляции приветствия: никакого дефолтного вступительного перечисления
    assert "Приветствую вас в салоне" not in reply
    assert "У нас представлены все 25 актуальных моделей" not in reply
    assert "Культовые классические: Ray-Ban Meta Wayfarer" not in reply

    # Проверка экспертного ответа по модели Ray-Ban Meta Gen 3
    reply_low = reply.lower()
    assert any(term in reply_low for term in ["gen 3", "ген 3", "zena", "третье", "2025"])
    assert any(term in reply_low for term in ["245 000", "ultra-wide", "камер", "тенге", "₸", "open-ear"])

def test_ai_chat_dialogue_context_preservation_across_turns():
    """
    Тест сохранения контекста и истории сообщений (Chat History):
    Пользователь задает короткий уточняющий вопрос 'а сколько они стоят?',
    и ИИ отвечает на основе контекста предыдущей реплики без сброса на дефолтные фразы.
    """
    payload = {
        "messages": [
            {"role": "assistant", "content": "Здравствуйте! Чем могу помочь?"},
            {"role": "user", "content": "Расскажи про модель Ray-Ban Meta Zena Gen 3"},
            {"role": "assistant", "content": "Ray-Ban Meta Zena (Gen 3) — это новинка 2025 года с формой кошачий глаз и камерой 3K."},
            {"role": "user", "content": "А сколько они стоят?"}
        ]
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    reply = data["reply"]

    # Ответ должен содержать цену обсуждаемой модели (Zena Gen 3 = 245 000 ₸)
    assert "Приветствую вас в салоне" not in reply
    assert "245 000" in reply or "тенге" in reply.lower() or "₸" in reply
