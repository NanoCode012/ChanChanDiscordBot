FROM python:3.9.2-slim-buster

WORKDIR /usr/src/app

COPY . /usr/src/app

RUN pip install -qr requirements.txt

CMD ["python", "bot.py"]
