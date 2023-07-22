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

## **assert_json_response**
This function can be used when we want to verify the response body and the response data is in json format.

Json data is usually more complex, so we can parse json by JsonPath. 

**Notes: When the Json has been parsed correctly by the JsonPath, the result is returned as a list(We'll call it JPL ). Remember that this affects the way we set the incoming parameters.**
- response: Response
- want: Any
- jsonpath: str
- overall: bool
- has_no: bool

`response`: A new response

`want`: Expected value.

`jsonpath`: JsonPath statement for parsing Json data

`has`: By default, the function determines that the expected value is in the JPL. We can set `has=False` to verify that the expected value is not in the JPL

`overall`: We can set `overall=True`, which will bypass Jsonpath parsing and verify that the expected value is exactly the same as the response data.

## **assert_xml_response**
当响应返回的内容是XML时可以使用该方法验证. 目前我们提供的验证方法时匹配符合xpth的元素, 并将这些元素的文本信息存放到列表中, 判断我们期望的数据是否在列表中
- response: Response
- xpath: str
- want: str

## **assert_by_jsonschema**
当我们对大数据采用类型/结构验证时(只关注数据类型和整体结构)可以用此方法, 此方法会依据响应生成JsonSchema, 利用JsonSchema进行断言

`generate` 默认是T, 意味着每一次调用此方法都会依据响应生产新的JsonSchema; `file_path` 默认是None, 若我们传入一个路径调用此方法时会将JsonSchema存入/读取出文件. 我们可以利用这两个参数组合出不同的使用方法:
| generate | file_path | 描述 |
| -------- | -------- | -------- |
| True | str | 生成新的JsonSchema并存入文件, 验证时通过读取文件内容验证 |
| True | None | 生成新的JsonSchema并直接进行验证, 不进行存储和读取文件的过程 |
| False | str | 不生成新的JsonSchema, 直接利用路径文件中的JsonSchema进行验证 |
| False | None | 报错: No Json Schema is generated and no file is passed in |
- response: Response
- generate: bool
- file_path: str|None

## **assert_from_db**
我们偶尔会对数据库进行断言(不推荐这样的做法, 操作数据库时是危险的事情), 此时可以使用该方法.
- sql: str
- want: str|None
- complete_match: bool

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
可以使用此方法获取并保存响应中的cookies, 后续使用cookies时直接调用 `self.cookies` 即可
- response: Response
