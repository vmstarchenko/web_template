FROM docker.io/python:3.12-slim-bookworm

ARG \
    UNAME=web \
    UID=1000 \
    GID=1000

# For Mysql: default-libmysqlclient-dev
# for some libs: gcc 
RUN set -ex \
    && apt-get update \
    && apt-get install \
        curl less \
        -y \
    && rm -rf /var/lib/apt/lists/*

RUN set -ex \
    && groupadd -g $GID -o $UNAME \
    && useradd --create-home --shell /bin/bash --home /home/$UNAME \
        -u $UID -g $GID $UNAME \
    && mkdir /var/www/static /var/www/media -p

USER $UNAME

ENV \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/home/$UNAME/venv \
    PATH=/home/$UNAME/venv/bin:/home/$UNAME/etc/scripts:$PATH \
    TERM=xterm-256color

EXPOSE 8000

WORKDIR /home/$UNAME/app
