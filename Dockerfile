FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl unzip git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy only the files needed for dependency installation first
COPY requirements.txt ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copy the rest of the application
COPY backend ./backend
COPY songs.json ./

# Place the virtual environment in the PATH
ENV PYTHONPATH=/app

# Run FastAPI with uvicorn
ENTRYPOINT ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]