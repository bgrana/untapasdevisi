# -*- coding: utf-8 -*-

import uuid
import requests
from flask import render_template


def generate_key():
    return uuid.uuid4().hex


class Mailer:
    def __init__(self, api_user, api_key, host):
        self.auth = ("api", api_key)
        self.host = host
        self.api_url = "https://api.mailgun.net/v2/%s.mailgun.org/messages" \
            % api_user
        self.email = "untapasdevisi@%s.mailgun.org" % api_user

    def send_validation_email(self, user, key):
        data = {
            "from": "UnTapasDevisi <%s>" % self.email,
            "to": [user.email],
            "subject": "Bienvenido a UntapasDevisi",
            "html": render_template(
                "validation_email.html", host=self.host, user=user, key=key)
        }
        return requests.post(self.api_url, auth=self.auth, data=data)

    def send_reset_password_email(self, user, key):
        data = {
            "from": "UnTapasDevisi <%s>" % self.email,
            "to": [user.email],
            "subject": "Recupera tu contraseña",
            "html": render_template(
                "reset_password_email.html",
                host=self.host, user=user, key=key)
        }
        return requests.post(self.api_url, auth=self.auth, data=data)