FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir fastapi uvicorn pydantic python-dotenv

COPY . .

# Generate data and train model at build time
RUN python src/data/generate_synthetic.py --customers 10000 && \
    python src/models/churn_model.py --train

EXPOSE 8000

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
