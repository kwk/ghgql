# read version from installed package
from importlib.metadata import version
__version__ = version("ghgql")

from .result import Result
from .ghgql import GithubGraphQL
