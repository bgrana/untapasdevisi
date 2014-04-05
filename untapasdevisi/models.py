# -*- coding: utf-8 -*-

import mongoengine as mongo
from passlib.hash import bcrypt


def connect_db():
    mongo.connect('untapasdevisi')

class User(mongo.Document):
    username = mongo.StringField(required=True, unique=True)
    firstname = mongo.StringField()
    lastname = mongo.StringField()
    location = mongo.StringField()
    email = mongo.StringField()
    created = mongo.DateTimeField()
    activated = mongo.BooleanField()
    password_hash = mongo.StringField()

    @staticmethod
    def authenticate(username, password):
        user = User.objects(username=username).first()
        if user and user.has_password(password):
            return user

    def activate(self):
        self.activated = True
        self.save()

    @staticmethod
    def register(username, password, email):
        user = User(username=username, email=email)
        user.password_hash = bcrypt.encrypt(password)
        user.save()
        return user

    def update(self, form):
        self.username = form.username.data
        self.email = form.email.data
        if form.password.data:
            self.password_hash = bcrypt.encrypt(form.password.data)
        self.location = form.location.data
        self.save()

    def has_password(self, password):
        return bcrypt.verify(password, self.password_hash)

    # methods used by flask-login

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False



class Local(mongo.Document):
    localname = mongo.StringField(required=True, unique=True)
    location = mongo.StringField()