FROM python:3.7.5-slim

WORKDIR /usr/src/app

COPY . /usr/src/app
CMD ["python", "bot.py"]
