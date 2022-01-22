# https://docs.docker.com/engine/reference/builder/

# WARNING Do not use alpine or slim python docker images as they lack compilers for building binaries form source (psycopg2, numpy, scipy, ..)
FROM python:3.8

ENV PYTHONUNBUFFERED 1

# Install node 12
RUN apt-get update
RUN apt-get -y install curl gnupg
RUN curl -sL https://deb.nodesource.com/setup_12.x  | bash -
RUN apt-get -y install nodejs

# Project Files and Settings
ARG PROJECT=pilotapp
ARG PROJECT_DIR=/var/www/${PROJECT}
RUN mkdir -p $PROJECT_DIR
WORKDIR $PROJECT_DIR

# Copy & install requirements
RUN mkdir ./requirements
COPY ./requirements/dev.txt ./requirements/
COPY ./requirements/common.txt ./requirements/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements/dev.txt

# Src files will be mounted in docker compose for dev
# COPY . .

# Server
EXPOSE 8000
STOPSIGNAL SIGINT
