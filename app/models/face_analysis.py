from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

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

class AlternativeFrame(BaseModel):
    frame_id: str
    name: str
    brand: str
    shape: str
    shape_name_ru: str
    match_score: int
    why_better_ru: str
    svg_url: str
    color: str
    material: str
    dimensions: str

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
