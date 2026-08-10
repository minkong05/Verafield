FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
COPY backend ./backend
COPY packages ./packages

RUN pip install --no-cache-dir .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
