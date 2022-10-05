"""
ghgql provides a thin wrapper library to query the Github GraphQL API.
"""
from importlib.metadata import version
__version__ = version("ghgql")

from .ghgql import GithubGraphQL
