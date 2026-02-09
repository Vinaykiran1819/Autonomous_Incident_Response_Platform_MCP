FROM python:3.9-slim

WORKDIR /app

RUN pip install fastapi uvicorn requests

COPY main.py .

RUN mkdir -p /app/shared-logs

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]