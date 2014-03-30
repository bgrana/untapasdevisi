# -*- coding: utf-8 -*-

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

    def __init__(self, username, password, email):
        self.username = username
        self.email = email
        self.password_hash = bcrypt.encrypt(password)

    @staticmethod
    def authenticate(username, password):
        user = User.get_by_username(username)
        if user and user.has_password(password):
            return user

    def validate(self):
        self.validated = True
        db.session.add(self)
        db.session.commit()

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

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    def update(self, form):
        if form.username.data:
            self.username = form.username.data
        if form.email.data:
            self.email = form.email.data
        if form.password.data:
            self.password_hash = bcrypt.encrypt(form.password.data)
        db.session.add(self)
        db.session.commit()

    def has_password(self, password):
        return bcrypt.verify(password, self.password_hash)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id