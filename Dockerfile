FROM python:3.7.5-slim

WORKDIR /usr/src/app

COPY . /usr/src/app

RUN pip install -qr requirements.txt

CMD ["python", "bot.py"]
