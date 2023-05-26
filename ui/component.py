from uuid import uuid4


class Component:
    """
    Class that mimics the functionality of React components in python, maintaining state within the argument chain.

    Parameters:

        params (dict) - dictionary of parameters which serves as the argument for the text renderers.

    Properties:

        params (dict) - same as the initialization argument. If the "id" key exists in parameters, it is replaced with a randomly generated UUID. Otherwise, the "id" key is set to a randomly generated UUID.

        class_files (dict) - the keys in this variable are the class file paths to which contents have been added, and the values are the concatenated contents. Class files are class properties, stored universally in the class. 

        instance_files (dict) - the keys are the instance file paths to which contents have been added, and the values are the concatenated contents. Instance files can differ between instances, and are called with the instance parameters.

        files (dict) - this dictionary is a concatenation of the class files and all the instance files

        renderer (function) - function that takes in self.params and outputs rendered HTML text

    Hidden Properties:

        _cfs (class property (dict)) - same as the class_files property, but instead of concatenated contents, are lists of content generating functions for class files

        _ifs (dict) - same as the instance_files property, but instead of concatenated contents, are lists of content generating functions for instance files

        _registry (class property (dict)) - a dictionary of classes inheriting from Component, and the objects that are instances of those classes

    """

    # class_file dictionary
    _cfs = {}

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

        self._ifs = {}

    def __str__(self):
        """
        String dunder function, used when transforming class instances into strings

        Parameters:

            None

        Returns:

            str - the text rendered with the self.params as an argument and self.renderer as the renderer

        """

        # when string is called, render with parameters
        return self.renderer(self.params)
    
    @classmethod
    def _add_cf(cls, contents, path):

        """
        Adds a class_file to the classpaths

        Parameters:

            contents (function) - Function that accepts zero arguments, and produces the rendered file content text

            path (string) - path to where the rendered file content text should be appended

        Returns:

            None

        """

        if path in cls._cfs:

            # add file contents to the class_file dictionary dynamically
            cls._cfs[path].append(contents)

        else:
            
            # insert new key
            cls._cfs |= {path: [contents]}
    
    def _add_if(self, contents, path):

        """
        Adds a instance_file to the instance

        Parameters:

            contents (function) - Function that accepts zero arguments, and produces the rendered file content text

            path (string) - path to where the rendered file content text should be appended

        Returns:

            None

        """

        if path in self._ifs:
            
            # add file contents to the instance_file dictionary dynamically
            self._ifs[path].append(contents)

        else:

            # insert new key
            self._ifs |= {path: [contents]}
    
    @classmethod
    @property
    def class_files(cls):

        """
        Accessor for the class_files property
        """

        # operate on a copy of the class_file dictionary
        class_file_copy = dict(cls._cfs)

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
        
        """
        Accessor for the instance_files property
        """

        # operate on a copy of the class_file dictionary
        instance_file_copy = dict(self._ifs)

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

        """
        Accessor for the files property
        """

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
        return combined_files


class MockStr(str):

    """
    String class encapsulator, such that a call to an instantiated object yields its string value, and its __name__ property yields itself
    """

    # fake string class that returns itself when called
    def __call__(self):

        return self
    
    # when name is referenced, also return itself
    @property
    def __name__(self):

        return self

    
def component(func):

    """
    Decorator to create a component out of a rendering function. 

    Parameters:

        func (function) - A rendering function that accepts one input parameter, of same type as Component.params, and outputs a string

    Returns:

        Component>class - A class with the same name as func that inherits from Component. Its renderer property is the func function

    """

    # create a new type that inherits from Component
    return type(func.__name__, (Component,), {"renderer": staticmethod(func)})

def class_file(path):

    """
    Decorator to add a class file to a class out of a rendering function

    Parameters:

        path (str) - The path to which the file contents should be appended

    Returns:

        function - A function that accepts the rendering function, which accepts zero parameters, and adds it to the class_file path system
    """

    # add a class_file using the add_cf classmethod
    def wrapper(func):

        Component._add_cf(func, path)
    
    return wrapper

def instance_file(inst, path):

    """
    Decorator to add an instance file to an instance out of a rendering function

    Parameters:

        inst (obj) - The object to which an instance file should be added

        path (str) - The path to which the file contents should be appended

    Returns:

        function - A function that accepts the rendering function, which accepts parameters of the same type as Component.params, and adds it to the instance_file path system
    """

    # add an instance_file using the add_if method
    def wrapper(func):

        inst._add_if(func, path)

    return wrapper