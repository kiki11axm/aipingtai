from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, DateTime, func, Text, Numeric, Boolean, Integer, JSON
from typing import AsyncGenerator
import uuid


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Plot(BaseModel):
    __tablename__ = "farm_plots"

    plot_code = Column(String(50), unique=True, nullable=False)
    plot_name = Column(String(200), nullable=False)
    plot_type = Column(String(20))
    boundary_geojson = Column(JSON, nullable=False)
    area_sqm = Column(Numeric(12, 2), nullable=False)
    area_mu = Column(Numeric(10, 2))
    perimeter_m = Column(Numeric(10, 2))
    elevation_m = Column(Numeric(8, 2))
    soil_type = Column(String(50))
    irrigation_type = Column(String(50))
    organization_id = Column(String(36))
    region_code = Column(String(20))
    status = Column(String(20), default="ACTIVE")


class CropRecord(BaseModel):
    __tablename__ = "farm_crop_records"

    plot_id = Column(String(36), nullable=False)
    crop_type = Column(String(50), nullable=False)
    crop_name = Column(String(100), nullable=False)
    crop_variety = Column(String(100))
    planting_date = Column(DateTime)
    expected_harvest_date = Column(DateTime)
    actual_harvest_date = Column(DateTime)
    planting_area_mu = Column(Numeric(10, 2))
    expected_yield_kg = Column(Numeric(10, 2))
    actual_yield_kg = Column(Numeric(10, 2))
    yield_unit = Column(String(20), default="KG/MU")
    growth_stage = Column(String(50))
    seed_brand = Column(String(100))
    seed_batch = Column(String(50))
    fertilizer_plan = Column(JSON)
    pesticide_plan = Column(JSON)
    status = Column(String(20), default="GROWING")


class SoilData(BaseModel):
    __tablename__ = "farm_soil_data"

    plot_id = Column(String(36), nullable=False)
    sample_point_lat = Column(Numeric(10, 7))
    sample_point_lon = Column(Numeric(10, 7))
    sample_depth_cm = Column(Integer)
    sample_time = Column(DateTime, nullable=False)
    ph_value = Column(Numeric(4, 2))
    organic_matter_pct = Column(Numeric(6, 3))
    nitrogen_mg_kg = Column(Numeric(8, 2))
    phosphorus_mg_kg = Column(Numeric(8, 2))
    potassium_mg_kg = Column(Numeric(8, 2))
    moisture_pct = Column(Numeric(5, 2))
    data_source = Column(String(20), default="MANUAL")
    data_quality = Column(String(20), default="VALID")
    raw_data = Column(JSON)


class OperationRecord(BaseModel):
    __tablename__ = "farm_operation_records"

    plot_id = Column(String(36), nullable=False)
    crop_record_id = Column(String(36))
    operation_type = Column(String(50), nullable=False)
    operation_name = Column(String(200))
    operation_time = Column(DateTime, nullable=False)
    operator_id = Column(String(36))
    operator_name = Column(String(100))
    equipment_id = Column(String(50))
    equipment_name = Column(String(100))
    operation_area_mu = Column(Numeric(10, 2))
    input_amount = Column(Numeric(10, 2))
    input_unit = Column(String(20))
    input_type = Column(String(50))
    input_name = Column(String(100))
    weather_conditions = Column(JSON)
    notes = Column(Text)
    gis_trace = Column(JSON)
    operation_quality = Column(String(20))


class FarmUser(BaseModel):
    __tablename__ = "farm_users"

    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    user_type = Column(String(20), nullable=False)
    organization_id = Column(String(36))
    status = Column(String(20), default="ACTIVE")
    last_login_time = Column(DateTime)
    last_login_ip = Column(String(50))


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/agri_carbon"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
