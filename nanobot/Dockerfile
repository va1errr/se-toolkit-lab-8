# Nanobot Dockerfile - multi-stage build with uv
# Build context is the root directory

# ---
# Stage 1: Build the application in the /app directory
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Disable Python downloads, use system interpreter
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Create virtual environment
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Install nanobot-ai first
RUN uv pip install "nanobot-ai @ https://github.com/HKUDS/nanobot/archive/refs/heads/main.zip"

# Copy all required packages
COPY mcp/mcp-lms /app/mcp-lms
COPY mcp/mcp-obs /app/mcp-obs
COPY nanobot-websocket-channel/nanobot-channel-protocol /app/nanobot-channel-protocol
COPY nanobot-websocket-channel/nanobot-webchat /app/nanobot-webchat
COPY nanobot-websocket-channel/mcp-webchat /app/mcp-webchat
COPY nanobot /app/nanobot-src

# Remove workspace/path source references from pyproject.toml files
RUN sed -i '/\[tool\.uv\.sources\]/,/^\[/ { /^\[tool\.uv\.sources\]/! { /^\[/!d } }' \
    /app/mcp-lms/pyproject.toml \
    /app/nanobot-channel-protocol/pyproject.toml \
    /app/nanobot-webchat/pyproject.toml \
    /app/mcp-webchat/pyproject.toml \
    /app/nanobot-src/pyproject.toml

# Install all local packages without dependencies first
RUN uv pip install --no-deps -e /app/mcp-lms /app/mcp-obs /app/nanobot-channel-protocol /app/nanobot-webchat /app/mcp-webchat /app/nanobot-src

# Install common dependencies
RUN uv pip install aiohttp websockets mcp httpx pydantic

# Copy workspace to template location for initialization
COPY nanobot/workspace /app/workspace-template

# ---
# Stage 2: Final runtime image
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Accept APP_UID and APP_GID as build args for consistent user IDs
ARG APP_UID=1000
ARG APP_GID=1000

# Create non-root user with specified IDs
RUN groupadd --system --gid ${APP_GID} appgroup \
    && useradd --system --gid ${APP_GID} --uid ${APP_UID} --create-home appuser

# Copy the application from builder
COPY --from=builder --chown=appuser:appgroup /app /app

# Set PATH to include the venv
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER appuser

WORKDIR /app/nanobot-src

# Run the entrypoint which resolves config and starts nanobot gateway
CMD ["python", "/app/nanobot-src/entrypoint.py"]
