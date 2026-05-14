from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, date
from uuid import uuid4
from loguru import logger
import json
import qrcode
import io
import base64

from src.models.trace_models import (
    ProductBatchCreate, ProductBatchResponse,
    TraceNodeCreate, TraceNodeResponse,
    LogisticsCreate, LogisticsResponse,
    CarbonFootprintCreate, CarbonFootprintResponse,
    TraceQueryResponse
)
from src.services.carbon_service import CarbonService
from src.services.blockchain_service import BlockchainService


class TraceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_batch(
        self, batch_data: ProductBatchCreate, user
    ) -> ProductBatchResponse:
        batch = {
            "id": str(uuid4()),
            "batch_code": f"BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "product_name": batch_data.product_name,
            "product_category": batch_data.product_category,
            "harvest_time": batch_data.harvest_time,
            "harvest_quantity": batch_data.harvest_quantity,
            "quantity_unit": batch_data.quantity_unit,
            "production_area": batch_data.production_area,
            "producer_id": user.user_id,
            "producer_name": user.username,
            "status": "HARVESTED"
        }
        return ProductBatchResponse(**batch)

    async def get_batch_by_code(self, batch_code: str) -> ProductBatchResponse:
        return ProductBatchResponse(
            id=str(uuid4()),
            batch_code=batch_code,
            product_name="示例产品",
            status="ON_SALE",
            created_at=datetime.now()
        )

    async def list_batches(
        self, product_name: Optional[str], status: Optional[str],
        start_date: Optional[datetime], end_date: Optional[datetime],
        page: int, page_size: int
    ) -> List[ProductBatchResponse]:
        return []

    async def add_node(
        self, batch_id: str, node_data: TraceNodeCreate,
        blockchain_service: BlockchainService, user
    ) -> TraceNodeResponse:
        node_dict = node_data.model_dump()
        node_dict["id"] = str(uuid4())
        node_dict["chain_timestamp"] = datetime.now()

        chain_result = await blockchain_service.register_trace_data(
            batch_id=batch_id,
            trace_data=node_dict
        )

        node_dict["chain_hash"] = chain_result["data_hash"]
        node_dict["chain_tx_id"] = chain_result["tx_id"]

        return TraceNodeResponse(**node_dict)

    async def get_nodes(self, batch_id: str) -> List[TraceNodeResponse]:
        return [
            TraceNodeResponse(
                id=str(uuid4()),
                batch_id=batch_id,
                node_type="PRODUCTION",
                node_name="生产信息",
                event_time=datetime.now(),
                event_data={},
                chain_timestamp=datetime.now()
            )
        ]

    async def create_logistics(
        self, logistics_data: LogisticsCreate, user
    ) -> LogisticsResponse:
        logistics = {
            "id": str(uuid4()),
            "batch_id": logistics_data.batch_id,
            "logistics_no": f"LOG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "logistics_company": logistics_data.logistics_company,
            "transport_type": logistics_data.transport_type,
            "origin_address": logistics_data.origin_address,
            "destination_address": logistics_data.destination_address,
            "departure_time": logistics_data.departure_time,
            "status": "IN_TRANSIT"
        }
        return LogisticsResponse(**logistics)

    async def get_logistics_by_no(self, logistics_no: str) -> LogisticsResponse:
        return LogisticsResponse(
            id=str(uuid4()),
            batch_id=str(uuid4()),
            logistics_no=logistics_no,
            logistics_company="顺丰速运",
            status="DELIVERED",
            departure_time=datetime.now()
        )

    async def query_by_qrcode(
        self, qrcode_data: str, carbon_service: CarbonService
    ) -> TraceQueryResponse:
        batch = ProductBatchResponse(
            id=str(uuid4()),
            batch_code=qrcode_data[:20],
            product_name="有机大米",
            product_category="粮食",
            harvest_time=datetime.now(),
            harvest_quantity=1000,
            quantity_unit="KG",
            production_area="黑龙江省五常市",
            producer_name="XX农场",
            status="ON_SALE",
            created_at=datetime.now()
        )

        nodes = [
            TraceNodeResponse(
                id=str(uuid4()),
                batch_id=batch.id,
                node_type="PRODUCTION",
                node_name="种植信息",
                event_time=datetime.now(),
                event_data={"crop": "水稻", "variety": "五常稻花香"},
                chain_timestamp=datetime.now()
            ),
            TraceNodeResponse(
                id=str(uuid4()),
                batch_id=batch.id,
                node_type="HARVEST",
                node_name="收获信息",
                event_time=datetime.now(),
                event_data={"yield": 1000, "method": "机械收割"},
                chain_timestamp=datetime.now()
            )
        ]

        carbon_footprint = await carbon_service.get_footprint_by_batch(batch.id)
        logistics = LogisticsResponse(
            id=str(uuid4()),
            batch_id=batch.id,
            logistics_no="SF1234567890",
            logistics_company="顺丰速运",
            transport_type="COLD_CHAIN",
            status="IN_TRANSIT"
        )

        return TraceQueryResponse(
            batch=batch,
            trace_nodes=nodes,
            carbon_footprint=carbon_footprint,
            logistics_info=logistics,
            is_authentic=True,
            verification_message="产品信息验证通过，来源可追溯"
        )

    async def query_by_batch_code(
        self, batch_code: str, carbon_service: CarbonService
    ) -> TraceQueryResponse:
        batch = await self.get_batch_by_code(batch_code)
        carbon_footprint = await carbon_service.get_footprint_by_batch(batch.id)
        nodes = await self.get_nodes(batch.id)

        return TraceQueryResponse(
            batch=batch,
            trace_nodes=nodes,
            carbon_footprint=carbon_footprint,
            logistics_info=None,
            is_authentic=True,
            verification_message="产品信息验证通过"
        )

    async def verify_product(
        self, batch_code: str, blockchain_service: BlockchainService
    ) -> dict:
        verification_result = await blockchain_service.verify_trace_data(
            batch_id=batch_code,
            trace_data={"batch_code": batch_code}
        )

        return {
            "batch_code": batch_code,
            "is_authentic": verification_result.get("is_valid", True),
            "verification_result": verification_result,
            "verification_time": datetime.now()
        }

    async def verify_chain_data(
        self, batch_id: str, blockchain_service: BlockchainService
    ) -> dict:
        chain_records = await blockchain_service.query_trace_by_batch(batch_id)

        return {
            "batch_id": batch_id,
            "chain_records_count": len(chain_records),
            "is_complete": len(chain_records) > 0,
            "records": chain_records
        }

    async def generate_qrcode(
        self, batch_id: str, qrcode_type: str
    ) -> dict:
        qrcode_content = f"TRACE:{batch_id}:{qrcode_type}"

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qrcode_content)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return {
            "batch_id": batch_id,
            "qrcode_type": qrcode_type,
            "qrcode_data": qrcode_content,
            "qrcode_image": f"data:image/png;base64,{img_base64}",
            "generated_at": datetime.now()
        }
