# -*- coding: utf-8 -*-

import datetime
from mongoengine import connect, Document, StringField, ListField
from mongoengine import ReferenceField, DateTimeField, BooleanField, Q
from mongoengine import GenericReferenceField, GenericEmbeddedDocumentField
from mongoengine import EmbeddedDocument, IntField
from passlib.hash import bcrypt

IMG_PATH = 'images'

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
    avatar = StringField()

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
        user.avatar = '/' + IMG_PATH + '/no_avatar.jpg'
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

    meta = {'allow_inheritance': True}


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

        friend_activity = FriendshipActivity.create(
            creator=self.creator, friend=self.friend)

    def get_friend(self, user):
        if user == self.creator:
            return self.friend
        else:
            return self.creator


class Activity(Document):
    creator = ReferenceField('User')
    target = GenericReferenceField()
    created = DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def search(creator, target):
        return Activity.objects.filter(
            Q(creator=creator) | Q(target=target))

    meta = {'allow_inheritance': True}


class FriendshipActivity(Activity):
    
    @staticmethod
    def create(creator, friend):
        activity = FriendshipActivity(creator=creator, target=friend)
        activity.save()
        return activity


class LikeActivity(Activity):

    @staticmethod
    def create(local, user):
        activity = LikeActivity(creator=user, target=local)
        activity.save()
        return activity


class DislikeActivity(Activity):

    @staticmethod
    def create(local, user):
        activity = DislikeActivity(creator=user, target=local)
        activity.save()
        return activity


class VoteActivity(Activity):
    points = IntField()

    @staticmethod
    def create(tasting, user, points):
        activity = VoteActivity(creator=user, target=tasting, points=points)
        activity.save()
        return activity


class CommentActivity(Activity):
   
    @staticmethod
    def create(target, creator):
        activity = CommentActivity(target=target, creator=creator)
        activity.save()
        return activity


class Local(Document):
    name = StringField(required=True, unique=True)
    slug = StringField(required=True, unique=True)
    location = StringField(required=True)
    description = StringField()
    avatar = StringField()
    created = DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def create_local(name, location, description="",
        avatar='/'+IMG_PATH+'/no_local_avatar.png'):
        
        name = name
        slug = Local.slugify(name)
        local = Local(
            name=name,
            slug=slug,
            location=location,
            description=description,
            avatar=avatar
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

    meta = {'allow_inheritance': True}


class Like(Document):
    local = ReferenceField('Local')
    user = ReferenceField('User')

    @staticmethod
    def create(local, user):
        like = Like(local.id, user.id)
        like.save()
        activity = LikeActivity.create(local, user)
        return like

    @staticmethod
    def get_by_local_and_user(local, user):
        a = Like.objects(Q(local=local.id) & Q(user=user.id)).first()
        return a


class Tasting(Document):
    name = StringField(required=True, unique=True)
    slug = StringField(required=True, unique=True)
    local_name = StringField(required=True)
    local_slug = StringField(required=True)
    recipe = StringField()
    avatar = StringField()
    points = IntField(default=0)
    user_votes = IntField(default=0)
    created = DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def create_tasting(name, local_name, recipe="",
        avatar='/'+IMG_PATH+'/no_tasting_avatar.png'):
        
        name = name
        slug = Tasting.slugify(name)
        local_name = local_name
        local_slug = Tasting.slugify(local_name)
        tasting = Tasting(
            name=name,
            slug=slug,
            local_name=local_name,
            local_slug=local_slug,
            recipe=recipe,
            avatar=avatar
        )
        tasting.save()
        return tasting

    @staticmethod
    def get_by_slug(slug):
        return Tasting.objects(slug=slug).first()

    @staticmethod
    def slugify(name):
        return name.strip().lower().replace(' ', '-')

    @staticmethod
    def search(q, n):
        return Local.objects(name__icontains=q).limit(5)

    meta = {'allow_inheritance': True}


class Vote(Document):
    user = ReferenceField('User')
    tasting = ReferenceField('Tasting')
    points = IntField()

    @staticmethod
    def create_vote(user, tasting, points):
        points = int(points)
        vote = Vote(user=user, tasting=tasting, points=points)
        vote.save()
        tasting.points += points
        tasting.user_votes += 1
        tasting.save()
        activity = VoteActivity.create(tasting, user, points)

    def update_vote(self, points):
        points = int(points)
        old_points = self.points
        self.points = points
        self.save()
        tasting = self.tasting
        tasting.points = tasting.points - old_points + self.points
        tasting.save()
        activity = VoteActivity.create(tasting, self.user, points)

class Comment(Document):
    message = StringField()
    user = ReferenceField('User')
    target = GenericReferenceField()
    created = DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def create_comment(target, user, message):
        comment = Comment(user=user, target=target, message=message)
        comment.save()
        activity = CommentActivity.create(target=target, creator=user)

    @staticmethod
    def search(user, target):
        return Comment.objects.filter(
            Q(user=user) | Q(target=target))