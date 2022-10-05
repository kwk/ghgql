"""
ghgql.ghgql
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This provides a simply class that can be used to query the Github GraphQL API.
"""


from typing import Dict, Union, Any
import fnc
from requests import Session
from requests.structures import CaseInsensitiveDict


class GithubGraphQL:
    """ A lightweight Github GraphQL API client.

    In order to properly close the session, use this class as a context manager:

        with GithubGraphQL(token="<GITHUB_API_TOKEN>") as g:
            g.query_from_file(filename="query.graphql", variables=None)

    or call the close() method manually

        g = GithubGraphQL(token="<GITHUB_API_TOKEN>")
        g.close()
    """

    def __init__(
            self,
            token: str = "",
            endpoint: str = "https://api.github.com/graphql",
            **kwargs):
        """
        Creates a session with the given bearer `token` and `endpoint`.

        Args:
            token (str): Your personal access token in Github (see https://github.com/settings/tokens)
            endpoint (str): The endpoint to query GraphQL from
            **kwargs: key-value pairs (e.g. {raise_on_error=True})
        """
        self.__endpoint = endpoint
        self.__token = token
        self.__encoding = "utf-8"
        self.__raise_on_error = kwargs.get('raise_on_error', None)
        self.__session = Session()
        self.__session.headers.update({
            "Authorization": f"Bearer {self.token}",
            # See #
            # https://github.blog/2021-11-16-graphql-global-id-migration-update/
            'X-Github-Next-Global-ID': '1'
        })

    @property
    def token(self) -> str:
        """ Returns the bearer token. """
        return self.__token

    @property
    def encoding(self) -> str:
        """ Returns the default encoding to be expected from query files. """
        return self.__encoding

    def query_from_file(self,
                        filename: str,
                        variables: Dict[str,
                                        Union[str,
                                              int]] = None,
                        **kwargs) -> Any:
        """
        Read the query from the given file and execute it with the variables
        applied. If not requested otherwise the plain result is returned. If you
        want to raise an exception in case of an error you can set
        `raise_on_error` to `True`.

        See also:
        https://docs.github.com/en/graphql/guides/forming-calls-with-graphql
        https://docs.github.com/en/graphql/overview/explorer

        Args:
            filename (str): The filename of the query file.
            variables (dict): The variables to be applied to the query.
            **kwargs: key-value pairs (e.g. {raise_on_error=True})
        """
        with open(file=filename, mode="r", encoding=self.encoding) as file_handle:
            query = file_handle.read()
        return self.query(query, variables, **kwargs)

    def __enter__(self):
        return self

    @property
    def session_headers(self) -> CaseInsensitiveDict:
        """ Returns the HTTP headers used for the session. """
        return self.__session.headers

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        """ Closes the session. """
        self.__session.close()

    def query(self,
              query: str,
              variables: Dict[str,
                              Union[str,
                                    int]] = None,
              **kwargs) -> Dict:
        """
        Execute the query with the variables applied. If not requested otherwise
        the plain result is returned. If you want to raise an exception in case
        of an error you can set `raise_on_error` to `True`.

        Args:
            query (str): The GraphQL query.
            variables (dict): The variables to be applied to the query.
            **kwargs: key-value pairs (e.g. {raise_on_error=True})

        Raises:
            RuntimeError: In case of an error when `raise` is `True`.

        Returns:
            Result: The result of the query. Inspect the result for errors!
        """
        req = self.__session.post(
            url=self.__endpoint,
            json={"query": query, "variables": variables})
        req.raise_for_status()
        res = dict(req.json())
        if "errors" in res and kwargs.get('raise_on_error', self.__raise_on_error):
            raise RuntimeError(str(fnc.get("errors[0].message", res, default="GraphQL Error")))
        return res
