from typing import List, Dict, Optional, Tuple
from app.models.face_analysis import FrameRecommendation, FaceShapeInfo, ShapeScore
from app.services.styling_engine import FACE_SHAPE_CATALOG, SHAPE_NAMES_RU, StylingEngine

# ──────────────────────────────────────────────────────────────────
#  Реальный каталог оправ — каждая карточка содержит:
#   • Настоящий бренд и модельный ряд
#   • Точную геометрическую форму (square / rectangular / round / aviator
#     / cat_eye / panto / geometric / clubmaster / wayfarer)
#   • Реальные размеры (lens-bridge-temple, мм)
#   • Материалы и цвет из оптического ассортимента
#   • Салоны наличия (Казахстан)
# ──────────────────────────────────────────────────────────────────
CATALOG_FRAMES: List[dict] = [
    # ─── ПРЯМОУГОЛЬНЫЕ (Rectangular) ──────────────────────────────
    {
        "frame_id": "abo-rec-01",
        "name": "Minimalist Edge",
        "brand": "abooptika Lab",
        "shape": "rectangular",
        "color": "Матовый графит (Matte Graphite)",
        "material": "Японский титан β-сплав",
        "price": 48500,
        "currency": "₸",
        "dimensions": "53-17-142",
        "style_tags": ["Унисекс", "Бизнес", "Минимализм"],
        "in_stock_salons": ["Салон Mega Park (Алматы)", "Салон Dostyk Plaza", "Центральный салон (Астана)"]
    },
    {
        "frame_id": "abo-rec-10",
        "name": "Porsche Design P'8801",
        "brand": "Porsche Design",
        "shape": "rectangular",
        "color": "Палладиум (Palladium)",
        "material": "Нержавеющая сталь / силиконовые носоупоры",
        "price": 62000,
        "currency": "₸",
        "dimensions": "55-16-140",
        "style_tags": ["Мужские", "Бизнес-класс", "Инженерный дизайн"],
        "in_stock_salons": ["Салон Esentai Mall (Алматы)", "Салон Talan Gallery (Астана)"]
    },

    # ─── АВИАТОРЫ (Aviator) ───────────────────────────────────────
    {
        "frame_id": "abo-avi-02",
        "name": "Aviator Classic RB3025",
        "brand": "Ray-Ban",
        "shape": "aviator",
        "color": "Полированное золото (Polished Gold)",
        "material": "Металлический сплав Monel",
        "price": 72000,
        "currency": "₸",
        "dimensions": "58-14-135",
        "style_tags": ["Икона стиля", "Двойной мост", "Премиум"],
        "in_stock_salons": ["Салон Dostyk Plaza (Алматы)", "Салон Esentai Mall"]
    },
    {
        "frame_id": "abo-avi-11",
        "name": "Bentley B-9220",
        "brand": "Bentley Eyewear",
        "shape": "aviator",
        "color": "Карбоновый серый (Carbon Grey)",
        "material": "Титан Grade 5 / карбон",
        "price": 115000,
        "currency": "₸",
        "dimensions": "56-15-140",
        "style_tags": ["Мужские", "Люкс", "Автомобильный стиль"],
        "in_stock_salons": ["Салон Esentai Mall (Алматы)"]
    },

    # ─── КОШАЧИЙ ГЛАЗ (Cat-Eye) ──────────────────────────────────
    {
        "frame_id": "abo-cat-03",
        "name": "Aurelia TF5812",
        "brand": "Tom Ford",
        "shape": "cat_eye",
        "color": "Тёмная Гавана с золотым Т-логотипом",
        "material": "Итальянский ацетат Mazzucchelli",
        "price": 98000,
        "currency": "₸",
        "dimensions": "54-16-140",
        "style_tags": ["Женские", "Лифтинг-эффект", "Люкс"],
        "in_stock_salons": ["Салон Esentai Mall (Алматы)", "Салон Talan Gallery (Астана)"]
    },
    {
        "frame_id": "abo-cat-12",
        "name": "MU 04UV",
        "brand": "Miu Miu",
        "shape": "cat_eye",
        "color": "Бордо / Прозрачный розовый",
        "material": "Многослойный ацетат",
        "price": 87000,
        "currency": "₸",
        "dimensions": "52-17-140",
        "style_tags": ["Женские", "Подиум", "Выразительные"],
        "in_stock_salons": ["Салон Dostyk Plaza (Алматы)", "Салон Keruen (Астана)"]
    },

    # ─── КРУГЛЫЕ (Round) ──────────────────────────────────────────
    {
        "frame_id": "abo-rnd-04",
        "name": "Gregory Peck OV5217",
        "brand": "Oliver Peoples",
        "shape": "round",
        "color": "Амбровый черепаховый (Amber Tortoise)",
        "material": "Натуральный био-ацетат",
        "price": 89000,
        "currency": "₸",
        "dimensions": "47-23-145",
        "style_tags": ["Интеллектуальный стиль", "Ретро", "Унисекс"],
        "in_stock_salons": ["Салон Mega Park (Алматы)", "Салон Keruen (Астана)"]
    },
    {
        "frame_id": "abo-rnd-13",
        "name": "RX6465 Jack",
        "brand": "Ray-Ban",
        "shape": "round",
        "color": "Чёрный / Демо-линзы",
        "material": "Металлический сплав / ацетат",
        "price": 54000,
        "currency": "₸",
        "dimensions": "49-20-140",
        "style_tags": ["Унисекс", "Городской стиль", "Классика"],
        "in_stock_salons": ["Салон Mega Park (Алматы)", "Салон Dostyk Plaza", "Салон Shymkent Plaza"]
    },

    # ─── КВАДРАТНЫЕ (Square) ──────────────────────────────────────
    {
        "frame_id": "abo-sqr-05",
        "name": "Bold Square GG0956O",
        "brand": "Gucci",
        "shape": "square",
        "color": "Глянцевый чёрный (Piano Black)",
        "material": "Утолщённый премиум-ацетат",
        "price": 105000,
        "currency": "₸",
        "dimensions": "55-18-145",
        "style_tags": ["Подиум", "Чёткая геометрия", "Акцентные"],
        "in_stock_salons": ["Салон Esentai Mall (Алматы)", "Салон Dostyk Plaza"]
    },
    {
        "frame_id": "abo-sqr-14",
        "name": "SL 276 MICA",
        "brand": "Saint Laurent",
        "shape": "square",
        "color": "Матовый чёрный / серебряный логотип",
        "material": "Ацетат с металлическими заушниками",
        "price": 93000,
        "currency": "₸",
        "dimensions": "53-16-145",
        "style_tags": ["Унисекс", "Минимализм", "Архитектурный"],
        "in_stock_salons": ["Салон Esentai Mall (Алматы)", "Салон Talan Gallery (Астана)"]
    },

    # ─── ПАНТО (Panto) ────────────────────────────────────────────
    {
        "frame_id": "abo-pnt-06",
        "name": "Urban Lite SPX 2599",
        "brand": "Silhouette",
        "shape": "panto",
        "color": "Шлифованный титан / Оливковый",
        "material": "High-Tech Titanium + SPX",
        "price": 82000,
        "currency": "₸",
        "dimensions": "49-19-145",
        "style_tags": ["Невесомые (3.5 г)", "Европейский дизайн", "Универсальные"],
        "in_stock_salons": ["Салон Mega Park", "Центральный салон (Астана)", "Салон Shymkent Plaza"]
    },
    {
        "frame_id": "abo-pnt-15",
        "name": "PE3275V",
        "brand": "Persol",
        "shape": "panto",
        "color": "Havana Terra di Siena",
        "material": "Ацетат ручной работы / Meflecto-шарниры",
        "price": 68000,
        "currency": "₸",
        "dimensions": "50-20-145",
        "style_tags": ["Итальянская классика", "Унисекс", "Ретро-люкс"],
        "in_stock_salons": ["Салон Dostyk Plaza (Алматы)", "Салон Keruen (Астана)"]
    },

    # ─── ГЕОМЕТРИЧЕСКИЕ (Geometric / Hexagonal) ──────────────────
    {
        "frame_id": "abo-geo-07",
        "name": "Hexagonal Strip 6451",
        "brand": "Lindberg",
        "shape": "geometric",
        "color": "Матовое серебро (Raw Silver)",
        "material": "Аэрокосмический титан",
        "price": 128000,
        "currency": "₸",
        "dimensions": "51-20-140",
        "style_tags": ["Авангард", "Безободковые акценты", "Эксклюзив"],
        "in_stock_salons": ["Салон Esentai Mall (Алматы)", "Салон Talan Gallery (Астана)"]
    },
    {
        "frame_id": "abo-geo-16",
        "name": "RB3556N Octagonal",
        "brand": "Ray-Ban",
        "shape": "geometric",
        "color": "Золото / Зелёные G-15 линзы",
        "material": "Полированный металл",
        "price": 58000,
        "currency": "₸",
        "dimensions": "53-21-145",
        "style_tags": ["Унисекс", "Фестивальный стиль", "Ретро-геометрия"],
        "in_stock_salons": ["Салон Mega Park (Алматы)", "Салон Dostyk Plaza"]
    },

    # ─── КЛУБМАСТЕР / БРОУЛАЙНЕР (Clubmaster) ────────────────────
    {
        "frame_id": "abo-clb-08",
        "name": "Clubmaster RB5154",
        "brand": "Ray-Ban",
        "shape": "clubmaster",
        "color": "Чёрный эбеновый / Золото",
        "material": "Ацетат + позолоченная сталь",
        "price": 68000,
        "currency": "₸",
        "dimensions": "51-21-145",
        "style_tags": ["Винтажный шик", "Акцент на бровях", "Культовая классика"],
        "in_stock_salons": ["Салон Dostyk Plaza", "Салон Mega Park", "Салон Keruen (Астана)"]
    },
    {
        "frame_id": "abo-clb-17",
        "name": "BE2387 Browline",
        "brand": "Burberry",
        "shape": "clubmaster",
        "color": "Тёмная Гавана / Клетка Nova Check",
        "material": "Ацетат + металл",
        "price": 78000,
        "currency": "₸",
        "dimensions": "53-20-145",
        "style_tags": ["Британский стиль", "Унисекс", "Элегантные"],
        "in_stock_salons": ["Салон Esentai Mall (Алматы)", "Салон Talan Gallery (Астана)"]
    },

    # ─── ВАЙФАРЕР (Wayfarer) ──────────────────────────────────────
    {
        "frame_id": "abo-way-09",
        "name": "New Wayfarer RB5184",
        "brand": "Ray-Ban",
        "shape": "wayfarer",
        "color": "Тёмный черепаховый (Dark Demi)",
        "material": "Био-ацетат ручной полировки",
        "price": 54000,
        "currency": "₸",
        "dimensions": "52-18-145",
        "style_tags": ["Городской кэжуал", "Усиленные шарниры", "Must Have"],
        "in_stock_salons": ["Все салоны сети (Алматы, Астана, Шымкент)"]
    },
    {
        "frame_id": "abo-way-18",
        "name": "Wayfarer Original RB2140",
        "brand": "abooptika Signature",
        "shape": "wayfarer",
        "color": "Матовый чёрный (Matte Black)",
        "material": "Переработанный нейлон G-15",
        "price": 46000,
        "currency": "₸",
        "dimensions": "50-22-150",
        "style_tags": ["Классика 1956", "Унисекс", "Экологичный"],
        "in_stock_salons": ["Все салоны сети (Алматы, Астана, Шымкент)"]
    },
]


