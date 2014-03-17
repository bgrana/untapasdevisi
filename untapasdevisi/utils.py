import uuid
import requests
from flask import render_template


def send_validation_email(user):
    url = "https://api.mailgun.net/v2/sandbox74944.mailgun.org/messages"
    # TODO: No poner la key de mailgun hardcoded
    auth = ("api", "key-84mxu54004c5y47zgym0z-d34jnsvl18")
    # TODO: No poner localhost hardcoded
    host = "127.0.0.1:5000"
    data = {
        "from": "UnTapasDevisi <untapasdevisi@sandbox74944.mailgun.org>",
        "to": [user.email],
        "subject": "Bienvenido a UntapasDevisi",
        "html": render_template("validation_email.html", host=host, user=user)
    }
    return requests.post(url, auth=auth, data=data)
