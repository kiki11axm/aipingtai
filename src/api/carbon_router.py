from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.core.database import get_db
from src.core.security import get_current_user, TokenData
from src.models.carbon_models import (
    EnterpriseAccountCreate, EnterpriseAccountResponse,
    EmissionLedgerCreate, EmissionLedgerResponse,
    CarbonAllocationResponse, CarbonAllocationCreate,
    CarbonTransactionResponse, CarbonTransactionCreate,
    EnergyConsumptionCreate, EnergyConsumptionResponse,
    SolarGenerationCreate, SolarGenerationResponse,
    CarbonDashboardResponse, RegionEmissionStats,
    CarbonReportResponse, EmissionForecastResponse
)
from src.services.carbon_service import CarbonService
from src.services.ai_service import AIService


router = APIRouter()


@router.post("/accounts", response_model=EnterpriseAccountResponse)
async def create_carbon_account(
    account_data: EnterpriseAccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.create_account(account_data, current_user)


@router.get("/accounts", response_model=List[EnterpriseAccountResponse])
async def list_accounts(
    enterprise_type: Optional[str] = None,
    compliance_status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.list_accounts(enterprise_type, compliance_status, page, page_size)


@router.get("/accounts/{account_no}", response_model=EnterpriseAccountResponse)
async def get_account(
    account_no: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.get_account_by_no(account_no)


@router.post("/ledger", response_model=EmissionLedgerResponse)
async def create_ledger_entry(
    entry_data: EmissionLedgerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.create_ledger_entry(entry_data, current_user)


@router.get("/ledger", response_model=List[EmissionLedgerResponse])
async def list_ledger_entries(
    account_no: Optional[str] = None,
    enterprise_id: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.list_ledger_entries(
        account_no, enterprise_id, year, month, page, page_size
    )


@router.post("/allocation", response_model=CarbonAllocationResponse)
async def create_allocation(
    allocation_data: CarbonAllocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.create_allocation(allocation_data, current_user)


@router.get("/allocation/account/{account_no}", response_model=List[CarbonAllocationResponse])
async def get_account_allocations(
    account_no: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.get_account_allocations(account_no)


@router.post("/transaction", response_model=CarbonTransactionResponse)
async def create_transaction(
    transaction_data: CarbonTransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.create_transaction(transaction_data, current_user)


@router.get("/transactions", response_model=List[CarbonTransactionResponse])
async def list_transactions(
    buyer_account_no: Optional[str] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.list_transactions(
        buyer_account_no, transaction_type, start_date, end_date, page, page_size
    )


@router.post("/energy", response_model=EnergyConsumptionResponse)
async def create_energy_record(
    record_data: EnergyConsumptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.create_energy_record(record_data, current_user)


@router.get("/energy/enterprise/{enterprise_id}", response_model=List[EnergyConsumptionResponse])
async def get_enterprise_energy(
    enterprise_id: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.get_enterprise_energy(enterprise_id, year, month)


@router.post("/solar", response_model=SolarGenerationResponse)
async def create_solar_record(
    record_data: SolarGenerationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.create_solar_record(record_data, current_user)


@router.get("/dashboard/region/{region_code}", response_model=CarbonDashboardResponse)
async def get_region_dashboard(
    region_code: str,
    year: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.get_region_dashboard(region_code, year)


@router.get("/emissions/structure", response_model=RegionEmissionStats)
async def get_emission_structure(
    region_code: Optional[str] = None,
    enterprise_id: Optional[str] = None,
    year: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.get_emission_structure(region_code, enterprise_id, year)


@router.post("/report/annual", response_model=CarbonReportResponse)
async def generate_annual_report(
    region_code: str,
    year: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.generate_annual_report(region_code, year)


@router.post("/forecast", response_model=EmissionForecastResponse)
async def forecast_emissions(
    region_code: str,
    target_year: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    ai_service = AIService()
    return await ai_service.forecast_carbon_emissions(region_code, target_year)


@router.get("/ranking/region", response_model=List[RegionEmissionStats])
async def get_region_ranking(
    year: int = Query(...),
    top_n: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.get_region_ranking(year, top_n)


@router.get("/ranking/industry", response_model=List[dict])
async def get_industry_ranking(
    year: int = Query(...),
    top_n: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    service = CarbonService(db)
    return await service.get_industry_ranking(year, top_n)
