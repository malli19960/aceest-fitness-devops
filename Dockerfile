FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS test

COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY app.py ./
COPY tests/ ./tests/
COPY Versions/ ./Versions/
RUN python -m compileall -q app.py tests Versions
CMD ["python", "-m", "pytest", "-q"]

FROM base AS runtime

RUN useradd --create-home --uid 10001 appuser && \
    mkdir -p /app/instance && \
    chown appuser:appuser /app/instance
COPY --chown=appuser:appuser app.py ./
USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
