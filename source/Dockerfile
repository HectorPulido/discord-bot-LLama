# syntax=docker/dockerfile:1

# pull official base image
FROM python:3.10

RUN apt-get -y update
RUN apt-get -y upgrade

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code
COPY requirements.txt /code/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt
COPY . /code/