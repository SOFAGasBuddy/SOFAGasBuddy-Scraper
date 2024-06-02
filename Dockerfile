FROM python:3.12.3-alpine3.19

RUN apk upgrade
RUN apk add vim bash

WORKDIR /app

COPY requirements.txt .
COPY main.py .
COPY helper_stuff.py .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
