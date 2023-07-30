# BaseRequests
## **http_methods**
A basic request method with a default timeout of 5 seconds.

required params:
- method: str
- url: str

`method`: method for the new Request object: GET, OPTIONS, HEAD, POST, PUT, PATCH, or DELETE.

`url`: URL for the new Request object.

The following params can be used as needed(For specific meanings, please refer to: [Main Interface](https://requests.readthedocs.io/en/latest/api/))：
- params
- json
- headers
- cookies
- files
- auth
- timeout
- allow_redirects
- proxies
- verify
- stream
- cert

## **http_with_proxy**
Request with proxy, we can capture requests by listening.
- method: str
- url: str
- host: str
- port: str

## **assert_status_code**
Verify response status code, default response is considered to be 200.
- response: Response
- e_status: int

## **assert_response**
This function can be used when we want to verify the response body(json/xml) with expr(jsonpath/xpath).

**Notes: When the Json/XML has been parsed correctly by the JsonPath/XPATH, the result is returned as a list(We'll call it EPL ). Remember that this affects the way we set the incoming parameters.**
- response: Response
- want: Any
- jsonpath: str
- has: bool

`response`: A new response

`want`: Expected value.

`expr`: JsonPath/XPATH statement for parsing Json/XML data. Since most of the response data is Json, the default value of our `expr` is `$.`.

`has`: By default, the function determines that the expected value is in the EPL. We can set `has=False` to verify that the expected value is not in the EPL

## **assert_from_db**
This method can be used when we occasionally assert the database (which is not recommended, and is a dangerous thing to do when working with databases).
- sql: str
- want: str|None
- complete_match: bool

## **assert_by_jsonschema**
Type/structure validation of data (focusing only on the data type and the overall structure) you can use this function, the function will be based on the response to generate a JsonSchema, the use of JsonSchema for the data assertions
- response: Response
- generate: bool
- file_path: str|None

`generate`: `True` by default, which means that each call to this method will generate a new JsonSchema based on the response

`file_path`: `None` by default, which means that if we pass a path to a file, the method will be called with the JsonSchema saved/read to/from the file. We can use these two parameters in different ways:
| generate | file_path | descriptions |
| -------- | -------- | -------- |
| True | str | Generate a new JsonSchema and store it in a file, validate it by reading the contents of the file. |
| True | None | Generate a new JsonSchema and validate it directly, without the process of storing and reading files. |
| False | str | Do not generate a new JsonSchema, directly utilize the JsonSchema in the path file for validation. |
| False | None | Error: No Json Schema is generated and no file is passed in |

## **assert_by_yamlmap**
During the course of the project, we usually want to manage the data in one place. `assert_by_yamlmap`is used to unify the processing of fine json data validation.
- response: Response
- path: str

How to use:
1. First we need to create a new yaml file for settings and data storage
2. The following format needs to be adhered to in the yaml file:
    ```yaml
    settings:
    # settings: The content under settings is the setup information.
        add_goods:  # Function name for calling the assert_by_yamlmap
            overall: True
            # We can set the 'overall', 'jsonpath', 'has' for assertions as needed.
            # overall: exact match validation with response results(Highest priority, 'jsonpath' and 'has' will be disabled if set to True.)
            # jsonpath: The jsonpath statement extracts the content of the response and then validates it.
            # has: Changing the validation method
                # True(default): existent
                # False: non-existent
        add_cart:
            jsonpath: "$.errmsg"
        delete_goods:
            overall: True

    assert:
    # assert: The content under assert is an assertion message.
        add_goods:  # Function name for calling the assert_by_yamlmap
            errno: 0
            errmsg: 成功
            # expected value
        add_cart: "成功"
        delete_goods:
            errno: 0
            errmsg: 成功
    ```

## **get_text_from_root**
Get the desired text message in the response result by JsonPath
- response: Response
- jsonpath

## **get_token**
You can use this method to obtain and save the token in the response, and directly call `self.token[]` when using the token in the future.

But we need to make sure that the JsonPath is correct during the fetching process
- response: Response
- jsonpath: str
- name : str

## **get_cookies**
You can use this method to get and save the cookies in the response, and then call `self.cookies` when you want to use the cookies later.
- response: Response
