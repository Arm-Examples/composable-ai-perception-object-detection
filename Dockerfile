# syntax=docker/dockerfile:1@sha256:ecfaec9ed6d810b56388c508f4121597bfbba70d41a6dfeee4d8cad5f295fc32
ARG UV_IMAGE=ghcr.io/astral-sh/uv:trixie-slim@sha256:4298dc3494124b50792f7abbdfe2cae7139c41f4e098f52573f4f6d912cf8bd7

FROM ${UV_IMAGE} AS builder

ARG OPK_HF_DETECTION_MODEL=Arm/yolo26n-640-int8-onnx-raspberrypi5
ARG ARTIFACTORY_USERNAME
ENV UV_PYTHON_INSTALL_DIR=/opt/uv/python
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

COPY scripts/download-model.sh /usr/local/bin/download-model.sh
RUN --mount=type=secret,id=hf_token,required=true \
    HF_TOKEN="$(cat /run/secrets/hf_token)" \
    OPK_HF_DETECTION_MODEL="${OPK_HF_DETECTION_MODEL}" \
    sh /usr/local/bin/download-model.sh

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=secret,id=artifactory_token,required=true \
    set -eu; \
    previous_umask="$(umask)"; umask 077; \
    printf 'machine artifactory.arm.com login %s password %s\n' "$ARTIFACTORY_USERNAME" "$(cat /run/secrets/artifactory_token)" > /tmp/artifactory.netrc; \
    umask "$previous_umask"; \
    NETRC=/tmp/artifactory.netrc \
    UV_INDEX_EDGE_AI_TOOLING_USERNAME="$ARTIFACTORY_USERNAME" \
    UV_INDEX_EDGE_AI_TOOLING_PASSWORD="$(cat /run/secrets/artifactory_token)" \
    uv sync --locked --no-dev --no-install-project; \
    rm /tmp/artifactory.netrc

FROM ${UV_IMAGE} AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /opt/uv/python /opt/uv/python
COPY main.py ./main.py
COPY --from=builder /models/ /models/
RUN useradd --create-home --uid 10001 app

USER app

CMD ["uv", "run", "main.py"]
