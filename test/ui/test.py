import unittest
from flask import Response

import ui.component as c
Component = c.Component
component = c.component
class_file = c.class_file
instance_file = c.instance_file
file = c.file


class TestComponent(unittest.TestCase):

    def __init__(self, *args, **kwargs):

        # define parameters for testing
        self.component_test_props = {"test_prop 1": 222, "test_prop 2": "function_sub_2", "test_prop 3": "test_string 2"}

        self.instance_1_test_params = {"test_param 1": 111, "test_param 2": "function_sub_1", "test_param 3": "test_string 1"}
        self.instance_2_test_params = {"test_param 1": 222, "test_param 2": "function_sub_2", "test_param 3": "test_string 2"}

        self.path_1 = "/path"
        self.path_2 = "/otherpath"

        # create component using decorator
        @component(self.component_test_props)
        def test_component(params, props):
            return f"""
            Main Component
            test_prop 1: {props["test_prop 1"]}
            test_prop 2: {props["test_prop 2"]}
            test_prop 3: {props["test_prop 3"]}
            test_param 1: {params["test_param 1"]}
            test_param 2: {params["test_param 2"]}
            test_param 3: {params["test_param 3"]}
            """
        self.test_component = test_component

        # create instances of components
        self.test_instance = self.test_component(self.instance_1_test_params)
        self.second_test_instance = self.test_component(self.instance_2_test_params)

        # add files to the request space
        @file(self.path_1)
        def path1(content):
            resp = Response(content)
            resp.headers["Content-Type"] = "text/css"
            return lambda: resp
        @file(self.path_2)
        def path2(content):
            resp = Response(content)
            resp.headers["Content-Type"] = "text/html"
            return lambda: resp

        super().__init__(*args, **kwargs)



    def test_step_1_component_decorator(self):

        self.assertEqual(type(self.test_component), type)
        self.assertIn(Component, self.test_component.__mro__)

    def test_step_2_class_file_decorator(self):

        self.assertEqual(Component.class_files, {})

        @class_file(self.test_component, self.path_1)
        def test_component_cf_1(props):
            return f"""
            /path Class File
            test_prop 1: {props["test_prop 1"]}
            test_prop 2: {props["test_prop 2"]}
            test_prop 3: {props["test_prop 3"]}
            """

        self.assertEqual(Component.class_files, 
            {
            self.path_1: f"""
            /path Class File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            """
            })

        @class_file(self.test_component, self.path_2)
        def test_component_cf_2(props):
            return f"""
            /otherpath Class File
            test_prop 1: {props["test_prop 1"]}
            test_prop 2: {props["test_prop 2"]}
            test_prop 3: {props["test_prop 3"]}
            """

        self.assertEqual(Component.class_files, 
            {
            self.path_1: f"""
            /path Class File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            """,

            self.path_2: f"""
            /otherpath Class File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            """
            })

    def test_step_3_instantiation(self):
        
        self.assertEqual(type(self.test_instance), self.test_component)
        self.assertEqual(self.test_instance.params | self.instance_1_test_params, self.test_instance.params)
        
        self.assertEqual(type(self.second_test_instance), self.test_component)
        self.assertEqual(self.second_test_instance.params | self.instance_2_test_params, self.second_test_instance.params)

    def test_step_4_instance_file_decorator(self):

        self.assertEqual(self.test_instance.instance_files, {})

        @instance_file(self.test_instance, self.path_1)
        def test_component_if_1(params, props):
            return f"""
            /path Instance File from test_instance
            test_prop 1: {props["test_prop 1"]}
            test_prop 2: {props["test_prop 2"]}
            test_prop 3: {props["test_prop 3"]}
            test_param 1: {params["test_param 1"]}
            test_param 2: {params["test_param 2"]}
            test_param 3: {params["test_param 3"]}
            """
        
        self.assertEqual(self.test_instance.instance_files, {
            self.path_1: f"""
            /path Instance File from test_instance
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            test_param 1: {self.instance_1_test_params["test_param 1"]}
            test_param 2: {self.instance_1_test_params["test_param 2"]}
            test_param 3: {self.instance_1_test_params["test_param 3"]}
            """
        })
        
        @instance_file(self.test_instance, self.path_2)
        def test_component_if_2(params, props):
            return f"""
            /otherpath Instance File from test_instance
            test_prop 1: {props["test_prop 1"]}
            test_prop 2: {props["test_prop 2"]}
            test_prop 3: {props["test_prop 3"]}
            test_param 1: {params["test_param 1"]}
            test_param 2: {params["test_param 2"]}
            test_param 3: {params["test_param 3"]}
            """
        
        self.assertEqual(self.test_instance.instance_files, {
            self.path_1: f"""
            /path Instance File from test_instance
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            test_param 1: {self.instance_1_test_params["test_param 1"]}
            test_param 2: {self.instance_1_test_params["test_param 2"]}
            test_param 3: {self.instance_1_test_params["test_param 3"]}
            """,

            self.path_2: f"""
            /otherpath Instance File from test_instance
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            test_param 1: {self.instance_1_test_params["test_param 1"]}
            test_param 2: {self.instance_1_test_params["test_param 2"]}
            test_param 3: {self.instance_1_test_params["test_param 3"]}
            """
        })
        
        @instance_file(self.second_test_instance, self.path_2)
        def second_test_component_if(params, props):
            return f"""
            /otherpath Instance File from second_test_instance
            test_prop 1: {props["test_prop 1"]}
            test_prop 2: {props["test_prop 2"]}
            test_prop 3: {props["test_prop 3"]}
            test_param 1: {params["test_param 1"]}
            test_param 2: {params["test_param 2"]}
            test_param 3: {params["test_param 3"]}
            """
        
        self.assertEqual(self.second_test_instance.instance_files, {
            self.path_2: f"""
            /otherpath Instance File from second_test_instance
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            test_param 1: {self.instance_2_test_params["test_param 1"]}
            test_param 2: {self.instance_2_test_params["test_param 2"]}
            test_param 3: {self.instance_2_test_params["test_param 3"]}
            """
        })

    def test_step_5_file_decorator(self):

        self.assertEqual(Component.files, {
            
            self.path_1: f"""
            /path Class File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            
            /path Instance File from test_instance
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            test_param 1: {self.instance_1_test_params["test_param 1"]}
            test_param 2: {self.instance_1_test_params["test_param 2"]}
            test_param 3: {self.instance_1_test_params["test_param 3"]}
            """,

            self.path_2: f"""
            /otherpath Class File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            
            /otherpath Instance File from test_instance
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            test_param 1: {self.instance_1_test_params["test_param 1"]}
            test_param 2: {self.instance_1_test_params["test_param 2"]}
            test_param 3: {self.instance_1_test_params["test_param 3"]}
            
            /otherpath Instance File from second_test_instance
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            test_param 1: {self.instance_2_test_params["test_param 1"]}
            test_param 2: {self.instance_2_test_params["test_param 2"]}
            test_param 3: {self.instance_2_test_params["test_param 3"]}
            """
        })


if __name__ == "__main__":

    unittest.main()