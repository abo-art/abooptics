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
    assert "совместимость" in worn["verdict_quote_ru"].lower()
    assert len(worn["verdict_quote_ru"]) > 15
    assert worn["fit_metrics"]["width_status"] in ["Идеально", "Широковата", "Узковата"]
    
    # 2. Топ-3 альтернативы
    alts = data.get("top_alternatives")
    assert len(alts) == 3
    for alt in alts:
        assert alt["match_score"] >= 88
        assert len(alt["why_better_ru"]) > 10
        assert alt["shape"] != "square" # Альтернативы исключают текущую неудачную форму
        assert len(alt["material"]) > 3
        assert len(alt["dimensions"]) > 3

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
    assert len(data["top_alternatives"]) == 3

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
    assert len(data["top_alternatives"]) == 3

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

