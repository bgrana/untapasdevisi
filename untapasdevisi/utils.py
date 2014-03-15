import uuid
import requests
from passlib.hash import bcrypt


def generate_key():
    return uuid.uuid4().hex


def send_simple_message(mail, key):
    return requests.post(
        "https://api.mailgun.net/v2/sandbox74944.mailgun.org/messages",
        auth=("api", "key-84mxu54004c5y47zgym0z-d34jnsvl18"),
        data={"from": "UnTapasDevIS <untapasdevisi@sandbox74944.mailgun.org>",
              "to": [mail],
              "subject": "UnTapasDevIS Activacion",
              "html": '<p>Pulsa sobre el enlace para activar tu cuenta:<br><a href="http://127.0.0.1:5000/keys/' + key + '">http://127.0.0.1:5000/keys/' + key + '</a>'})


def hash_pwd(password):
	return bcrypt.encrypt(password)


def check_pwd(password, hashed_pwd):
	return bcrypt.verify(password, hashed_pwd)