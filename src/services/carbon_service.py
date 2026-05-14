from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from uuid import uuid4
from loguru import logger
import json

from src.models.carbon_models import (
    EnterpriseAccountCreate, EnterpriseAccountResponse,
    EmissionLedgerCreate, EmissionLedgerResponse,
    CarbonAllocationCreate, CarbonAllocationResponse,
    CarbonTransactionCreate, CarbonTransactionResponse,
    EnergyConsumptionCreate, EnergyConsumptionResponse,
    SolarGenerationCreate, SolarGenerationResponse,
    CarbonDashboardResponse, RegionEmissionStats,
    CarbonReportResponse, EmissionForecastResponse
)
from src.models.trace_models import CarbonFootprintCreate, CarbonFootprintResponse
from src.services.blockchain_service import BlockchainService
from src.services.ai_service import AIService


class CarbonService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_account(
        self, account_data: EnterpriseAccountCreate, user
    ) -> EnterpriseAccountResponse:
        account = {
            "id": str(uuid4()),
            "account_no": f"CA-{datetime.now().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}",
            "enterprise_id": account_data.enterprise_id,
            "enterprise_name": account_data.enterprise_name,
            "enterprise_type": account_data.enterprise_type.value if hasattr(account_data.enterprise_type, 'value') else str(account_data.enterprise_type),
            "industry_code": account_data.industry_code,
            "carbon_year": datetime.now().year,
            "total_allocation_t_co2e": account_data.initial_allocation,
            "total_emissions_t_co2e": 0,
            "current_balance_t_co2e": account_data.initial_allocation,
            "compliance_status": "PENDING",
            "created_at": datetime.now()
        }
        return EnterpriseAccountResponse(**account)

    async def list_accounts(
        self, enterprise_type: Optional[str], compliance_status: Optional[str],
        page: int, page_size: int
    ) -> List[EnterpriseAccountResponse]:
        return []

    async def get_account_by_no(self, account_no: str) -> EnterpriseAccountResponse:
        return EnterpriseAccountResponse(
            id=str(uuid4()),
            account_no=account_no,
            enterprise_name="示例企业",
            enterprise_type="KEY_EMISSION",
            carbon_year=datetime.now().year,
            total_allocation_t_co2e=10000,
            total_emissions_t_co2e=8500,
            current_balance_t_co2e=1500,
            compliance_status="COMPLIANT",
            created_at=datetime.now()
        )

    async def create_ledger_entry(
        self, entry_data: EmissionLedgerCreate, user
    ) -> EmissionLedgerResponse:
        total_emissions = float(entry_data.activity_data) * float(entry_data.emission_factor)

        ledger = {
            "id": str(uuid4()),
            "ledger_no": f"LED-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "account_id": entry_data.account_id,
            "enterprise_id": entry_data.enterprise_id,
            "emission_year": entry_data.emission_year,
            "emission_month": entry_data.emission_month,
            "emission_source": entry_data.emission_source.value if hasattr(entry_data.emission_source, 'value') else str(entry_data.emission_source),
            "fuel_type": entry_data.fuel_type,
            "activity_data": entry_data.activity_data,
            "emission_factor": entry_data.emission_factor,
            "total_emissions_t_co2e": total_emissions,
            "data_quality": "VALID",
            "created_at": datetime.now()
        }
        return EmissionLedgerResponse(**ledger)

    async def list_ledger_entries(
        self, account_no: Optional[str], enterprise_id: Optional[str],
        year: Optional[int], month: Optional[int],
        page: int, page_size: int
    ) -> List[EmissionLedgerResponse]:
        return []

    async def create_allocation(
        self, allocation_data: CarbonAllocationCreate, user
    ) -> CarbonAllocationResponse:
        allocation = {
            "id": str(uuid4()),
            "allocation_no": f"ALL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "account_id": allocation_data.account_id,
            "enterprise_id": allocation_data.enterprise_id,
            "allocation_year": allocation_data.allocation_year,
            "allocation_type": allocation_data.allocation_type.value if hasattr(allocation_data.allocation_type, 'value') else str(allocation_data.allocation_type),
            "quota_amount_t_co2e": allocation_data.quota_amount,
            "used_amount_t_co2e": 0,
            "remaining_amount_t_co2e": allocation_data.quota_amount,
            "allocation_date": date.today(),
            "status": "ACTIVE"
        }
        return CarbonAllocationResponse(**allocation)

    async def get_account_allocations(
        self, account_no: str
    ) -> List[CarbonAllocationResponse]:
        return [
            CarbonAllocationResponse(
                id=str(uuid4()),
                account_id=str(uuid4()),
                allocation_no="ALL-2026-001",
                enterprise_id=str(uuid4()),
                allocation_year=2026,
                allocation_type="FREE",
                quota_amount_t_co2e=10000,
                used_amount_t_co2e=3000,
                remaining_amount_t_co2e=7000,
                allocation_date=date.today(),
                status="ACTIVE"
            )
        ]

    async def create_transaction(
        self, transaction_data: CarbonTransactionCreate, user
    ) -> CarbonTransactionResponse:
        transaction = {
            "id": str(uuid4()),
            "transaction_no": f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "transaction_type": transaction_data.transaction_type.value if hasattr(transaction_data.transaction_type, 'value') else str(transaction_data.transaction_type),
            "buyer_account_id": transaction_data.buyer_account_id,
            "seller_account_id": transaction_data.seller_account_id,
            "carbon_credit_type": "CCER",
            "quantity_t_co2e": transaction_data.quantity,
            "unit_price": transaction_data.unit_price,
            "total_amount": float(transaction_data.quantity) * float(transaction_data.unit_price),
            "transaction_date": datetime.now(),
            "status": "COMPLETED"
        }
        return CarbonTransactionResponse(**transaction)

    async def list_transactions(
        self, buyer_account_no: Optional[str], transaction_type: Optional[str],
        start_date: Optional[datetime], end_date: Optional[datetime],
        page: int, page_size: int
    ) -> List[CarbonTransactionResponse]:
        return []

    async def create_energy_record(
        self, record_data: EnergyConsumptionCreate, user
    ) -> EnergyConsumptionResponse:
        emissions = float(record_data.consumption_amount) * 0.84 if str(record_data.energy_type) == "ELECTRICITY" else 0

        record = {
            "id": str(uuid4()),
            "enterprise_id": record_data.enterprise_id,
            "consumption_year": record_data.consumption_year,
            "consumption_month": record_data.consumption_month,
            "energy_type": record_data.energy_type.value if hasattr(record_data.energy_type, 'value') else str(record_data.energy_type),
            "consumption_amount": record_data.consumption_amount,
            "consumption_unit": record_data.consumption_unit,
            "associated_emissions_t_co2e": emissions,
            "created_at": datetime.now()
        }
        return EnergyConsumptionResponse(**record)

    async def get_enterprise_energy(
        self, enterprise_id: str, year: Optional[int], month: Optional[int]
    ) -> List[EnergyConsumptionResponse]:
        return []

    async def create_solar_record(
        self, record_data: SolarGenerationCreate, user
    ) -> SolarGenerationResponse:
        record = {
            "id": str(uuid4()),
            "enterprise_id": record_data.enterprise_id,
            "installation_id": record_data.installation_id,
            "capacity_kw": record_data.capacity_kw,
            "generation_date": record_data.generation_date,
            "generation_hour": record_data.generation_hour,
            "generation_kwh": record_data.generation_kwh,
            "self_consumption_kwh": record_data.generation_kwh * 0.3,
            "grid_feed_kwh": record_data.generation_kwh * 0.7,
            "created_at": datetime.now()
        }
        return SolarGenerationResponse(**record)

    async def calculate_and_register_footprint(
        self, footprint_data: CarbonFootprintCreate,
        blockchain_service: BlockchainService, user
    ) -> CarbonFootprintResponse:
        ai_service = AIService()
        carbon_result = await ai_service.calculate_carbon_footprint(
            footprint_data.model_dump()
        )

        footprint_id = f"CF-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        chain_result = await blockchain_service.register_carbon_footprint(
            footprint_id=footprint_id,
            carbon_data=carbon_result
        )

        footprint = {
            "id": str(uuid4()),
            "footprint_id": footprint_id,
            "batch_id": footprint_data.batch_id,
            "product_name": footprint_data.product_name,
            "product_unit": footprint_data.product_unit,
            "total_emissions_kg": carbon_result["total_emissions_kg"],
            "production_emissions_kg": carbon_result["production_emissions_kg"],
            "processing_emissions_kg": carbon_result["processing_emissions_kg"],
            "logistics_emissions_kg": carbon_result["logistics_emissions_kg"],
            "packaging_emissions_kg": carbon_result["packaging_emissions_kg"],
            "data_quality_factor": carbon_result["data_quality_factor"],
            "calculation_method": carbon_result["calculation_method"],
            "status": "CALCULATED",
            "chain_hash": chain_result["data_hash"],
            "chain_timestamp": datetime.now()
        }

        return CarbonFootprintResponse(**footprint)

    async def get_footprint(self, footprint_id: str) -> CarbonFootprintResponse:
        return CarbonFootprintResponse(
            id=str(uuid4()),
            footprint_id=footprint_id,
            batch_id=str(uuid4()),
            product_name="示例产品",
            total_emissions_kg=25.5,
            status="CALCULATED",
            created_at=datetime.now()
        )

    async def get_footprint_by_batch(self, batch_id: str) -> Optional[CarbonFootprintResponse]:
        return CarbonFootprintResponse(
            id=str(uuid4()),
            footprint_id=f"CF-{batch_id[:8]}",
            batch_id=batch_id,
            product_name="有机大米",
            product_unit="KG",
            total_emissions_kg=1.85,
            production_emissions_kg=1.2,
            processing_emissions_kg=0.35,
            logistics_emissions_kg=0.2,
            packaging_emissions_kg=0.1,
            status="CALCULATED",
            created_at=datetime.now()
        )

    async def get_region_dashboard(
        self, region_code: str, year: int
    ) -> CarbonDashboardResponse:
        return CarbonDashboardResponse(
            region_code=region_code,
            year=year,
            total_emissions_t_co2e=1250000,
            total_allocation_t_co2e=1500000,
            compliance_rate=83.3,
            industry_breakdown=[
                {"industry": "工业", "emissions_t": 750000, "pct": 60.0},
                {"industry": "能源", "emissions_t": 300000, "pct": 24.0},
                {"industry": "农业", "emissions_t": 125000, "pct": 10.0},
                {"industry": "其他", "emissions_t": 75000, "pct": 6.0}
            ]
        )

    async def get_emission_structure(
        self, region_code: Optional[str], enterprise_id: Optional[str], year: int
    ) -> RegionEmissionStats:
        return RegionEmissionStats(
            region_code=region_code or "ALL",
            year=year,
            total_emissions_t_co2e=1250000,
            total_allocation_t_co2e=1500000,
            compliance_rate=83.3,
            industry_breakdown=[
                {"industry": "工业", "emissions_t": 750000, "pct": 60.0},
                {"industry": "能源", "emissions_t": 300000, "pct": 24.0},
                {"industry": "农业", "emissions_t": 125000, "pct": 10.0},
                {"industry": "其他", "emissions_t": 75000, "pct": 6.0}
            ]
        )

    async def generate_annual_report(
        self, region_code: str, year: int
    ) -> CarbonReportResponse:
        return CarbonReportResponse(
            region_code=region_code,
            year=year,
            report_no=f"CR-{region_code}-{year}",
            generated_at=datetime.now(),
            total_emissions_t_co2e=1250000,
            total_allocation_t_co2e=1500000,
            compliance_rate=83.3,
            industry_breakdown=[],
            quarterly_emissions=[],
            year_over_year_change_pct=-5.2
        )

    async def get_region_ranking(
        self, year: int, top_n: int
    ) -> List[RegionEmissionStats]:
        results = []
        for i in range(min(top_n, 5)):
            results.append(RegionEmissionStats(
                region_code=f"REGION-{i}",
                year=year,
                total_emissions_t_co2e=1250000 - i * 50000,
                total_allocation_t_co2e=1500000,
                compliance_rate=83.3 + i * 0.5,
                industry_breakdown=[]
            ))
        return results

    async def get_industry_ranking(self, year: int, top_n: int) -> List[Dict[str, Any]]:
        return [
            {"industry": "钢铁", "emissions_t": 350000, "enterprise_count": 45},
            {"industry": "水泥", "emissions_t": 280000, "enterprise_count": 62},
            {"industry": "电力", "emissions_t": 250000, "enterprise_count": 38},
            {"industry": "化工", "emissions_t": 180000, "enterprise_count": 85},
            {"industry": "铝业", "emissions_t": 120000, "enterprise_count": 30}
        ][:top_n]
