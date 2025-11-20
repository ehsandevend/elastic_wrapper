FROM python:3.13-slim-trixie AS app

ARG ENVIRONMENT

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements/ requirements/

RUN pip install --no-cache-dir -r requirements/${ENVIRONMENT}.txt

COPY . .

RUN chmod +x /app/entrypoint.py

CMD ["python", "/app/entrypoint.py"]
