"""
ghgql provides a thin wrapper library to query the Github GraphQL API.
"""
from importlib.metadata import version
__version__ = version("ghgql")

from .result import Result
from .ghgql import GithubGraphQL
