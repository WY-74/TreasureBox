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

    def _get_items_by_xpath(self, obj: Element, expr: str):
        items: List[Any] = obj.findall(f".{expr}")
        if not items:
            raise Exception("Xpath did not match the content")
        return items

    def http_methods(self, method: str, url: str, **kwargs) -> Response:
        if not kwargs.get("timeout"):
            kwargs["timeout"] = 5
        return requests.request(method, url, **kwargs)

    def http_with_proxy(self, method: str, url: str, host: str, port: str, **kwargs) -> Response:
        http: str = f"http://{host}:{port}"
        https: str = f"https://{host}:{port}"
        proxies = {"http": http, "https": https}
        return self.http_methods(method, url, proxies=proxies, verify=False, **kwargs)

    def assert_status_code(self, response: Response, e_status: int = 200):
        status = response.status_code
        assert status == e_status

    def assert_response(self, response: Response, want: Any, expr: str = "$..", has: bool = True):
        try:
            root = response.json()
            response_type = "json"
        except JSONDecodeError:
            # Means that the response value is not in json format
            root = ElementTree.fromstring(response.text)
            response_type = "xml"

        if response_type == "json":
            items = self._get_items_by_jsonpath(root, expr)
        else:
            items = self._get_items_by_xpath(root, expr)
            items = [item.text for item in items]

        try:
            if has:
                assert want in items
                return
            assert want not in items
        except Exception:
            raise Exception(f"response: {response.json()}\nitems: {items}")

    def assert_from_db(self, sql: str, want: str | None = None, complete_match: bool = False):
        if complete_match and want == None:
            raise Exception("[assert_from_db]: We need to pass in the 'want' or change the 'assert_mothod' to False!")

        result = execute_sql(sql)
        if not complete_match:
            assert result != None
            return
        assert result == want

    def assert_by_jsonschema(self, response: Response, generate: bool = True, file_path: str | None = None):
        response = response.json()
        if generate:
            schema = generate_jsonschema(response, file_path)
        assert validate_jsonschema(response, schema, file_path)

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
