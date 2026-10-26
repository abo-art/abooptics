import re
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator

# Регулярное выражение для валидации: принимает как чистый base64, так и data-URI (data:image/...;base64,...)
BASE64_IMAGE_PATTERN = r"^(?:data:image\/[a-zA-Z0-9.+_-]+;base64,)?[A-Za-z0-9+/_\-\s\r\n=]+$"
BASE64_IMAGE_REGEX = re.compile(BASE64_IMAGE_PATTERN, re.IGNORECASE)
DATA_URI_PREFIX_REGEX = re.compile(r"^data:image\/[a-zA-Z0-9.+_-]+;base64,", re.IGNORECASE)

class AnalyzeRequest(BaseModel):
    """
    Модель входящего запроса на биометрический анализ геометрии лица и оправы.
    Принимает изображение в формате base64 (чистый base64 либо data-URI схема: data:image/jpeg;base64,...).
    """
    image_base64: str = Field(
        ...,
        description="Base64-строка изображения (чистый base64 либо Data URI data:image/jpeg;base64,...)",
        pattern=BASE64_IMAGE_PATTERN
    )
    frame_shape: Optional[str] = Field(
        None,
        description="Опциональная подсказка формы оправы (square, round, oval, aviator, etc.)"
    )

    @field_validator("image_base64")
    @classmethod
    def validate_image_base64_format(cls, value: str) -> str:
        if not value or not isinstance(value, str):
            raise ValueError("image_base64 не может быть пустым")

        trimmed = value.strip()
        if not trimmed:
            raise ValueError("image_base64 не может содержать только пробелы")

        if not BASE64_IMAGE_REGEX.match(trimmed):
            raise ValueError(
                "Некорректный формат base64. Ожидается чистая base64-строка или data-URI схема (data:image/...;base64,...)"
            )

        return trimmed

    def get_clean_base64(self) -> str:
        """
        Возвращает очищенную от data-URI префикса и пробелов base64-строку.
        """
        raw = self.image_base64.strip()
        if "," in raw:
            raw = raw.split(",", 1)[1]
        else:
            raw = DATA_URI_PREFIX_REGEX.sub("", raw)
        return re.sub(r"\s+", "", raw)

class KeyPoint2D(BaseModel):
    x: float
    y: float
    z: Optional[float] = 0.0

class LandmarkSummary(BaseModel):
    left_eye_pupil: KeyPoint2D
    right_eye_pupil: KeyPoint2D
    nose_bridge: KeyPoint2D
    chin_tip: KeyPoint2D
    forehead_center: KeyPoint2D
    left_cheek: KeyPoint2D
    right_cheek: KeyPoint2D
    left_jaw: KeyPoint2D
    right_jaw: KeyPoint2D
    pupillary_distance_norm: float
    face_mesh_points: Optional[List[List[float]]] = None

class FaceMetrics(BaseModel):
    height_to_width_ratio: float = Field(..., description="Отношение длины лица к ширине скул")
    jaw_to_cheek_ratio: float = Field(..., description="Отношение ширины челюсти к ширине скул")
    forehead_to_cheek_ratio: float = Field(..., description="Отношение ширины лба к ширине скул")
    chin_sharpness_deg: float = Field(..., description="Угол контура подбородка в градусах")
    symmetry_score: float = Field(..., description="Оценка симметрии лица от 0 до 100%")

class FaceShapeInfo(BaseModel):
    shape_id: str = Field(..., description="oval, round, square, heart, oblong, diamond")
    shape_name_ru: str
    shape_name_en: str
    confidence: float
    description_ru: str
    styling_advice_ru: str
    icon: str

class FitMetrics(BaseModel):
    width_status: str = Field(..., description="Идеально / Широковата / Узковата")
    width_ratio: float = Field(..., description="Отношение ширины оправы к скулам")
    width_feedback_ru: str
    pupil_status: str = Field(..., description="Идеально по центру / Смещены")
    pupil_feedback_ru: str
    eyebrow_status: str = Field(..., description="Гармонично / Перекрывает брови")
    eyebrow_feedback_ru: str

class WornFrameEvaluation(BaseModel):
    has_glasses: bool = Field(..., description="Надета ли оправа клиентом")
    detected_shape: str
    detected_shape_name_ru: str
    compatibility_score: int = Field(..., description="Процент совместимости (0-100%)")
    match_badge: str
    verdict_quote_ru: str = Field(..., description="Главная цитата стилиста оптики")
    pros_ru: List[str] = Field(default_factory=list, description="Сильные стороны посадки")
    cons_ru: List[str] = Field(default_factory=list, description="Что можно улучшить")
    fit_metrics: FitMetrics
    bridge_nuance_ru: Optional[str] = Field(None, description="Экспертный разбор мостика и носоупоров")
    temple_nuance_ru: Optional[str] = Field(None, description="Экспертный разбор заушников с батареями")
    ai_recommendation_ru: Optional[str] = Field(None, description="Рекомендация ИИ-оптометриста")
    is_ai_powered: bool = Field(default=False, description="Сгенерировано ли заключение моделью Gemini AI")
    ai_model_name: Optional[str] = Field(default=None, description="Имя модели ИИ")

class AlternativeFrame(BaseModel):
    frame_id: str
    name: str
    brand: str
    shape: str
    shape_name_ru: str
    profile_id: Optional[str] = None
    match_score: int
    why_better_ru: str
    svg_url: str
    color: str
    material: str
    dimensions: str
    model_line: Optional[str] = None
    generation: Optional[str] = None
    camera: Optional[str] = None
    display: Optional[str] = None
    has_display: Optional[bool] = False
    audio: Optional[str] = None
    price: Optional[int] = None
    currency: Optional[str] = "₸"
    weight_g: Optional[float] = None
    fit_type: Optional[str] = None
    smart_features: Optional[List[str]] = None

class FrameRecommendation(BaseModel):
    frame_id: str
    name: str
    brand: str
    shape: str
    shape_name_ru: str
    match_score: int
    match_badge: str
    reason_ru: str
    style_tags: List[str]
    svg_url: str
    color: str
    material: str
    dimensions: str
    model_line: Optional[str] = None
    generation: Optional[str] = None
    camera: Optional[str] = None
    display: Optional[str] = None
    has_display: Optional[bool] = False
    audio: Optional[str] = None
    price: Optional[int] = None
    currency: Optional[str] = "₸"
    weight_g: Optional[float] = None
    fit_type: Optional[str] = None

class ShapeScore(BaseModel):
    shape_id: str
    shape_name_ru: str
    score: int
    verdict: str

class AnalyzeResponse(BaseModel):
    success: bool
    face_detected: bool
    message: Optional[str] = None
    face_shape: Optional[FaceShapeInfo] = None
    metrics: Optional[FaceMetrics] = None
    landmarks: Optional[LandmarkSummary] = None
    worn_frame_evaluation: Optional[WornFrameEvaluation] = None
    top_alternatives: List[AlternativeFrame] = []
    top_recommendations: List[FrameRecommendation] = []
    all_shapes_scores: List[ShapeScore] = []
    processing_time_ms: float = 0.0

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' или 'assistant'")
    content: str = Field(..., description="Текст сообщения")

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="История диалога")
    client_context: Optional[Dict[str, Any]] = Field(default=None, description="Биометрический контекст сканирования лица")

class ChatResponse(BaseModel):
    success: bool = True
    reply: str
    suggested_prompts: List[str] = Field(default_factory=list)
