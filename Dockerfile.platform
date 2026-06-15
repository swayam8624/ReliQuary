FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    cargo \
    pkg-config \
    rustc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY apps ./apps
COPY auth ./auth
COPY config ./config
COPY config_package ./config_package
COPY core ./core
COPY agents ./agents
COPY observability ./observability
COPY vaults ./vaults
COPY zk ./zk
COPY rust_modules ./rust_modules
COPY scripts/build_rust_modules.sh ./scripts/build_rust_modules.sh
COPY main.py ./main.py

RUN PYTHON=python ./scripts/build_rust_modules.sh

RUN mkdir -p /app/logs /app/data /tmp/vaults

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
