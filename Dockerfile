FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /fastapi-template
COPY . .

RUN uv sync --locked

ENTRYPOINT ["uv", "run", "uvicorn", "src:app", "--reload", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000