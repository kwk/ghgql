# ghgql

Thin wrapper for interacting with the [Github GraphQL API](https://docs.github.com/en/graphql).

## Status

[![Documentation Status](https://readthedocs.org/projects/ghgql/badge/?version=latest)](https://ghgql.readthedocs.io/en/latest/?badge=latest)
[![CodeQL](https://github.com/kwk/ghgql/actions/workflows/codeql.yml/badge.svg)](https://github.com/kwk/ghgql/actions/workflows/codeql.yml)
[![ci-cd](https://github.com/kwk/ghgql/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/kwk/ghgql/actions/workflows/ci-cd.yml)
[![codecov](https://codecov.io/gh/kwk/ghgql/branch/main/graph/badge.svg?token=ASSPTOL3JU)](https://codecov.io/gh/kwk/ghgql)
[![release](https://img.shields.io/github/release/kwk/ghgql.svg)](https://github.com/kwk/ghgql/releases)

## Documentation

Please find the documentation and usage examples here: https://ghgql.readthedocs.io/en/latest/

## Installation

```bash
$ pip install ghgql
```

## Usage

For a more in-depth example, take a look at [the example in the documentation](https://ghgql.readthedocs.io/en/latest/example.html). Here's a basic example.

```python
import os
import fnc
import ghgql

query = """
query ($searchQuery: String!) {
  search(query: $searchQuery, type: ISSUE, first: 1) {
    edges {
      node {
        ... on Issue {
          id
          number
          title
          url
        }
      }
    }
  }
}
"""

with ghgql.GithubGraphQL(token=os.getenv("GITHUB_TOKEN")) as ghapi:
    result = ghapi.query(query=query, variables={"searchQuery": "llvm/llvm-project"})
    print(fnc.get("search.edges", result))
```

Should output something like this:

```yaml
[{'node': {'id': 'I_kwDOHicqdc5RG-tC',
   'number': 16,
   'title': 'llvm/llvm-project',
   'url': 'https://github.com/KhushP786/open-sauced-goals/issues/16'}}]
```

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

### Commit message conventions and semantic versioniong (semver)

We use semantic versioning and [these commit message conventions](https://www.conventionalcommits.org/en/v1.0.0/)
can be used to automatically bump the version number and generate the changelog.

## License

`ghgql` was created by Konrad Kleine. It is licensed under the terms of the MIT license.

## Credits

This project was created with the help of [this python packaging documentation](https://py-pkgs.org/01-introduction).

`ghgql` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
