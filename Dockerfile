FROM python:3.7.5-slim

WORKDIR /usr/src/app

COPY . /usr/src/app

RUN pip install -qr requirements.txt

RUN source .env

CMD ["python", "bot.py"]
