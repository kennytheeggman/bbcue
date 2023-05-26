from uuid import uuid4


class Component:

    # class_file dictionary
    cfs = {}

    # object registry
    _registry = {}
    
    def __init__(self, params):

        # add object to registry
        if type(self) in self._registry:

            self._registry[type(self)].append((self, type(self)))
        
        else:

            self._registry |= {type(self): [self]}

        # declare parameters including a random id
        self.params = params | {"id": uuid4()}

        self.ifs = {}

    def __str__(self):

        # when string is called, render with parameters
        return self.renderer(self.params)
    
    @classmethod
    def add_cf(cls, contents, path):

        if path in cls.cfs:

            # add file contents to the class_file dictionary dynamically
            cls.cfs[path].append(contents)

        else:
            
            # insert new key
            cls.cfs |= {path: [contents]}
    
    def add_if(self, contents, path):

        if path in self.ifs:
            
            # add file contents to the instance_file dictionary dynamically
            self.ifs[path].append(contents)

        else:

            # insert new key
            self.ifs |= {path: [contents]}
    
    @classmethod
    @property
    def class_files(cls):

        # operate on a copy of the class_file dictionary
        class_file_copy = dict(cls.cfs)

        # for every path
        for path in class_file_copy:

            combined = ""

            # combine the rendered files into one file
            for content in class_file_copy[path]:

                combined += content()

            # write the combined file to the copy
            class_file_copy[path] = MockStr(combined)

        # return the rendered files
        return class_file_copy

    @property
    def instance_files(self):

        # operate on a copy of the class_file dictionary
        instance_file_copy = dict(self.ifs)

        # for every path
        for path in instance_file_copy:

            combined = ""

            # combine the rendered files into one file
            for content in instance_file_copy[path]:

                # call content function with parameters
                combined += content(self.params)

            # write the combined file to the copy
            instance_file_copy[path] = MockStr(combined)
        
        # return the rendered files
        return instance_file_copy
    
    @classmethod
    @property
    def files(cls):

        # get class files
        combined_files = cls.class_files

        # combine class files and instance files
        for _, objs in cls._registry.items():
                
            for obj in objs:

                for path, content in obj.instance_files.items():
                    
                    # merge instance files one at a time with class files
                    if path in combined_files:

                        combined_files[path] += content

                    else:

                        combined_instance_files |= {path: content}
        
        # set everything to a mock string, so the routing works properly
        for path, content in combined_files.items():

            combined_files[path] = MockStr(content)        

        # return combined files
        return combined_instance_files


class MockStr(str):

    # fake string class that returns itself when called
    def __call__(self):

        return self

    
def component(func):

    # create a new type that inherits from Component
    return type(func.__name__, (Component,), {"renderer": staticmethod(func)})

def class_file(cls, path):

    # add a class_file using the add_cf classmethod
    def wrapper(func):

        cls.add_cf(func, path)
    
    return wrapper

def instance_file(inst, path):

    # add an instance_file using the add_if method
    def wrapper(func):

        inst.add_if(func, path)

    return wrapper