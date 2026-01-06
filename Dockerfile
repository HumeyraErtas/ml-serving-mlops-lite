FROM python:3.11-slim

WORKDIR /app

# scikit-learn için runtime kütüphaneleri (wheels genelde yeterli; libgomp güvenli)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts
COPY pyproject.toml .
COPY README.md .

# Model artifacts runtime’da volume ile gelebilir; local demo için script ile üretilebilir
COPY models ./models

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
