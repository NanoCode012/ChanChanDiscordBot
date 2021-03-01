#!/bin/bash
# Run via : sudo bash run_docker.sh

echo 'Removing any old containers if exist ..'

sudo docker stop chanchan_discordbot || true && sudo docker rm chanchan_discordbot || true

sudo docker build -t chanchan_discordbot .
sudo docker run -d --rm --env-file .env --name chanchan_discordbot chanchan_discordbot

echo 'Container has been built and is running ..'
