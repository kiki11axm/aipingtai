from fastapi import APIRouter, Depends, Query, Body
from typing import Optional
from datetime import datetime
from loguru import logger

from src.core.security import get_current_user, TokenData
from src.services.ai_service import AIService
from src.services.data_collection_service import DataCollectionService


router = APIRouter()


@router.post("/ndvi/analyze")
async def analyze_ndvi(
    plot_id: str = Query(...),
    satellite_source: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    ai_service = AIService()
    result = await ai_service.analyze_ndvi(type('obj', (object,), {
        'plot_id': plot_id,
        'satellite_source': satellite_source,
        'start_date': start_date,
        'end_date': end_date
    })())
    return result


@router.post("/pest/detect")
async def detect_pest_disease(
    plot_id: str = Query(...),
):
    ai_service = AIService()
    result = await ai_service.detect_pest_disease(b"", plot_id)
    return result


@router.post("/yield/estimate")
async def estimate_yield(
    plot_id: str = Query(...),
):
    ai_service = AIService()
    result = await ai_service.estimate_yield(plot_id)
    return result


@router.post("/fertilizer/prescribe")
async def generate_fertilizer_prescription(
    plot_id: str = Query(...),
    target_yield_kg: float = Query(...),
    soil_n: float = Query(...),
    soil_p: float = Query(...),
    soil_k: float = Query(...),
):
    ai_service = AIService()
    result = await ai_service.generate_fertilizer_prescription(
        plot_id, target_yield_kg, soil_n, soil_p, soil_k
    )
    return result


@router.post("/carbon/footprint")
async def calculate_carbon_footprint(
    activity_data: dict = Body(...),
):
    ai_service = AIService()
    result = await ai_service.calculate_carbon_footprint(activity_data)
    return result


@router.post("/carbon/forecast")
async def forecast_carbon_emissions(
    region_code: str = Query(...),
    target_year: int = Query(...),
):
    ai_service = AIService()
    result = await ai_service.forecast_carbon_emissions(region_code, target_year)
    return result


@router.post("/carbon/peak-pathway")
async def analyze_peak_pathway(
    region_code: str = Query(...),
):
    ai_service = AIService()
    result = await ai_service.analyze_peak_pathway(region_code)
    return result


@router.get("/model/status")
async def get_model_status():
    return {
        "models": [
            {
                "name": "ndvi_analyzer",
                "status": "ONLINE",
                "version": "v1.0",
                "avg_response_time_ms": 150
            },
            {
                "name": "pest_detector",
                "status": "ONLINE",
                "version": "v1.0",
                "avg_response_time_ms": 200
            },
            {
                "name": "yield_estimator",
                "status": "ONLINE",
                "version": "v1.0",
                "avg_response_time_ms": 250
            },
            {
                "name": "fertilizer_prescriber",
                "status": "ONLINE",
                "version": "v1.0",
                "avg_response_time_ms": 180
            },
            {
                "name": "carbon_calculator",
                "status": "ONLINE",
                "version": "v1.0",
                "avg_response_time_ms": 200
            }
        ],
        "total_requests_today": 1547,
        "success_rate": 99.5
    }
