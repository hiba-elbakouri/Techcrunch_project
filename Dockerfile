FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app


USER root

RUN mkdir -p ./db

RUN chmod 700 ./db

VOLUME ./output ./db



EXPOSE 5000


CMD ["python", "app.py"]