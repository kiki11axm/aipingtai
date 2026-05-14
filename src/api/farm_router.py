from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from src.core.database import get_db
from src.core.security import get_current_user, TokenData
from src.models.farm_models import (
    PlotCreate, PlotResponse, PlotUpdate,
    CropRecordCreate, CropRecordResponse,
    SoilDataCreate, SoilDataResponse,
    OperationRecordCreate, OperationRecordResponse,
    FertilizerPrescriptionResponse, PrescriptionCreate,
    YieldEstimationResponse, NDVIAnalysisRequest, NDVIAnalysisResponse,
    OperationStats, FarmDashboardResponse
)
from src.services.farm_service import FarmService
from src.services.ai_service import AIService
from src.services.data_collection_service import DataCollectionService
import io


router = APIRouter()


@router.post("/plots", response_model=PlotResponse)
async def create_plot(
    plot_data: PlotCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = FarmService(db)
    return await service.create_plot(plot_data, current_user)


@router.get("/plots", response_model=List[PlotResponse])
async def list_plots(
    organization_id: Optional[str] = None,
    region_code: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = FarmService(db)
    return await service.list_plots(organization_id, region_code, page, page_size)


@router.get("/plots/{plot_id}", response_model=PlotResponse)
async def get_plot(
    plot_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = FarmService(db)
    return await service.get_plot(plot_id)


@router.put("/plots/{plot_id}", response_model=PlotResponse)
async def update_plot(
    plot_id: str,
    plot_data: PlotUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = FarmService(db)
    return await service.update_plot(plot_id, plot_data)


@router.delete("/plots/{plot_id}")
async def delete_plot(
    plot_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = FarmService(db)
    await service.delete_plot(plot_id)
    return {"message": "地块删除成功"}


@router.post("/plots/{plot_id}/crop-records", response_model=CropRecordResponse)
async def create_crop_record(
    plot_id: str,
    record_data: CropRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = FarmService(db)
    return await service.create_crop_record(plot_id, record_data)


@router.get("/plots/{plot_id}/crop-records", response_model=List[CropRecordResponse])
async def list_crop_records(
    plot_id: str,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = FarmService(db)
    return await service.list_crop_records(plot_id, status)


@router.post("/soil-data", response_model=SoilDataResponse)
async def create_soil_data(
    data: SoilDataCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = FarmService(db)
    return await service.create_soil_data(data)


@router.get("/plots/{plot_id}/soil-data", response_model=List[SoilDataResponse])
async def get_soil_data(
    plot_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = FarmService(db)
    return await service.get_soil_data(plot_id, start_time, end_time)


@router.post("/operations", response_model=OperationRecordResponse)
async def create_operation(
    data: OperationRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = FarmService(db)
    return await service.create_operation(data, current_user)


@router.get("/operations/stats", response_model=OperationStats)
async def get_operation_stats(
    plot_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = FarmService(db)
    return await service.get_operation_stats(plot_id, start_date, end_date)


@router.post("/prescriptions", response_model=FertilizerPrescriptionResponse)
async def generate_prescription(
    data: PrescriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = FarmService(db)
    ai_service = AIService()
    return await service.generate_prescription(data, ai_service, current_user)


@router.get("/plots/{plot_id}/yield-estimation", response_model=YieldEstimationResponse)
async def get_yield_estimation(
    plot_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = FarmService(db)
    ai_service = AIService()
    return await service.get_yield_estimation(plot_id, ai_service)


@router.post("/ndvi-analysis", response_model=NDVIAnalysisResponse)
async def analyze_ndvi(
    data: NDVIAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    ai_service = AIService()
    return await ai_service.analyze_ndvi(data)


@router.get("/dashboard", response_model=FarmDashboardResponse)
async def get_dashboard(
    organization_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = FarmService(db)
    return await service.get_dashboard(organization_id)


@router.post("/data/satellite")
async def upload_satellite_data(
    file: UploadFile = File(...),
    source: str = Query(..., description="数据源: sentinel, gaofen"),
    capture_time: datetime = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    contents = await file.read()
    collection_service = DataCollectionService(db)
    result = await collection_service.process_satellite_data(
        file_data=contents,
        filename=file.filename,
        source=source,
        capture_time=capture_time,
        user_id=current_user.user_id
    )
    return result


@router.post("/data/drone")
async def upload_drone_data(
    file: UploadFile = File(...),
    plot_id: str = Query(...),
    flight_time: datetime = Query(...),
    operation_type: str = Query("mapping"),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    contents = await file.read()
    collection_service = DataCollectionService(db)
    result = await collection_service.process_drone_data(
        file_data=contents,
        filename=file.filename,
        plot_id=plot_id,
        flight_time=flight_time,
        operation_type=operation_type,
        user_id=current_user.user_id
    )
    return result
