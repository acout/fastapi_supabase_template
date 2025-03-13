# Mis à jour pour refléter la nouvelle structure
FROM python:3.12-slim-bookworm

# Print logs immediately
ENV PYTHONUNBUFFERED=1

# Arguments for user creation
ARG USERNAME=""
ARG USER_UID=1000
ARG USER_GID=1000
ARG BUILD_ENV="prod"

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
        sudo \
        git \
        curl \
        ca-certificates \
        wget \
        procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create user for development if needed
RUN if [ -n "$USERNAME" ] && [ "$BUILD_ENV" = "dev" ]; then \
    groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME; \
    fi

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.6.4 /uv /uvx /bin/

# Configure UV for system-wide installation in container
ENV UV_SYSTEM_PYTHON=/usr/local/bin/python
ENV UV_CACHE_DIR=/app/backend/.cache/uv
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

# Create cache directory
RUN mkdir -p $UV_CACHE_DIR && \
    chmod -R 777 $UV_CACHE_DIR

# Copy backend files for dependency installation
COPY ./backend /app/backend

# Install dependencies
WORKDIR /app/backend
RUN --mount=type=cache,target=$UV_CACHE_DIR \
    set -x && \
    # Install dependencies
    uv sync --frozen && \
    # Install project in editable mode
    uv pip install --system -e .

# Switch to non-root user if specified
USER ${USERNAME:-root}
WORKDIR /app/backend

# Update the command to point to the correct module path
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
