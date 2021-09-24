FROM docker.io/python:3.6.4-slim

WORKDIR /app
COPY requirements.txt .
COPY main.py .
RUN pip install -r requirements.txt

CMD ["python", "-u", "/app/main.py"]