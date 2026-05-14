from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class PlotType(str, Enum):
    CULTIVATED = "CULTIVATED"
    ORCHARD = "ORCHARD"
    GREENHOUSE = "GREENHOUSE"
    FISHING = "FISHING"


class OperationType(str, Enum):
    PLANTING = "PLANTING"
    FERTILIZING = "FERTILIZING"
    IRRIGATION = "IRRIGATION"
    PESTICIDE = "PESTICIDE"
    HARVEST = "HARVEST"


class GrowthStage(str, Enum):
    SEEDLING = "SEEDLING"
    GROWING = "GROWING"
    FLOWERING = "FLOWERING"
    FRUITING = "FRUITING"
    MATURATION = "MATURATION"
    HARVESTED = "HARVESTED"


class PlotCreate(BaseModel):
    plot_name: str
    plot_type: PlotType
    boundary_geojson: Dict[str, Any]
    area_sqm: float
    organization_id: Optional[str] = None
    region_code: Optional[str] = None


class PlotUpdate(BaseModel):
    plot_name: Optional[str] = None
    boundary_geojson: Optional[Dict[str, Any]] = None
    irrigation_type: Optional[str] = None


class PlotResponse(BaseModel):
    id: str
    plot_code: str
    plot_name: str
    plot_type: str
    area_sqm: float
    area_mu: Optional[float] = None
    organization_id: Optional[str] = None
    region_code: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CropRecordCreate(BaseModel):
    crop_type: str
    crop_name: str
    crop_variety: Optional[str] = None
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    planting_area_mu: Optional[float] = None
    expected_yield_kg: Optional[float] = None


class CropRecordResponse(BaseModel):
    id: str
    plot_id: str
    crop_type: str
    crop_name: str
    crop_variety: Optional[str] = None
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    planting_area_mu: Optional[float] = None
    growth_stage: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class SoilDataCreate(BaseModel):
    plot_id: str
    sample_point_lat: Optional[float] = None
    sample_point_lon: Optional[float] = None
    sample_depth_cm: Optional[int] = 20
    sample_time: datetime
    ph_value: Optional[float] = None
    organic_matter_pct: Optional[float] = None
    nitrogen_mg_kg: Optional[float] = None
    phosphorus_mg_kg: Optional[float] = None
    potassium_mg_kg: Optional[float] = None
    moisture_pct: Optional[float] = None
    data_source: Optional[str] = "MANUAL"


class SoilDataResponse(BaseModel):
    id: str
    plot_id: str
    sample_time: datetime
    ph_value: Optional[float] = None
    nitrogen_mg_kg: Optional[float] = None
    phosphorus_mg_kg: Optional[float] = None
    potassium_mg_kg: Optional[float] = None
    moisture_pct: Optional[float] = None
    data_source: str
    data_quality: str
    created_at: datetime

    class Config:
        from_attributes = True


class OperationRecordCreate(BaseModel):
    plot_id: str
    crop_record_id: Optional[str] = None
    operation_type: OperationType
    operation_name: Optional[str] = None
    operation_time: datetime
    equipment_id: Optional[str] = None
    equipment_name: Optional[str] = None
    operation_area_mu: Optional[float] = None
    input_amount: Optional[float] = None
    input_unit: Optional[str] = None
    input_type: Optional[str] = None
    input_name: Optional[str] = None
    gis_trace: Optional[Dict[str, Any]] = None


class OperationRecordResponse(BaseModel):
    id: str
    plot_id: str
    operation_type: str
    operation_name: str
    operation_time: datetime
    operator_name: Optional[str] = None
    equipment_name: Optional[str] = None
    operation_area_mu: Optional[float] = None
    input_amount: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PrescriptionCreate(BaseModel):
    plot_id: str
    crop_record_id: Optional[str] = None
    target_yield_kg: float


class FertilizerPrescriptionResponse(BaseModel):
    id: str
    plot_id: str
    prescription_no: str
    target_yield_kg: float
    soil_available_n: float
    soil_available_p: float
    soil_available_k: float
    organic_fertilizer_n: float
    organic_fertilizer_p: float
    organic_fertilizer_k: float
    total_fertilizer_kg: float
    base_fertilizer_kg: float
    top_dressing_kg: float
    recommended_date: date
    ai_confidence: float
    created_at: datetime

    class Config:
        from_attributes = True


class YieldEstimationResponse(BaseModel):
    id: str
    plot_id: str
    estimation_no: str
    estimation_time: datetime
    estimated_yield_kg: float
    confidence_level: float
    growth_stage: str
    ndvi_value: Optional[float] = None
    ai_model_version: str
    created_at: datetime

    class Config:
        from_attributes = True


class NDVIAnalysisRequest(BaseModel):
    plot_id: str
    satellite_source: Optional[str] = "sentinel"
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class NDVIAnalysisResponse(BaseModel):
    plot_id: str
    ndvi_value: float
    ndvi_grade: str
    healthy_area_pct: float
    analysis_date: datetime
    satellite_source: str
    vegetation_distribution: List[Dict[str, Any]]


class OperationStats(BaseModel):
    total_operations: int
    operation_breakdown: List[Dict[str, Any]]


class FarmDashboardResponse(BaseModel):
    total_plots: int
    growing_plots: int
    total_area_mu: float
    today_operations: int
    alert_count: int
