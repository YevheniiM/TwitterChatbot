FROM python:3.8-alpine

ENV PYTHONUNBUFFERED=1

RUN mkdir /proj
RUN mkdir -p /data/logs/

COPY requirements/* /proj/requirements/

RUN apk add --no-cache --update bash ca-certificates gcc linux-headers make musl-dev libffi-dev jpeg-dev zlib-dev git bash
RUN apk add --no-cache musl-dev mariadb-dev openssh

RUN pip install -r proj/requirements/base.txt

COPY . /proj/

RUN chmod +x /proj/config/start.sh
WORKDIR /proj/