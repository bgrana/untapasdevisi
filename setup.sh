#!/bin/bash

# Script de instalación de Untapasdevisi

# Virtualenv
apt-get install -y virtualenvwrapper

# Redis
DIR=$(pwd)
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
apt-get install -y redis-server
cd $DIR

# Python-dev
apt-get install -y python-dev

# Mongodb
apt-get install -y mongodb

# Activar el virtualenv
virtualenv .
. ./bin/activate

# SetupTools
curl https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py | python

# Dependencias
pip install -r requirements.txt