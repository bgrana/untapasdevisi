import untapasdevisi.models as models
from untapasdevisi.forms import RegisterForm

models.connect_db()

users = [
    models.User.register(RegisterForm(username="dbarbera", password="qwerty",
        email="diego@dbarbera.name", firstname="Diego", lastname="Barbera")),
    models.User.register(RegisterForm(username="jesus", password="qwerty",
        email="jesus@vatican.va", firstname="Jesus"))
]