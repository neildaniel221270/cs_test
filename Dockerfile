FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive         PYTHONDONTWRITEBYTECODE=1         PYTHONUNBUFFERED=1         PIP_NO_CACHE_DIR=1         HF_HUB_OFFLINE=1         TRANSFORMERS_OFFLINE=1         XDG_CACHE_HOME=/app/.cache

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends         ffmpeg         curl         build-essential         cmake         libopenblas-dev         dos2unix         && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip &&         CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"         pip install -r /app/requirements.txt

COPY scripts/ /app/scripts/
COPY docker/ /app/docker/

RUN chmod +x /app/docker/*.sh &&         dos2unix /app/docker/*.sh

RUN mkdir -p /app/models /workspace/input /workspace/Data

ENTRYPOINT ["/app/docker/entrypoint.sh"]
