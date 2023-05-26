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
    
    @classmethod
    @property
    def class_files(cls):

        # operate on oa copy of the class_file dictionary
        class_file_copy = dict(cls.cfs)

        # for every class
        for path in class_file_copy:

            combined = ""

            # combine the rendered files into one file
            for content in class_file_copy[path]:

                combined += content()

            # write the combined file to the copy
            class_file_copy[path] = MockStr(combined)

        # return the rendered files
        return class_file_copy
    
    def add_if(self, contents, path):

        if path in self.ifs:

            self.ifs[path].append(contents)

        else:

            self.ifs |= {path: [contents]}

    @property
    def instance_files(self):

        instance_file_copy = dict(self.ifs)

        for path in instance_file_copy:

            combined = ""

            for content in instance_file_copy[path]:

                combined += content(self.params)

            instance_file_copy[path] = MockStr(combined)
        
        return instance_file_copy
    
    @classmethod
    @property
    def files(cls):

        combined_instance_files = cls.class_files

        for _, objs in cls._registry.items():
                
            for obj in objs:

                for path, content in obj.instance_files.items():

                    if path in combined_instance_files:

                        combined_instance_files[path] += content

                    else:

                        combined_instance_files |= {path: content}
        
        for path, content in combined_instance_files.items():

            combined_instance_files[path] = MockStr(content)        

        return combined_instance_files


class MockStr(str):

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

    def wrapper(func):

        inst.add_if(func, path)

    return wrapper