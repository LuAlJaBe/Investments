FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /bi

COPY ./requirements.txt /bi/requirements.txt

RUN apt update && \
    apt upgrade -y && \
    apt install -y \
    python3-dev \
    nodejs \
    npm \
    default-libmysqlclient-dev \
    libssl-dev \
    build-essential

RUN python -m pip install -r requirements.txt

COPY ./bi /bi/
