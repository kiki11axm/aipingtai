from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.core.database import get_db
from src.core.security import get_current_user, TokenData
from src.models.trace_models import (
    ProductBatchCreate, ProductBatchResponse,
    TraceNodeCreate, TraceNodeResponse,
    LogisticsCreate, LogisticsResponse,
    CarbonFootprintResponse, CarbonFootprintCreate,
    TraceQueryResponse, QRCodeResponse
)
from src.services.trace_service import TraceService
from src.services.carbon_service import CarbonService
from src.services.blockchain_service import BlockchainService


router = APIRouter()


@router.post("/batches", response_model=ProductBatchResponse)
async def create_batch(
    batch_data: ProductBatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = TraceService(db)
    return await service.create_batch(batch_data, current_user)


@router.get("/batches/{batch_code}", response_model=ProductBatchResponse)
async def get_batch(
    batch_code: str,
    db: AsyncSession = Depends(get_db)
):
    service = TraceService(db)
    return await service.get_batch_by_code(batch_code)


@router.get("/batches", response_model=List[ProductBatchResponse])
async def list_batches(
    product_name: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = TraceService(db)
    return await service.list_batches(
        product_name, status, start_date, end_date, page, page_size
    )


@router.post("/batches/{batch_id}/nodes", response_model=TraceNodeResponse)
async def add_trace_node(
    batch_id: str,
    node_data: TraceNodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = TraceService(db)
    blockchain_service = BlockchainService()
    return await service.add_node(batch_id, node_data, blockchain_service, current_user)


@router.get("/batches/{batch_id}/nodes", response_model=List[TraceNodeResponse])
async def get_trace_nodes(
    batch_id: str,
    db: AsyncSession = Depends(get_db)
):
    service = TraceService(db)
    return await service.get_nodes(batch_id)


@router.post("/logistics", response_model=LogisticsResponse)
async def create_logistics(
    logistics_data: LogisticsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = TraceService(db)
    return await service.create_logistics(logistics_data, current_user)


@router.get("/logistics/{logistics_no}", response_model=LogisticsResponse)
async def get_logistics(
    logistics_no: str,
    db: AsyncSession = Depends(get_db)
):
    service = TraceService(db)
    return await service.get_logistics_by_no(logistics_no)


@router.post("/carbon-footprint", response_model=CarbonFootprintResponse)
async def calculate_carbon_footprint(
    footprint_data: CarbonFootprintCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    carbon_service = CarbonService(db)
    blockchain_service = BlockchainService()
    return await carbon_service.calculate_and_register_footprint(
        footprint_data, blockchain_service, current_user
    )


@router.get("/carbon-footprint/{footprint_id}", response_model=CarbonFootprintResponse)
async def get_carbon_footprint(
    footprint_id: str,
    db: AsyncSession = Depends(get_db)
):
    carbon_service = CarbonService(db)
    return await carbon_service.get_footprint(footprint_id)


@router.get("/query/qrcode/{qrcode_data}", response_model=TraceQueryResponse)
async def query_by_qrcode(
    qrcode_data: str,
    db: AsyncSession = Depends(get_db)
):
    service = TraceService(db)
    carbon_service = CarbonService(db)
    return await service.query_by_qrcode(qrcode_data, carbon_service)


@router.get("/query/batch/{batch_code}", response_model=TraceQueryResponse)
async def query_by_batch(
    batch_code: str,
    db: AsyncSession = Depends(get_db)
):
    service = TraceService(db)
    carbon_service = CarbonService(db)
    return await service.query_by_batch_code(batch_code, carbon_service)


@router.post("/verify/{batch_code}")
async def verify_product(
    batch_code: str,
    db: AsyncSession = Depends(get_db)
):
    service = TraceService(db)
    blockchain_service = BlockchainService()
    return await service.verify_product(batch_code, blockchain_service)


@router.get("/qrcode/{batch_id}", response_model=QRCodeResponse)
async def generate_qrcode(
    batch_id: str,
    qrcode_type: str = Query("BOTH", description="QR码类型: TRACE, CARBON, BOTH"),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = TraceService(db)
    return await service.generate_qrcode(batch_id, qrcode_type)


@router.post("/chain/verify")
async def verify_chain_data(
    batch_id: str,
    db: AsyncSession = Depends(get_db)
):
    blockchain_service = BlockchainService()
    service = TraceService(db)
    return await service.verify_chain_data(batch_id, blockchain_service)
