import os
import time
import base64
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import re
from typing import Optional, Tuple, List, Dict

from app.models.face_analysis import (
    AnalyzeResponse,
    FaceMetrics,
    FaceShapeInfo,
    KeyPoint2D,
    LandmarkSummary,
    DATA_URI_PREFIX_REGEX,
    BASE64_IMAGE_REGEX
)
from app.services.styling_engine import StylingEngine
from app.services.catalog_service import CatalogService

def extract_and_decode_base64(raw_b64: str) -> bytes:
    """
    Очищает и декодирует base64-строку изображения:
    1. Автоматически удаляет data-URI префикс (типа data:image/...;base64,) если он передан с фронтенда.
    2. Удаляет любые пробелы, табуляции и переносы строк.
    3. Поддерживает URL-safe base64 (- и _).
    4. Автоматически выравнивает длину padding символами '='.
    5. Декодирует в байты изображения с валидацией минимального размера.
    """
    if not raw_b64 or not isinstance(raw_b64, str):
        raise ValueError("Base64 строка пуста или не является строковым значением")

    cleaned = raw_b64.strip()

    # Удаление префикса data-URI, если присутствует запятая
    if "," in cleaned:
        cleaned = cleaned.split(",", 1)[1].strip()
    elif cleaned.lower().startswith("data:"):
        cleaned = DATA_URI_PREFIX_REGEX.sub("", cleaned).strip()

    # Удаление всех пробельных символов и переводов строк
    cleaned = re.sub(r"\s+", "", cleaned)

    if not cleaned:
        raise ValueError("Base64 данные отсутствуют после очистки префикса")

    # Поддержка URL-safe base64
    cleaned = cleaned.replace("-", "+").replace("_", "/")

    # Выравнивание padding до кратности 4
    missing_padding = len(cleaned) % 4
    if missing_padding:
        cleaned += "=" * (4 - missing_padding)

    try:
        decoded_bytes = base64.b64decode(cleaned, validate=False)
    except Exception as exc:
        raise ValueError(f"Ошибка декодирования base64: {str(exc)}")

    if not decoded_bytes or len(decoded_bytes) < 100:
        raise ValueError("Декодированные данные изображения слишком малы или повреждены")

    return decoded_bytes

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "face_landmarker.task")

