from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class EnterpriseType(str, Enum):
    KEY_EMISSION = "KEY_EMISSION"
    VOLUNTARY = "VOLUNTARY"
    SMALL = "SMALL"


class ComplianceStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    PENDING = "PENDING"


class EmissionSource(str, Enum):
    STATIONARY = "STATIONARY"
    MOBILE = "MOBILE"
    PROCESS = "PROCESS"
    FUGITIVE = "FUGITIVE"


class EnergyType(str, Enum):
    ELECTRICITY = "ELECTRICITY"
    NATURAL_GAS = "NATURAL_GAS"
    COAL = "COAL"
    OIL = "OIL"
    RENEWABLE = "RENEWABLE"


class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    OFFSET = "OFFSET"
    RETIREMENT = "RETIREMENT"


class AllocationType(str, Enum):
    FREE = "FREE"
    PAID = "PAID"
    OFFSET = "OFFSET"


class EnterpriseAccountCreate(BaseModel):
    enterprise_id: str
    enterprise_name: str
    enterprise_type: EnterpriseType
    industry_code: Optional[str] = None
    registration_date: Optional[date] = None
    initial_allocation: float = 0


class EnterpriseAccountResponse(BaseModel):
    id: str
    account_no: str
    enterprise_name: str
    enterprise_type: str
    carbon_year: int
    total_allocation_t_co2e: float
    total_emissions_t_co2e: float
    total_offset_t_co2e: Optional[float] = 0
    current_balance_t_co2e: float
    compliance_status: str
    created_at: datetime


class EmissionLedgerCreate(BaseModel):
    account_id: str
    enterprise_id: str
    emission_year: int
    emission_month: Optional[int] = None
    emission_source: EmissionSource
    fuel_type: Optional[str] = None
    activity_data: float
    emission_factor: float
    calculation_method: Optional[str] = "IPCC"


class EmissionLedgerResponse(BaseModel):
    id: str
    ledger_no: str
    account_id: str
    enterprise_id: str
    emission_year: int
    emission_month: Optional[int] = None
    emission_source: str
    fuel_type: Optional[str] = None
    activity_data: float
    emission_factor: float
    total_emissions_t_co2e: float
    data_quality: str
    verification_status: Optional[str] = None
    created_at: datetime


class CarbonAllocationCreate(BaseModel):
    account_id: str
    enterprise_id: str
    allocation_year: int
    allocation_type: AllocationType = AllocationType.FREE
    quota_amount: float
    quota_price: Optional[float] = None


class CarbonAllocationResponse(BaseModel):
    id: str
    allocation_no: str
    account_id: str
    enterprise_id: str
    allocation_year: int
    allocation_type: str
    quota_amount_t_co2e: float
    used_amount_t_co2e: float
    remaining_amount_t_co2e: float
    allocation_date: date
    status: str


class CarbonTransactionCreate(BaseModel):
    transaction_type: TransactionType
    buyer_account_id: str
    seller_account_id: Optional[str] = None
    carbon_credit_type: str = "CCER"
    quantity: float
    unit_price: float


class CarbonTransactionResponse(BaseModel):
    id: str
    transaction_no: str
    transaction_type: str
    buyer_account_id: str
    seller_account_id: Optional[str] = None
    carbon_credit_type: str
    quantity_t_co2e: float
    unit_price: float
    total_amount: float
    transaction_date: datetime
    status: str


class EnergyConsumptionCreate(BaseModel):
    account_id: Optional[str] = None
    enterprise_id: str
    consumption_year: int
    consumption_month: Optional[int] = None
    energy_type: EnergyType
    consumption_amount: float
    consumption_unit: str = "KWH"
    cost: Optional[float] = None


class EnergyConsumptionResponse(BaseModel):
    id: str
    enterprise_id: str
    consumption_year: int
    consumption_month: Optional[int] = None
    energy_type: str
    consumption_amount: float
    consumption_unit: str
    associated_emissions_t_co2e: Optional[float] = None
    created_at: datetime


class SolarGenerationCreate(BaseModel):
    enterprise_id: str
    installation_id: Optional[str] = None
    capacity_kw: float
    generation_date: date
    generation_hour: Optional[int] = None
    generation_kwh: float


class SolarGenerationResponse(BaseModel):
    id: str
    enterprise_id: str
    capacity_kw: float
    generation_date: date
    generation_hour: Optional[int] = None
    generation_kwh: float
    self_consumption_kwh: Optional[float] = None
    grid_feed_kwh: Optional[float] = None
    created_at: datetime


class CarbonDashboardResponse(BaseModel):
    region_code: str
    year: int
    total_emissions_t_co2e: float
    total_allocation_t_co2e: float
    compliance_rate: float
    industry_breakdown: List[Dict[str, Any]]


class RegionEmissionStats(BaseModel):
    region_code: str
    year: int
    total_emissions_t_co2e: float
    total_allocation_t_co2e: float
    compliance_rate: float
    industry_breakdown: List[Dict[str, Any]]


class CarbonReportResponse(BaseModel):
    region_code: str
    year: int
    report_no: str
    generated_at: datetime
    total_emissions_t_co2e: float
    total_allocation_t_co2e: float
    compliance_rate: float
    industry_breakdown: List[Dict[str, Any]]
    quarterly_emissions: List[Dict[str, Any]]
    year_over_year_change_pct: float


class EmissionForecastResponse(BaseModel):
    region_code: str
    target_year: int
    forecast_date: datetime
    predicted_emissions_t: float
    confidence_interval: List[float]
    peak_year: Optional[int] = None
    carbon_intensity_reduction_pct: Optional[float] = None
