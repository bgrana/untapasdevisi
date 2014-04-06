# -*- coding: utf-8 -*-

import datetime
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
    created = mongo.DateTimeField(default=datetime.datetime.now)
    activated = mongo.BooleanField()
    password_hash = mongo.StringField()
    friends = mongo.ListField(mongo.ReferenceField('User', dbref=True))

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

    def get_requests(self):
        return FriendshipRequest.objects(receiver=self)

    def accept_request(self, request):
        self.add_friend(request.sender)
        request.delete()

    def has_request_from(self, user):
        request = FriendshipRequest.objects(sender=user.to_dbref(), receiver=self.to_dbref()).first()
        return request is not None

    def request_friendship(self, user):
        request = FriendshipRequest(sender=user.to_dbref(), receiver=self.to_dbref())
        request.save()

    def add_friend(self, user):
        self.friends.append(user.to_dbref())
        self.save()
        FriendshipActivity(creator=self.to_dbref(), friend=user.to_dbref()).save()

        user.friends.append(self.to_dbref())
        user.save()
        FriendshipActivity(creator=user.to_dbref(), friend=self.to_dbref()).save()

    def remove_friend(self, user):
        self.friends.remove(user)
        self.save()
        user.friends.remove(self)
        user.save()

    def is_friend(self, user):
        return user in self.friends

    # methods used by flask-login

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False


class FriendshipRequest(mongo.Document):
    sender = mongo.ReferenceField('User', dbref=True)
    receiver = mongo.ReferenceField('User', dbref=True)
    created = mongo.DateTimeField(default=datetime.datetime.now)


class Activity(mongo.Document):
    creator = mongo.ReferenceField('User', dbref=True)
    created = mongo.DateTimeField(default=datetime.datetime.now)

    meta = {'allow_inheritance': True}


class FriendshipActivity(Activity):
    friend = mongo.ReferenceField('User', dbref=True)


class Local(mongo.Document):
    localname = mongo.StringField(required=True, unique=True)
    location = mongo.StringField()