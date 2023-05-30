from uuid import uuid4
from flask import Response
import string
import random


class Component:

    """
    Class that mimics the functionality of React components in python, maintaining state within the argument chain.

    Parameters:

        params (dict) - Dictionary of parameters which serves as the argument for the text renderers.

    Properties:

        params (dict) - Same as the initialization argument. If the "id" key exists in parameters, it is replaced with a randomly generated UUID. Otherwise, the "id" key is set to a randomly generated UUID.

        class_files (class property (dict)) - The keys in this variable are the class file paths to which contents have been added, and the values are the concatenated contents. Class files are class properties, stored universally in the class. 

        class_files_response (class property (dict)) - Identical to class_files except each file content has been processed to become a Response object, for response header and type support

        instance_files (dict) - The keys are the instance file paths to which contents have been added, and the values are the concatenated contents. Instance files can differ between instances, and are called with the instance parameters.

        instance_files_response (dict) - Identical to instance_files except each file content has been processed to become a Response object, for response header and type support

        files (class property (dict)) - This dictionary is a concatenation of the class files and all the instance files

        files_response (class property (dict)) - Identical to files except each file content has been processed to become a Response object, for response header and type support

        renderer (function) - Function that takes in self.params and outputs rendered HTML text

    Hidden Properties:

        _cfs (class property (dict)) - Same as the class_files property, but instead of concatenated contents, are lists of content generating functions for class files

        _ifs (dict) - Same as the instance_files property, but instead of concatenated contents, are lists of content generating functions for instance files

        _registry (class property (dict)) - A dictionary of classes inheriting from Component, and the objects that are instances of those classes

        _cparams (class property (dict)) - Same purpose as params, but for class-wide interfacing. This is an argument in all renderers

    """

    # class_file dictionary
    _cfs = {}

    # object registry
    _registry = {}

    # class parameters
    _cparams = {}

    _file_resps = {}
    
    def __init__(self, params):

        # add object to registry
        if type(self) in self._registry:

            self._registry[type(self)].append(self)
        
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

            str - The text rendered with the self.params and cls._cparams as an argument and self.renderer as the renderer

        """

        # when string is called, render with parameters
        return self.renderer(self.params, type(self)._cparams | Component._cparams)
    
    @classmethod
    def _add_cf(cls, contents, path):

        """
        Adds a class_file to the classpaths

        Parameters:

            contents (function) - Function that accepts zero arguments, and produces the rendered file content text

            path (string) - Path to where the rendered file content text should be appended

        Returns:

            None

        """

        print(cls)

        if cls in cls._cfs:

            if path in cls._cfs[cls]:

                # add file contents to the class_file dictionary dynamically
                cls._cfs[cls][path].append(contents)

            else:
                
                # insert new key
                cls._cfs[cls] |= {path: [contents]}
        
        else:

            cls._cfs |= {cls: {path: [contents]}}
    
    def _add_if(self, contents, path):

        """
        Adds a instance_file to the instance

        Parameters:

            contents (function) - Function that accepts zero arguments, and produces the rendered file content text

            path (string) - Path to where the rendered file content text should be appended

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

        new_class_file = {}

        # for every path
        for t, class_files in class_file_copy.items():

            # combine the rendered files into one file
            for path in class_files:

                combined = ""

                for content in class_files[path]:

                    combined += content(t._cparams | Component._cparams)

                if path in new_class_file:
                
                    new_class_file[path] += combined
                
                else:

                    new_class_file[path] = combined           


        # write the combined file to the copy
        for path in new_class_file:

            new_class_file[path] = (new_class_file[path])

        # return the rendered files
        return new_class_file
    
    @classmethod
    @property
    def class_files_response(cls):

        """
        Accessor for class_files_response property
        """

        copy = {}

        # for each class file
        for path in Component.class_files:
            
            # if the path has a response function, use the response function
            if path in Component._file_resps:
                
                copy[path] = Component._file_resps[path](Component.class_files[path])

            # otherwise, encapsulate in a default response function
            else:

                copy[path] = lambda: Response(Component.class_files[path])
        
        return copy

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
                combined += content(self.params, type(self)._cparams | Component._cparams)

            # write the combined file to the copy
            instance_file_copy[path] = (combined)
        
        # return the rendered files
        return instance_file_copy
            
    @property
    def instance_files_response(self):

        """
        Accessor for instance_files_response property
        """

        copy = {}

        # for each instance file
        for path in self.instance_files:
            
            # if the path has a response function, use the response function
            if path in Component._file_resps:
                
                copy[path] = Component._file_resps[path](self.instance_files[path])

            # otherwise use the default response function
            else:

                copy[path] = lambda: Response(self.instance_files[path])
        
        return copy
    
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

                        combined_files |= {path: content}
        
        # set everything to a mock string, so the routing works properly
        for path, content in combined_files.items():

            combined_files[path] = (content)        

        # return combined files
        return combined_files
    
    @classmethod
    @property
    def files_response(cls):

        """
        Accessor for files_response property
        """

        copy = {}
        
        # for each file
        for path in Component.files:
            
            # if the path has a response function, use the response function
            if path in Component._file_resps:
                
                copy[path] = Component._file_resps[path](Component.files[path])
            
            # otherwise use the default response function
            else:

                copy[path] = lambda: Response(Component.files[path])
        
        return copy

    @classmethod
    def component(cls, params):

        """
        Decorator to create a component out of a rendering function. 

        Parameters:

            params (dict) - The dictionary specifying the class parameters for the new class inheriting from Component

        Returns:

            function - A function that creates a class inheriting from Component with the same name as the calling function, and predefined renderer and class parameters

        """

        print(cls)

        def wrapper(func):

            # create a new type that inherits from Component
            return type(func.__name__, (cls,), {"renderer": staticmethod(func), "_cparams": params})
        
        return wrapper


    @staticmethod
    def class_file(cls, path):

        """
        Decorator to add a class file to a class out of a rendering function

        Parameters:

            path (str) - The path to which the file contents should be appended

        Returns:

            function - A function that accepts the rendering function, which accepts zero parameters, and adds it to the class_file path system
        
        """

        # add a class_file using the add_cf classmethod
        def wrapper(func):

            cls._add_cf(func, path)
        
        return wrapper


    @staticmethod
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

    @staticmethod
    def file(path):

        """
        Decorator to add a file to the request space

        Parameters: 

            path (string) - String to the path, corresponding to a key

        Returns:

            function - A function that accepts the function that maps from file content to Response object, and adds it to the list of response functions
        """

        # add the function to the response functions list
        def wrapper(func):

            Component._file_resps |= {path: func}

        return wrapper

alphabet = string.ascii_lowercase
def rid():
    return ''.join(random.choices(alphabet, k=8))

def create_component_context():

    return type(rid(), tuple(), dict(Component.__dict__))