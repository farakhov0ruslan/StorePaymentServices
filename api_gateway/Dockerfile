FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/api_gateway


EXPOSE 80
CMD ["uvicorn", "api_gateway.main:app", "--host", "0.0.0.0", "--port", "80"]
