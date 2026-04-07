FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .

CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]
