import jsonpath
import requests
from .utils import generate_jsonschema, validate_jsonschema, execute_sql
from dataclasses import dataclass
from io import BufferedReader
from requests import Response
from typing import Dict, Any, List
from xml.etree import ElementTree
from xml.etree.ElementTree import Element


@dataclass
class Methods:
    get: str = "get"
    post: str = "post"
    put: str = "put"
    delete: str = "delete"


@dataclass
class TimeOut:
    fast: int = 3
    normal: int = 10


class BaseRequests:
    ParamsType = Dict[str, str | int] | None

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

    def http_methods(
        self,
        method: str,
        url: str,
        params: ParamsType = None,
        headers: Dict[str, str] | None = None,
        json_params: ParamsType = None,
        data_params: ParamsType = None,
        cookies: Dict[str, str] | None = None,
        timeout: int = TimeOut.fast,
    ) -> Response:
        return requests.request(
            method,
            url,
            params=params,
            headers=headers,
            json=json_params,
            data=data_params,
            cookies=cookies,
            timeout=timeout,
        )

    def http_with_proxy(
        self, method: str, url: str, http: str = "127.0.0.1:8888", https: str | None = None, **kwargs
    ) -> Response:
        https = http if https == None else https
        proxies = {"http": f"http://{http}", "https": f"http://{https}"}
        return requests.request(method, url, proxies=proxies, verify=False, **kwargs)

    def http_with_file(self, url: str, path: str, name: str = "name by tframe"):
        files: Dict[str, BufferedReader] = {name: open(path, "rb")}
        return requests.request(Methods.post, url, files=files)

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

    def get_token(self, response: Response, expr: str):
        root = response.json()
        items = self._get_items_by_jsonpath(root, expr)
        if not items:
            raise Exception("Get token JsonPath did not match the content")

        self.token = items[0]

    def get_cookies(self, response: Response):
        cookies = response.cookies
        for cookie in cookies:
            self.cookies[cookie.name] = cookie.value
