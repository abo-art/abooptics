import os
import json
import logging
from typing import Dict, Any, Optional, List
import httpx
from dotenv import load_dotenv

from app.models.face_analysis import ChatMessage, ChatResponse
from app.services.catalog_service import CatalogService

load_dotenv()
logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"
GEMINI_FALLBACK_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"


class ChatService:
    """
    Интеллектуальный ИИ-консультант и стилист сети салонов AbooOptika.
    Обеспечивает диалоговое консультирование клиентов по всему каталогу
    смарт-очков Meta и объяснение результатов биометрии лица.
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
        client_context: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """
        Генерирует экспертный ответ консультанта AbooOptika.
        При наличии ключа обращается к Gemini API,
        при отсутствии или ошибке задействует экспертный локальный движок.
        """
        api_key = cls.get_api_key()
        last_user_message = ""
        for m in reversed(messages):
            if m.role == "user":
                last_user_message = m.content
                break

        if not api_key:
            logger.info("GEMINI_API_KEY отсутствует, задействован локальный экспертный движок чата AbooOptika.")
            fallback_text, suggested = cls._generate_fallback_reply(last_user_message, client_context)
            return ChatResponse(success=True, reply=fallback_text, suggested_prompts=suggested)

        system_instruction = cls._build_system_instruction(client_context)
        contents = cls._format_gemini_contents(messages)

        # Вызов Gemini API
        for endpoint in [GEMINI_API_URL, GEMINI_FALLBACK_URL]:
            try:
                url = f"{endpoint}?key={api_key}"
                payload = {
                    "systemInstruction": {
                        "parts": [{"text": system_instruction}]
                    },
                    "contents": contents,
                    "generationConfig": {
                        "temperature": 0.4,
                        "maxOutputTokens": 1000
                    }
                }

                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                reply_text = parts[0]["text"].strip()
                                suggested = cls._extract_or_generate_prompts(reply_text, client_context)
                                return ChatResponse(
                                    success=True,
                                    reply=reply_text,
                                    suggested_prompts=suggested
                                )
                    else:
                        logger.warning(f"Gemini Chat API вернул статус {resp.status_code}: {resp.text[:150]}")
            except Exception as e:
                logger.warning(f"Ошибка вызова Gemini Chat API ({endpoint}): {e}")

        # Безопасный экспертный fallback при сбое сети
        fallback_text, suggested = cls._generate_fallback_reply(last_user_message, client_context)
        return ChatResponse(success=True, reply=fallback_text, suggested_prompts=suggested)

    @classmethod
    def _build_system_instruction(cls, client_context: Optional[Dict[str, Any]] = None) -> str:
        """Формирует глубокий системный промпт консультанта AbooOptika с базой знаний каталога."""
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

        context_text = "Биометрическое сканирование пока не проводилось. Предложите клиенту отсканировать лицо для точного подбора."
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

        return f"""Ты — Главный Консультант-Оптометрист и Персональный ИИ-Стилист сети салонов оптики AbooOptika (Казахстан).

ТВОЯ РОЛЬ И СТИЛЬ:
- Ты общаешься вежливо, экспертно, вдохновляюще и точно.
- Отлично разбираешься в оптике, эргономике смарт-очков Meta и анатомии человеческого лица.
- Говори на чистом русском языке. При оформлении ответов используй аккуратную структуру: абзацы, маркированные списки, выделяй названия моделей жирным шрифтом.
- Все цены всегда указывай в казахстанских тенге (₸).

{context_text}

БАЗА ЗНАНИЙ КАТАЛОГА СМАРТ-ОЧКОВ META (25 МОДЕЛЕЙ ABOOOPTIKA):
{catalog_text}

ПРАВИЛА ОТВЕТА:
1. Если вопрос касается подбора очков:
   - Если есть данные биометрии клиента, обязательно ссылайся на них («Учитывая вашу форму лица...»).
   - Рекомендуй конкретные модели из официального каталога AbooOptika с указанием формы, размеров и цены.
2. Если вопрос касается моделей (LISA Edition, Fury, Orion, Zena, Clubmaster Audio, Burbank Audio, Vanguard):
   - Раскрывай уникальные особенности (материал, линзы Transitions, разрешение камеры 12MP POV или 3K 60fps, open-ear динамики).
3. Если вопрос касается аудио-версий без камер:
   - Особо выдели Ray-Ban Meta Clubmaster Audio и Burbank Audio для клиентов, ценящих конфиденциальность в офисе.
