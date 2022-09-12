""" Unittests for ghgql.Result """

from typing import Dict, Any
import unittest
from ghgql import Result


class TestResult(unittest.TestCase):
    """ Testcases for the Result class. """

    def test_get_ok(self):
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

    def test_get_raises_runtime_error_errors_present(self):
        """
        Test that a RuntimeError is raised under these conditions:

          1. Errors are present
        """
        result = Result({'errors': [{'message': "this is an artifical error"}]})
        self.assertIsNotNone(result.errors)
        self.assertIsNone(result.data)

        with self.assertRaises(RuntimeError) as ex:
            result.get(key="foo.bar")
        self.assertEqual(str(ex.exception), "errors are present")

    def test_get_raises_runtime_error_no_default(self):
        """
        Test that a RuntimeError is raised under these conditions:

          1. Data is empty and default is given
        """
        result = Result()
        self.assertIsNone(result.errors)
        self.assertIsNone(result.data)

        with self.assertRaises(RuntimeError) as ex:
            result.get(key="foo.bar")
        self.assertAlmostEqual(str(ex.exception), "data is None and no default is given")
        self.assertEqual(result.get(key="foo.bar", default=42), 42)

    def test_get_key_error_unresolveable_key_and_no_default(self):
        """
        Test that a KeyError is raised under these conditions:

           1. Key cannot be resolved and no default is given
        """
        result = Result({
            "data": {
                "status": {
                    "item": {
                        "id": "123"
                    }
                }
            }
        })
        self.assertIsNone(result.errors)
        self.assertIsNotNone(result.data)

        with self.assertRaises(KeyError) as ex:
            result.get(key="status.item.foo")
        self.assertEqual(str(ex.exception), "'key \"status.item.foo\" is not found and default is not present'")
        self.assertEqual(result.get(key="status.item.foo", default=42), 42)

    def test_get_key_error_invalid_key_no_default(self):
        """
        Test that a KeyError is raised under these conditions:

           1.Key is invalid and no default is given
        """
        result = Result({
            "data": {
                "status": {
                    "item": {
                        "id": "123"
                    }
                }
            }
        })
        self.assertIsNone(result.errors)
        self.assertIsNotNone(result.data)

        with self.assertRaises(KeyError) as ex:
            result.get(key="status.item..foo")
        self.assertEqual(str(ex.exception), "'invalid key \"status.item..foo\" because of empty element'")
        self.assertEqual(result.get(key="status.item.foo", default=42), 42)

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
