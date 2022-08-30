FROM docker.io/mysql:debian

ARG UNAME=db \
    UID=1000 \
    GID=1000

RUN set -ex \
    && groupadd -g $GID -o UNAME \
    && useradd --create-home --shell /bin/bash --home /home/$UNAME \
        -u $UID -g $GID $UNAME \
    && mkdir /home/$UNAME/data

USER $UNAME

COPY my.cnf /etc/mysql/my.cnf
