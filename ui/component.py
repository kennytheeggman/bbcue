from uuid import uuid4


class Component:
    
    def __init__(self, name, params):

        self.name = name
        self.params = params

        self.id = uuid4()

    def __str__(self):

        return self.renderer(self.params | {"id": self.id})
    
def component(func):

    return type(func.__name__, (Component,), {"renderer": staticmethod(func)})
