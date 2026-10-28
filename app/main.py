import os
import json
import base64
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.models.face_analysis import AnalyzeResponse, AnalyzeRequest, ChatRequest, ChatResponse
from app.services.face_mesh_service import FaceMeshService, extract_and_decode_base64
from app.services.catalog_service import CatalogService
from app.services.chat_service import ChatService

app = FastAPI(
    title="abooptika — AI Optical Fitting & Geometry Analysis API",
    description="Инструмент компьютерного зрения для подбора очков и оценки посадки в салоне оптики",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "abooptika AI service is running", "docs": "/docs"}

@app.api_route("/favicon.ico", methods=["GET", "HEAD"], include_in_schema=False)
async def favicon():
    fav_path = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(fav_path):
        return FileResponse(fav_path, media_type="image/x-icon")
    raise HTTPException(status_code=404)

@app.api_route("/manifest.json", methods=["GET", "HEAD"], include_in_schema=False)
async def manifest():
    man_path = os.path.join(STATIC_DIR, "manifest.json")
    if os.path.exists(man_path):
        return FileResponse(man_path, media_type="application/manifest+json")
    raise HTTPException(status_code=404)

@app.api_route("/apple-touch-icon.png", methods=["GET", "HEAD"], include_in_schema=False)
async def apple_touch_icon():
    icon_path = os.path.join(STATIC_DIR, "apple-touch-icon.png")
    if os.path.exists(icon_path):
        return FileResponse(icon_path, media_type="image/png")
    raise HTTPException(status_code=404)

@app.get("/api/health", tags=["Система и статус"])
async def health_check():
    try:
        service = FaceMeshService.get_instance()
        return {
            "status": "healthy",
            "service": "abooptika-ai",
            "model": "MediaPipe FaceLandmarker v1.1.1",
            "catalog_count": len(CatalogService.get_all_frames())
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "degraded", "error": str(e)}
        )

@app.post("/api/analyze", response_model=AnalyzeResponse, tags=["Биометрия и компьютерное зрение"])
async def analyze_face(request: Request):
    """
    Основной API-эндпоинт анализа геометрии лица и оценки посадки надетой оправы.
    Принимает изображение:
      - application/json: валидируется моделью AnalyzeRequest (поддерживает чистый base64 и data-URI),
      - multipart/form-data: загрузка файла через поле 'file'.
    Выполняет автоматическую очистку префикса data:image/...;base64, и валидацию паттерна.
    """
    content_type = request.headers.get("content-type", "")
    image_bytes = None
    frame_shape_hint = request.query_params.get("frame_shape")

    if "multipart/form-data" in content_type:
        form = await request.form()
        uploaded_file = form.get("file")
        if uploaded_file and hasattr(uploaded_file, "read"):
            image_bytes = await uploaded_file.read()
        if not frame_shape_hint and form.get("frame_shape"):
            frame_shape_hint = str(form.get("frame_shape"))
    elif "application/json" in content_type:
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Некорректный JSON в теле запроса")

        try:
            analyze_req = AnalyzeRequest.model_validate(body)
        except ValidationError as e:
            error_details = [f"{err['loc'][-1]}: {err['msg']}" for err in e.errors()]
            raise HTTPException(
                status_code=422,
                detail=f"Ошибка валидации входных данных: {'; '.join(error_details)}"
            )

        if not frame_shape_hint and analyze_req.frame_shape:
            frame_shape_hint = str(analyze_req.frame_shape)

        try:
            image_bytes = extract_and_decode_base64(analyze_req.image_base64)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Ошибка декодирования base64 данных: {str(e)}")
    else:
        raw_body = await request.body()
        if raw_body and len(raw_body) > 100:
            try:
                parsed_json = json.loads(raw_body.decode("utf-8"))
                analyze_req = AnalyzeRequest.model_validate(parsed_json)
                if not frame_shape_hint and analyze_req.frame_shape:
                    frame_shape_hint = str(analyze_req.frame_shape)
                image_bytes = extract_and_decode_base64(analyze_req.image_base64)
            except Exception:
                image_bytes = raw_body

    if not image_bytes or len(image_bytes) < 100:
        raise HTTPException(
            status_code=400,
            detail="Необходимо передать файл (multipart/form-data) или валидную base64-строку изображения (application/json)"
        )

    try:
        service = FaceMeshService.get_instance()
        result = service.analyze_image_bytes(image_bytes, frame_shape_hint=frame_shape_hint)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "face_detected": False,
                "message": f"Ошибка анализа: {str(e)}",
                "detail": f"Внутренняя ошибка сервиса биометрии: {str(e)}"
            }
        )

@app.get("/api/catalog", tags=["Каталог смарт-очков Meta"])
async def get_catalog(
    shape: Optional[str] = Query(None, description="Фильтр по форме (wayfarer, panto, cat_eye, round, geometric, rectangular, aviator)"),
    generation: Optional[str] = Query(None, description="Фильтр по поколению (Gen 1, Gen 2, Gen 3)"),
    brand: Optional[str] = Query(None, description="Фильтр по бренду (Ray-Ban Meta, Stories, Meta)"),
    profile: Optional[str] = Query(None, description="Фильтр по профилю (profile-wayfarer, profile-round-headliner, profile-cateye-skyler, profile-aviator, profile-shield-display)")
):
    frames = CatalogService.get_all_frames()
    if shape:
        frames = [f for f in frames if f.get("shape", "").lower() == shape.lower()]
    if generation:
        frames = [f for f in frames if generation.lower() in f.get("generation", "").lower()]
    if brand:
        frames = [f for f in frames if brand.lower() in f.get("brand", "").lower()]
    if profile:
        frames = [f for f in frames if f.get("profile_id") == profile]
    return {
        "catalog": "Meta & Ray-Ban Meta Smart Glasses",
        "total": len(frames),
        "frames": frames
    }

@app.get("/api/catalog/profiles", tags=["Каталог смарт-очков Meta"])
async def get_catalog_profiles():
    """Возвращает 5 ключевых геометрических профилей смарт-очков Meta и их размерные сетки."""
    profiles = CatalogService.get_all_profiles()
    return {
        "source": "https://www.meta.com/ai-glasses/shop-all/",
        "total": len(profiles),
        "total_profiles": len(profiles),
        "profiles": profiles
    }

@app.post("/api/chat", response_model=ChatResponse, tags=["ИИ-консультант Gemini AI"])
async def chat_with_optometrist(chat_req: ChatRequest):
    """
    Интерактивный ИИ-консультант AbooOptika по смарт-очкам Meta и биометрии лица.
    Работает в реальном времени через защищенный эндпоинт Gemini API.
    """
    if not chat_req.messages:
        raise HTTPException(status_code=400, detail="Список сообщений не может быть пустым")

    response = ChatService.generate_reply(
        messages=chat_req.messages,
        client_context=chat_req.client_context
    )
    return response
