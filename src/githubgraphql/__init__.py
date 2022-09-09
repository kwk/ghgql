# read version from installed package
from importlib.metadata import version
__version__ = version("githubgraphql")

from .result import Result
from .githubgraphql import GithubGraphQL