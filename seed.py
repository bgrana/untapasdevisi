# -*- coding: utf-8 -*-

import untapasdevisi.models as models
from untapasdevisi.forms import RegisterForm

models.connect_db('untapasdevisi')

# TODO: refactor register to not use form

dbarbera = models.User.register(RegisterForm(
    username="dbarbera",
    password="qwerty",
    email="diego@dbarbera.name",
    firstname="Diego",
    lastname="Barberá"
))

dbarbera.activated = True
dbarbera.save()

jesus = models.User.register(RegisterForm(
    username="jesus",
    password="qwerty",
    email="jesus@vatican.va",
    firstname="Jesús"
))

bpaco = models.Local.create_local(name="Bar Paco", location="Madrid")
bpepe = models.Local.create_local(name="Bar Pepe", location="Madrid")
chino = models.Local.create_local(name="Restaurante Chino Gran Sol", location="Madrid")

models.Like.create(bpaco, dbarbera)
models.Like.create(bpaco, jesus)
models.Like.create(chino, dbarbera)

friendship = models.Friendship.create(dbarbera, jesus)
friendship.confirm()
