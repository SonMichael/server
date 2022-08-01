FROM python:3.8-slim

COPY . /app
WORKDIR /app/

RUN apt update
RUN apt -y install build-essential libwrap0-dev libssl-dev libc-ares-dev uuid-dev xsltproc
RUN apt-get update -qq \
    && apt-get install --no-install-recommends --yes \
        build-essential \
        gcc \
        python3-dev \
        mosquitto \
        mosquitto-clients
RUN apt-get install ffmpeg libsm6 libxext6  -y


RUN pip3 install --upgrade pip setuptools wheel