import unittest
from flask import Response

import ui.component as c
Component = c.Component
component = c.component
class_file = c.class_file
instance_file = c.instance_file
file = c.file


class TestComponent(unittest.TestCase):
    """Tests for creation and usage of the Component class and related functions"""

    def __init__(self, *args, **kwargs):

        # define parameters for testing
        self.component_test_props = {"test_prop 1": 123, "test_prop 2": "test_component", "test_prop 3": "Component"}
        self.second_component_test_props = {"test_prop 1": 123, "test_prop 2": "second_test_component", "test_prop 3": "Component"}

        self.instance_1_test_params = {"test_param 1": 123, "test_param 2": "test_instance", "test_param 3": "test_component"}
        self.instance_2_test_params = {"test_param 1": 123, "test_param 2": "second_test_instance", "test_param 3": "test_component"}

        self.path_1 = "/path"
        self.path_2 = "/otherpath"

        # create components using decorator
        @component(self.component_test_props)
        def test_component(params, props):
            return f"""
            test_prop 1: {props["test_prop 1"]}
            test_prop 2: {props["test_prop 2"]}
            test_prop 3: {props["test_prop 3"]}
            test_param 1: {params["test_param 1"]}
            test_param 2: {params["test_param 2"]}
            test_param 3: {params["test_param 3"]}
            """
        self.test_component = test_component
        @component(self.second_component_test_props)
        def second_test_component(params, props):
            return f"""
            test_prop 1: {props["test_prop 1"]}
            test_prop 2: {props["test_prop 2"]}
            test_prop 3: {props["test_prop 3"]}
            test_param 1: {params["test_param 1"]}
            test_param 2: {params["test_param 2"]}
            test_param 3: {params["test_param 3"]}
            """
        self.second_test_component = second_test_component

        # create instances of components
        self.test_instance = self.test_component(self.instance_1_test_params)
        self.second_test_instance = self.test_component(self.instance_2_test_params)

        # add files to the request space
        @file(self.path_1)
        def path1(content):
            resp = Response(content)
            resp.headers["Content-Type"] = "text/css"
            return lambda: resp
        
        # self.path_2 is not added to test for if path_2's response function is not defined 

        # call parent initialization for compatibility
        super().__init__(*args, **kwargs)


    def test_step_1_component_decorator(self):

        """
        Created components must result in classes that inherit from Component
        """

        # ensure test_component is a class that inherits from Component
        self.assertEqual(type(self.test_component), type,
            "component decorator did not produce a class"                 
        )
        self.assertIn(Component, self.test_component.__mro__,
            "component decorator does not inherit from Component"
        )

    def test_step_2_class_file_decorator(self):

        """
        Class files must reflect the concatenation of file contents in the same path and must be separated by file paths and class files from different classes must all be combined. The response object must have function values which return Response objects. 
        """

        # ensure class_files is empty before any addition
        self.assertEqual(Component.class_files, {},
            "Class Files are not initialized as empty"
        )

        # ensure class_files is as expected after one addition
        @class_file(self.test_component, self.path_1)
        # given value
        def test_component_cf_1(props):
            return f"""
            /path Class File
            test_prop 1: {props["test_prop 1"]}
            test_prop 2: {props["test_prop 2"]}
            test_prop 3: {props["test_prop 3"]}
            """
        # expected value
        self.assertEqual(Component.class_files, {
            self.path_1: f"""
            /path Class File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            """
            },
            "Adding a single class file test case failed"
        )

        # ensure class_files is as expected after two additions from different classes
        @class_file(self.second_test_component, self.path_1)
        # given value
        def second_test_component_cf_1(props):
            return f"""
            /path Class File
            test_prop 1: {props["test_prop 1"]}
            test_prop 2: {props["test_prop 2"]}
            test_prop 3: {props["test_prop 3"]}
            """
        # expected value
        self.assertEqual(Component.class_files, {
            self.path_1: f"""
            /path Class File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            
            /path Class File
            test_prop 1: {self.second_component_test_props["test_prop 1"]}
            test_prop 2: {self.second_component_test_props["test_prop 2"]}
            test_prop 3: {self.second_component_test_props["test_prop 3"]}
            """
            },
            "Adding a two class files from different classes test case failed"
        )

        # ensure class_files is as expected after another addition to a different path
        @class_file(self.test_component, self.path_2)
        # given value
        def test_component_cf_2(props):
            return f"""
            /otherpath Class File
            test_prop 1: {props["test_prop 1"]}
            test_prop 2: {props["test_prop 2"]}
            test_prop 3: {props["test_prop 3"]}
            """
        # expected value
        self.assertEqual(Component.class_files, 
            {
            self.path_1: f"""
            /path Class File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            
            /path Class File
            test_prop 1: {self.second_component_test_props["test_prop 1"]}
            test_prop 2: {self.second_component_test_props["test_prop 2"]}
            test_prop 3: {self.second_component_test_props["test_prop 3"]}
            """,
            self.path_2: f"""
            /otherpath Class File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            """
            },
            "Adding two class files from the same class to different paths test case failed"
        )

        # ensure that all responses are of type Response
        for response in Component.class_files_response.values():
            
            self.assertTrue(callable(response), "Response value is not callable")
            self.assertEqual(type(response()), Response, "Response value does not return a Response object")

    def test_step_3_instantiation(self):

        """
        Instantiation must maintain input parameters
        """
        
        # ensure instantiation occured with correct parameters
        self.assertEqual(type(self.test_instance), self.test_component, "Instantiation failed")
        self.assertEqual(self.test_instance.params | self.instance_1_test_params, self.test_instance.params, "Instantiation did not isntantiate with correct parameters")
        
        self.assertEqual(type(self.second_test_instance), self.test_component, "Instantiation failed")
        self.assertEqual(self.second_test_instance.params | self.instance_2_test_params, self.second_test_instance.params, "Instantiation did not isntantiate with correct parameters")

    def test_step_4_instance_file_decorator(self):

        """
        Instance files must reflect the concatenation of file contents in the same path and must be separated by file paths and instance files from different instances must be isolated. The response object must have function values which return Response objects.
        """

        # ensure instance files are clean
        self.assertEqual(self.test_instance.instance_files, {}, "Instace Files are not instatiated as empty")
        self.assertEqual(self.second_test_instance.instance_files, {}, "Instance files are not instantiated as empty")

        # ensure instance_files is as expected after one addition
        @instance_file(self.test_instance, self.path_1)
        # given value
        def test_component_if_1(params, props):
            return f"""
            /path Instance File
            test_prop 1: {props["test_prop 1"]}
            test_prop 2: {props["test_prop 2"]}
            test_prop 3: {props["test_prop 3"]}
            test_param 1: {params["test_param 1"]}
            test_param 2: {params["test_param 2"]}
            test_param 3: {params["test_param 3"]}
            """
        # expected value
        self.assertEqual(self.test_instance.instance_files, {
            self.path_1: f"""
            /path Instance File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            test_param 1: {self.instance_1_test_params["test_param 1"]}
            test_param 2: {self.instance_1_test_params["test_param 2"]}
            test_param 3: {self.instance_1_test_params["test_param 3"]}
            """
            },
            "Adding one instance file test case failed"
        )
        
        # ensure instance_files is as expected after another addition to a different path
        @instance_file(self.test_instance, self.path_2)
        # given value
        def test_component_if_2(params, props):
            return f"""
            /otherpath Instance File
            test_prop 1: {props["test_prop 1"]}
            test_prop 2: {props["test_prop 2"]}
            test_prop 3: {props["test_prop 3"]}
            test_param 1: {params["test_param 1"]}
            test_param 2: {params["test_param 2"]}
            test_param 3: {params["test_param 3"]}
            """
        # expected value
        self.assertEqual(self.test_instance.instance_files, {
            self.path_1: f"""
            /path Instance File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            test_param 1: {self.instance_1_test_params["test_param 1"]}
            test_param 2: {self.instance_1_test_params["test_param 2"]}
            test_param 3: {self.instance_1_test_params["test_param 3"]}
            """,
            self.path_2: f"""
            /otherpath Instance File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            test_param 1: {self.instance_1_test_params["test_param 1"]}
            test_param 2: {self.instance_1_test_params["test_param 2"]}
            test_param 3: {self.instance_1_test_params["test_param 3"]}
            """
            },
            "Adding two instance files to different paths test case failed"
        )
        
        # esnure instance_files is as expected after one addition to a different instance
        @instance_file(self.second_test_instance, self.path_2)
        # given value
        def second_test_component_if(params, props):
            return f"""
            /otherpath Instance File
            test_prop 1: {props["test_prop 1"]}
            test_prop 2: {props["test_prop 2"]}
            test_prop 3: {props["test_prop 3"]}
            test_param 1: {params["test_param 1"]}
            test_param 2: {params["test_param 2"]}
            test_param 3: {params["test_param 3"]}
            """
        # expected value
        self.assertEqual(self.second_test_instance.instance_files, {
            self.path_2: f"""
            /otherpath Instance File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            test_param 1: {self.instance_2_test_params["test_param 1"]}
            test_param 2: {self.instance_2_test_params["test_param 2"]}
            test_param 3: {self.instance_2_test_params["test_param 3"]}
            """
            },
            "Adding instance files from different instances test case failed"    
        )
        
        # ensure that all responses are of type response
        for response in self.test_instance.instance_files_response.values():
            
            self.assertTrue(callable(response), "Response value not callable")
            self.assertEqual(type(response()), Response, "Response value does not return a Response object")

        for response in self.second_test_instance.instance_files_response.values():
            
            self.assertTrue(callable(response), "Response value not callable")
            self.assertEqual(type(response()), Response, "Response value does not return a Response object")

    def test_step_5_file_decorator(self):
        
        """
        Files must reflect the concatenation of file contents in the same path and must be separated by file paths. Files must be combined from all class files and all instance files. The response object must have function values which return Response objects.
        """

        # ensure files is as expected after all additions
        self.assertEqual(Component.files, {
            self.path_1: f"""
            /path Class File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            
            /path Class File
            test_prop 1: {self.second_component_test_props["test_prop 1"]}
            test_prop 2: {self.second_component_test_props["test_prop 2"]}
            test_prop 3: {self.second_component_test_props["test_prop 3"]}
            
            /path Instance File
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
            
            /otherpath Instance File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            test_param 1: {self.instance_1_test_params["test_param 1"]}
            test_param 2: {self.instance_1_test_params["test_param 2"]}
            test_param 3: {self.instance_1_test_params["test_param 3"]}
            
            /otherpath Instance File
            test_prop 1: {self.component_test_props["test_prop 1"]}
            test_prop 2: {self.component_test_props["test_prop 2"]}
            test_prop 3: {self.component_test_props["test_prop 3"]}
            test_param 1: {self.instance_2_test_params["test_param 1"]}
            test_param 2: {self.instance_2_test_params["test_param 2"]}
            test_param 3: {self.instance_2_test_params["test_param 3"]}
            """
            },
            "Combining all instance files and class files test case failed"    
        )

        # ensure that all responses are of type response
        for response in Component.files_response.values():
            
            self.assertTrue(callable(response), "Response value not callable")
            self.assertEqual(type(response()), Response, "Response value does not return a Response object")


if __name__ == "__main__":

    unittest.main()