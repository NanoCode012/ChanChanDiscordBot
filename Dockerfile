FROM python:3.9.2-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app

RUN pip install -qr requirements.txt

COPY . /usr/src/app

CMD ["python", "-u", "bot.py"]
