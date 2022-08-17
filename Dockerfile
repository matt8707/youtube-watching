FROM python:3.10-slim

COPY requirements.txt .
RUN pip install -r requirements.txt && mkdir /config

COPY ./app ./app

CMD ["python", "./app/main.py"]
