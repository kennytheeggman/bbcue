from .component import Component, File
from flask import Response
from mimetypes import guess_type


class ComponentContext:

    def __init__(self):

        self.components = []
        self.resp_funcs = {}

    def accumulate_files(self):

        def concat_dicts(dict1, dict2):

            combine = {}

            for key, value in dict1.items():

                if key in combine:
                    combine[key] += value
                else:
                    combine |= {key: value}

            for key, value in dict2.items():

                if key in combine:
                    combine[key] += value
                else:
                    combine |= {key: value}

            return combine

        files = {}

        for cls in self.components:
            files = concat_dicts(files, cls.accumulate_files())

        return files

    # collect all files from all classes

    def route_app(self, app):

        for url, content in self.files_responses.items():
            app.add_url_rule(url, view_func=content)

    # add all path routes from classes

    def from_folder(self, path, props, exclude=None, **kwargs):

        # imports for acquiring file names
        if exclude is None:
            exclude = []
        from os import listdir
        from os.path import isfile, join

        # get files
        files = [f for f in listdir(path) if isfile(join(path, f)) and f not in exclude]
        files.sort()

        # identify candidates for primary files
        main_candidates = [valid for valid in files if valid.startswith("index") or valid.startswith("main")]

        # get first main candidate if main candidate exists, else get first alphabetical file
        main = main_candidates[0] if len(main_candidates) > 0 else files[0]
        main_file = File.from_file(join(path, main), **kwargs)
        component = self.component(props)(main_file.renderer)

        files.remove(main)

        for file in files:

            component.class_file(f"/{path}/{file}")(File.from_file(join(path, file), **kwargs).renderer)

            def wrapper(content):

                resp = Response(content)

                if guess_type(join(path, file))[0]:
                    resp.headers["Content-Type"] = guess_type(join(path, file))[0]

                return lambda: resp

            self.file(f"/{path}/{file}")(wrapper)

        return component

    def component(self, props):

        # raise NotImplementedError

        def wrapper(func):
            
            p = {"props": props, "renderer": File(func), "_cfs": {}, "instances": []}
            cls = type(func.__name__, (Component,), p)

            self.components.append(cls)

            return cls

        return wrapper

    # create new component with props and function and add it to the registered components

    @property
    def files(self):

        return self.accumulate_files()

    @property
    def files_responses(self):

        files = {}

        for path in self.files:

            if path in self.resp_funcs:
                files[path] = self.resp_funcs[path](self.files[path])

            else:
                files[path] = lambda: Response(self.files[path])

        return files

    def file(self, path):

        def wrapper(func):
            self.resp_funcs |= {path: func}

        return wrapper

    # register a file to the routing space
