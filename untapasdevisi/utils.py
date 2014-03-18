# -*- coding: utf-8 -*-

import uuid
import requests
from flask import render_template


def generate_key():
    return uuid.uuid4().hex


# Nota: Estos dos métodos son muy parecidos. Si vamos a enviar mas
# emails quizás sería interesante creat alguna clase Sender que
# contuviese la url, auth y host para enviar mails

def send_validation_email(user, key):
    url = "https://api.mailgun.net/v2/sandbox74944.mailgun.org/messages"
    # TODO: No poner la key de mailgun hardcoded
    auth = ("api", "key-84mxu54004c5y47zgym0z-d34jnsvl18")
    # TODO: No poner localhost hardcoded
    host = "127.0.0.1:5000"
    data = {
        "from": "UnTapasDevisi <untapasdevisi@sandbox74944.mailgun.org>",
        "to": [user.email],
        "subject": "Bienvenido a UntapasDevisi",
        "html": render_template("validation_email.html", host=host, user=user, key=key)
    }
    return requests.post(url, auth=auth, data=data)


def sent_reset_password_email(user, key):
    url = "https://api.mailgun.net/v2/sandbox74944.mailgun.org/messages"
    # TODO: No poner la key de mailgun hardcoded
    auth = ("api", "key-84mxu54004c5y47zgym0z-d34jnsvl18")
    # TODO: No poner localhost hardcoded
    host = "127.0.0.1:5000"
    data = {
        "from": "UnTapasDevisi <untapasdevisi@sandbox74944.mailgun.org>",
        "to": [user.email],
        "subject": "Recupera tu contraseña",
        "html": render_template("reset_password_email.html", host=host, user=user, key=key)
    }
    return requests.post(url, auth=auth, data=data)