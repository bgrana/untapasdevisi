# -*- coding: utf-8 -*-

import uuid
import requests
from flask import render_template


class Valut():
    def __init__(self, redis):
        self.redis = redis

    def put(self, data, ttl=None):
        key = uuid.uuid4().hex
        # This implementation is not secure. The key must be handled as
        # securely as a password. It must be hashed.
        self.redis.set("valut:%s" % key, data)
        if ttl:
            self.redis.expire("valut:%s" % key, ttl)
        return key

    def get(self, key):
        return self.redis.get("valut:%s" % key)

    def delete(self, key):
        self.redis.delete("valut:%s" % key)


class Postman:
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
