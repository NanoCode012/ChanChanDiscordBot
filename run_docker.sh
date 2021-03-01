#!/bin/bash

sudo docker stop chanchan_discordbot || true && sudo docker rm chanchan_discordbot || true

sudo docker build -t chanchan_discordbot .
sudo docker run -it --env-file .env chanchan_discordbot

echo 'Started'
