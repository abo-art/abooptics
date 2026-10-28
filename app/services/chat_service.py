import os
import re
import json
import logging
from typing import Dict, Any, Optional, List
import httpx
from dotenv import load_dotenv

from app.models.face_analysis import ChatMessage, ChatResponse
from app.services.catalog_service import CatalogService

load_dotenv()
logger = logging.getLogger(__name__)

GEMINI_MODELS = [
    "gemini-3-flash-preview",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest"
]


class ChatService:
    """
    Интеллектуальный ИИ-консультант и стилист сети салонов AbooOptika.
    Обеспечивает диалоговое консультирование клиентов по всему каталогу
    смарт-очков Meta, стилю, моде, streetwear-аутфитам и биометрии лица.
    """

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        key = os.getenv("GEMINI_API_KEY")
        if key:
            key = key.strip()
        return key or None

    @classmethod
    def generate_reply(
        cls,
        messages: List[ChatMessage],
        client_context: Optional[Dict[str, Any]] = None,
        language: Optional[str] = "ru"
    ) -> ChatResponse:
        """
        Генерирует экспертный ответ консультанта AbooOptika.
        При наличии ключа обращается к Gemini API с передачей всей истории диалога,
        при отсутствии или ошибке задействует экспертный локальный движок.
        Поддерживает мультиязычность (RU и EN) для международного жюри.
        """
        api_key = cls.get_api_key()
        last_user_message = ""
        for m in reversed(messages):
            if m.role == "user":
                last_user_message = m.content
                break

        if not api_key:
            logger.info("GEMINI_API_KEY отсутствует, задействован локальный экспертный движок чата AbooOptika.")
            fallback_text, suggested = cls._generate_fallback_reply(last_user_message, client_context, messages, language)
            return ChatResponse(success=True, reply=fallback_text, suggested_prompts=suggested)

        system_instruction = cls._build_system_instruction(client_context, language)
        contents = cls._format_gemini_contents(messages)

        # Вызов Gemini API с поддержкой непрерывного диалога через приоритетный список моделей
        for model in GEMINI_MODELS:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                payload = {
                    "systemInstruction": {
                        "parts": [{"text": system_instruction}]
                    },
                    "contents": contents,
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 2000
                    }
                }

                with httpx.Client(timeout=6.0) as client:
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                reply_text = parts[0]["text"].strip()
                                suggested = cls._extract_or_generate_prompts(reply_text, client_context, language)
                                return ChatResponse(
                                    success=True,
                                    reply=reply_text,
                                    suggested_prompts=suggested
                                )
                    else:
                        logger.warning(f"Gemini Chat API ({model}) вернул статус {resp.status_code}: {resp.text[:150]}")
            except Exception as e:
                logger.warning(f"Ошибка вызова Gemini Chat API ({model}): {e}")

        # Безопасный экспертный fallback при сбое сети
        fallback_text, suggested = cls._generate_fallback_reply(last_user_message, client_context, messages, language)
        return ChatResponse(success=True, reply=fallback_text, suggested_prompts=suggested)

    @classmethod
    def _build_system_instruction(
        cls,
        client_context: Optional[Dict[str, Any]] = None,
        language: Optional[str] = "ru"
    ) -> str:
        """
        Формирует системный промпт консультанта AbooOptika
        с жестким соблюдением директив Open Scope, Anti-Loop и Dynamic Context.
        """
        catalog_frames = CatalogService.get_all_frames()
        catalog_summary = []
        for f in catalog_frames:
            catalog_summary.append(
                f"- {f['name']} ({f.get('generation', '')}, {f.get('shape_name_ru', f['shape'])}): "
                f"размеры {f.get('dimensions', '')} мм, {f.get('material', '')}, {f.get('color', '')}. "
                f"Камера: {f.get('camera', 'нет')}, Аудио: {f.get('audio', '')}. "
                f"Цена: {f.get('price', 0):,} ₸. Особенности: {f.get('optometric_notes', '')}"
            )
        catalog_text = "\n".join(catalog_summary)

        context_text = "Биометрический статус: сканирование лица клиентом еще не проводилось. Не навязывай сканирование, если клиент сам не просит о подборе по лицу."
        if client_context:
            parts = []
            if client_context.get("face_shape_ru"):
                parts.append(f"Форма лица: {client_context['face_shape_ru']}")
            metrics = client_context.get("metrics") or {}
            if metrics:
                parts.append(
                    f"Метрики: длина/скулы {metrics.get('height_to_width_ratio', '')}, "
                    f"челюсть/скулы {metrics.get('jaw_to_cheek_ratio', '')}, "
                    f"угол челюсти {metrics.get('chin_sharpness_deg', '')}°"
                )
            worn = client_context.get("worn_frame") or {}
            if worn:
                if worn.get("has_glasses"):
                    parts.append(f"Текущая примерка: оправа «{worn.get('detected_shape_name_ru', '')}», статус: {worn.get('match_badge', '')}")
                else:
                    parts.append("Клиент сканировал лицо БЕЗ очков (первичный анатомический подбор)")
            if client_context.get("top_recommendations"):
                parts.append(f"Рекомендованные модели: {', '.join(client_context['top_recommendations'])}")

            if parts:
                context_text = "АКТУАЛЬНЫЙ БИОМЕТРИЧЕСКИЙ КОНТЕКСТ КЛИЕНТА:\n" + "\n".join(parts)

        return f"""Ты — главный эксперт и ИИ-консультант платформы AbooOptika (сеть премиальных салонов оптики в Казахстане).

1. ПРИНЦИП АБСОЛЮТНОЙ ОТКРЫТОСТИ (OPEN SCOPE):
Ты — главный эксперт и ИИ-консультант платформы AbooOptika. Твоя задача — отвечать на ЛЮБЫЕ, абсолютно любые вопросы пользователя.
- Если вопрос касается каталога Meta, оптики, биометрии лица — давай глубокий экспертный ответ.
- Если вопрос касается стиля, моды, streetwear-аутфитов — консультируй как стилист: подбирай готовые образы (худи, брюки-карго, бомберы, кроссовки, сочетания цветов и фактур), подсказывай, какие очки идеально завершат аутфит.
- Если вопрос отвлеченный, бытовой или вообще не связан с очками — не отказывай и не зацикливайся на шаблонах. Отвечай на любой вопрос остроумно, полезно, развернуто и по делу от лица бренда AbooOptika.

2. ИЗОЛЯЦИЯ ПРИВЕТСТВИЯ И СТРОГИЙ ЗАПРЕТ НА ВВОДНЫЕ ШАБЛОНЫ (STRICT NO-GREETING RULE):
Приветственное сообщение с представлением ИИ-консультанта и общим описанием ассортимента УЖЕ ПОКАЗАНО пользователю при открытии нового сеанса чата.
- КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО генерировать приветственные фразы («Приветствую вас в салоне AbooOptika...», «Здравствуйте! Я ваш персональный ИИ-консультант...», «Рад вас приветствовать...»).
- КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО каждый раз выводить шаблонное перечисление ассортимента («У нас представлены все 25 актуальных моделей...: Культовые классические, Лимитированные...»).
- СРАЗУ, с первого же предложения, отвечай непосредственно на заданный вопрос пользователя, опираясь на текущий контекст диалога и базу знаний каталога AbooOptika.
- Запрещено в каждом сообщении требовать сканировать лицо или распечатать талон. Ссылайся на биометрию только тогда, когда это органично связано с подбором очков.
- Формулируй мысли свежо, используй богатый словарный запас, тонкую иронию и дружелюбный тон.

3. НЕПРЕРЫВНЫЙ ДИАЛОГ И УЧЕТ ИСТОРИИ (CHAT HISTORY & CONTINUOUS DIALOGUE):
Все последующие сообщения пользователя должны обрабатываться в режиме диалога, где ты отвечаешь непосредственно на заданный вопрос, опираясь на текущий контекст и системный промпт, без повтора вводных фраз.
- Внимательно следи за нитью разговора: если пользователь задает короткие или уточняющие вопросы («а сколько они стоят?», «а какие цвета?», «а они подойдут мне?»), понимай, о какой именно модели шла речь в предыдущих сообщениях, и развивай беседу без сброса на дефолтные фразы.

4. ЯЗЫК, ФОРМАТИРОВАНИЕ И БРЕНД ABOOOPTIKA (MULTILINGUAL RU / EN):
- Всегда общайся на том языке, на котором пишет пользователь (русский или английский).
- IF THE USER COMMUNICATES IN ENGLISH (or if UI language is 'en'):
  • Respond in natural, fluent, elegant, and professional English.
  • Keep the same strict no-greeting and continuous dialogue rules (no introductory templates, start directly with the answer).
  • When discussing prices, ALWAYS provide both Kazakhstani Tenge (₸) and approximate USD equivalent (~$USD at ~500 KZT/USD) so American hackathon judges and international clients easily understand (e.g., "185,000 ₸ (~$370 USD)", "245,000 ₸ (~$490 USD)", "290,000 ₸ (~$580 USD)", "350,000 ₸ (~$700 USD)").
- Если пользователь пишет на русском: общайся на грамотном, естественном русском языке. Цены указывай в тенге (₸).
- Структурируй ответы: применяй абзацы, списки, выделяй ключевые мысли и названия моделей **жирным шрифтом**.
- Твой бренд — **AbooOptika**. Никогда не используй сторонние технические обозначения вроде «Smart Meta Lab» или «Gemini 3.5 Flash Lite».

{context_text}

БАЗА ЗНАНИЙ КАТАЛОГА СМАРТ-ОЧКОВ META (25 МОДЕЛЕЙ ABOOOPTIKA):
{catalog_text}
"""

    @classmethod
    def _format_gemini_contents(cls, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """
        Конвертирует историю сообщений в формат Gemini API (role: user / model).
        Обеспечивает непрерывность диалога:
        - Исключает сброс на дефолтное приветствие
        - Очищает пустые реплики
        - Обеспечивает корректный старт сессии с реплики 'user'
        - Объединяет последовательные реплики одной роли для строгого чередования (alternating turns)
        """
        raw: List[tuple[str, str]] = []
        for msg in messages:
            content = (msg.content or "").strip()
            if not content:
                continue
            role = "user" if msg.role == "user" else "model"
            raw.append((role, content))

        if not raw:
            return [{"role": "user", "parts": [{"text": "Здравствуйте! Расскажите, чем может помочь консультант AbooOptika."}]}]

        # Если первая реплика — системное приветствие модели из UI, а за ним следуют реплики пользователя,
        # начинаем диалог с реплики пользователя для строгого соблюдения спецификации Gemini API
        if raw[0][0] == "model":
            if len(raw) > 1:
                raw = raw[1:]
            else:
                raw = [("user", "Здравствуйте! Чем может помочь консультант AbooOptika?")]

        # Объединение последовательных реплик одной роли для предотвращения ошибок Gemini
        merged: List[Dict[str, Any]] = []
        for role, text in raw:
            if merged and merged[-1]["role"] == role:
                merged[-1]["parts"][0]["text"] += f"\n\n{text}"
            else:
                merged.append({"role": role, "parts": [{"text": text}]})

        # Гарантируем, что диалог в contents начинается с роли user
        if merged and merged[0]["role"] != "user":
            merged.insert(0, {"role": "user", "parts": [{"text": "Здравствуйте!"}]})

        return merged

    @classmethod
    def _extract_or_generate_prompts(
        cls,
        reply_text: str,
        client_context: Optional[Dict[str, Any]] = None,
        language: Optional[str] = "ru"
    ) -> List[str]:
        """Генерирует 3-4 релевантных кликабельных подсказки для продолжения диалога на соответствующем языке (RU или EN)."""
        low = reply_text.lower()
        is_en = (language == "en") or bool(re.search(r'[a-zA-Z]{4,}', reply_text) and not re.search(r'[а-яА-ЯёЁ]{4,}', reply_text))

        if is_en:
            if "gen 3" in low or "zena" in low:
                return [
                    "How much is Ray-Ban Meta Zena Gen 3 in USD?",
                    "What is the difference between Gen 2 and Gen 3?",
                    "Which colors are available for Zena Gen 3?",
                    "Can I install prescription lenses?"
                ]
            elif "wayfarer" in low or "headliner" in low or "skyler" in low:
                return [
                    "Compare Wayfarer and Headliner",
                    "Which size should I pick: 50 or 53?",
                    "How to book an in-store trial fitting?",
                    "How much are Transitions GEN S lenses?"
                ]
            elif "streetwear" in low or "outfit" in low or "style" in low or "hoodie" in low or "sneaker" in low:
                return [
                    "Which outfit matches Ray-Ban Meta Wayfarer?",
                    "How to pair glasses with an oversized hoodie?",
                    "Recommend accessories for this look",
                    "Which glasses fit a smart-casual office look?"
                ]
            elif "lisa" in low:
                return [
                    "How much is Adventurer LISA Edition in USD?",
                    "Difference between Capri and Adventurer?",
                    "Audio-only glasses without camera",
                    "How to reserve a trial fitting at AbooOptika?"
                ]
            elif "audio" in low or "clubmaster" in low or "burbank" in low or "sound" in low:
                return [
                    "Compare Clubmaster Audio and Burbank Audio",
                    "Can prescription lenses be installed?",
                    "How does open-ear audio sound outdoors?",
                    "Battery talk-time life?"
                ]
            elif "fury" in low or "vanguard" in low or "sport" in low or "oakley" in low:
                return [
                    "Tell me about Oakley Meta Vanguard",
                    "What camera is inside Meta Fury?",
                    "Weight of Swiss TR90 polymer frames?",
                    "Book an in-store trial fitting"
                ]
            elif "lens" in low or "transition" in low or "prescription" in low:
                return [
                    "How do Transitions GEN S lenses work?",
                    "Can prescription lenses be installed?",
                    "Are polarized sun lenses available?",
                    "How long does lens production take?"
                ]
            elif "price" in low or "cost" in low or "usd" in low or "dollar" in low or "tenge" in low or "₸" in low:
                return [
                    "Tell me about Ray-Ban Meta Wayfarer",
                    "How much is Ray-Ban Meta Zena Gen 3?",
                    "What makes LISA Edition special?",
                    "How to book an in-store trial?"
                ]
            elif client_context and client_context.get("face_shape_ru"):
                shape = client_context.get("face_shape_en") or client_context["face_shape_ru"]
                return [
                    f"Why is this frame optimal for {shape}?",
                    "Are Transitions GEN S lenses available?",
                    "Show Oakley Meta sport models",
                    "Print fitting slip for consultant"
                ]
            else:
                return [
                    "Tell me about Ray-Ban Meta Gen 3",
                    "Recommend smart glasses for my face shape",
                    "Audio-only glasses without cameras for office",
                    "How much do top models cost in USD?"
                ]

        # Русские подсказки
        if "gen 3" in low or "ген 3" in low or "zena" in low:
            return [
                "Сколько стоят Ray-Ban Meta Zena Gen 3?",
                "В чем разница между Gen 2 и Gen 3?",
                "Какие цвета доступны для Zena Gen 3?",
                "Можно ли поставить линзы с диоптриями?"
            ]
        elif "wayfarer" in low or "headliner" in low or "skyler" in low or "вайфарер" in low:
            return [
                "Сравни Wayfarer и Headliner",
                "Какой размер Wayfarer выбрать: 50 или 53?",
                "Как записаться на примерку в салон?",
                "Сколько стоят линзы Transitions GEN S?"
            ]
        elif "streetwear" in low or "аутфит" in low or "стил" in low or "лук" in low or "худи" in low or "кроссовк" in low:
            return [
                "Какой аутфит подойдет под Ray-Ban Meta Wayfarer?",
                "Как сочетать очки с оверсайз худи и карго?",
                "Посоветуй аксессуары к образу",
                "Какие очки впишутся в деловой smart-casual?"
            ]
        elif "lisa" in low:
            return [
                "Сколько стоит Adventurer LISA Edition?",
                "В чем разница между Capri и Adventurer?",
                "Посоветуй очки со звуком без камеры",
                "Как забронировать примерку в AbooOptika?"
            ]
        elif "аудио" in low or "clubmaster" in low or "burbank" in low or "динамик" in low or "звук" in low:
            return [
                "Сравни Clubmaster Audio и Burbank Audio",
                "Можно ли вставить диоптрийные линзы?",
                "Как звучат open-ear динамики на улице?",
                "Сколько часов они работают без подзарядки?"
            ]
        elif "fury" in low or "vanguard" in low or "спортивн" in low:
            return [
                "Подробнее про спортивные Oakley Vanguard",
                "Какая камера установлена в Meta Fury?",
                "Какой вес у оправы из швейцарского TR90?",
                "Как записаться на примерку в салон?"
            ]
        elif "линз" in low or "transition" in low or "диоптри" in low:
            return [
                "Как работают линзы Transitions GEN S?",
                "Можно ли поставить рецептурные линзы с диоптриями?",
                "Есть ли поляризационные линзы от солнца?",
                "Сколько времени занимает изготовление линз?"
            ]
        elif "цен" in low or "стоим" in low or "тенге" in low or "₸" in low:
            return [
                "Подробнее про Ray-Ban Meta Wayfarer",
                "Сколько стоят очки Ray-Ban Meta Zena Gen 3?",
                "В чем особенность серии LISA Edition?",
                "Как оформить бронь на примерку?"
            ]
        elif client_context and client_context.get("face_shape_ru"):
            shape = client_context["face_shape_ru"]
            return [
                f"Почему эта форма подходит для {shape}?",
                "Есть ли модели с фотохромными линзами Transitions?",
                "Покажи спортивные модели Oakley Meta",
                "Распечатать талон для консультанта в зале"
            ]
        else:
            return [
                "Расскажи про Ray-Ban Meta Gen 3",
                "Подбери смарт-очки под мой стиль",
                "Очки со звуком без видеокамер для офиса",
                "Сколько стоят топовые модели в тенге (₸)?"
            ]

    @classmethod
    def _generate_fallback_reply(
        cls,
        user_message: str,
        client_context: Optional[Dict[str, Any]] = None,
        messages: Optional[List[ChatMessage]] = None,
        language: Optional[str] = "ru"
    ) -> tuple[str, List[str]]:
        """
        Интеллектуальный экспертный локальный движок AbooOptika.
        Обеспечивает строгое соблюдение требований ТЗ и мультиязычность (RU и EN):
        - Приветствие изолировано (показывается только один раз при открытии виджета)
        - Никаких шаблонных вводных фраз и перечислений ассортимента
        - Прямой и точный ответ на заданный вопрос пользователя
        - Сохранение контекста и истории всей переписки
        - Автоматическая поддержка английского языка для международного жюри с ценами в ₸ и USD.
        """
        msg = user_message.lower().strip()
        face_shape_ru = client_context.get("face_shape_ru", "вашего лица") if client_context else "вашего типа лица"
        face_shape_en = client_context.get("face_shape_en", "your face shape") if client_context else "your face shape"

        # Детекция английского языка: параметр language == 'en' ИЛИ наличие английских слов без кириллицы
        is_en = (
            language == "en"
            or (client_context and client_context.get("language") == "en")
            or bool(re.search(r'[a-zA-Z]{3,}', user_message) and not re.search(r'[а-яА-ЯёЁ]{3,}', user_message))
        )

        # =========================================================================
        # 1. АНГЛИЙСКИЙ ЯЗЫК (ENGLISH ENGINE FOR US HACKATHON JURY & CLIENTS)
        # =========================================================================
        if is_en:
            is_gen3_en = (
                any(w in msg for w in ["gen 3", "gen3", "zena", "orion", "third generation", "3rd gen", "generation 3"])
                or ("meta" in msg and "3" in msg)
                or ("rayban" in msg and "3" in msg)
                or ("ray-ban" in msg and "3" in msg)
                or ("glasses" in msg and "3" in msg)
            )
            if is_gen3_en:
                reply = (
                    "The third-generation flagship smart glasses **Ray-Ban Meta Gen 3 (2025)** at **AbooOptika** "
                    "are headlined by **Ray-Ban Meta Zena (Gen 3)** (245,000 ₸ / ~$490 USD):\n\n"
                    "• **Design & Ergonomics**: Trendsetting geometric cat-eye silhouette (dimensions: 52-21-145 mm), ultralight aerospace polymer frame weighing just 47 grams. Available in classic Shiny Black and caramel transparencies.\n"
                    "• **12 MP Ultra-Wide Camera**: 122° field-of-view sensor with enhanced low-light optics and stabilized first-person 3K video recording.\n"
                    "• **Studio Acoustics & Microphones**: 5-mic directional array with active wind suppression and custom open-ear speakers with 35% deeper bass than Gen 2.\n"
                    "• **Battery & Fast Charge**: Up to 6 hours continuous runtime and up to 36 hours with the leather charging case (fast charge: 50% in 20 minutes).\n"
                    "• **Multimodal Meta AI**: Instant voice assistance for visual identification, real-time sight translation, and hands-free notes.\n\n"
                    "The Gen 3 lineup also includes the futuristic holographic prototype with full MicroLED waveguide displays — **Meta Orion** (650,000 ₸ / ~$1,300 USD)."
                )
                prompts = [
                    "How much is Ray-Ban Meta Zena Gen 3 in USD?",
                    "What is the difference between Gen 2 and Gen 3?",
                    "Which colors are available for Zena Gen 3?",
                    "Can I install prescription lenses?"
                ]

            elif any(w in msg for w in ["wayfarer", "headliner", "skyler", "stories", "gen 2", "gen2", "second gen"]):
                reply = (
                    "The iconic **Ray-Ban Meta (Gen 2)** collection represents the gold standard of daily smart eyewear at **AbooOptika**:\n\n"
                    "• **Ray-Ban Meta Wayfarer** (from 185,000 ₸ / ~$370 USD) — The timeless trapezoidal silhouette. Available in Standard (50-22) and Large (53-22). Features 12 MP camera, 5 microphones, open-ear audio, and temple touchpad.\n"
                    "• **Ray-Ban Meta Headliner** (190,000 ₸ / ~$380 USD) — Rounded frame with a keyhole bridge (50-23), ideal for square and angular faces.\n"
                    "• **Ray-Ban Meta Skyler** (195,000 ₸ / ~$390 USD) — Sophisticated vintage cat-eye silhouette (52-20) tailored for narrow to medium faces.\n\n"
                    "All models record 1080p vertical video for Instagram and TikTok, stream music via open-ear speakers, and handle crystal-clear phone calls with directional beamforming."
                )
                prompts = [
                    "Compare Wayfarer vs Headliner",
                    "Should I get Wayfarer size 50 or 53?",
                    "How do I book a salon fitting?",
                    "How much are Transitions GEN S lenses?"
                ]

            elif any(w in msg for w in ["streetwear", "outfit", "style", "hoodie", "cargo", "sneaker", "fashion", "look", "cloth"]):
                reply = (
                    "As **AbooOptika's** personal AI stylist, smart glasses are the ultimate statement accessory to elevate your complete outfit! 🔥\n\n"
                    "Here are our curated styling formulas:\n\n"
                    "1. **Modern Streetwear & Techwear**:\n"
                    "• Frames: Translucent icy **Meta Fury Limited Edition** (350,000 ₸ / ~$700 USD) or aerodynamic **Oakley Vanguard** (270,000 ₸ / ~$540 USD).\n"
                    "• Outfit: Heavyweight charcoal oversized hoodie, tactical nylon cargo trousers with utilitarian straps, and a boxy puffer vest.\n"
                    "• Footwear: Technical trail sneakers (Salomon XT-6, Roa Hiking, or Asics Gel-Kayano 14).\n\n"
                    "2. **Clean Minimalist / Old Money**:\n"
                    "• Frames: Classic **Ray-Ban Meta Wayfarer** in Shiny Black (185,000 ₸ / ~$370 USD) or **Clubmaster Audio** (175,000 ₸ / ~$350 USD).\n"
                    "• Outfit: Tailored relaxed wool overcoat, heavyweight crewneck knit sweater, straight-leg pleat chinos.\n"
                    "• Footwear: Minimalist leather court sneakers or suede penny loafers.\n\n"
                    "3. **High-Fashion Statement**:\n"
                    "• Frames: Burgundy and gold **Meta Capri LISA Edition** (295,000 ₸ / ~$590 USD).\n"
                    "• Outfit: Oversized distressed leather bomber, relaxed raw denim, and subtle gold accents matching frame hardware."
                )
                prompts = [
                    "Which glasses match my personal style?",
                    "Tell me more about Meta Capri LISA Edition",
                    "Which model works with business suits?",
                    "How do I book a salon styling session?"
                ]

            elif any(w in msg for w in ["lisa", "limited", "capri", "adventurer"]):
                reply = (
                    "The limited-edition **LISA Edition** is Meta's premier luxury collaboration, blending haute couture aesthetics with cutting-edge smart technology:\n\n"
                    "1. **Meta Adventurer LISA Edition** (290,000 ₸ / ~$580 USD) — High-gloss Shiny Black acetate with Rose Gold micro-engraved hinges. Balanced classic square geometry (54-19-145).\n"
                    "2. **Meta Capri LISA Edition** (295,000 ₸ / ~$590 USD) — Expressive cat-eye silhouette in rich Burgundy Tortoise with 24K gold hardware accents.\n\n"
                    "Both models feature the 12 MP Ultra-wide camera, 5-microphone beamforming array, and custom debossed leather rapid-charging cases. Available in limited quantities at AbooOptika boutiques."
                )
                prompts = [
                    "Does Capri LISA suit my face shape?",
                    "Compare Adventurer LISA vs Wayfarer",
                    "How do I reserve a fitting at AbooOptika?",
                    "What other limited editions are available?"
                ]

            elif any(w in msg for w in ["audio", "sound", "speaker", "no camera", "without camera", "clubmaster", "burbank"]):
                reply = (
                    "For professional workplace environments, confidential meetings, and strict business dress codes without cameras, Meta offers two dedicated audio smart frames:\n\n"
                    "1. **Ray-Ban Meta Clubmaster Audio Edition** (175,000 ₸ / ~$350 USD) — Heritage Browline silhouette (51-21-145) with gold metallic rim and black upper brow.\n"
                    "2. **Ray-Ban Meta Burbank Audio Edition** (170,000 ₸ / ~$340 USD) — Sleek rectangular frame (54-20-145) in Havana Tortoise.\n\n"
                    "Both models feature custom directional open-ear acoustic drivers with deep bass and wind-cancellation mics for phone calls, with zero cameras or recording LEDs."
                )
                prompts = [
                    "Can I install prescription lenses?",
                    "How long does the talk time battery last?",
                    "Compare Clubmaster Audio and Burbank Audio",
                    "Match a model to my face shape"
                ]

            elif any(w in msg for w in ["fury", "vanguard", "sport", "oakley", "translucent", "ice", "display", "ar", "orion"]):
                reply = (
                    "At the forefront of eyewear innovation, **AbooOptika** presents high-performance smart frames:\n\n"
                    "• **Meta Fury (Limited Edition)** (350,000 ₸ / ~$700 USD) — Semi-transparent Crystal Ice chassis crafted from Swiss TR90 (46g total weight), 12 MP Ultra-wide camera with electronic stabilization, and touchpad navigation.\n"
                    "• **Oakley Meta Vanguard** (270,000 ₸ / ~$540 USD) — Aerodynamic shield lens with Unobtainium grip earsocks and IPX4 weatherproofing.\n"
                    "• **Meta Orion (AR Holographic Display)** (650,000 ₸ / ~$1,300 USD) — Prototype with MicroLED projectors, 70° holographic field of view, and neural wristband control.\n\n"
                    "Each model is available for private demonstration in our flagship boutiques."
                )
                prompts = [
                    "How does the AR display in Meta Orion work?",
                    "Difference between Fury and Oakley Vanguard?",
                    "Book an in-store trial fitting",
                    "Match smart glasses to my face shape"
                ]

            elif any(w in msg for w in ["lens", "transition", "prescription", "diopter", "photochromic", "vision"]):
                reply = (
                    "All smart glasses in the **AbooOptika** collection support custom prescription and sun lens installation:\n\n"
                    "• **Transitions® GEN S™** — Next-generation ultra-responsive photochromic lenses (activate in 25 seconds, fade back in 2 minutes indoors).\n"
                    "• **Prescription Rx Lenses** (from -12.00 to +8.00 D) with premium anti-reflective, oleophobic, and hydrophobic coatings.\n"
                    "• **Polarized Blue-Blocker** — Glare-free driving lenses with harmful digital screen blue-light filtering.\n\n"
                    "Our in-store optometrists custom-grind and mount each lens while preserving full Meta factory warranty."
                )
                prompts = [
                    "How much are Transitions GEN S lenses?",
                    "Can smart glasses handle astigmatism?",
                    "Which colors are available for Transitions?",
                    "Book an optical examination"
                ]

            elif any(w in msg for w in ["price", "cost", "how much", "usd", "dollar", "tenge", "kzt", "buy", "order"]):
                reply = (
                    "Official pricing catalogue for Meta smart glasses at **AbooOptika** (in KZT ₸ and approximate USD):\n\n"
                    "• **Ray-Ban Stories (Gen 1)**: From 115,000 ₸ (~$230 USD)\n"
                    "• **Audio-Only Series (No Cameras)**: 170,000 ₸ (~$340 USD) for Burbank Audio, 175,000 ₸ (~$350 USD) for Clubmaster Audio\n"
                    "• **Ray-Ban Meta (Gen 2)**: 185,000 ₸ (~$370 USD) for Wayfarer, up to 195,000 ₸ (~$390 USD) for Headliner / Skyler\n"
                    "• **Gen 3 Flagships (2025)**: 245,000 ₸ (~$490 USD) for Ray-Ban Meta Zena\n"
                    "• **Oakley Meta Performance**: 220,000 ₸ (~$440 USD) for HSTN, 270,000 ₸ (~$540 USD) for Vanguard\n"
                    "• **Limited Editions**: 290,000 ₸ (~$580 USD) for Adventurer LISA, 295,000 ₸ (~$590 USD) for Capri LISA, 350,000 ₸ (~$700 USD) for Meta Fury\n"
                    "• **AR Waveguide Concept**: 650,000 ₸ (~$1,300 USD) for Meta Orion\n\n"
                    "All purchases include official manufacturer warranty, leather charging case, fast-charging cable, and custom in-salon optical alignment."
                )
                prompts = [
                    "Tell me about Ray-Ban Meta Wayfarer",
                    "How much is Ray-Ban Meta Zena Gen 3?",
                    "What is special about the LISA Edition?",
                    "How can I book a salon trial fitting?"
                ]

            elif any(w in msg for w in ["face", "shape", "fit", "jaw", "cheek", "recommend", "size", "caliber"]):
                reply = (
                    f"Based on optical harmonization principles for **{face_shape_en}**, the ideal balance is achieved through geometric contrast:\n\n"
                    "• **Square Face**: Soft rounded silhouettes like **Ray-Ban Meta Headliner** (50-23, 190,000 ₸ / ~$380 USD) or panto **Meta Nova** soften a strong angular jawline.\n"
                    "• **Round Face**: Structured angular silhouettes like **Ray-Ban Meta Wayfarer** (50-22 / 53-22, 185,000 ₸ / ~$370 USD) or **Meta Adventurer** visually elongate the facial oval.\n"
                    "• **Oval Face**: Universally balanced proportions. Suits almost all silhouettes, especially **Meta Capri** (210,000 ₸ / ~$420 USD) and titanium **Meta Smart Aviator** (260,000 ₸ / ~$520 USD).\n\n"
                    "You can try any model in our boutique or print your biometric trial slip right now!"
                )
                prompts = [
                    "Tell me more about Ray-Ban Meta Wayfarer",
                    "How do Transitions GEN S lenses work?",
                    "How much is the Orion AR display model?",
                    "Recommend an outfit for smart glasses"
                ]

            elif msg in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "howdy"]:
                reply = (
                    "Hello! How can I assist you right now: explore our **Gen 3** flagships and classic **Wayfarer**, "
                    "match a frame to your facial biometrics, or review pricing and Transitions lenses?"
                )
                prompts = [
                    "Tell me about Ray-Ban Meta Gen 3",
                    "Which glasses match my face shape?",
                    "How much do glasses cost in USD?",
                    "Show me audio-only glasses without cameras"
                ]

            else:
                prev_context = ""
                for prev_m in (messages or []):
                    if prev_m.content:
                        prev_context += " " + prev_m.content.lower()

                if any(k in prev_context for k in ["zena", "gen 3", "gen3"]):
                    reply = (
                        "Regarding the third-generation flagship **Ray-Ban Meta Zena (Gen 3)**: the model is priced at **245,000 ₸ (~$490 USD)**, "
                        "features a 12 MP Ultra-wide camera with 3K stabilized recording, next-generation deep-bass open-ear drivers, "
                        "and weighs just 47 grams. The companion charging case offers up to 36 hours of battery life."
                    )
                elif any(k in prev_context for k in ["wayfarer", "headliner"]):
                    reply = (
                        "Returning to **Ray-Ban Meta Wayfarer** (from 185,000 ₸ / ~$370 USD): available in Standard (50-22) "
                        "and Large (53-22). It includes a 12 MP camera, intuitive temple touchpad, open-ear audio, and supports custom prescription lenses."
                    )
                elif any(k in prev_context for k in ["lisa", "capri", "adventurer"]):
                    reply = (
                        "In the limited-edition **LISA Edition**, we offer **Adventurer LISA** (290,000 ₸ / ~$580 USD, Shiny Black with Rose Gold) "
                        "and **Capri LISA** (295,000 ₸ / ~$590 USD, Burgundy Tortoise with 24K gold). Both include rapid-charge leather cases."
                    )
                elif any(k in prev_context for k in ["fury", "vanguard", "sport"]):
                    reply = (
                        "High-performance models **Oakley Vanguard** (270,000 ₸ / ~$540 USD) and **Meta Fury** (350,000 ₸ / ~$700 USD) are built "
                        "from aerospace TR90 polymer, IPX4 splash-resistant, and ideal for running, cycling, and active lifestyles."
                    )
                else:
                    reply = (
                        "I'd be glad to help! At **AbooOptika**, we specialize in the complete 2025 Meta smart glasses collection, "
                        "optical facial biometrics, and eyewear styling.\n\n"
                        "Could you please specify: are you interested in a particular model (such as the **Gen 3** flagship or classic **Wayfarer**), "
                        "fitting a frame to your facial geometry, prescription lenses, or current pricing in USD / KZT?"
                    )
                prompts = [
                    "Tell me about Ray-Ban Meta Gen 3",
                    "Recommend smart glasses for my style",
                    "How much do top models cost in USD?",
                    "Audio-only glasses without cameras for office"
                ]

            return reply, prompts

        # =========================================================================
        # 2. РУССКИЙ ЯЗЫК (RUSSIAN ENGINE)
        # =========================================================================
        # 1. СМАРТ-ОЧКИ ТРЕТЬЕГО ПОКОЛЕНИЯ (RAY-BAN META GEN 3 / ZENA)
        is_gen3 = (
            any(w in msg for w in ["ген 3", "gen 3", "gen3", "3 поколен", "третье поколен", "третьем поколен", "zena", "зена"])
            or ("рейбан" in msg and "3" in msg)
            or ("meta" in msg and "3" in msg)
            or ("очк" in msg and "3" in msg)
            or ("поколен" in msg and "3" in msg)
        )
        if is_gen3:
            reply = (
                "Смарт-очки третьего поколения **Ray-Ban Meta Gen 3 (2025)** в салоне **AbooOptika** представлены флагманской моделью "
                "**Ray-Ban Meta Zena (Gen 3)** (245 000 ₸):\n\n"
                "• **Дизайн и посадка**: Трендовый геометрический «кошачий глаз» (калибр 52-21-145 мм), корпус из ультралегкого инновационного полимера весом всего 47 граммов. Доступны в классическом Shiny Black и полупрозрачных карамельных расцветках.\n"
                "• **Камера 12 MP Ultra-wide**: Угол обзора 122°, сенсор нового поколения с улучшенной ночной съёмкой и записью стабилизированного видео в формате 3K от первого лица.\n"
                "• **Акустика и микрофоны**: 5 студийных микрофонов с активным подавлением шума ветра и кастомные Open-Ear динамики с расширенным басовым диапазоном (на 35% глубже, чем у Gen 2).\n"
                "• **Автономность**: До 6 часов активной работы без подзарядки и до 36 часов с кожаным кейсом-пауэрбанком с функцией быстрой зарядки (50% за 20 минут).\n"
                "• **Интеллектуальные функции**: Мультимодальный Meta AI для распознавания объектов, перевода иностранных текстов перед глазами и голосовых заметок.\n\n"
                "Также в поколение Gen 3 входит футуристический концептуальный прототип с голографическим MicroLED-дисплеем — **Meta Orion** (650 000 ₸)."
            )
            prompts = [
                "Сколько стоят Ray-Ban Meta Zena Gen 3?",
                "В чем разница между Gen 2 и Gen 3?",
                "Какие цвета доступны для Zena Gen 3?",
                "Можно ли поставить линзы с диоптриями?"
            ]

        # 2. КУЛЬТОВЫЕ МОДЕЛИ RAY-BAN META GEN 2 (WAYFARER, HEADLINER, SKYLER)
        elif any(w in msg for w in ["wayfarer", "вайфарер", "headliner", "хедлайнер", "skyler", "скайлер", "stories", "сторис", "рейбан", "ray-ban", "rayban", "ген 2", "gen 2", "gen2", "второ"]):
            reply = (
                "Культовая серия **Ray-Ban Meta (Gen 2)** — флагман повседневного комфорта и смарт-технологий в салоне **AbooOptika**:\n\n"
                "• **Ray-Ban Meta Wayfarer** (от 185 000 ₸) — легендарный трапециевидный силуэт. Доступен в двух калибрах: Standard (50-22) и Large (53-22). 12MP Ultra-wide камера, 5 микрофонов, открытые динамики и сенсорное управление на дужке.\n"
                "• **Ray-Ban Meta Headliner** (190 000 ₸) — округлый силуэт с мостиком Keyhole (50-23), идеален для квадратных и угловатых лиц.\n"
                "• **Ray-Ban Meta Skyler** (195 000 ₸) — изящная ретро-оправа Cat-Eye (52-20) для узких и средних лиц.\n\n"
                "Все модели позволяют снимать видео 1080p вертикально для соцсетей, слушать музыку без наушников и принимать звонки с кристально чистым шумоподавлением."
            )
            prompts = [
                "Сравни Wayfarer и Headliner",
                "Какой размер Wayfarer выбрать: 50 или 53?",
                "Как записаться на примерку в салон?",
                "Сколько стоят линзы Transitions GEN S?"
            ]

        # 3. СТИЛЬ, МОДА, STREETWEAR И АУТФИТЫ
        elif any(w in msg for w in ["стил", "streetwear", "стритвир", "аутфит", "лук", "одежд", "худи", "карго", "кроссовк", "мод"]):
            reply = (
                "Как персональный стилист **AbooOptika**, я всегда говорю: смарт-очки — это не просто гаджет, "
                "а ключевой визуальный акцент всего аутфита! 🔥\n\n"
                "Вот топовые формулы стилизации:\n\n"
                "1. **Modern Streetwear / Techwear**:\n"
                "• Очки: полупрозрачные ледяные **Meta Fury (Limited Edition)** (350 000 ₸) или футуристичные **Oakley Vanguard** (270 000 ₸).\n"
                "• Одежда: оверсайз худи графитового цвета, нейлоновые брюки-карго с акцентными стропами, дутый жилет.\n"
                "• Обувь: трейловые кроссовки (Salomon XT-6, Roa или Asics Gel-Kayano 14).\n\n"
                "2. **Clean Minimalist / Old Money**:\n"
                "• Очки: элегантные **Ray-Ban Meta Wayfarer** (185 000 ₸) в черном глянце или **Clubmaster Audio** (175 000 ₸).\n"
                "• Одежда: шерстяное пальто свободного кроя, плотный вязаный свитер с круглым воротом, прямые брюки чинос.\n"
                "• Обувь: минималистичные кожаные кеды или замшевые лоферы.\n\n"
                "3. **High-Fashion / Statement**:\n"
                "• Очки: бордовые с золотом **Meta Capri LISA Edition** (295 000 ₸).\n"
                "• Одежда: кожаный оверсайз бомбер, широкий деним и лаконичные аксессуары в тон отделке очков."
            )
            prompts = [
                "Как подобрать оправу под мой стиль одежды?",
                "Расскажи подробнее про Meta Capri LISA Edition",
                "Какие очки впишутся в классический офисный костюм?",
                "Как записаться на примерку в AbooOptika?"
            ]

        # 4. СЕРИЯ LISA EDITION
        elif any(w in msg for w in ["lisa", "лиза", "лиса", "лимит"]):
            reply = (
                "Лимитированная серия **LISA Edition** — это эксклюзивная коллаборация Meta, "
                "сочетающая передовые технологии и высокую моду:\n\n"
                "1. **Meta Adventurer LISA Edition** (290 000 ₸) — глубокий глянцевый чёрный цвет Shiny Black "
                "с акцентами цвета розового золота (Rose Gold) на петлях и гравировках. Классический сбалансированный квадрат (54-19-145).\n"
                "2. **Meta Capri LISA Edition** (295 000 ₸) — выразительный силуэт Cat-Eye в оттенке Burgundy Tortoise "
                "(бордовая черепаха) с 24K золотыми деталями.\n\n"
                "Обе модели оснащены 12MP Ultra-wide камерой, 5 микрофонами и футляром из тисненой кожи с функцией быстрой зарядки. "
                "Модели доступны в ограниченном количестве в салонах AbooOptika."
            )
            prompts = [
                "Подойдет ли Capri LISA для моего лица?",
                "Сравнить Adventurer с Wayfarer",
                "Как забронировать примерку в салоне?",
                "Какие еще лимитированные серии есть?"
            ]

        # 5. АУДИО БЕЗ КАМЕР
        elif any(w in msg for w in ["аудио", "звук", "без камер", "clubmaster", "burbank", "динамик"]):
            reply = (
                "Если для вас важна конфиденциальность и деловой дресс-код без видеокамер, "
                "в коллекции Meta представлены две специализированные аудио-модели:\n\n"
                "1. **Ray-Ban Meta Clubmaster Audio Edition** (175 000 ₸) — винтажный силуэт Browline (51-21-145), "
                "золотой металлический ободок и черный верх. Идеален для делового стиля.\n"
                "2. **Ray-Ban Meta Burbank Audio Edition** (170 000 ₸) — строгая прямоугольная оправа (54-20-145) "
                "в черепаховом цвете Havana Tortoise.\n\n"
                "Обе модели оснащены направленными open-ear динамиками с глубоким басом и системой шумоподавления для звонков, "
                "при этом полностью лишены камер и светодиодов записи."
            )
            prompts = [
                "Можно ли установить линзы с диоптриями?",
                "Сколько держит батарея в режиме разговора?",
                "Сравни Clubmaster и Burbank Audio",
                "Подобрать модель под мое лицо"
            ]

        # 6. FURY И ИННОВАЦИОННЫЕ МОДЕЛИ
        elif any(w in msg for w in ["fury", "фьюри", "прозрачн", "vanguard", "orion", "дисплей", "ar"]):
            reply = (
                "В авангарде инноваций **AbooOptika** представлены флагманские смарт-оправы:\n\n"
                "• **Meta Fury (Limited Edition)** (350 000 ₸) — полупрозрачный ледяной корпус Crystal Ice из швейцарского TR90 (вес 46 г), "
                "12MP Ultra-wide камера 122° с электронной стабилизацией и сенсорным управлением.\n"
                "• **Oakley Meta Vanguard** (270 000 ₸) — монолинза со спортивной аэродинамикой, гидрофобным покрытием Unobtainium и защитой IPX4.\n"
                "• **Meta Orion (AR Display)** (650 000 ₸) — концептуальная модель с микро-светодиодными проекторами MicroLED, "
                "голографическим полем зрения 70° и нейроинтерфейсом управления.\n\n"
                "Каждая модель доступна для закрытой демонстрации в наших флагманских салонах."
            )
            prompts = [
                "Как работает AR-дисплей в Meta Orion?",
                "В чем отличие Fury от Oakley Vanguard?",
                "Как забронировать тест-драйв?",
                "Подобрать модель под мой стиль"
            ]

        # 7. ЛИНЗЫ, ДИОПТРИИ И TRANSITIONS
        elif any(w in msg for w in ["линз", "transition", "диоптри", "фотохром", "поляриз", "зрен"]):
            reply = (
                "Все смарт-очки из каталога **AbooOptika** поддерживают профессиональную установку медицинских и солнцезащитных линз:\n\n"
                "• **Transitions® GEN S™** — новейшие ультрабыстрые фотохромные линзы (активация за 25 секунд, полное осветление за 2 минуты в помещении).\n"
                "• **Рецептурные линзы с диоптриями** (от -12.00 до +8.00 D) с антибликовым, олеофобным и гидрофобным покрытием.\n"
                "• **Polarized Blue-Blocker** — линзы с поляризацией для водителей и фильтрацией вредного синего спектра мониторов.\n\n"
                "Наш оптометрический кабинет в салоне изготовит и установит индивидуальные линзы с сохранением заводской гарантии Meta."
            )
            prompts = [
                "Сколько стоит установка линз Transitions?",
                "Подойдут ли смарт-очки при астигматизме?",
                "Какие цвета доступны для линз Transitions?",
                "Записаться на диагностику зрения"
            ]

        # 8. ЦЕНЫ, СТОИМОСТЬ, ТЕНГЕ
        elif any(w in msg for w in ["цена", "цены", "стоим", "почем", "тенге", "₸", "прайс", "купит", "заказ", "скидк"]):
            reply = (
                "Актуальный прайс-лист каталога смарт-очков в салоне **AbooOptika** (в казахстанских тенге ₸):\n\n"
                "• **Ray-Ban Stories (Gen 1)**: от 115 000 ₸ (Meteor, Round Stories)\n"
                "• **Аудио-серии без камер**: от 170 000 ₸ (Burbank Audio) до 175 000 ₸ (Clubmaster Audio)\n"
                "• **Ray-Ban Meta (Gen 2)**: от 185 000 ₸ (Wayfarer) до 195 000 ₸ (Headliner, Skyler)\n"
                "• **Флагманы Gen 3 (2025)**: 245 000 ₸ (Ray-Ban Meta Zena)\n"
                "• **Спортивные Oakley Meta**: от 220 000 ₸ (HSTN) до 270 000 ₸ (Vanguard)\n"
                "• **Лимитированные издания**: 290 000 ₸ (Adventurer LISA), 295 000 ₸ (Capri LISA), 350 000 ₸ (Meta Fury Limited)\n"
                "• **Концепт с AR-дисплеем**: 650 000 ₸ (Meta Orion)\n\n"
                "В стоимость входит официальная гарантия, зарядный футляр, кабель и индивидуальная оптическая юстировка в салоне."
            )
            prompts = [
                "Подробнее про Ray-Ban Meta Wayfarer",
                "Сколько стоят очки Ray-Ban Meta Zena Gen 3?",
                "В чем особенность серии LISA Edition?",
                "Как оформить бронь на примерку?"
            ]

        # 9. ПОДБОР ПО ЛИЦУ И БИОМЕТРИЯ
        elif any(w in msg for w in ["подбор", "подойд", "лицо", "форму", "рекоменд", "размер", "калибр", "скул", "челюст"]):
            reply = (
                f"На основе правил оптической гармонии для **{face_shape_ru}** ключевое значение имеет баланс пропорций:\n\n"
                "• **Квадратное лицо**: округлые силуэты **Ray-Ban Meta Headliner** (50-23, 190 000 ₸) "
                "или панто **Meta Nova** (51-20, 205 000 ₸) смягчают линию челюсти.\n"
                "• **Круглое лицо**: четкие геометрические формы **Ray-Ban Meta Wayfarer** (50-22 / 53-22, 185 000 ₸) "
                "или **Meta Adventurer** (220 000 ₸) визуально вытягивают овал.\n"
                "• **Овальное лицо**: универсальная посадка, идеально смотрятся **Meta Capri** (210 000 ₸) "
                "и титановые **Meta Smart Aviator** (260 000 ₸).\n\n"
                "Вы можете примерить любую понравившуюся оправу или распечатать талон с точными замерами!"
            )
            prompts = [
                "Подробнее про Ray-Ban Meta Wayfarer",
                "Расскажи про линзы Transitions GEN S",
                "Сколько стоят очки с AR-дисплеем Orion?",
                "Подобрать очки под streetwear-аутфит"
            ]

        # 10. КРАТКОЕ ПРИВЕТСТВИЕ (БЕЗ ДЕФОЛТНОГО ОПИСАНИЯ АССОРТИМЕНТА)
        elif msg in ["привет", "здравствуйте", "добрый день", "добрый вечер", "салем", "сәлем"]:
            reply = (
                "Здравствуйте! Чем могу помочь прямо сейчас: рассказать о флагманах **Gen 3** и классике **Wayfarer**, "
                "подобрать оправу под геометрию вашего лица или проконсультировать по ценам и линзам Transitions?"
            )
            prompts = [
                "Расскажи про Ray-Ban Meta Gen 3",
                "Какие очки подойдут для моего лица?",
                "Сколько стоят очки в тенге (₸)?",
                "Посоветуй аудио-версию без камер"
            ]

        # 11. КОНТЕКСТНЫЕ И ОТВЛЕЧЕННЫЕ ВОПРОСЫ (DYNAMIC CONTEXT & OPEN SCOPE)
        else:
            prev_context = ""
            for prev_m in (messages or []):
                if prev_m.content:
                    prev_context += " " + prev_m.content.lower()

            if any(k in prev_context for k in ["zena", "ген 3", "gen 3"]):
                reply = (
                    "Касательно флагмана третьего поколения **Ray-Ban Meta Zena (Gen 3)**: модель стоит **245 000 ₸**, "
                    "оснащена сенсором 12 MP Ultra-wide с 3K видеосъемкой, динамиками Open-Ear нового поколения с глубоким басом "
                    "и весит всего 47 граммов. Зарядный кейс обеспечивает до 36 часов автономности."
                )
            elif any(k in prev_context for k in ["wayfarer", "вайфарер"]):
                reply = (
                    "Возвращаясь к **Ray-Ban Meta Wayfarer** (от 185 000 ₸): модель представлена в размерах Standard (50-22) "
                    "и Large (53-22). Она оснащена 12 MP камерой, сенсорным управлением на дужке и поддерживает установку линз с диоптриями."
                )
            elif any(k in prev_context for k in ["lisa", "лиза"]):
                reply = (
                    "В лимитированной серии **LISA Edition** представлены **Adventurer LISA** (290 000 ₸, чёрный глянец с розовым золотом) "
                    "и **Capri LISA** (295 000 ₸, бордовая черепаха с 24K золотом). Обе модели идут в комплекте с кожаным футляром быстрой зарядки."
                )
            elif any(k in prev_context for k in ["fury", "vanguard", "спорт"]):
                reply = (
                    "Спортивные и хай-тек модели **Oakley Vanguard** (270 000 ₸) и **Meta Fury** (350 000 ₸) изготовлены из сверхпрочного "
                    "легкого полимера TR90, защищены от брызг (IPX4) и идеально подходят для бега, велоспорта и активного трейлраннинга."
                )
            else:
                reply = (
                    "С удовольствием отвечу на ваш вопрос! В **AbooOptika** мы знаем все детали коллекции смарт-очков Meta 2025 года, "
                    "оптической биометрии и стиля.\n\n"
                    "Уточните, пожалуйста: вас интересует конкретная модель (например, флагман **Gen 3** или классика **Wayfarer**), "
                    "подбор оправы под ваше лицо, рецептурные линзы или актуальные цены в тенге?"
                )
            prompts = [
                "Расскажи про Ray-Ban Meta Gen 3",
                "Подбери смарт-очки под мой стиль",
                "Сколько стоят топовые модели в тенге (₸)?",
                "Очки со звуком без видеокамер для офиса"
            ]

        return reply, prompts

