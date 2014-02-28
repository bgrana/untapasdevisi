# -*- coding: utf-8 -*-
from bulbs.neo4jserver import Graph as Neo4jGraph
from bulbs.model import Node
from bulbs.property import String


g = Neo4jGraph()

class User(Node):
    #element_type = "user"
    # unique, index (assume all index, and index=False)
    password =  String(nullable=False)
    username = String(nullable=False)  

    def __init__(self, uname, upass):
        self.username = uname
        self.password = upass

    @staticmethod
    def authenticate(uname, upass):
        user = g.vertices.index.lookup(username=uname).next()
        if not user or user.password != upass:
            return
        return user

    @staticmethod
    def register(uname, upass):
        user = g.vertices.index.lookup(username=uname).next()
        if not user:
            user = g.vertices.create(username=uname,password=upass)
            return user
        else:
            return

    @staticmethod
    def get(id):
        return g.vertices.get(id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return g.vertices.index.lookup(username=self.username).next().eid #No creo que funcione
    

    
