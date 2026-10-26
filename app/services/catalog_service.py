import os
import json
import logging
from typing import List, Dict, Optional, Tuple, Any
from app.models.face_analysis import FrameRecommendation, FaceShapeInfo, ShapeScore
from app.services.styling_engine import FACE_SHAPE_CATALOG, SHAPE_NAMES_RU, StylingEngine

logger = logging.getLogger(__name__)

DATA_FILE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "meta_smart_glasses.json"
)

# ──────────────────────────────────────────────────────────────────
# Оптометрические обоснования геометрии смарт-очков Meta:
# Учитывают не только форму лица и оправы, но и эргономику носимых
# смарт-устройств (направление open-ear динамиков, угол обзора 12MP POV
# камеры, балансировку веса батарей в дужках и анатомию переносицы).
# ──────────────────────────────────────────────────────────────────
OPTOMETRIC_REASONS: Dict[str, Dict[str, str]] = {
    "oval": {
        "wayfarer":    "Трапециевидная геометрия Wayfarer гармонично ложится по скулам. Угол обзора 12MP камеры идеально ориентирован по линии естественного взгляда.",
        "panto":       "Скругленный силуэт Headliner с замковым мостом не перегружает лобную зону и центрирует зрачки точно на оптической оси.",
        "cat_eye":     "Восходящие линии модели Skyler акцентируют скулы, не нарушая природную симметрию овального контура лица.",
        "rectangular": "Прямоугольная рамка Meta Orion AR сбалансированно ложится по скуловой дуге. Волноводы 70° FOV попадают в активную зрительную зону.",
        "geometric":   "Винтажные грани Meteor создают выразительный контраст с мягким овалом, добавляя характер без утяжеления.",
        "round":       "Круглые линзы Stories Round подчеркивают плавные линии овала. Открытые микродинамики точно направлены в слуховой проход.",
        "aviator":     "Каплевидный проем повторяет вертикаль лица; тонкие дужки обеспечивают комфортную посадку.",
        "clubmaster":  "Акцентная верхняя дужка подчеркивает линию бровей овального лица.",
        "square":      "Прямые углы оправы создают избыточный геометрический контраст с мягким контуром овального подбородка."
    },
    "round": {
        "wayfarer":    "Прямые горизонтальные линии и трапециевидный профиль Wayfarer структурируют мягкий контур щек, визуально вытягивая круглое лицо.",
        "rectangular": "Прямоугольная геометрия Meta Orion AR вносит недостающие горизонтальные акценты, балансируя полноту щек.",
        "geometric":   "Гранёный контур Stories Meteor разбивает округлость лица, создавая динамичные углы и четкую оптическую структуру.",
        "cat_eye":     "Приподнятый височный край Skyler создаёт эффект оптического лифтинга, визуально удлиняя и сужая круглое лицо.",
        "clubmaster":  "Верхний акцент надбровной планки приподнимает фокус взгляда, отвлекая внимание от округлости щек.",
        "panto":       "Скругленная нижняя часть Headliner частично повторяет контур щек; рекомендуется при выраженных скулах.",
        "aviator":     "Каплевидные линзы частично дублируют округлость лица, не создавая достаточного контраста.",
        "square":      "Квадратная оправа добавляет углов, но полная симметрия может выглядеть излишне массивной.",
        "round":       "Круглая форма линз полностью дублирует контур круглого лица, визуально расширяя щеки. Не рекомендуется."
    },
    "square": {
        "panto":       "Скругленный нижний контур Headliner и замковый мост сглаживают массивность челюсти и смягчают геометрию лица.",
        "round":       "Радиусные линзы Stories Round эффективно нейтрализуют прямой угол челюсти, создавая гармоничный визуальный баланс.",
        "cat_eye":     "Восходящие уголки Skyler переносят визуальный акцент вверх от тяжёлой челюсти к глазам и бровям.",
        "wayfarer":    "Классический силуэт Wayfarer (особенно в размере Large 53 мм) компенсирует ширину скул без сдавливания висков.",
        "aviator":     "Каплевидная форма уводит фокус от нижней трети лица, смягчая угловатые челюстные кости.",
        "clubmaster":  "Акцент на бровях переносит центр внимания вверх, облегчая массивную линию подбородка.",
        "geometric":   "Гранёная форма Meteor дублирует природные углы челюсти — требует осторожного подбора калибра.",
        "rectangular": "Прямоугольная оправа повторяет горизонтальные линии челюсти, усиливая угловатость. Рекомендуются скругленные модели.",
        "square":      "Прямые углы оправы прямо дублируют массивную квадратную челюсть, усиливая тяжеловесный контур лица."
    },
    "heart": {
        "panto":       "Мягкое скругление Headliner с замковым мостом визуально компенсирует зауженный подбородок, не расширяя лоб.",
        "round":       "Круглые линзы Stories Round создают мягкий контраст с острым подбородком, центрируя баланс на уровне глаз.",
        "wayfarer":    "Трапециевидная форма Wayfarer создает гармоничный противовес узкой нижней челюсти при стандартной посадке 50 мм.",
        "cat_eye":     "Приподнятые уголки Skyler подчеркивают выразительные скулы, но требуют аккуратной центровки по височной линии.",
        "rectangular": "Прямоугольная модель Meta Orion AR открывает нижнюю треть лица, а вес магниевой оправы стабильно распределяется на переносице.",
        "aviator":     "Каплевидный проем расширяется книзу, визуально компенсируя диспропорцию между широким лбом и узким подбородком.",
        "clubmaster":  "Массивная верхняя планка может визуально утяжелять широкий лоб сердцевидного лица.",
        "geometric":   "Грани оправы могут вступать в конфликт с острыми линиями подбородка.",
        "square":      "Массивный квадрат утяжеляет верхнюю часть лица, нарушая баланс треугольного силуэта."
    },
    "oblong": {
        "wayfarer":    "Высота линзы Wayfarer Large (43.7 мм) превосходно разбивает вертикаль вытянутого лица, добавляя гармоничную ширину.",
        "panto":       "Глубокий световой проем Headliner (43.1 мм) компенсирует удлиненные пропорции, распределяя вес электронных модулей.",
        "geometric":   "Широкая гранёная форма Stories Meteor горизонтально разрезает вертикаль лица, добавляя необходимый объем.",
        "round":       "Высокий круглый проем Stories Round (44.5 мм) уменьшает зрительную вытянутость лица.",
        "cat_eye":     "Восходящие линии Skyler добавляют горизонтальную динамику и открывают нижнюю челюсть.",
        "rectangular": "Прямоугольная оправа Meta Orion AR разрывает вертикаль, если высота рамки превышает 40 мм.",
        "square":      "Широкая квадратная рамка эффективно сокращает вертикаль, добавляя объем в средней трети.",
        "aviator":     "Каплевидная форма укорачивает пропорции, но требует достаточной высоты светового окна.",
        "clubmaster":  "Акцент на бровях привлекает внимание к верху лица, но может оставлять нижнюю треть визуально вытянутой."
    },
    "diamond": {
        "cat_eye":     "Идеальное попадание: восходящие уголки Skyler вторят высоким скулам, открывая лоб и балансируя заостренный подбородок.",
        "panto":       "Скругленные контуры Headliner смягчают выступающие скуловые кости, не выступая за височные границы.",
        "wayfarer":    "Классический Wayfarer шириной 133 мм выравнивает пропорции между широкими скулами и узкими висками.",
        "round":       "Мягкий круг линз Stories Round сглаживает углы и сужения, создавая гармоничное обрамление глаз.",
        "rectangular": "Прямоугольная оправа Meta Orion AR визуально выравнивает разницу между шириной скул и зауженным лбом.",
        "aviator":     "Каплевидные линзы открывают виски и не создают избыточного давления на переносицу.",
        "clubmaster":  "Акцент на верхней рамке добавляет объем узкому лбу, компенсируя широкие скулы.",
        "geometric":   "Избыточная угловатость на ромбовидном лице рискует подчеркнуть резкие перепады контура.",
        "square":      "Квадрат на ромбовидном лице создает конфликт линий между острыми углами челюсти и скул."
    }
}


