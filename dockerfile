FROM python:3.9-slim-buster AS builder
WORKDIR /app
COPY requirements.txt /app/
RUN pip uninstall -y blinker
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python3", "auth and fitur.py"]