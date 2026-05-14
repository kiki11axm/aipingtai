# 使用官方 Python 3.11 基础镜像，这是你项目的稳定运行环境
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（geopandas 等需要）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目所有代码
COPY . .

#  Railway 会通过 $PORT 环境变量自动分配端口
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]