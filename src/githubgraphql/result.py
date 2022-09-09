"""
githubgraphql.result
~~~~~~~~~~~~~~~~~~~~

A thin layer around the "dict" result of a Github GraphQL operation.
"""

from typing import Dict, Any
import unittest
import json

class Result(dict):
    """
    This is a dict that has a few helper functions to make it easier to
    work with the data returned from the Github GraphQL API.
    """

    def get(self, key: str, default: Any = None) -> Any:
        """
        Helper function to get data from a deeply nested dict.

        This syntax:

            a = result.get(key="status.item.id", default=42)

        is roughly equivalent to:

            result["status"]["item"]["id"]

        plus that it handles if a key doesn't exist and a default value should
        be used.
        """
        keys = key.split(".")

        current_value = self.data
        for k in keys:
            if isinstance(current_value, str) and current_value != "null":
                current_value = json.loads(current_value)
            if k in current_value:
                current_value = current_value[k]
            else:
                return default
        return current_value

    @property
    def data(self) -> Dict:
        """
        This returns the data dict.
        """
        if "data" in self:
            return self["data"]
        return None

    @property
    def errors(self) -> Any:
        """
        This returns the errors dict.
        """
        if "errors" in self:
            return self["errors"]
        return None

class TestResult(unittest.TestCase):
    """ Testcases for the Result class. """

    def test_get(self):
        """ Test the get method. """
        result = Result({
            "data": {
                "status": {
                    "item": {
                        "id": "123"
                    }
                }
            }
        })
        self.assertEqual(result.get(key="status.item.id"), "123")
        self.assertEqual(result.get(key="status.item.id", default=42), "123")
        self.assertEqual(result.get(key="status.item.id2", default=42), 42)

    def test_data(self):
        """ Test the data property. """
        result = Result({
            "data": {
                "status": {
                    "item": {
                        "id": "123"
                    }
                }
            }
        })
        self.assertEqual(result.data, {
            "status": {
                "item": {
                    "id": "123"
                }
            }
        })

    def test_errors(self):
        """ Test the errors property. """
        result = Result({'errors': [{'extensions': {'code': 'undefinedField',
                                                       'fieldName': 'MADEUPFIELD',
                                                       'typeName': 'User'},
                                        'locations': [{'column': 19, 'line': 1}],
                                        'message': "Field 'MADEUPFIELD' doesn't exist on type 'User'",
                                        'path': ['query', 'viewer', 'MADEUPFIELD']}]})
        self.assertEqual(result.errors, [{'extensions': {'code': 'undefinedField',
                                                       'fieldName': 'MADEUPFIELD',
                                                       'typeName': 'User'},
                                        'locations': [{'column': 19, 'line': 1}],
                                        'message': "Field 'MADEUPFIELD' doesn't exist on type 'User'",
                                        'path': ['query', 'viewer', 'MADEUPFIELD']}])

    def test_data_none(self):
        """ Test the data property when there is no data. """
        result = Result({})
        self.assertEqual(result.data, None)

    def test_errors_none(self):
        """ Test the errors property when there are no errors. """
        result = Result({})
        self.assertEqual(result.errors, None)

if __name__ == '__main__':
    unittest.main()
