ARG DOCKER_REPO_URL
FROM ${DOCKER_REPO_URL}/python:3.12-slim AS app

ARG ENVIRONMENT

USER root

RUN groupadd -r appuser && useradd -r -g appuser appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/usr/bin/tini", "--"]

WORKDIR /app

COPY requirements/ requirements/

RUN pip install --no-cache-dir -r requirements/${ENVIRONMENT}.txt

COPY . .

RUN chmod +x /app/entrypoint.py && \
    chown -R appuser:appuser /app

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "print('healthy')" || exit 1

USER appuser

CMD ["python", "/app/entrypoint.py"]
