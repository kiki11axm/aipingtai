from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import uuid
from loguru import logger

from src.core.config import settings
from src.core.database import engine, Base, get_db
from src.api import farm_router, trace_router, carbon_router, data_collection_router, ai_router, auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("启动现代农业与绿色低碳AI平台...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库初始化完成")
    yield
    logger.info("关闭平台...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="现代农业与绿色低碳AI平台 - 精准农事管理、农产品溯源、碳排放核算",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    if process_time > 500:
        logger.warning(f"请求处理时间超过500ms: {request.url.path} - {process_time:.2f}ms")
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


app.include_router(auth_router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(farm_router, prefix="/api/v1/farm", tags=["精准农事"])
app.include_router(trace_router, prefix="/api/v1/trace", tags=["溯源系统"])
app.include_router(carbon_router, prefix="/api/v1/carbon", tags=["双碳管理"])
app.include_router(data_collection_router, prefix="/api/v1/collection", tags=["数据采集"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["AI服务"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
