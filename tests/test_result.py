""" Unittests for ghgql.Result """

from typing import Dict, Any
import unittest
from ghgql import Result


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
        self.assertEqual(result.errors,
                         [{'extensions': {'code': 'undefinedField',
                                          'fieldName': 'MADEUPFIELD',
                                          'typeName': 'User'},
                           'locations': [{'column': 19,
                                          'line': 1}],
                             'message': "Field 'MADEUPFIELD' doesn't exist on type 'User'",
                             'path': ['query',
                                      'viewer',
                                      'MADEUPFIELD']}])

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
