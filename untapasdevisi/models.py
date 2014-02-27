# -*- coding: utf-8 -*-
#from bulbs.neo4jserver import Graph 
from bulbs.model import Node
from bulbs.neo4jserver import Graph
from bulbs.property import String, Integer

g = Graph();
g.add_proxy("user", User) #Esto no haría falta, de hecho casi toda la clase user sobra :(

class User(Node):
    #id = Integer() La id está implicita, es un long que se obtiene con .id
    username = String(nullable=False)
    password = String(nullable=False)
    
    # REESCRIBIR
    # cambiar los atributos de la clase como os sea necesario para vuestra base de datos
    def __init__(self, username, password):
        self.username = username
        self.password = password

    # REESCRIBIR
    # este metodo recibe un nombre de usuario y contraseña y debe devolver el usuario asociado a ellos
    # si la contraseña es incorrecta o hay algun error devolver null
    @staticmethod
    def authenticate(uname, upass):
        ret_user = g.user.index.lookup(username=uname).next() #Busca el usuario por el parametro dado
        if not ret_user or ret_user.password != upass:
            return
        return ret_user

    # REESCRIBIR
    # este metodo debe crear un nuevo usuario en la base de datos y devolverlo
    # si hay algun error devolver null
    @staticmethod
    def register(uname, upass):
        ret_user = g.user.index.lookup(username=uname).next() #Busca el usuario por el parametro dado
        if ret_user: #El usuario existe
            return
        ret_user = g.user.create(username=uname,password=upass)
        return ret_user
        
    # REESCRIBIR
    # este metodo recive como argumento el atributo que useis en el metodo get_id que esta
    # mas abajo y debe devolver el usuario asociado a esa id
    @staticmethod
    def get(id):
        return g.user.get(id) #Tal vez en vez del indice "user" haya que usar el indice "vertices" (que es global)

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
        return self.id