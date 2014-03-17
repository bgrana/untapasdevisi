import uuid
import requests


def generate_key():
    return uuid.uuid4().hex


def send_validation_email(email, key):
    url = "https://api.mailgun.net/v2/sandbox74944.mailgun.org/messages"
    # TODO: No poner la key de mailgun hardcoded
    auth = ("api", "key-84mxu54004c5y47zgym0z-d34jnsvl18")
    data = {
        "from": "UnTapasDevisi <untapasdevisi@sandbox74944.mailgun.org>",
        "to": [email],
        "subject": "Bienvenido a UntapasDevisi",
        "html": '<p>Pulsa sobre el enlace para activar tu cuenta:<br><a href="http://127.0.0.1:5000/keys/' + key + '">http://127.0.0.1:5000/keys/' + key + '</a>'
    }
    return requests.post(url, auth=auth, data=data)