# ──────────────────────────────────────────────────────────────────
# Оптометрические обоснования: почему конкретная форма подходит
# или не подходит конкретному типу лица. Ключ — face_shape_id,
# вложенный ключ — frame_shape_id.
# ──────────────────────────────────────────────────────────────────
OPTOMETRIC_REASONS: Dict[str, Dict[str, str]] = {
    "oval": {
        "rectangular": "Горизонтальная линия оправы подчёркивает природную гармонию пропорций. Ширина прямоугольной рамки визуально совпадает со скуловой линией.",
        "aviator":     "Каплевидный световой проём повторяет плавный контур овала. Тонкий металлический мост не перегружает переносицу.",
        "geometric":   "Угловая нестандартная геометрия создаёт контраст с мягким овалом, добавляя характер без нарушения пропорций.",
        "cat_eye":     "Приподнятый внешний край акцентирует верхнюю треть лица. Хорошо работает при анатомически симметричных скулах.",
        "panto":       "Смешанная геометрия (плоский верх + скруглённый низ) не конфликтует с овальным контуром.",
        "clubmaster":  "Массивная надбровная часть утяжеляет верхнюю линию — сбалансировано для пропорционального овала.",
        "wayfarer":    "Трапециевидный силуэт добавляет лёгкую угловатость, но не нарушает общую гармонию овального лица.",
        "round":       "Круглые линзы повторяют плавные линии овала — нет контраста. Рекомендовано выбирать размер не шире скул.",
        "square":      "Острые углы оправы создают избыточный контраст с мягким контуром подбородка овального лица.",
    },
    "round": {
        "rectangular": "Прямые горизонтальные линии создают чёткую структуру и визуально вытягивают круглое лицо по горизонтали.",
        "wayfarer":    "Угловатый трапециевидный силуэт вносит линейность, компенсируя округлость щёк и подбородка.",
        "geometric":   "Гранёные линии ломают мягкость контура, добавляя структурированность лицу без резкого контраста.",
        "cat_eye":     "Восходящая линия от переносицы к вискам зрительно удлиняет пропорции круглого лица.",
        "clubmaster":  "Акцент на надбровной дуге поднимает визуальный центр и уменьшает визуальную округлость щёк.",
        "square":      "Квадратная форма вносит угловатость, но полная симметрия углов может выглядеть тяжеловесно.",
        "aviator":     "Каплевидная форма частично повторяет округлость. Двойной мост помогает, но эффект контраста слабый.",
        "panto":       "Скруглённая нижняя часть дублирует форму щёк, что усиливает визуальную округлость лица.",
        "round":       "Круглые линзы на круглом лице — прямое дублирование контура. Лицо выглядит шире и плоскостнее.",
    },
    "square": {
        "round":       "Радиусные линзы сглаживают выраженные углы челюсти и создают визуальный баланс с широким подбородком.",
        "panto":       "Плоская верхняя линия сохраняет структуру, а скруглённый низ смягчает массивность нижней челюсти.",
        "aviator":     "Каплевидный проём уводит акцент от нижней трети лица, компенсируя ширину челюсти.",
        "clubmaster":  "Акцент на бровях переносит визуальный центр вверх, отвлекая от массивной линии подбородка.",
        "cat_eye":     "Восходящий угол рамки смягчает квадратность, но может конфликтовать с широким лбом.",
        "square":      "Прямые углы оправы дублируют массивную квадратную челюсть, усиливая тяжёлый контур.",
        "geometric":   "Гранёные формы добавляют ещё больше углов — рискует выглядеть перегруженно.",
        "wayfarer":    "Угловатый трапециевидный силуэт не создаёт достаточного контраста с квадратными линиями лица.",
        "rectangular": "Прямоугольная оправа повторяет горизонтальные линии челюсти — нет визуальной компенсации.",
    },
    "heart": {
        "aviator":     "Каплевидная форма расширяется к низу, визуально балансируя узкий подбородок с широким лбом.",
        "round":       "Мягкие округлые линзы компенсируют острый подбородок, не утяжеляя верхнюю часть лица.",
        "panto":       "Закруглённый низ оправы добавляет объём в зоне узкой челюсти, создавая визуальный баланс.",
        "clubmaster":  "Акцентированная верхняя рамка работает на сердцевидном лице, если ширина строго по скулам.",
        "rectangular": "Горизонтальная линия может утяжелить широкий лоб, если оправа шире висков.",
        "cat_eye":     "Приподнятые углы акцентируют и без того широкую верхнюю часть лица — нужна осторожность.",
        "wayfarer":    "Расширение вверх дублирует пропорции сердца — рискует визуально увеличить лоб.",
        "geometric":   "Угловатая структура создаёт контраст с острым подбородком, но может подчеркнуть асимметрию.",
        "square":      "Квадратная оправа максимально утяжеляет верхнюю треть, нарушая и без того неровный баланс.",
    },
    "oblong": {
        "square":      "Широкая квадратная рамка визуально разрывает вертикаль лица, добавляя необходимую ширину.",
        "wayfarer":    "Трапециевидный силуэт с увеличенной высотой линзы компенсирует вытянутость лица.",
        "aviator":     "Высокий каплевидный проём визуально укорачивает пропорции, сбалансирует длинное лицо.",
        "geometric":   "Широкая гранёная форма горизонтально разрезает вертикаль лица, добавляя объём.",
        "panto":       "Комбинированная форма создаёт ощущение ширины, но эффект слабее чем у квадратных форм.",
        "round":       "Круглые линзы разрывают вертикаль, но при маленьком диаметре эффект недостаточен.",
        "clubmaster":  "Надбровная часть создаёт горизонтальный акцент, но высота линзы может быть мала.",
        "cat_eye":     "Восходящий угол может визуально удлинить лицо ещё сильнее — рискует работать наоборот.",
        "rectangular": "Узкая прямоугольная оправа подчёркивает вытянутость. Допустима только при большой высоте линзы.",
    },
    "diamond": {
        "cat_eye":     "Восходящая линия от переносицы к вискам идеально повторяет и акцентирует широкие скулы.",
        "clubmaster":  "Массивная надбровная часть добавляет объём узкому лбу, балансируя ромбовидные пропорции.",
        "round":       "Мягкие круглые линзы смягчают заострённые скулы и добавляют гармонию овальности.",
        "panto":       "Комбинированная форма подстраивается под скулы, не конфликтуя ни с лбом, ни с подбородком.",
        "aviator":     "Каплевидный проём открывает виски и не перегружает узкую линию лба.",
        "rectangular": "Прямая горизонталь может визуально расширить уже и без того заметные скулы.",
        "wayfarer":    "Трапеция может усилить контраст между скулами и подбородком, если оправа широкая.",
        "geometric":   "Гранёная угловатость на ромбовидном лице рискует создать визуальный хаос из углов.",
        "square":      "Квадрат на ромбовидном лице — максимальный конфликт линий и углов. Не рекомендуется.",
    },
}


