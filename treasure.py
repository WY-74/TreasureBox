import jsonpath
import requests
from .utils import generate_jsonschema, validate_jsonschema, execute_sql
from requests import Response
from typing import Dict, Any, List
from xml.etree import ElementTree
from xml.etree.ElementTree import Element


class BaseRequests:
    def __init__(self, driver: None):
        self.token: Dict[str, str] = {}
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

    def assert_json_response(
        self, response: Response, want: Any, jsonpath: str = "$", has: bool = True, overall: bool = False
    ):
        root = response.json()

        if overall:
            try:
                assert want == root
                return
            except Exception:
                raise Exception(f"The respoonse(json): {root}")

        items: List[Any] = self._get_items_by_jsonpath(root, jsonpath)
        if has:
            assert want in items
            return
        assert want not in items

    def assert_xml_response(self, response: Response, xpath: str, want: str):
        root: Element = ElementTree.fromstring(response.text)
        items: List[Any] = self._get_items_by_xpath(root, xpath)
        items_text = [item.text for item in items]
        assert want in items_text

    def assert_by_jsonschema(self, response: Response, generate: bool = True, file_path: str | None = None):
        response = response.json()
        if generate:
            schema = generate_jsonschema(response, file_path)
        assert validate_jsonschema(response, schema, file_path)

    def assert_from_db(self, sql: str, want: str | None = None, complete_match: bool = False):
        if complete_match and want == None:
            raise Exception("[assert_from_db]: We need to pass in the 'want' or change the 'assert_mothod' to False!")

        result = execute_sql(sql)
        if not complete_match:
            assert result != None
            return
        assert result == want

    def get_text_from_root(self, response: Response, jsonpath: str):
        root = response.json()
        text = self._get_items_by_jsonpath(root, jsonpath)[0]
        return text

    def get_token(self, response: Response, jsonpath: str, name: str):
        token = self.get_text_from_root(response, jsonpath)
        self.token[name] = token

    def get_cookies(self, response: Response):
        cookies = response.cookies
        for cookie in cookies:
            self.cookies[cookie.name] = cookie.value
