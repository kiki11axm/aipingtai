from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class NodeType(str, Enum):
    PRODUCTION = "PRODUCTION"
    PROCESSING = "PROCESSING"
    LOGISTICS = "LOGISTICS"
    RETAIL = "RETAIL"
    CONSUMER = "CONSUMER"


class TransportType(str, Enum):
    COLD_CHAIN = "COLD_CHAIN"
    NORMAL = "NORMAL"
    EXPRESS = "EXPRESS"


class BatchStatus(str, Enum):
    HARVESTED = "HARVESTED"
    PROCESSING = "PROCESSING"
    PACKAGED = "PACKAGED"
    ON_SALE = "ON_SALE"
    SOLD_OUT = "SOLD_OUT"


class ProductBatchCreate(BaseModel):
    product_name: str
    product_category: Optional[str] = None
    crop_record_id: Optional[str] = None
    plot_id: Optional[str] = None
    harvest_time: Optional[datetime] = None
    harvest_quantity: Optional[float] = None
    quantity_unit: Optional[str] = "KG"
    production_area: Optional[str] = None
    producer_id: Optional[str] = None
    production_license: Optional[str] = None
    quality_grade: Optional[str] = None
    organic_cert_no: Optional[str] = None


class ProductBatchResponse(BaseModel):
    id: str
    batch_code: str
    product_name: str
    product_category: Optional[str] = None
    harvest_time: Optional[datetime] = None
    harvest_quantity: Optional[float] = None
    quantity_unit: Optional[str] = None
    production_area: Optional[str] = None
    producer_name: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TraceNodeCreate(BaseModel):
    node_type: NodeType
    node_sequence: int
    node_name: str
    operator_id: Optional[str] = None
    operator_name: Optional[str] = None
    location_name: Optional[str] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    event_time: datetime
    event_type: Optional[str] = None
    event_data: Dict[str, Any]


class TraceNodeResponse(BaseModel):
    id: str
    batch_id: str
    node_type: str
    node_sequence: int
    node_name: str
    location_name: Optional[str] = None
    event_time: datetime
    event_data: Dict[str, Any]
    chain_hash: Optional[str] = None
    chain_tx_id: Optional[str] = None
    chain_timestamp: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LogisticsCreate(BaseModel):
    batch_id: str
    logistics_company: Optional[str] = None
    transport_type: TransportType = TransportType.NORMAL
    vehicle_no: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    origin_address: Optional[str] = None
    destination_address: Optional[str] = None
    departure_time: Optional[datetime] = None
    estimated_arrival_time: Optional[datetime] = None
    temperature_records: Optional[List[Dict[str, Any]]] = None


class LogisticsResponse(BaseModel):
    id: str
    batch_id: str
    logistics_no: str
    logistics_company: Optional[str] = None
    transport_type: str
    origin_address: Optional[str] = None
    destination_address: Optional[str] = None
    departure_time: Optional[datetime] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CarbonFootprintCreate(BaseModel):
    batch_id: str
    product_name: str
    product_unit: str = "KG"
    production_energy: Optional[float] = 0
    processing_energy: Optional[float] = 0
    logistics_distance_km: Optional[float] = 0
    logistics_weight_kg: Optional[float] = 0
    packaging_materials_kg: Optional[float] = 0


class CarbonFootprintResponse(BaseModel):
    id: str
    footprint_id: str
    batch_id: str
    product_name: Optional[str] = None
    product_unit: Optional[str] = None
    total_emissions_kg: float
    production_emissions_kg: Optional[float] = None
    processing_emissions_kg: Optional[float] = None
    logistics_emissions_kg: Optional[float] = None
    packaging_emissions_kg: Optional[float] = None
    data_quality_factor: Optional[float] = 1.0
    calculation_method: Optional[str] = None
    status: str
    chain_hash: Optional[str] = None
    chain_timestamp: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TraceQueryResponse(BaseModel):
    batch: ProductBatchResponse
    trace_nodes: List[TraceNodeResponse]
    carbon_footprint: Optional[CarbonFootprintResponse] = None
    logistics_info: Optional[LogisticsResponse] = None
    is_authentic: bool
    verification_message: str


class QRCodeResponse(BaseModel):
    batch_id: str
    qrcode_type: str
    qrcode_data: str
    qrcode_image: str
    generated_at: datetime
