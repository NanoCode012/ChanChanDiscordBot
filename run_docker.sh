#!/bin/bash

echo 'Removing any old containers if exist ..'

sudo docker stop chanchan_discordbot || true && sudo docker rm chanchan_discordbot || true

sudo docker build -t chanchan_discordbot .
sudo docker run -d --env-file .env chanchan_discordbot

echo 'Container has been built and is running ..'
