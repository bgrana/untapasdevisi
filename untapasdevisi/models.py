# -*- coding: utf-8 -*-

import uuid

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from passlib.hash import bcrypt


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80))
    validated = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(80))
    validation_key = db.Column(db.String(80))

    def __init__(self, username, password, email):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.encrypt(password)
        self.validation_key = uuid.uuid4().hex

    @staticmethod
    def authenticate(username, password):
        user = User.query.filter_by(username=username).first()
        if user or user.has_password(password):
            return user

    @staticmethod
    def validate(username, key):
        user = User.query.filter_by(username=username).first()
        if user and not user.validated and user.has_validation_key(key):
            user.validate = True
            db.session.add(user)
            db.session.commit()
            return user

    @staticmethod
    def register(username, password, email):
        try:
            user = User(username, password, email)
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            return

    @staticmethod
    def get(id):
        return User.query.get(id)

    def has_password(self, password):
        return bcrypt.verify(password, self.password_hash)

    def has_validation_key(self, key):
        return self.validation_key == key

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id