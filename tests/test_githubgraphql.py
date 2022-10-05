""" Tests for ghgql.ghgql """

import unittest
from uuid import uuid4
import functools
from tempfile import NamedTemporaryFile
from os import getenv
from contextlib import contextmanager
import requests
import fnc
import ghgql


def skip_if_no_token(func):
    """
    This is a decorator function you can use to skip a test if no GITHUB_TOKEN
    token is specifyied in the environment.
    """
    @functools.wraps(func)
    def wrapper(test_case):
        if test_case.api_token is None:
            test_case.skipTest(
                "Skipping test case because no GITHUB_TOKEN environment variable is set.")
        func(test_case)
    return wrapper


class TestGithubGraphQL(unittest.TestCase):
    """ Testcases for the GithubGraphQL class. """

    def setUp(self) -> None:
        self.__token = getenv(key="GITHUB_TOKEN", default=None)
        self.__viewer_login = getenv(key="GITHUB_LOGIN", default=None)

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
                self.assertIsInstance(actual, dict)

    @skip_if_no_token
    def test_query_with_raise_on_error(self):
        """ Test that we raise an error when requested """
        with ghgql.GithubGraphQL(token=self.api_token) as ghapi:
            query = " query { viewer { MADEUPFIELD } }"
            with self.get_query_as_file(query=query) as filename:
                expected = {'errors': [{'extensions': {'code': 'undefinedField',
                                                       'fieldName': 'MADEUPFIELD',
                                                       'typeName': 'User'},
                                        'locations': [{'column': 19, 'line': 1}],
                                        'message': "Field 'MADEUPFIELD' doesn't exist on type 'User'",
                                        'path': ['query', 'viewer', 'MADEUPFIELD']}]}
                with self.assertRaises(RuntimeError) as ex:
                    ghapi.query_from_file(filename=filename, raise_on_error=True)
                self.assertAlmostEqual(str(ex.exception), fnc.get("errors[0].message", expected))

    @skip_if_no_token
    def test_query_with_raise_on_error_in_ctor(self):
        """ Test that we raise an error when requested """
        with ghgql.GithubGraphQL(token=self.api_token, raise_on_error=True) as ghapi:
            query = " query { viewer { MADEUPFIELD } }"
            with self.get_query_as_file(query=query) as filename:
                expected = {'errors': [{'extensions': {'code': 'undefinedField',
                                                       'fieldName': 'MADEUPFIELD',
                                                       'typeName': 'User'},
                                        'locations': [{'column': 19, 'line': 1}],
                                        'message': "Field 'MADEUPFIELD' doesn't exist on type 'User'",
                                        'path': ['query', 'viewer', 'MADEUPFIELD']}]}
                with self.assertRaises(RuntimeError) as ex:
                    ghapi.query_from_file(filename=filename)
                self.assertAlmostEqual(str(ex.exception), fnc.get("errors[0].message", expected))

    @skip_if_no_token
    def test_raise_on_error_precedence(self):
        """
        Test that we don't raise an error when disable locally but enabled
        globally.
        """
        with ghgql.GithubGraphQL(token=self.api_token, raise_on_error=True) as ghapi:
            query = " query { viewer { MADEUPFIELD } }"
            expected = {'errors': [{'extensions': {'code': 'undefinedField',
                                                    'fieldName': 'MADEUPFIELD',
                                                    'typeName': 'User'},
                                    'locations': [{'column': 19, 'line': 1}],
                                    'message': "Field 'MADEUPFIELD' doesn't exist on type 'User'",
                                    'path': ['query', 'viewer', 'MADEUPFIELD']}]}
            # This should not raise an exception because it was explicitly
            # disabled locally:
            actual = ghapi.query(query=query, raise_on_error=False)
            self.assertEqual(actual, expected)

    # Test for https://github.com/kwk/ghgql/issues/4
    def test_session_headers_have_token_set(self):
        """ Test that the session is properly equiped with a bearer token in the
        header when the GithubGraphQL object is instantiated without a context
        manager. """
        ghapi = ghgql.GithubGraphQL(token="foobar")
        headers = ghapi.session_headers
        self.assertTrue("Authorization" in headers, "session headers are missing Authorization")
        self.assertEqual(headers["Authorization"], "Bearer foobar", "Authorization token in session headers mismatch")

    @skip_if_no_token
    def test_real_example(self):
        """ Test a real world example query and analysis """
        query = """
        query($org: String!, $number: Int!) {
            organization(login: $org) {
                projectV2(number: $number) {
                items(last: 100) {
                    nodes {
                    id

                    fieldValues(first: 8) {
                        nodes {
                        ... on ProjectV2ItemFieldSingleSelectValue {
                            name
                            field {
                            ... on ProjectV2FieldCommon {
                                name
                            }
                            }
                        }
                        ... on ProjectV2ItemFieldTextValue {
                            text
                            field {
                            ... on ProjectV2FieldCommon {
                                name
                            }
                            }
                        }
                        ... on ProjectV2ItemFieldPullRequestValue {
                            pullRequests(last: 10) {
                            nodes {
                                url
                                number
                            }
                            }
                        }
                        }
                    }

                    content {
                        ...on Issue {
                        title
                        number
                        url
                        state
                        milestone {
                            number
                        }
                        }
                    }
                    }
                }
                }
            }
        }
        """
        with ghgql.GithubGraphQL(token=self.api_token) as ghapi:
            result = ghapi.query(query=query, variables={"org": "kwk-org", "number": 1})
            nodes = fnc.get("data.organization.projectV2.items.nodes", result)
            milestone_numbers = fnc.map("content.milestone.number", nodes)
            self.assertEqual(list(milestone_numbers), [1,2,3])

            # Get the milestone using the iterator protocol (as requested in #5)
            i = 1
            for node in nodes:
                self.assertEqual(i, fnc.get("content.milestone.number", node))
                i+=1

if __name__ == '__main__':
    unittest.main()
