import jsonpath
import requests
from .utils import generate_jsonschema, validate_jsonschema, execute_sql
from requests import Response
from typing import Dict, Any, List
from xml.etree import ElementTree
from xml.etree.ElementTree import Element


class BaseRequests:
    def __init__(self, driver: None):
        self.token = ""
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
        self, response: Response, want: List[Any], expr: str = "$", overall: bool = False, has_no: bool = False
    ):
        root = response.json()

        if overall:
            assert want == root

        items: List[Any] = self._get_items_by_jsonpath(root, expr)
        if has_no:
            assert want not in items
        assert want in items

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
        assert result == want

    def get_token(self, response: Response, jsonpath: str):
        root = response.json()
        items = self._get_items_by_jsonpath(root, jsonpath)
        self.token = items[0]

    def get_cookies(self, response: Response):
        cookies = response.cookies
        for cookie in cookies:
            self.cookies[cookie.name] = cookie.value
