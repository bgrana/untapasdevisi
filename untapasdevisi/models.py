class User():
    def __init__(self, username):
        self.username = username

    # reescribir estos metodos para que funcionen con la base de datos que useis
    @staticmethod
    def authenticate(username, password):
        return User(username)

    @staticmethod
    def register(username, password):
        return User(username)

    @staticmethod
    def get(username):
        return User(username)

    # metodos usados por Flask-login, reescribirlos que funcionen con la base de datos que useis
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username