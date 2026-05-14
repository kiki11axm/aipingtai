from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, date
from uuid import uuid4
from loguru import logger
import json

from src.models.farm_models import (
    PlotCreate, PlotResponse, PlotUpdate,
    CropRecordCreate, CropRecordResponse,
    SoilDataCreate, SoilDataResponse,
    OperationRecordCreate, OperationRecordResponse,
    FertilizerPrescriptionResponse, PrescriptionCreate,
    YieldEstimationResponse, FarmDashboardResponse, OperationStats
)
from src.services.data_collection_service import DataCollectionService
from src.core.database import Plot, CropRecord, SoilData, OperationRecord, FarmUser


class FarmService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_plot(self, plot_data: PlotCreate, user) -> PlotResponse:
        plot = Plot(
            id=str(uuid4()),
            plot_code=f"PLOT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            plot_name=plot_data.plot_name,
            plot_type=plot_data.plot_type,
            boundary_geojson=json.dumps(plot_data.boundary_geojson),
            area_sqm=plot_data.area_sqm,
            area_mu=plot_data.area_sqm / 666.7,
            organization_id=plot_data.organization_id,
            region_code=plot_data.region_code,
            status="ACTIVE"
        )
        self.db.add(plot)
        await self.db.commit()
        await self.db.refresh(plot)
        return PlotResponse(**plot.__dict__)

    async def list_plots(
        self, organization_id: Optional[str], region_code: Optional[str],
        page: int, page_size: int
    ) -> List[PlotResponse]:
        query = select(Plot).where(Plot.status == "ACTIVE")
        if organization_id:
            query = query.where(Plot.organization_id == organization_id)
        if region_code:
            query = query.where(Plot.region_code == region_code)
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        plots = result.scalars().all()
        return [PlotResponse(**p.__dict__) for p in plots]

    async def get_plot(self, plot_id: str) -> PlotResponse:
        query = select(Plot).where(Plot.id == plot_id)
        result = await self.db.execute(query)
        plot = result.scalar_one_or_none()
        if not plot:
            raise ValueError(f"地块 {plot_id} 不存在")
        return PlotResponse(**plot.__dict__)

    async def update_plot(self, plot_id: str, plot_data: PlotUpdate) -> PlotResponse:
        query = select(Plot).where(Plot.id == plot_id)
        result = await self.db.execute(query)
        plot = result.scalar_one_or_none()
        if not plot:
            raise ValueError(f"地块 {plot_id} 不存在")
        update_data = plot_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "boundary_geojson":
                setattr(plot, key, json.dumps(value))
            else:
                setattr(plot, key, value)
        plot.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(plot)
        return PlotResponse(**plot.__dict__)

    async def delete_plot(self, plot_id: str):
        query = select(Plot).where(Plot.id == plot_id)
        result = await self.db.execute(query)
        plot = result.scalar_one_or_none()
        if not plot:
            raise ValueError(f"地块 {plot_id} 不存在")
        plot.status = "DELETED"
        await self.db.commit()

    async def create_crop_record(
        self, plot_id: str, record_data: CropRecordCreate
    ) -> CropRecordResponse:
        crop_record = CropRecord(
            id=str(uuid4()),
            plot_id=plot_id,
            crop_type=record_data.crop_type,
            crop_name=record_data.crop_name,
            crop_variety=record_data.crop_variety,
            planting_date=record_data.planting_date,
            expected_harvest_date=record_data.expected_harvest_date,
            planting_area_mu=record_data.planting_area_mu,
            growth_stage="SEEDLING",
            status="GROWING"
        )
        self.db.add(crop_record)
        await self.db.commit()
        await self.db.refresh(crop_record)
        return CropRecordResponse(**crop_record.__dict__)

    async def list_crop_records(
        self, plot_id: str, status: Optional[str] = None
    ) -> List[CropRecordResponse]:
        query = select(CropRecord).where(CropRecord.plot_id == plot_id)
        if status:
            query = query.where(CropRecord.status == status)
        query = query.order_by(CropRecord.created_at.desc())
        result = await self.db.execute(query)
        records = result.scalars().all()
        return [CropRecordResponse(**r.__dict__) for r in records]

    async def create_soil_data(self, data: SoilDataCreate) -> SoilDataResponse:
        soil_data = SoilData(
            id=str(uuid4()),
            plot_id=data.plot_id,
            sample_point_lat=data.sample_point_lat,
            sample_point_lon=data.sample_point_lon,
            sample_depth_cm=data.sample_depth_cm,
            sample_time=data.sample_time,
            ph_value=data.ph_value,
            organic_matter_pct=data.organic_matter_pct,
            nitrogen_mg_kg=data.nitrogen_mg_kg,
            phosphorus_mg_kg=data.phosphorus_mg_kg,
            potassium_mg_kg=data.potassium_mg_kg,
            moisture_pct=data.moisture_pct,
            data_source=data.data_source or "MANUAL",
            data_quality="VALID"
        )
        self.db.add(soil_data)
        await self.db.commit()
        await self.db.refresh(soil_data)
        return SoilDataResponse(**soil_data.__dict__)

    async def get_soil_data(
        self, plot_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[SoilDataResponse]:
        query = select(SoilData).where(SoilData.plot_id == plot_id)
        if start_time:
            query = query.where(SoilData.sample_time >= start_time)
        if end_time:
            query = query.where(SoilData.sample_time <= end_time)
        query = query.order_by(SoilData.sample_time.desc())
        result = await self.db.execute(query)
        records = result.scalars().all()
        return [SoilDataResponse(**r.__dict__) for r in records]

    async def create_operation(
        self, data: OperationRecordCreate, user
    ) -> OperationRecordResponse:
        operation = OperationRecord(
            id=str(uuid4()),
            plot_id=data.plot_id,
            crop_record_id=data.crop_record_id,
            operation_type=data.operation_type,
            operation_name=data.operation_name,
            operation_time=data.operation_time,
            operator_id=user.user_id,
            operator_name=user.username,
            equipment_id=data.equipment_id,
            equipment_name=data.equipment_name,
            operation_area_mu=data.operation_area_mu,
            input_amount=data.input_amount,
            input_unit=data.input_unit,
            input_type=data.input_type,
            input_name=data.input_name,
            gis_trace=json.dumps(data.gis_trace) if data.gis_trace else None
        )
        self.db.add(operation)
        await self.db.commit()
        await self.db.refresh(operation)
        return OperationRecordResponse(**operation.__dict__)

    async def get_operation_stats(
        self, plot_id: Optional[str],
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> OperationStats:
        query = select(
            OperationRecord.operation_type,
            func.count(OperationRecord.id).label("count"),
            func.sum(OperationRecord.operation_area_mu).label("total_area")
        ).group_by(OperationRecord.operation_type)
        if plot_id:
            query = query.where(OperationRecord.plot_id == plot_id)
        if start_date:
            query = query.where(OperationRecord.operation_time >= start_date)
        if end_date:
            query = query.where(OperationRecord.operation_time <= end_date)
        result = await self.db.execute(query)
        rows = result.all()
        stats = {
            "total_operations": sum(r.count for r in rows),
            "operation_breakdown": [
                {"type": r.operation_type, "count": r.count, "area": float(r.total_area or 0)}
                for r in rows
            ]
        }
        return OperationStats(**stats)

    async def generate_prescription(
        self, data: PrescriptionCreate, ai_service, user
    ) -> FertilizerPrescriptionResponse:
        soil_query = select(SoilData).where(
            SoilData.plot_id == data.plot_id
        ).order_by(SoilData.sample_time.desc()).limit(1)
        soil_result = await self.db.execute(soil_query)
        soil = soil_result.scalar_one_or_none()

        soil_n = float(soil.nitrogen_mg_kg) if soil else 0
        soil_p = float(soil.phosphorus_mg_kg) if soil else 0
        soil_k = float(soil.potassium_mg_kg) if soil else 0

        ai_result = await ai_service.generate_fertilizer_prescription(
            plot_id=data.plot_id,
            target_yield=data.target_yield_kg,
            soil_n=soil_n,
            soil_p=soil_p,
            soil_k=soil_k
        )

        prescription = {
            "id": str(uuid4()),
            "plot_id": data.plot_id,
            "crop_record_id": data.crop_record_id,
            "prescription_no": f"RX-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "target_yield_kg": data.target_yield_kg,
            "soil_available_n": soil_n,
            "soil_available_p": soil_p,
            "soil_available_k": soil_k,
            "organic_fertilizer_n": ai_result.get("organic_n", 0),
            "organic_fertilizer_p": ai_result.get("organic_p", 0),
            "organic_fertilizer_k": ai_result.get("organic_k", 0),
            "fertilizer_formula": ai_result.get("formula", {}),
            "total_fertilizer_kg": ai_result.get("total_kg", 0),
            "base_fertilizer_kg": ai_result.get("base_kg", 0),
            "top_dressing_kg": ai_result.get("top_kg", 0),
            "recommended_date": date.today(),
            "ai_model_version": "v1.0",
            "ai_confidence": ai_result.get("confidence", 0.85)
        }
        return FertilizerPrescriptionResponse(**prescription)

    async def get_yield_estimation(self, plot_id: str, ai_service) -> YieldEstimationResponse:
        ai_result = await ai_service.estimate_yield(plot_id)
        estimation = {
            "id": str(uuid4()),
            "plot_id": plot_id,
            "estimation_no": f"YE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "estimation_time": datetime.now(),
            "estimated_yield_kg": ai_result.get("yield_kg", 0),
            "confidence_level": ai_result.get("confidence", 0.85),
            "growth_stage": ai_result.get("growth_stage", "MATURATION"),
            "ndvi_value": ai_result.get("ndvi", 0),
            "ai_model_version": "v1.0"
        }
        return YieldEstimationResponse(**estimation)

    async def get_dashboard(self, organization_id: Optional[str]) -> FarmDashboardResponse:
        plot_query = select(func.count(Plot.id)).where(Plot.status == "ACTIVE")
        if organization_id:
            plot_query = plot_query.where(Plot.organization_id == organization_id)
        plot_result = await self.db.execute(plot_query)
        total_plots = plot_result.scalar() or 0

        crop_query = select(func.count(CropRecord.id)).where(CropRecord.status == "GROWING")
        crop_result = await self.db.execute(crop_query)
        growing_plots = crop_result.scalar() or 0

        return FarmDashboardResponse(
            total_plots=total_plots,
            growing_plots=growing_plots,
            total_area_mu=0,
            today_operations=0,
            alert_count=0
        )
