# -*- coding: utf-8 -*-

import datetime
from mongoengine import connect, Document, StringField
from mongoengine import ReferenceField, DateTimeField, BooleanField, Q
from passlib.hash import bcrypt


def connect_db(dbname):
    connect(dbname)


class User(Document):
    username = StringField(required=True, unique=True)
    firstname = StringField(required=True)
    lastname = StringField()
    location = StringField()
    email = StringField()
    created = DateTimeField(default=datetime.datetime.now)
    activated = BooleanField()
    password_hash = StringField()

    @staticmethod
    def authenticate(username, password):
        user = User.objects(username=username).first()
        if user and user.has_password(password):
            return user

    @staticmethod
    def register(form):
        user = User(
            username=form.username.data, firstname=form.firstname.data,
            lastname=form.lastname.data, email=form.email.data)
        user.password_hash = bcrypt.encrypt(form.password.data)
        user.save()
        return user

    @property
    def screen_name(self):
        name = self.firstname.capitalize()
        if self.lastname:
            name += " " + self.lastname.capitalize()
        return name

    @staticmethod
    def search(q, n):
        return User.objects.filter(
            Q(firstname__icontains=q) | Q(lastname__icontains=q) |
            Q(username__icontains=q))

    def activate(self):
        self.activated = True
        self.save()

    def update(self, form):
        self.username = form.username.data
        self.email = form.email.data
        if form.password.data:
            self.password_hash = bcrypt.encrypt(form.password.data)
        self.firstname = form.firstname.data
        self.lastname = form.lastname.data
        self.location = form.location.data
        self.save()

    def update_password(self, password):
        self.password_hash = bcrypt.encrypt(password)
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


class Friendship(Document):
    creator = ReferenceField('User')
    friend = ReferenceField('User')
    created = DateTimeField(default=datetime.datetime.now)
    confirmed = BooleanField(default=False)

    @staticmethod
    def create(creator, friend):
        friendship = Friendship(creator=creator.id, friend=friend.id)
        friendship.save()

        return friendship

    @staticmethod
    def get_from_users(users):
        if users[0] == users[1]:
            return None

        query = Friendship.objects.filter(
            (Q(creator=users[0].id) & Q(friend=users[1].id)) |
            (Q(creator=users[1].id) & Q(friend=users[0].id))
        )

        return query.first()

    @staticmethod
    def get_confirmed_from_user(user):
        return Friendship.objects.filter(
            (Q(creator=user.id) | Q(friend=user.id)) & Q(confirmed=True))

    @staticmethod
    def get_unconfirmed_from_friend(friend):
        return Friendship.objects.filter(
            Q(friend=friend.id) & Q(confirmed=False))

    def can_confirm(self, user):
        return user == self.friend

    def confirm(self):
        self.confirmed = True
        self.save()

        creator_activity = FriendshipActivity(
            creator=self.creator.id, friend=self.friend.id)
        creator_activity.save()

        friend_activity = FriendshipActivity(
            creator=self.friend.id, friend=self.creator.id)
        friend_activity.save()

    def get_friend(self, user):
        if user == self.creator:
            return self.friend
        else:
            return self.creator


class Activity(Document):
    creator = ReferenceField('User')
    created = DateTimeField(default=datetime.datetime.now)

    meta = {'allow_inheritance': True}


class FriendshipActivity(Activity):
    friend = ReferenceField('User')


class Local(Document):
    name = StringField(required=True, unique=True)
    slug = StringField(required=True, unique=True)
    location = StringField(required=True)
    description = StringField()
    created = DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def create_local(name, location, description=""):
        name = name
        slug = Local.slugify(name)
        local = Local(
            name=name,
            slug=slug,
            location=location,
            description=description
        )
        local.save()
        return local

    @staticmethod
    def get_by_slug(slug):
        return Local.objects(slug=slug).first()

    @staticmethod
    def slugify(name):
        return name.strip().lower().replace(' ', '-')

    @staticmethod
    def search(q, n):
        return Local.objects(name__icontains=q).limit(5)
