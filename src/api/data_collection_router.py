from fastapi import APIRouter, Depends, Query, Body
from typing import Optional, List, Any, Dict
from datetime import datetime
from loguru import logger
import json

from src.core.security import get_current_user, TokenData
from src.services.data_collection_service import DataCollectionService


router = APIRouter()


@router.post("/sensor/data")
async def upload_sensor_data(
    sensor_type: str = Query(..., description="传感器类型: soil, weather, irrigation"),
    sensor_id: str = Query(..., description="传感器ID"),
    timestamp: datetime = Query(..., description="数据采集时间"),
    data: str = Body(..., description="传感器数据 JSON 字符串"),
):
    collection_service = DataCollectionService(None)
    data_dict = json.loads(data) if isinstance(data, str) else data
    result = await collection_service.process_sensor_data(
        sensor_type=sensor_type,
        sensor_id=sensor_id,
        data=data_dict,
        timestamp=timestamp
    )
    return result


@router.post("/gps/vehicle")
async def upload_vehicle_gps(
    vehicle_id: str = Query(...),
    latitude: float = Query(...),
    longitude: float = Query(...),
    speed: float = Query(...),
    heading: float = Query(...),
    timestamp: datetime = Query(...),
):
    collection_service = DataCollectionService(None)
    result = await collection_service.process_vehicle_gps(
        vehicle_id=vehicle_id,
        latitude=latitude,
        longitude=longitude,
        speed=speed,
        heading=heading,
        timestamp=timestamp
    )
    return result


@router.get("/device/{device_id}/status")
async def get_device_status(
    device_id: str,
):
    collection_service = DataCollectionService(None)
    return await collection_service.get_device_status(device_id)


@router.post("/batch/import")
async def batch_import_data(
    data_type: str = Query(..., description="数据类型: sensor, gps, satellite"),
    records: str = Body(..., description="批量数据记录 JSON 字符串"),
):
    collection_service = DataCollectionService(None)
    records_list = json.loads(records) if isinstance(records, str) else records
    result = await collection_service.batch_import_data(
        data_type=data_type,
        records=records_list,
        user_id="system"
    )
    return result


@router.get("/sources")
async def get_data_sources():
    return {
        "satellite": [
            {"name": "Sentinel-2", "provider": "ESA", "resolution": "10m", "frequency": "5-10天"},
            {"name": "高分系列", "provider": "中国资源卫星中心", "resolution": "2m", "frequency": "3-5天"}
        ],
        "weather": [
            {"name": "国家气象站", "provider": "中国气象局", "frequency": "15分钟"},
            {"name": "商业气象API", "provider": "第三方", "frequency": "1小时"}
        ],
        "iot": [
            {"name": "土壤传感器", "protocol": "LoRa/NB-IoT", "frequency": "1小时"},
            {"name": "气象站", "protocol": "LoRa/NB-IoT", "frequency": "15分钟"},
            {"name": "灌区控制器", "protocol": "MQTT", "frequency": "实时"}
        ]
    }


@router.get("/satellite/tiles")
async def get_satellite_tiles(
    plot_id: str = Query(...),
    date: Optional[datetime] = Query(None),
):
    return {
        "plot_id": plot_id,
        "tiles": [
            {
                "tile_id": "tile_001",
                "date": "2026-04-20",
                "cloud_coverage_pct": 15.5,
                "url": "/api/v1/collection/satellite/tiles/tile_001"
            },
            {
                "tile_id": "tile_002",
                "date": "2026-04-15",
                "cloud_coverage_pct": 8.2,
                "url": "/api/v1/collection/satellite/tiles/tile_002"
            }
        ]
    }


@router.get("/statistics")
async def get_collection_statistics():
    return {
        "total_records_today": 15420,
        "sensor_records": 12000,
        "gps_records": 3000,
        "satellite_records": 120,
        "drone_records": 300,
        "data_quality_pass_rate": 98.5,
        "devices_online_rate": 95.2
    }
