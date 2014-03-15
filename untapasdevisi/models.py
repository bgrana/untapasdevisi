# -*- coding: utf-8 -*-
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80))
    validated = db.Column(db.Boolean, default=False)
    # TODO: modificar esto usar bcrypt para guardar el hash y no el password en plaintext
    password = db.Column(db.String(80))

    def __init__(self, username, password, email):
        self.username = username
        self.email = email
        self.password = password


    def validate(self):
        User.query.filter_by(username = self.username).\
    update({"validated":True}, synchronize_session=False)


    def authenticate(username, password):
        user = User.query.filter_by(username=username).first()
        if not user or user.password != password:
            return
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

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id