def _load_catalog_raw() -> Dict[str, Any]:
    """Загрузка полного документа каталога смарт-очков из JSON файла."""
    if os.path.exists(DATA_FILE_PATH):
        try:
            with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            logger.error(f"Ошибка чтения каталога из {DATA_FILE_PATH}: {e}")

    # Fallback: генерация через скрипт если файл отсутствует
    try:
        from scripts.generate_meta_catalog import build_catalog, save_catalog_to_file
        save_catalog_to_file(DATA_FILE_PATH)
        return build_catalog()
    except Exception as e:
        logger.error(f"Не удалось инициализировать каталог через генератор: {e}")
        return {"profiles": [], "frames": []}


def _load_catalog_from_json() -> List[dict]:
    """Загрузка плоского списка моделей смарт-очков."""
    raw = _load_catalog_raw()
    return raw.get("frames", [])


# Глобальный кэш каталога смарт-очков Meta
CATALOG_FRAMES: List[dict] = _load_catalog_from_json()


class CatalogService:
    _cached_frames: Optional[List[dict]] = None
    _cached_profiles: Optional[List[dict]] = None
    _last_mtime: float = 0.0

    @classmethod
    def _check_and_reload(cls) -> None:
        if os.path.exists(DATA_FILE_PATH):
            current_mtime = os.path.getmtime(DATA_FILE_PATH)
            if current_mtime > cls._last_mtime or cls._cached_frames is None or cls._cached_profiles is None:
                cls._last_mtime = current_mtime
                raw = _load_catalog_raw()
                cls._cached_frames = raw.get("frames", [])
                cls._cached_profiles = raw.get("profiles", [])
                global CATALOG_FRAMES
                CATALOG_FRAMES = cls._cached_frames

    @classmethod
    def reload_catalog(cls) -> List[dict]:
        """Принудительная перезагрузка каталога из JSON файла."""
        global CATALOG_FRAMES
        raw = _load_catalog_raw()
        cls._cached_frames = raw.get("frames", [])
        cls._cached_profiles = raw.get("profiles", [])
        CATALOG_FRAMES = cls._cached_frames
        if os.path.exists(DATA_FILE_PATH):
            cls._last_mtime = os.path.getmtime(DATA_FILE_PATH)
        return cls._cached_frames

    @classmethod
    def get_all_profiles(cls) -> List[dict]:
        """Возвращает 5 ключевых геометрических профилей Meta."""
        cls._check_and_reload()
        if cls._cached_profiles is not None:
            return cls._cached_profiles
        raw = _load_catalog_raw()
        cls._cached_profiles = raw.get("profiles", [])
        return cls._cached_profiles

    @classmethod
    def get_profile_by_id(cls, profile_id: str) -> Optional[dict]:
        for p in cls.get_all_profiles():
            if p.get("profile_id") == profile_id:
                return p
        return None

    @classmethod
    def get_profile_for_shape(cls, shape: str) -> Optional[dict]:
        sh = shape.lower()
        for p in cls.get_all_profiles():
            if p.get("primary_shape") == sh or sh in p.get("supported_shapes", []):
                return p
        return None

    @classmethod
    def get_all_frames(cls) -> List[dict]:
        """Возвращает все актуальные модели смарт-очков Meta."""
        cls._check_and_reload()
        if cls._cached_frames is not None:
            return cls._cached_frames
        return CATALOG_FRAMES

    @classmethod
    def get_frame_by_id(cls, frame_id: str) -> Optional[dict]:
        for frame in cls.get_all_frames():
            if frame.get("frame_id") == frame_id:
                return frame
        return None

    @classmethod
    def get_frames_by_shape(cls, shape: str) -> List[dict]:
        return [f for f in cls.get_all_frames() if f.get("shape", "").lower() == shape.lower()]

    @classmethod
    def get_frames_by_profile(cls, profile_id: str) -> List[dict]:
        return [f for f in cls.get_all_frames() if f.get("profile_id") == profile_id]

    @classmethod
    def get_frames_by_generation(cls, generation_prefix: str) -> List[dict]:
        return [f for f in cls.get_all_frames() if generation_prefix.lower() in f.get("generation", "").lower()]

    @staticmethod
    def get_recommendations_for_face(face_shape: FaceShapeInfo, shape_scores: Dict[str, int]) -> Tuple[List[FrameRecommendation], List[ShapeScore]]:
        """
        Возвращает отсортированный список смарт-очков Meta по проценту совместимости для определённого типа лица,
        а также сводную таблицу по всем геометрическим формам.
        """
        recs: List[FrameRecommendation] = []
        frames = CatalogService.get_all_frames()
        reasons_map = OPTOMETRIC_REASONS.get(face_shape.shape_id, OPTOMETRIC_REASONS.get("oval", {}))

        for frame in frames:
            shape_key = frame["shape"]
            base_score = shape_scores.get(shape_key, 75)
            
            # Тонкая калибровка для смарт-очков:
            # Модели Gen 2 с 12MP камерой и легким весом получают +2 балла за эргономику
            if "Gen 2" in frame.get("generation", ""):
                score = min(98, base_score + 2)
            elif "Gen 3" in frame.get("generation", ""):
                score = min(99, base_score + 3)
            else:
                score = base_score

            badge, _ = StylingEngine.get_badge_and_verdict(score)
            default_reason = f"Смарт-очки формы «{SHAPE_NAMES_RU.get(shape_key, shape_key)}» создают сбалансированную оптическую посадку."
            reason = reasons_map.get(shape_key, default_reason)

            # Если у модели есть конкретные оптометрические примечания, используем их для обогащения
            if frame.get("optometric_notes"):
                reason = f"{reason} {frame.get('optometric_notes')}"

            rec = FrameRecommendation(
                frame_id=frame["frame_id"],
                name=frame["name"],
                brand=frame["brand"],
                shape=shape_key,
                shape_name_ru=frame.get("shape_name_ru", SHAPE_NAMES_RU.get(shape_key, shape_key.title())),
                match_score=score,
                match_badge=badge,
                reason_ru=reason,
                style_tags=frame.get("style_tags", []),
                svg_url="",
                color=frame.get("color", ""),
                material=frame.get("material", ""),
                dimensions=frame.get("dimensions", ""),
                model_line=frame.get("model_line"),
                generation=frame.get("generation"),
                camera=frame.get("camera"),
                display=frame.get("display"),
                has_display=frame.get("has_display", False),
                audio=frame.get("audio"),
                price=frame.get("price"),
                currency=frame.get("currency", "₸"),
                weight_g=frame.get("weight_g"),
                fit_type=frame.get("fit_type")
            )
            recs.append(rec)

        # Сортируем: сначала самые совместимые
        recs.sort(key=lambda x: x.match_score, reverse=True)

        # Сводный список по всем формам очков
        all_shapes_list: List[ShapeScore] = []
        for s_id, s_name in SHAPE_NAMES_RU.items():
            sc = shape_scores.get(s_id, 75)
            _, verd = StylingEngine.get_badge_and_verdict(sc)
            all_shapes_list.append(ShapeScore(
                shape_id=s_id,
                shape_name_ru=s_name,
                score=sc,
                verdict=verd
            ))
        all_shapes_list.sort(key=lambda x: x.score, reverse=True)

        return recs, all_shapes_list
