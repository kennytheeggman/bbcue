import re
import string
import random


class Component:

    def __init__(self, params):

        cls = type(self)

        cls.instances.append(self)
        cls.props = cls.renderer.props | cls.props

        self.params = params
        self._ifs = {}

    def __str__(self):

        cls = type(self)
        return cls.renderer.renderer(cls.props, self.params)

    @classmethod
    def _add_cf(cls, path, func):

        file = File(func)

        if path in cls._cfs:
            cls._cfs[path].append(file)

        else:
            cls._cfs |= {path: [file]}

        cls.props = file.props | cls.props

    @classmethod
    def class_file(cls, path):

        def wrapper(func):
            cls._add_cf(path, func)

        return wrapper

    @classmethod
    @property
    def class_files(cls):

        class_files = {}

        for path, funcs in cls._cfs.items():

            combined = ""

            for func in funcs:
                
                value = func.renderer(cls.props)
                combined += value

            class_files[path] = combined

        return class_files

    def _add_if(self, path, func):

        file = File(func)

        if path in self._ifs:
            self._ifs[path].append(file)

        else:
            self._ifs |= {path: [file]}

        self.params = file.params | self.params

    def instance_file(self, path):

        def wrapper(func):
            self._add_if(path, func)

        return wrapper

    @property
    def instance_files(self):

        instance_files = {}

        cls = type(self)

        for path, funcs in self._ifs.items():

            combined = ""

            for func in funcs:
                value = func.renderer(cls.props, self.params)
                combined += value

            instance_files[path] = combined

        return instance_files

    @classmethod
    def accumulate_files(cls):

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

        for instance in cls.instances:
            files = concat_dicts(files, instance.instance_files)

        files = concat_dicts(files, cls.class_files)

        return files

    @classmethod
    @property
    def files(cls):

        return cls.accumulate_files()


class File:

    def __init__(self, renderer):

        self.renderer = renderer
        self.props, self.params = File.get_keys(renderer)

    @classmethod
    def from_file(cls, path, m_prop=r'\$"(.*?)"', m_param=r'\&"(.*?)"', r_prop=r'{props[\1]}', r_param=r'{params[\1]}'):

        f = open(path)
        regex = f.read()

        # ensure number of groups in regex sequence are correct
        if re.compile(m_prop).groups < 1:
            raise GroupException("No groups found in match_props")
        elif re.compile(m_prop).groups > 1:
            raise GroupException("Too many groups found in match_props")
        elif re.compile(m_param).groups < 1:
            raise GroupException("No groups found in match_params")
        elif re.compile(m_param).groups > 1:
            raise GroupException("Too many groups found in match_params")

        # replace single curly braces with doubles for string formatting consistency
        escaped = re.sub(r'}', r'}}', re.sub(r'{', r'{{', regex))

        # substitute the pattern
        p1 = re.sub(m_prop, r_prop, escaped)
        p2 = re.sub(m_param, r_param, p1)

        def r(props, params={}):

            return p2.format(props=props, params=params)

        return File(r)

    @staticmethod
    def get_keys(func):

        test_props = {}
        test_params = {}

        key = None

        while True:

            try:
                func(test_props, test_params)

            except KeyError as e:
                key = str(e)[1:-1]
                test_props[key] = File.rid()

            else:
                break

            try:
                func(test_props, test_params)

            except KeyError as e:

                if str(e)[1:-1] != key:
                    continue

                else:
                    test_props.pop(key)
                    test_params[key] = File.rid()

            else:
                continue

            try:
                func(test_props, test_params)

            except KeyError as e:

                if str(e)[1:-1] != key:
                    continue

                else:
                    test_props[key] = File.rid()

        return test_props, test_params

    @staticmethod
    def rid():
        
        alphabet = string.ascii_lowercase
        return ''.join(random.choices(alphabet, k=8))


class GroupException(Exception):
    pass
