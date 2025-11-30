FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl unzip git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Place the virtual environment in the PATH
ENV PYTHONPATH=/app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy only the files needed for dependency installation first
COPY pyproject.toml uv.lock ./

# Install dependencies (including git dependencies)
# --frozen: ensure lockfile is respected
# --no-install-project: install dependencies only, not the project itself yet
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Copy the rest of the application
COPY backend ./backend
COPY songs.json ./

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Place the virtual environment in the PATH
ENV PATH="/app/.venv/bin:$PATH"


# Run FastAPI with uvicorn
ENTRYPOINT ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]