class CatalogService:
    @staticmethod
    def get_all_frames() -> List[dict]:
        return CATALOG_FRAMES

    @staticmethod
    def get_recommendations_for_face(face_shape: FaceShapeInfo, shape_scores: Dict[str, int]) -> Tuple[List[FrameRecommendation], List[ShapeScore]]:
        """
        Возвращает отсортированный список оправ по проценту совместимости для определённого типа лица,
        а также сводную таблицу по всем геометрическим формам.
        """
        recs: List[FrameRecommendation] = []
        reasons_map = OPTOMETRIC_REASONS.get(face_shape.shape_id, OPTOMETRIC_REASONS.get("oval", {}))

        for frame in CATALOG_FRAMES:
            shape_key = frame["shape"]
            score = shape_scores.get(shape_key, 75)
            badge, _ = StylingEngine.get_badge_and_verdict(score)
            reason = reasons_map.get(
                shape_key,
                f"Оправа формы «{SHAPE_NAMES_RU.get(shape_key, shape_key)}» нейтрально сочетается с контуром лица."
            )

            rec = FrameRecommendation(
                frame_id=frame["frame_id"],
                name=frame["name"],
                brand=frame["brand"],
                shape=shape_key,
                shape_name_ru=SHAPE_NAMES_RU.get(shape_key, shape_key.title()),
                match_score=score,
                match_badge=badge,
                reason_ru=reason,
                style_tags=frame["style_tags"],
                svg_url="",
                color=frame["color"],
                material=frame["material"],
                dimensions=frame["dimensions"]
            )
            recs.append(rec)

        # Сортируем: сначала самые совместимые
        recs.sort(key=lambda x: x.match_score, reverse=True)

        # Сводный список по всем формам
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
