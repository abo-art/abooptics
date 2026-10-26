import os
import json
import logging
from typing import Dict, Any, Optional, List
import httpx
from dotenv import load_dotenv

# Загрузка переменных окружения строго через python-dotenv
load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"
GEMINI_FALLBACK_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"


class AIOptometristService:
    """
    Интеллектуальный ИИ-оптометрист AbooOptika AI Biometrics:
    - Анализирует биометрию лица из MediaPipe Face Mesh
    - Оценивает посадку надетой оправы с точки зрения смарт-эргономики Meta
    - Формирует глубокий разбор: процент совместимости, плюсы, минусы, нюансы мостика и электронных дужек
    """

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Безопасное получение ключа API исключительно через переменные окружения."""
        key = os.getenv("GEMINI_API_KEY")
        if key:
            key = key.strip()
        return key or None

    @classmethod
    def generate_expert_consultation(
        cls,
        face_shape_id: str,
        face_shape_ru: str,
        metrics_dict: Dict[str, Any],
        worn_fit_dict: Dict[str, Any],
        top_meta_profiles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Генерирует экспертное заключение оптометриста.
        При наличии ключа и сети обращается к Gemini API,
        при отсутствии ключа или сбое мгновенно возвращает профессиональный оптический анализ локального движка.
        """
        api_key = cls.get_api_key()
        if not api_key:
            logger.info("GEMINI_API_KEY не задан в окружении, задействуется локальный оптический движок.")
            return cls._fallback_expert_consultation(face_shape_id, face_shape_ru, metrics_dict, worn_fit_dict)

        prompt = cls._build_optometric_prompt(
            face_shape_ru=face_shape_ru,
            metrics_dict=metrics_dict,
            worn_fit_dict=worn_fit_dict,
            top_meta_profiles=top_meta_profiles
        )

        # Вызов Gemini API с таймаутом и fallback на flash-lite
        for endpoint in [GEMINI_API_URL, GEMINI_FALLBACK_URL]:
            try:
                url = f"{endpoint}?key={api_key}"
                payload = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": prompt}]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 800,
                        "responseMimeType": "application/json"
                    }
                }

                with httpx.Client(timeout=8.0) as client:
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                text_json = parts[0]["text"].strip()
                                parsed = json.loads(text_json)
                                parsed["is_ai_generated"] = True
                                parsed["ai_model"] = "AbooOptika AI Optometrist"
                                return parsed
                    else:
                        logger.warning(f"Gemini API вернул статус {resp.status_code}: {resp.text[:150]}")
            except Exception as e:
                logger.warning(f"Ошибка вызова Gemini API ({endpoint}): {e}")

        # Безопасный локальный fallback при недоступности внешнего API
        fallback_res = cls._fallback_expert_consultation(face_shape_id, face_shape_ru, metrics_dict, worn_fit_dict)
        fallback_res["is_ai_generated"] = False
        return fallback_res

    @staticmethod
    def _build_optometric_prompt(
        face_shape_ru: str,
        metrics_dict: Dict[str, Any],
        worn_fit_dict: Dict[str, Any],
        top_meta_profiles: List[Dict[str, Any]]
    ) -> str:
        profiles_summary = "\n".join([
            f"- {p.get('name_ru', p.get('name'))} (форма: {p.get('primary_shape')}, размеры: {[s['dimensions'] for s in p.get('size_grid', [])]})"
            for p in top_meta_profiles[:5]
        ])

        has_glasses = worn_fit_dict.get("has_glasses", True)
        if not has_glasses:
            glasses_context = "КЛИЕНТ БЕЗ ОЧКОВ: Первичное сканирование биометрии лица. Очки на лице не надеты. Не оценивай посадку надетой оправы! Сформируй рекомендации по идеальной оправе под анатомию лица."
        else:
            glasses_context = f"""ТЕКУЩАЯ НАДЕТАЯ ОПРАВА КЛИЕНТА:
- Форма: {worn_fit_dict.get('detected_shape_name_ru', 'Оправа')}
- Ширина оправы относительно скул: {worn_fit_dict.get('width_ratio', 1.0):.2f} ({worn_fit_dict.get('width_status', 'Идеально')})
- Центровка зрачка: {worn_fit_dict.get('pupil_status', 'Идеально')}
- Линия надбровной дуги: {worn_fit_dict.get('eyebrow_status', 'Гармонично')}"""

        return f"""Ты — Главный Оптометрист и Эксперт по оптической биометрии сети оптик AbooOptika (Казахстан).
Тебе переданы высокоточные данные компьютерного зрения MediaPipe Face Mesh после биометрического сканирования клиента:

ДАННЫЕ ЛИЦА КЛИЕНТА:
- Контур лица: {face_shape_ru}
- Отношение длины к ширине скул: {metrics_dict.get('height_to_width_ratio', 1.3):.2f} (норма: 1.25-1.35)
- Отношение ширины челюсти к скулам: {metrics_dict.get('jaw_to_cheek_ratio', 0.88):.2f}
- Угол подбородка: {metrics_dict.get('chin_sharpness_deg', 120):.0f}°
- Индекс симметрии лица: {metrics_dict.get('symmetry_score', 95):.1f}%

{glasses_context}

ДОСТУПНЫЕ ЭТАЛОННЫЕ ПРОФИЛИ СМАРТ-ОЧКОВ META:
{profiles_summary}

СФОРМИРУЙ СТРОГИЙ СТИЛЬНЫЙ JSON СО СЛЕДУЮЩИМИ ПОЛЯМИ:
{{
  "compatibility_score": целое число от 50 до 98 (если без очков - 98),
  "verdict_quote": "Краткое (1-2 предложения), авторитетное заключение оптометриста AbooOptika о геометрии лица и рекомендациях",
  "pros": ["конкретный анатомический плюс 1", "конкретный плюс 2"],
  "cons": ["фактор риска/ограничение формы 1", "фактор 2"],
  "bridge_nuance": "Профессиональный комментарий по ширине мостика (мм), носоупорам (нужен ли Low Bridge Fit)",
  "temple_nuance": "Профессиональный комментарий по заушникам (давление дужек, прилегание динамиков open-ear, нужен ли Large Fit L)",
  "expert_recommendation": "Какую именно модель/профиль смарт-очков Meta рекомендуется примерить клиенту и почему"
}}
Выдай строго валидный JSON без Markdown-разметки."""

    @staticmethod
    def _fallback_expert_consultation(
        face_shape_id: str,
        face_shape_ru: str,
        metrics_dict: Dict[str, Any],
        worn_fit_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        has_glasses = worn_fit_dict.get("has_glasses", True)
        if not has_glasses:
            return {
                "compatibility_score": 98,
                "verdict_quote": f"Оправа на лице отсутствует. На основе биометрии лица ({face_shape_ru}) составлены персональные оптические рекомендации по подбору оправы.",
                "pros": [
                    f"Анатомический контур: {face_shape_ru}",
                    "Зафиксированы пропорции скул, челюсти и межзрачкового расстояния"
                ],
                "cons": [],
                "bridge_nuance": f"Для формы «{face_shape_ru}» оптимален мостик 20–22 мм (Keyhole или Saddle) для равномерного распределения веса оправы.",
                "temple_nuance": "Рекомендуемая длина заушников: 145–150 мм с равномерным охватом височной области без сдавливания.",
                "expert_recommendation": f"Для формы лица «{face_shape_ru}» рекомендуются модели из каталога Meta с анатомической посадкой."
            }

        # Расчет совместимости для надетой оправы
        base_scores = {
            "oval": {"wayfarer": 96, "panto": 94, "cat_eye": 92, "aviator": 91, "rectangular": 90, "round": 88, "square": 78},
            "round": {"wayfarer": 96, "rectangular": 95, "geometric": 92, "cat_eye": 90, "panto": 84, "round": 45, "square": 78},
            "square": {"round": 96, "panto": 95, "cat_eye": 91, "wayfarer": 88, "aviator": 88, "square": 62, "rectangular": 56},
            "heart": {"panto": 96, "round": 94, "aviator": 92, "wayfarer": 89, "cat_eye": 88, "rectangular": 82, "square": 55},
            "oblong": {"wayfarer": 96, "square": 94, "panto": 93, "round": 88, "geometric": 90, "rectangular": 60, "cat_eye": 85},
            "diamond": {"cat_eye": 98, "panto": 94, "round": 92, "wayfarer": 89, "rectangular": 86, "aviator": 84, "square": 58}
        }

        shape_score = base_scores.get(face_shape_id, {}).get(detected_shape, 82)
        penalty = 0
        if width_ratio > 1.04:
            penalty = int((width_ratio - 1.04) * 60)
        elif width_ratio < 0.96:
            penalty = int((0.96 - width_ratio) * 70)

        final_score = max(45, min(97, shape_score - penalty))

        pros = [
            "Вертикальное положение зрачков совпадает с фокусной осью светового проёма",
            "Верхняя планка оправы ориентирована параллельно надбровным дугам"
        ]
        cons = []

        if width_ratio > 1.04:
            cons.append("Рамка выступает за височные линии: электронные дужки со встроенными батареями будут оттопыриваться")
            cons.append("Увеличенное расстояние от дужек до ушного канала снижает глубину баса open-ear аудио")
            temple_nuance = "Заушники сидят свободно. Для смарт-очков критично плотное прилегание в височной зоне для качественного акустического резонанса."
        elif width_ratio < 0.96:
            cons.append("Оправа уже скул: жесткие заушники смарт-очков будут пережимать височные артерии")
            cons.append("Зрачки визуально смещены к внешним краям светового проёма")
            temple_nuance = "Рекомендуется переход на увеличенный калибр Large Fit (53 мм, 139 мм общая ширина) для устранения давления дужек."
        else:
            pros.append("Ширина рамки строго соответствует скуловой дуге — оптимально для направленных микродинамиков")
            temple_nuance = "Идеальный охват височной кости: электронные модули заушников сбалансированы без перекоса."

        if face_shape_id in ["square", "round"]:
            bridge_nuance = "Мостик 22-23 мм с замковым профилем (Keyhole) обеспечивает свободную посадку на носу без сползания."
        else:
            bridge_nuance = "Стандартный мостик 20-22 мм гарантирует стабильное распределение веса смарт-очков (48-50 г)."

        verdict_quote = f"Оправа «{shape_name}»: совместимость {final_score}%. Посадка на {face_shape_ru} " + (
            "выверена по оптической оси." if final_score >= 85 else "требует корректировки калибра или геометрии."
        )

        return {
            "compatibility_score": final_score,
            "verdict_quote": verdict_quote,
            "pros": pros,
            "cons": cons if cons else ["Незначительное отклонение ширины требует примерки смежного размера"],
            "bridge_nuance": bridge_nuance,
            "temple_nuance": temple_nuance,
            "expert_recommendation": f"Для {face_shape_ru} оптимален силуэт Ray-Ban Meta Headliner (панто) или Wayfarer в калибре Standard/Large."
        }
