import untapasdevisi.models as models

models.connect_db()

users = [
    models.User.register("dbarbera", "qwerty", "diego@dbarbera.name"),
    models.User.register("jesus", "qwerty", "jesus@vatican.va")
]