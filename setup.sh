#!/bin/bash

# Script de instalación de Untapasdevisi

# Virtualenv
apt-get install -y virtualenvwrapper

# Redis
apt-get install -y redis-server

# Python-dev
apt-get install -y python-dev

# Mongodb
apt-get install -y mongodb

# Activar el virtualenv
virtualenv venv
. venv/bin/activate

# Dependencias
pip install -r requirements.txt