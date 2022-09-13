"""
ghgql.result
~~~~~~~~~~~~~~~~~~~~

A thin layer around the "dict" result of a Github GraphQL operation.
"""

from typing import Dict, Any
import json


class Result(dict):
    """
    This is a dict that has a few helper functions to make it easier to
    work with the data returned from the Github GraphQL API.
    """

    def get(self, key: str, **kwargs) -> Any:
        """
        Helper function to get data from a deeply nested dict.

        This syntax:

            a = result.get(key="status.item.id", default=42)

        is roughly equivalent to:

            result["status"]["item"]["id"]

        plus that it handles if a key doesn't exist and a default value should
        be used

        Args:
            key (str): dot-separated key to access
            **kwargs: key-value pairs (e.g. {default=42})

        Raises:
            RuntimeError: If `errors` are present or if data is empty and no
                          `default` is given.
            KeyError: If `key` is invalid (e.g. `"foo..bar"`) and no `default`
                      is given. Or if key cannot be resolved and no `default`
                      is given.
        """
        if self.errors is not None:
            raise RuntimeError("errors are present")

        default = kwargs.get('default', None)
        default_is_given = 'default' in kwargs

        if self.data is None:
            if default_is_given:
                return default
            raise RuntimeError("data is None and no default is given")

        keys = key.split(".")

        current_value = self.data
        for k in keys:
            if (k := k.strip()) == '':
                raise KeyError(f"invalid key \"{key}\" because of empty element")
            if isinstance(current_value, str) and current_value != "null":
                current_value = json.loads(current_value)
            if current_value is not None and k in current_value:
                current_value = current_value[k]
            else:
                if not default_is_given:
                    raise KeyError(f"key \"{key}\" is not found and default is not present")
                return default
        return current_value

    @property
    def data(self) -> Dict:
        """
        This returns the data dict.
        """
        if "data" in self:
            return self["data"]
        return None

    @property
    def errors(self) -> Any:
        """
        This returns the errors dict.
        """
        if "errors" in self:
            return self["errors"]
        return None
