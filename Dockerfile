FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl unzip git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
# RUN --mount=type=cache,target=/root/.cache/uv \
# uv sync --frozen
# ENV PATH="/app/.venv/bin:$PATH"

RUN pip install -r requirements.txt

ENTRYPOINT ["reflex", "run", "--env", "prod", "--backend-only"]