# syntax=docker/dockerfile:1@sha256:ecfaec9ed6d810b56388c508f4121597bfbba70d41a6dfeee4d8cad5f295fc32
ARG UV_IMAGE=ghcr.io/astral-sh/uv:trixie-slim@sha256:95611d89b7324e0517fe7257bb00979cf1f68461e5fb2b2d027d039da054bc07

FROM ${UV_IMAGE} AS builder

ARG OPK_HF_DETECTION_MODEL=Arm/yolo26n-320-int8-onnx-raspberrypi5
ENV UV_PYTHON_INSTALL_DIR=/opt/uv/python
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

COPY scripts/download-model.sh /usr/local/bin/download-model.sh
RUN OPK_HF_DETECTION_MODEL="${OPK_HF_DETECTION_MODEL}" \
    sh /usr/local/bin/download-model.sh

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

FROM ${UV_IMAGE} AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /opt/uv/python /opt/uv/python
COPY main.py ./main.py
COPY --from=builder /models/ /models/
RUN useradd --create-home --uid 10001 app

USER app

CMD ["uv", "run", "main.py"]
