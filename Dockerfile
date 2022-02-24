FROM python:3.9-alpine

ENV PATH="/scripts:${PATH}"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

RUN apk add --update --no-cahce --virtual .tmp gcc libc-dev linux-headers

RUN python -m pip install -r requirements.txt

RUN apk del .tmp

COPY ./bi /bi/

WORKDIR /bi

RUN apk add nodejs npm

COPY ./scripts /scripts

RUN chmod +x /scripts/*

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/

RUN adduser -D user
RUN chown -R user:user /vol
RUN chmod -R 755 /vol/web
USER user
CMD ["entrypoint.sh"]