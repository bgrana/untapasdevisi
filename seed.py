import untapasdevisi.models as models
from untapasdevisi.forms import RegisterForm

models.connect_db('untapasdevisi')

users = [
    models.User.register(RegisterForm(username="dbarbera", password="qwerty",
        email="diego@dbarbera.name", firstname="Diego", lastname="Barberá")),
    models.User.register(RegisterForm(username="jesus", password="qwerty",
        email="jesus@vatican.va", firstname="Jesus"))
]

locals = [
    models.Local.create_local(
        name="Bar Paco",
        location="Madrid"
    ),
    models.Local.create_local(
        name="Bar Pepe",
        location="Madrid"
    ),
    models.Local.create_local(
        name="Restaurante Chino Gran Sol",
        location="Madrid"
    )
]
