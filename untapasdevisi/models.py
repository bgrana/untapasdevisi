# -*- coding: utf-8 -*-
from bulbs.neo4jserver import Graph as Neo4jGraph
from bulbs.model import Node, Relationship
from bulbs.property import String , Integer


class Graph(Neo4jGraph):    
    def __init__(self, config=None):
        super(Graph, self).__init__(config)
        
    @staticmethod
    def createGraph(config):
        return Graph(config)
        
##ESTO HAY QUE CAMBIARLO Y PONERLE UNA CONFIG (O NO)
g = Graph.createGraph(config=None) #Genero una instancia del grafo (ahora mismo la ruta es la de por defecto
#3g = Graph()

class User(Node):
    
    element_type = "user"

    #unique, index (if no index=True, index all properties)
    password =  String(nullable=False, indexed=False)
    username = String(nullable=False, unique=True, indexed=True)
    email = String(nullable=True, unique=True, indexed=False)
    photo = String(nullable=True, indexed=False) #Imagen en Base64 (TODO Ciclo2)
    
    @staticmethod
    def authenticate(uname, upass):
        try:
            user = g.user.index.lookup(username=uname).next()#Intentamos sacar el primer elemento
            if user and user.password == upass:
                return user
        except Exception:
            return
        
    @staticmethod
    def register(uname, upass):
        try:
            g.user.index.lookup(username=uname).next() #Intentamos sacar el primer elemento
        except Exception: #No hay elemento
            user = g.user.create(username=uname,password=upass) #Lo creamos
            return user
        return
    
    @staticmethod
    def get(id):
        return g.user.get(id)
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        #return g.user.index.lookup(username=self.username).next().eid #No creo que funcione
        return self.eid
class Local(Node):
    
    element_type = "local"

    #unique, index (if no index=True, index all properties)
    localname = String(nullable=False, unique=True, indexed=True)
    address = String(nullable=False, unique=True, indexed=True)
    photo = String(nullable=True, indexed=False) #Imagen en Base64 (TODO Ciclo2)
    
    @staticmethod
    def register(lname, laddress):
        try:
            g.local.index.lookup(localname=lname,address=laddress).next() #Comprobar si puedes buscar varios par/valores
        except Exception: #No hay elemento
            user = g.local.create(localname=lname,address=laddress) #Lo creamos
            return user
        return
    
    @staticmethod
    def get(id):
        return g.local.get(id)

    def get_id(self):
        return self.eid
    
class Friend(Relationship):
    
    label = "friend"
    created = DateTime(default=current_datetime, nullable=False)
    
    @staticmethod
    def create(node1, node2):
        g.friend.create(node1,node2)
    
    @staticmethod
    def get(id):
        return g.friend.get(id)

    def get_id(self):
        return self.eid
    
class fPending(Relationship):
    
    label = "fPending"
    created = DateTime(default=current_datetime, nullable=False)
    
    @staticmethod
    def create(node1, node2):#Necesita 2 objetos de tipo NODE (User o Local)
        g.friendRequests.create(node1,node2)
    
    @staticmethod
    def get(id):
        return g.friendRequests.get(id)

    def get_id(self):
        return self.eid
    
class Likes(Relationship):
    
    label = "likes"
    created = DateTime(default=current_datetime, nullable=False)
    
    @staticmethod
    def create(node1, node2):#Necesita 2 objetos de tipo NODE (User o Local)
        g.likes.create(node1,node2)
    
    @staticmethod
    def get(id):
        return g.likes.get(id)

    def get_id(self):
        return self.eid
    
#g.user = g.build_proxy(User) #Son terminos equivalentes
g.add_proxy("user", User)
g.add_proxy("local", Local)
g.add_proxy("friend", Friend)
g.add_proxy("fPending", fPending)
g.add_proxy("likes", Likes)
