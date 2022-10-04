"""
ghgql.ghgql
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This provides a simply class that can be used to query the Github GraphQL API.
"""


from typing import Dict, Union
from requests import Session
from requests.structures import CaseInsensitiveDict
from .result import Result


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
            endpoint: str = "https://api.github.com/graphql"):
        """ Creates a session with the given bearer `token` and `endpoint`. """
        self.__endpoint = endpoint
        self.__token = token
        self.__encoding = "utf-8"
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
                                              int]] = None) -> Result:
        """
        Read the query from the given file and execute it with the variables
        applied. An exception is raised if there's an error; otherwise the
        result data is returned.

        See also:
        https://docs.github.com/en/graphql/guides/forming-calls-with-graphql
        https://docs.github.com/en/graphql/overview/explorer

        Args:
            filename (str): The filename of the query file.
            variables (dict): The variables to be applied to the query.
        """
        with open(file=filename, mode="r", encoding=self.encoding) as file_handle:
            query = file_handle.read()
        return self.query(query, variables)

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
                                    int]] = None) -> Result:
        """
        Execute the query with the variables applied. An exception is raised if
        there's an error; otherwise the result data is returned.

        Args:
            query (str): The GraphQL query.
            variables (dict): The variables to be applied to the query.

        Returns:
            Result: The result of the query. Inspect the result for errors!
        """
        req = self.__session.post(
            url=self.__endpoint,
            json={"query": query, "variables": variables})
        req.raise_for_status()
        return Result(req.json())
