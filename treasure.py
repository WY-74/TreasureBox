import inspect
import jsonpath
import requests
from .utils import generate_jsonschema, validate_jsonschema, execute_sql, load_yaml_map
from json import JSONDecodeError
from requests import Response
from typing import Dict, Any, List
from xml.etree import ElementTree
from xml.etree.ElementTree import Element


class BaseRequests:
    def __init__(self, driver: None):
        self.token: str = ""
        self.cookies: Dict[str, Any] = {}

    def _get_items_by_jsonpath(self, obj, expr: str):
        items: List[Any] | bool = jsonpath.jsonpath(obj, expr)
        if not items:
            raise Exception("JsonPath did not match the content")
        return items

    def http_methods(self, method: str, url: str, **kwargs) -> Response:
        if not kwargs.get("timeout"):
            kwargs["timeout"] = 5
        return requests.request(method, url, **kwargs)

    def assert_status_code(self, response: Response, want: int = 200):
        status = response.status_code
        assert status == want

    def assert_response(self, response: Response, want: Any, expr: str = "$..", has: bool = True):
        root = response.json()
        items = self._get_items_by_jsonpath(root, expr)

        try:
            if has:
                assert want in items
                return
            assert want not in items
        except Exception:
            raise Exception(f"response: {response.json()}\nitems: {items}")

    def assert_by_yamlmap(self, response: Response, path: str):
        caller_frame = inspect.stack()[1].frame
        caller_name = caller_frame.f_code.co_name
        raw = load_yaml_map(path)

        set = raw["settings"][caller_name]
        want = raw["assert"][caller_name]
        self.assert_response(response, want, **set)

    def get_text_from_root(self, response: Response, jsonpath: str):
        root = response.json()
        text = self._get_items_by_jsonpath(root, jsonpath)[0]
        return text

    def get_token(self, response: Response, jsonpath: str):
        return self.get_text_from_root(response, jsonpath)

    def get_cookies(self, response: Response):
        cookies = response.cookies
        for cookie in cookies:
            self.cookies[cookie.name] = cookie.value
