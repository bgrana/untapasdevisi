class User():
    # REESCRIBIR
    # cambiar los atributos de la clase como os sea necesario para vuestra base de datos
    def __init__(self, username):
        self.username = username

    # REESCRIBIR
    # este metodo recibe un nombre de usuario y contraseña y debe devolver el usuario asociado a ellos
    # si la contraseña es incorrecta o hay algun error devolver null
    @staticmethod
    def authenticate(username, password):
        return User(username)

    # REESCRIBIR
    # este metodo debe crear un nuevo usuario en la base de datos y devolverlo
    # si hay algun error devolver null
    @staticmethod
    def register(username, password):
        return User(username)

    # REESCRIBIR
    # este metodo recive como argumento el atributo que useis en el metodo get_id que esta
    # mas abajo y debe devolver el usuario asociado a esa id
    @staticmethod
    def get(id):
        return User(id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    # REESCRIBIR
    # este metodo debe retornar el atributo que va a userse para la cookie. Lo normal seria devolver
    # la key del modelo, el id, o lo que sea equivalente en vuestras bases de datos
    def get_id(self):
        return self.username