4. В конце содержательного ответа ненавязчиво предложи примерить очки в салоне AbooOptika или распечатать талон примерки.
"""

    @classmethod
    def _format_gemini_contents(cls, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """Конвертирует историю сообщений в формат Gemini API (role: user / model)."""
        contents = []
        for msg in messages:
            role = "user" if msg.role == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })
        if not contents:
            contents = [{"role": "user", "parts": [{"text": "Здравствуйте! Расскажите о смарт-очках Meta."}]}]
        return contents

    @classmethod
    def _extract_or_generate_prompts(
        cls,
        reply_text: str,
        client_context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Генерирует 3 релевантных кликабельных подсказки для продолжения диалога."""
        low = reply_text.lower()
        if "lisa" in low:
            return [
                "Сколько стоит Adventurer LISA Edition?",
                "В чем разница между Capri и Adventurer?",
                "Посоветуй очки со звуком без камеры"
            ]
        elif "аудио" in low or "clubmaster" in low or "burbank" in low:
            return [
                "Сравни Clubmaster Audio и Burbank Audio",
                "Можно ли вставить диоптрийные линзы?",
                "Как звучат open-ear динамики на улице?"
            ]
        elif "fury" in low or "vanguard" in low:
            return [
                "Подробнее про спортивные Oakley Vanguard",
                "Какая камера в Meta Fury?",
                "Как записаться на примерку в AbooOptika?"
            ]
        elif client_context and client_context.get("face_shape_ru"):
            shape = client_context["face_shape_ru"]
            return [
                f"Почему эта форма подходит для {shape}?",
                "Есть ли модели с фотохромными линзами Transitions?",
                "Распечатать талон для консультанта"
            ]
        else:
            return [
                "Какие смарт-очки подойдут для моего лица?",
                "Расскажи про лимитированную LISA Edition",
                "В чем разница между Gen 2 и Gen 3?"
            ]

    @classmethod
    def _generate_fallback_reply(
        cls,
        user_message: str,
        client_context: Optional[Dict[str, Any]] = None
    ) -> tuple[str, List[str]]:
        """
        Интеллектуальный экспертный оффлайн-ответ AbooOptika при недоступности внешнего API.
        """
        msg = user_message.lower().strip()
        face_shape_ru = client_context.get("face_shape_ru", "вашего лица") if client_context else "вашего типа лица"

        if any(w in msg for w in ["lisa", "лиза", "лиса", "лимит"]):
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
                "Как забронировать примерку?"
            ]
        elif any(w in msg for w in ["аудио", "звук", "без камер", "clubmaster", "burbank"]):
            reply = (
                "Если для вас важна конфиденциальность и деловой дресс-код без видеокамер, "
                "в коллекции Meta представлены две специализированные аудио-модели:\n\n"
                "1. **Ray-Ban Meta Clubmaster Audio Edition** (175 000 ₸) — винтажный силуэт Browline (51-21-145), "
                "золотой металлический ободок и черный верх. Идеален для классического стиля.\n"
                "2. **Ray-Ban Meta Burbank Audio Edition** (170 000 ₸) — строгая прямоугольная оправа (54-20-145) "
                "в черепаховом цвете Havana Tortoise.\n\n"
                "Обе модели оснащены направленными open-ear динамиками с глубоким басом и системой шумоподавления для звонков, "
                "при этом полностью лишены камер и светодиодов записи."
            )
            prompts = [
                "Можно ли установить линзы с диоптриями?",
                "Сколько держит батарея в режиме разговора?",
                "Подобрать модель под мое лицо"
            ]
        elif any(w in msg for w in ["fury", "фьюри", "прозрачн"]):
            reply = (
                "**Meta Fury (Limited Edition)** (350 000 ₸) — это флагманская футуристичная модель "
                "в полупрозрачном ледяном корпусе Crystal Ice:\n\n"
                "• Вес всего 46 грамм за счет ультралегкого швейцарского нейлона TR90.\n"
                "• 12MP Ultra-wide камера с углом обзора 122° и стабилизацией движения.\n"
                "• Сенсорное управление на дужках и интеграция с голосовым ассистентом Meta AI.\n\n"
                "Оправа имеет геометрический профиль, отлично структурирующий овальные и круглые лица."
            )
            prompts = [
                "Какие еще есть геометрические модели?",
                "В чем отличие от Oakley Vanguard?",
                "Распечатать талон примерки"
            ]
        elif any(w in msg for w in ["подбор", "подойд", "лицо", "форму", "рекоменд"]):
            reply = (
                f"На основе оптической биометрии для **{face_shape_ru}** ключевое правило — "
                "создать гармоничный визуальный баланс:\n\n"
                "• **Квадратное лицо**: рекомендуем округлые силуэты **Ray-Ban Meta Headliner** (50-23, 190 000 ₸) "
                "или ретро-панто **Meta Nova** (51-20, 205 000 ₸) для смягчения линии челюсти.\n"
                "• **Круглое лицо**: идеально подойдут строгие формы **Ray-Ban Meta Wayfarer** (50-22 / 53-22, от 185 000 ₸) "
                "или **Meta Adventurer** (220 000 ₸).\n"
                "• **Овальное лицо**: универсальная анатомия, превосходно смотрятся **Meta Capri** (210 000 ₸) "
                "и титановые **Meta Smart Aviator** (260 000 ₸).\n\n"
                "Нажмите «Показать консультанту в зале», чтобы получить готовый талон с вашими точными миллиметровыми замерами!"
            )
            prompts = [
                "Подробнее про Ray-Ban Meta Wayfarer",
                "Расскажи про линзы Transitions GEN S",
                "Сколько стоят очки с AR-дисплеем Orion?"
            ]
        else:
            reply = (
                "Приветствую вас в салоне **AbooOptika**! Я ваш персональный ИИ-консультант по всей "
                "коллекции смарт-очков Meta 2025 года.\n\n"
                "У нас представлены все 25 актуальных моделей:\n"
                "• **Культовые классические**: Ray-Ban Meta Wayfarer, Headliner, Skyler (от 185 000 ₸)\n"
                "• **Лимитированные издания**: Meta Adventurer & Capri LISA Edition, Meta Fury (до 350 000 ₸)\n"
                "• **Аудио-серии без камер**: Clubmaster Audio и Burbank Audio (от 170 000 ₸)\n"
                "• **Спортивные и хай-тек**: Oakley Meta HSTN & Vanguard, Meta Orion AR Display (650 000 ₸)\n\n"
                "Задайте мне любой вопрос по характеристикам, линзам, совместимости с вашим лицом или ценам!"
            )
            prompts = [
                "Какие смарт-очки подойдут для моего лица?",
                "В чем особенность серии LISA Edition?",
                "Посоветуй аудио-версию для офиса"
            ]

        return reply, prompts
