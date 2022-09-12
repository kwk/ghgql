""" Tests for ghgql.ghgql """

import unittest
from uuid import uuid4
import functools
from tempfile import NamedTemporaryFile
from os import getenv
from contextlib import contextmanager
import ghgql
import requests


def skip_if_no_token(func):
    """
    This is a decorator function you can use to skip a test if no GITHUB_TOKEN
    token is specifyied in the environment.
    """
    @functools.wraps(func)
    def wrapper(test_case):
        if test_case.api_token is None:
            test_case.skipTest(
                "Skipping test because no GITHUB_TOKEN environment variable is set.")
        func(test_case)
    return wrapper


class TestGithubGraphQL(unittest.TestCase):
    """ Testcases for the GithubGraphQL class. """

    def __init__(self, methodName: str = ...) -> None:
        self.__token = getenv(key="GITHUB_TOKEN", default=None)
        self.__viewer_login = getenv(key="GITHUB_LOGIN", default=None)
        super().__init__(methodName)

    @property
    def api_token(self) -> str:
        """ Returns the Github API token. """
        return self.__token

    @property
    def viewer_login(self) -> str:
        """ Returns the expected Github login that corresponds to the API token """
        return self.__viewer_login

    @contextmanager
    def get_query_as_file(self, query: str) -> str:
        """
        Returns a temporary filename with the given query written to it.
        Use this as a context manager:

            with self.get_query_as_file(query="query {}") as filename:
                g.query_from_file(filename)
        """
        file_handle = NamedTemporaryFile(mode="w+", encoding="utf-8")
        file_handle.writelines(query)
        file_handle.flush()
        try:
            yield file_handle.name
        finally:
            file_handle.close()

    def test_query_file_not_found(self):
        """ Test what happens when we try to query with a file that doesn't exist. """
        with ghgql.GithubGraphQL() as ghapi:
            filename = str(uuid4())
            with self.assertRaises(FileNotFoundError):
                ghapi.query_from_file(filename)

    def test_query_file_is_directory(self):
        """ Test what happens when the query file is a directory. """
        with ghgql.GithubGraphQL() as ghapi:
            with self.assertRaises(IsADirectoryError):
                ghapi.query_from_file("/")

    @skip_if_no_token
    def test_wrong_query(self):
        """ Test what happens when we try use an invalid query string """
        with ghgql.GithubGraphQL(token=self.api_token) as ghapi:
            query = "foo"
            with self.get_query_as_file(query) as filename:
                expected = {'errors': [{'locations': [{'column': 1, 'line': 1}],
                                        'message': 'Parse error on "foo" (IDENTIFIER) at [1, 1]'}]}
                self.assertEqual(ghapi.query_from_file(filename), expected)

    @skip_if_no_token
    def test_empty_query(self):
        """ Test what happens when we try use an empty query string """
        with ghgql.GithubGraphQL(token=self.api_token) as ghapi:
            query = ""
            with self.get_query_as_file(query) as filename:
                expected = {'errors': [
                    {'message': 'A query attribute must be specified and must be a string.'}]}
                self.assertEqual(ghapi.query_from_file(filename), expected)

    def test_wrong_endpoint_returns_non_json(self):
        """ Test what happens when we try use an invalid endpoint """
        with ghgql.GithubGraphQL(endpoint="https://www.example.com") as ghapi:
            query = " query { viewer { login } }"
            with self.get_query_as_file(query) as filename:
                with self.assertRaises(requests.JSONDecodeError):
                    ghapi.query_from_file(filename)

    @skip_if_no_token
    def test_ok_get_viewers_login(self):
        """ Test that we can get the login of the viewer """
        with ghgql.GithubGraphQL(token=self.api_token) as ghapi:
            query = " query { viewer { login } }"
            with self.get_query_as_file(query) as filename:
                expected = {"data": {"viewer": {"login": self.viewer_login}}}
                actual = ghapi.query_from_file(filename)
                self.assertEqual(actual, expected)
                print(type(actual))
                self.assertIsInstance(actual, ghgql.Result)

    @skip_if_no_token
    def test_undefined_field_madeupfield(self):
        """ Test that we get an error when we try to query an undefined field """
        with ghgql.GithubGraphQL(token=self.api_token) as ghapi:
            query = " query { viewer { MADEUPFIELD } }"
            with self.get_query_as_file(query) as filename:
                expected = {'errors': [{'extensions': {'code': 'undefinedField',
                                                       'fieldName': 'MADEUPFIELD',
                                                       'typeName': 'User'},
                                        'locations': [{'column': 19, 'line': 1}],
                                        'message': "Field 'MADEUPFIELD' doesn't exist on type 'User'",
                                        'path': ['query', 'viewer', 'MADEUPFIELD']}]}
                actual = ghapi.query_from_file(filename)
                self.assertEqual(actual, expected)
                self.assertIsInstance(actual, ghgql.Result)


if __name__ == '__main__':
    unittest.main()
