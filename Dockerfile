FROM python:3.8-slim-bullseye

ENV PATH="/scripts:${PATH}"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN apt update && \
    apt upgrade -y && \
    apt install -y \
    # If you do not install these development tools some packages en Pipfile could not be installed.
    python3-dev \
    default-libmysqlclient-dev \
    libssl-dev \
    build-essential \
    nodejs \
    npm

RUN apt install -y nginx

RUN python -m pip install -r requirements.txt

COPY ./bi /bi/

WORKDIR /bi

COPY ./scripts /scripts

RUN chmod +x /scripts/*

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

RUN adduser --disabled-login user
RUN chown -R user:user /vol
RUN chown -R user:user /bi/theme
RUN chmod -R 755 /vol/web
RUN chmod -R 777 /bi/theme/static
USER user
CMD ["entrypoint.sh"]