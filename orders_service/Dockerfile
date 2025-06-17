FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY infrastructure/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/orders_service
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh



EXPOSE 80

ENTRYPOINT ["wait-for-it.sh", "-t", "60", "rabbitmq:5672", "--strict", "--"]

CMD ["uvicorn", "orders_service.main:app", "--host", "0.0.0.0", "--port", "80"]