class FaceMeshService:
    _instance: Optional["FaceMeshService"] = None
    _detector: Optional[vision.FaceLandmarker] = None

    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"MediaPipe model file not found at: {MODEL_PATH}")
        
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1
        )
        self._detector = vision.FaceLandmarker.create_from_options(options)

    @classmethod
    def get_instance(cls) -> "FaceMeshService":
        if cls._instance is None:
            cls._instance = FaceMeshService()
        return cls._instance

    def _decode_image(self, image_data: bytes) -> np.ndarray:
        arr = np.frombuffer(image_data, np.uint8)
        img_bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise ValueError("Не удалось декодировать изображение. Неверный формат.")
        return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    def _calculate_angle(self, p1: Tuple[float, float], vertex: Tuple[float, float], p3: Tuple[float, float]) -> float:
        v1 = np.array([p1[0] - vertex[0], p1[1] - vertex[1]])
        v2 = np.array([p3[0] - vertex[0], p3[1] - vertex[1]])
        cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-7)
        cos_theta = np.clip(cos_theta, -1.0, 1.0)
        return float(np.degrees(np.arccos(cos_theta)))

    def _detect_glasses_fit(self, rgb_img: np.ndarray, landmarks) -> Dict[str, any]:
        """
        Анализирует наличие и геометрию надетой оправы в орбитальной зоне лица.
        Определяет форму оправы (9 категорий), соотношение ширины к скулам и центровку.

        Классификация использует многофакторный подход:
        - Циркулярность контура (4π·Area / Perimeter²)
        - Соотношение сторон линзы (ширина / высота)
        - Количество и углы вершин аппроксимирующего полигона
        - Вертикальная асимметрия контура (подъём наружного края)
        - Анализ верхней кромки оправы (прямая линия vs кривая)
        """
        h, w = rgb_img.shape[:2]
        gray = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)

        # 1. Расчет ширины лица между скулами (234 и 454)
        lc = np.array([landmarks[234].x * w, landmarks[234].y * h])
        rc = np.array([landmarks[454].x * w, landmarks[454].y * h])
        face_width = float(np.linalg.norm(rc - lc) + 1e-6)

        # 2. Зрачки
        lp = np.array([landmarks[468].x * w, landmarks[468].y * h])
        rp = np.array([landmarks[473].x * w, landmarks[473].y * h])
        pd = float(np.linalg.norm(rp - lp) + 1e-6)

        # 3. Выделяем область глаз и переносицы (ROI) с увеличенным запасом
        y_top = int(max(0, min(landmarks[70].y, landmarks[300].y) * h - 20))
        y_bottom = int(min(h, max(landmarks[117].y, landmarks[346].y) * h + 30))
        x_left = int(max(0, landmarks[234].x * w - 30))
        x_right = int(min(w, landmarks[454].x * w + 30))

        roi_gray = gray[y_top:y_bottom, x_left:x_right]
        if roi_gray.size == 0 or roi_gray.shape[0] < 10 or roi_gray.shape[1] < 20:
            return {"has_glasses": False, "shape": "rectangular", "width_ratio": 1.04}

        # 4. Анализ границ (Canny edges) — адаптивные пороги
        median_val = np.median(roi_gray)
        canny_low = int(max(20, 0.66 * median_val))
        canny_high = int(min(200, 1.33 * median_val))
        edges = cv2.Canny(roi_gray, canny_low, canny_high)

        # Поиск внешних границ оправы по горизонтальным проекциям
        col_edges = np.sum(edges, axis=0)
        thresh = np.max(col_edges) * 0.12 if np.max(col_edges) > 0 else 1
        active_cols = np.where(col_edges > thresh)[0]

        glasses_width_px = face_width  # fallback
        if len(active_cols) > 20:
            glasses_width_px = float(active_cols[-1] - active_cols[0])
            width_ratio = round(glasses_width_px / face_width, 2)
        else:
            width_ratio = 1.04

        row_edges = np.sum(edges, axis=1)
        active_rows = np.where(row_edges > np.max(row_edges) * 0.15)[0] if np.max(row_edges) > 0 else []
        lens_height_px = float(active_rows[-1] - active_rows[0]) if len(active_rows) > 10 else 45.0

        # Соотношение ширины полу-рамки к высоте линзы
        half_frame_ar = glasses_width_px / (2.0 * lens_height_px + 1e-5)

        # ═══════════════════════════════════════════════════════════
        # 5. МНОГОФАКТОРНАЯ КЛАССИФИКАЦИЯ ФОРМЫ ОПРАВЫ (9 категорий)
        # ═══════════════════════════════════════════════════════════

        # --- 5a. Анализ контуров левой линзы ---
        roi_h, roi_w = edges.shape
        half_w = roi_w // 2
        left_lens_roi = edges[:, :half_w]
        contours, _ = cv2.findContours(left_lens_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Выбираем самый большой контур (это и есть линза)
        best_contour = None
        best_area = 0
        for c in contours:
            area = cv2.contourArea(c)
            if area > best_area and area > 60:
                best_area = area
                best_contour = c

        # Метрики контура
        circularity = 0.5
        approx_vertices = 5
        contour_ar = half_frame_ar  # fallback
        top_edge_straightness = 0.5
        vertical_asymmetry = 0.0  # положительное = наружный край выше

        if best_contour is not None and best_area > 80:
            peri = cv2.arcLength(best_contour, True)
            circularity = (4.0 * np.pi * best_area) / (peri * peri + 1e-6)

            # Аппроксимация полигоном
            approx = cv2.approxPolyDP(best_contour, 0.03 * peri, True)
            approx_vertices = len(approx)

            # Bounding rect соотношение сторон
            bx, by, bw, bh = cv2.boundingRect(best_contour)
            contour_ar = bw / (bh + 1e-5)

            # Анализ вертикальной асимметрии (cat-eye: наружный край выше)
            pts = best_contour.reshape(-1, 2)
            inner_quarter = pts[pts[:, 0] < bx + bw * 0.25]
            outer_quarter = pts[pts[:, 0] > bx + bw * 0.75]
            if len(inner_quarter) > 2 and len(outer_quarter) > 2:
                inner_top = np.min(inner_quarter[:, 1])
                outer_top = np.min(outer_quarter[:, 1])
                vertical_asymmetry = (inner_top - outer_top) / (bh + 1e-5)

            # Анализ верхней кромки: прямая линия (clubmaster/wayfarer) vs кривая
            top_pts = pts[pts[:, 1] < by + bh * 0.3]
            if len(top_pts) > 4:
                # Fit прямой линии, оценить отклонение
                if len(top_pts) > 2:
                    vx, vy, x0, y0 = cv2.fitLine(top_pts, cv2.DIST_L2, 0, 0.01, 0.01)
                    line_dir = np.array([vx.item(), vy.item()])
                    line_pt = np.array([x0.item(), y0.item()])
                    deviations = []
                    for p in top_pts:
                        diff = p - line_pt
                        proj = np.dot(diff, line_dir) * line_dir
                        perp = diff - proj
                        deviations.append(np.linalg.norm(perp))
                    top_edge_straightness = 1.0 - min(1.0, np.mean(deviations) / (bh * 0.15 + 1e-5))
                else:
                    top_edge_straightness = 0.5
            else:
                top_edge_straightness = 0.5
        else:
            # Нет чёткого контура — грубая оценка на основе aspect ratio
            circularity = 0.5
            approx_vertices = 5
            contour_ar = half_frame_ar
            top_edge_straightness = 0.5

        # --- 5b. Система голосования по формам ---
        shape_votes: Dict[str, float] = {
            "rectangular": 0, "square": 0, "round": 0, "aviator": 0,
            "cat_eye": 0, "panto": 0, "wayfarer": 0, "clubmaster": 0,
            "geometric": 0
        }

        # ● Циркулярность (0..1, чем ближе к 1 — тем круглее)
        if circularity > 0.78:
            shape_votes["round"] += 3.0
            shape_votes["panto"] += 1.0
        elif circularity > 0.65:
            shape_votes["panto"] += 2.0
            shape_votes["round"] += 1.5
            shape_votes["aviator"] += 1.0
        elif circularity > 0.50:
            shape_votes["wayfarer"] += 1.5
            shape_votes["aviator"] += 1.5
            shape_votes["clubmaster"] += 1.0
        else:
            shape_votes["rectangular"] += 2.0
            shape_votes["square"] += 2.0
            shape_votes["geometric"] += 1.5

        # ● Соотношение сторон контура (ширина / высота)
        if contour_ar > 1.55:
            shape_votes["rectangular"] += 3.0
            shape_votes["cat_eye"] += 1.0
        elif contour_ar > 1.25:
            shape_votes["wayfarer"] += 2.0
            shape_votes["aviator"] += 1.5
            shape_votes["clubmaster"] += 1.5
            shape_votes["rectangular"] += 1.0
        elif contour_ar > 0.95:
            shape_votes["square"] += 2.5
            shape_votes["panto"] += 1.5
            shape_votes["geometric"] += 1.0
        else:
            shape_votes["round"] += 2.5
            shape_votes["square"] += 1.0

        # ● Количество вершин аппроксимации
        if approx_vertices <= 4:
            shape_votes["rectangular"] += 2.0
            shape_votes["square"] += 2.0
        elif approx_vertices <= 6:
            shape_votes["wayfarer"] += 1.5
            shape_votes["clubmaster"] += 1.5
            shape_votes["geometric"] += 2.0
        elif approx_vertices <= 8:
            shape_votes["geometric"] += 2.5
            shape_votes["aviator"] += 1.0
        else:
            shape_votes["round"] += 2.0
            shape_votes["panto"] += 1.0
            shape_votes["aviator"] += 0.5

        # ● Вертикальная асимметрия (cat-eye detector)
        if vertical_asymmetry > 0.15:
            shape_votes["cat_eye"] += 4.0
        elif vertical_asymmetry > 0.08:
            shape_votes["cat_eye"] += 2.5
            shape_votes["wayfarer"] += 0.5

        # ● Прямой верхний край (clubmaster / wayfarer / rectangular)
        if top_edge_straightness > 0.75:
            shape_votes["clubmaster"] += 2.5
            shape_votes["wayfarer"] += 1.5
            shape_votes["rectangular"] += 1.0
        elif top_edge_straightness > 0.55:
            shape_votes["wayfarer"] += 1.0
            shape_votes["panto"] += 1.5
        else:
            shape_votes["round"] += 1.0
            shape_votes["aviator"] += 0.5

        # ● Дополнительные корректировки:
        # Aviator: средняя циркулярность + каплевидная вытянутость вниз
        if 0.55 < circularity < 0.75 and 1.15 < contour_ar < 1.45:
            shape_votes["aviator"] += 2.0

        # Panto: высокая циркулярность + прямоватый верх
        if circularity > 0.60 and top_edge_straightness > 0.55 and contour_ar < 1.25:
            shape_votes["panto"] += 2.5

        # Разрешение конфликта square vs round:
        # Квадрат = низкая циркулярность + 4 вершины + AR ≈ 1
        # Круг = высокая циркулярность + >6 вершин
        if shape_votes["square"] > 0 and shape_votes["round"] > 0:
            if circularity > 0.70 and approx_vertices > 6:
                shape_votes["square"] *= 0.3  # явно круглая
            elif circularity < 0.55 and approx_vertices <= 5:
                shape_votes["round"] *= 0.3  # явно квадратная

        # Определяем финальную форму
        detected_shape = max(shape_votes, key=lambda k: shape_votes[k])

        # Нормализуем ширину в реалистичный оптический диапазон
        width_ratio = min(1.18, max(0.92, width_ratio))

        return {
            "has_glasses": True,
            "shape": detected_shape,
            "width_ratio": width_ratio,
            "aspect_ratio": round(half_frame_ar, 2),
            "lens_height_px": round(lens_height_px, 1)
        }

    def analyze_image_bytes(self, image_bytes: bytes, frame_shape_hint: Optional[str] = None) -> AnalyzeResponse:
        start_time = time.time()
        
        try:
            rgb_img = self._decode_image(image_bytes)
        except Exception as e:
            return AnalyzeResponse(
                success=False,
                face_detected=False,
                message=f"Ошибка обработки изображения: {str(e)}",
                processing_time_ms=round((time.time() - start_time) * 1000, 2)
            )

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)
        detection_result = self._detector.detect(mp_image)

        if not detection_result.face_landmarks:
            return AnalyzeResponse(
                success=True,
                face_detected=False,
                message="Лицо не распознано. Убедитесь, что лицо хорошо освещено и полностью помещается в овал сканирования.",
                processing_time_ms=round((time.time() - start_time) * 1000, 2)
            )

        landmarks = detection_result.face_landmarks[0]

        # 1. Основные реперные точки
        p_top = landmarks[10]       # верх лба
        p_chin = landmarks[152]     # низ подбородка
        p_lcheek = landmarks[234]   # левая скула
        p_rcheek = landmarks[454]   # правая скула
        p_ljaw = landmarks[58]      # левый угол челюсти
        p_rjaw = landmarks[288]     # правый угол челюсти
        p_ltemple = landmarks[127]  # левый висок
        p_rtemple = landmarks[356]  # правый висок
        p_bridge = landmarks[168]   # переносица

        if len(landmarks) > 473:
            p_lpupil = landmarks[468]
            p_rpupil = landmarks[473]
        else:
            p_lpupil = landmarks[159]
            p_rpupil = landmarks[386]

        # 2. Вычисление евклидовых расстояний (нормализованные координаты 0..1)
        face_height = float(np.sqrt((p_top.x - p_chin.x)**2 + (p_top.y - p_chin.y)**2))
        cheek_width = float(np.sqrt((p_lcheek.x - p_rcheek.x)**2 + (p_lcheek.y - p_rcheek.y)**2) + 1e-6)
        jaw_width = float(np.sqrt((p_ljaw.x - p_rjaw.x)**2 + (p_ljaw.y - p_rjaw.y)**2))
        forehead_width = float(np.sqrt((p_ltemple.x - p_rtemple.x)**2 + (p_ltemple.y - p_rtemple.y)**2))
        pupil_dist = float(np.sqrt((p_lpupil.x - p_rpupil.x)**2 + (p_lpupil.y - p_rpupil.y)**2))

        # 3. Индексы пропорций
        hw_ratio = round(face_height / cheek_width, 3)
        jc_ratio = round(jaw_width / cheek_width, 3)
        fc_ratio = round(forehead_width / cheek_width, 3)

        p_chin_l = landmarks[148]
        p_chin_r = landmarks[377]
        chin_angle = round(self._calculate_angle(
            (p_chin_l.x, p_chin_l.y),
            (p_chin.x, p_chin.y),
            (p_chin_r.x, p_chin_r.y)
        ), 1)

        dist_left = np.sqrt((p_bridge.x - p_lcheek.x)**2 + (p_bridge.y - p_lcheek.y)**2)
        dist_right = np.sqrt((p_bridge.x - p_rcheek.x)**2 + (p_bridge.y - p_rcheek.y)**2)
        sym_diff = abs(dist_left - dist_right) / (max(dist_left, dist_right) + 1e-6)
        symmetry_score = round(max(70.0, min(99.0, (1.0 - sym_diff) * 100)), 1)

        metrics = FaceMetrics(
            height_to_width_ratio=hw_ratio,
            jaw_to_cheek_ratio=jc_ratio,
            forehead_to_cheek_ratio=fc_ratio,
            chin_sharpness_deg=chin_angle,
            symmetry_score=symmetry_score
        )

        key_indices = [
            10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152,
            148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109,
            33, 133, 159, 145, 362, 263, 386, 374, 168, 1, 2, 98, 327, 468, 473
        ]
        mesh_points = [[round(landmarks[idx].x, 4), round(landmarks[idx].y, 4)] for idx in key_indices if idx < len(landmarks)]

        summary = LandmarkSummary(
            left_eye_pupil=KeyPoint2D(x=round(p_lpupil.x, 4), y=round(p_lpupil.y, 4)),
            right_eye_pupil=KeyPoint2D(x=round(p_rpupil.x, 4), y=round(p_rpupil.y, 4)),
            nose_bridge=KeyPoint2D(x=round(p_bridge.x, 4), y=round(p_bridge.y, 4)),
            chin_tip=KeyPoint2D(x=round(p_chin.x, 4), y=round(p_chin.y, 4)),
            forehead_center=KeyPoint2D(x=round(p_top.x, 4), y=round(p_top.y, 4)),
            left_cheek=KeyPoint2D(x=round(p_lcheek.x, 4), y=round(p_lcheek.y, 4)),
            right_cheek=KeyPoint2D(x=round(p_rcheek.x, 4), y=round(p_rcheek.y, 4)),
            left_jaw=KeyPoint2D(x=round(p_ljaw.x, 4), y=round(p_ljaw.y, 4)),
            right_jaw=KeyPoint2D(x=round(p_rjaw.x, 4), y=round(p_rjaw.y, 4)),
            pupillary_distance_norm=round(pupil_dist, 4),
            face_mesh_points=mesh_points
        )

        # 4. Классификация формы лица
        face_shape, shape_scores = StylingEngine.classify_face_shape(metrics)
        recommendations, all_shapes_scores = CatalogService.get_recommendations_for_face(face_shape, shape_scores)

        # 5. НОВЫЙ СЦЕНАРИЙ: Оценка надетой оправы и подбор Топ-3 альтернатив
        glasses_info = self._detect_glasses_fit(rgb_img, landmarks)
        if frame_shape_hint and frame_shape_hint.strip():
            glasses_info["shape"] = frame_shape_hint.strip().lower()

        catalog_frames = CatalogService.get_all_frames()
        worn_evaluation, top_alternatives = StylingEngine.evaluate_worn_frame(
            face_shape=face_shape,
            face_metrics=metrics,
            glasses_info=glasses_info,
            catalog_frames=catalog_frames
        )

        elapsed = round((time.time() - start_time) * 1000, 2)

        return AnalyzeResponse(
            success=True,
            face_detected=True,
            message="Анализ лица и оценка посадки оправы успешно завершены",
            face_shape=face_shape,
            metrics=metrics,
            landmarks=summary,
            worn_frame_evaluation=worn_evaluation,
            top_alternatives=top_alternatives,
            top_recommendations=recommendations,
            all_shapes_scores=all_shapes_scores,
            processing_time_ms=elapsed
        )

    def analyze_base64(self, base64_str: str, frame_shape_hint: Optional[str] = None) -> AnalyzeResponse:
        """
        Анализирует изображение, переданное в виде base64-строки:
        автоматически очищает data-URI префикс (data:image/...;base64,) и валидирует данные.
        """
        image_bytes = extract_and_decode_base64(base64_str)
        return self.analyze_image_bytes(image_bytes, frame_shape_hint=frame_shape_hint)

