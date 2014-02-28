# -*- coding: utf-8 -*-
from bulbs.neo4jserver import Graph as Neo4jGraph
from bulbs.model import Node
from bulbs.property import String , Integer


class Graph(Neo4jGraph):    
    def __init__(self, config=None):
        super(Graph, self).__init__(config)
        # Node Proxies
            
g = Graph()


class User(Node):
    
    element_type = "person"

    # unique, index (assume all index, and index=False)

    password =  String(nullable=False)
    username = String(nullable=False)
    
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
        return g.user.index.lookup(username=self.username).next().eid #No creo que funcione

g.user = g.build_proxy(User)
g.add_proxy("user", User)
