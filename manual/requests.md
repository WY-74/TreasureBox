# Requests环境
## **http_methods**
一个最为基础的请求方法. 为了避免手动输入可能造成的错误, 我们已经有了预设的method: `utils/data_sets.py::Method`, 因此当我们使用 `http_methods` 方法时可以通过调用 `Method` 传入 `method` 参数.

timeout我们也提供了预设的值: `utils/data_sets.py::TimeOut`, 且默认超时为3s, 若想要调整超时时间请通过调用 `TimeOut` 传入 `timeout` 参数.
- method: str
- url: str
- params: Dict[str, str|int] | None
- headers: Dict[str, str] | None
- json_params: Any
- data_params: Dict[str, str | int] | None
- cookies: Dict[str, str]
- timeout: int

## **http_with_proxy**
为请求增加代理, `https`默认与`http`相同, `http`默认为 `127.0.0.1:8888`
- method: str
- url: str
- http: str
- https: str|None

## **http_with_file**
一个处理上传文件接口的方法
- url: str
- path: str
- name: str

## **assert_status_code**
一个用于断言响应状态码的函数, 默认验证响应码为200
- response: Response
- e_status: int

## **assert_json_response**
当我们希望断言响应数据，并且响应的数据是json结构时可以使用此函数. 

Json数据可能会存在嵌套的情况, 因此我们使用该函数的过程中需要借助JsonPath尽可能的解析Json, 我们提供了 [JsonPath](https://github.com/WY-74/fragmented-notes/blob/master/base/006.md) 相关文章来帮助您熟悉JsonPath. `has_no` 会控制我们验证的方式, 默认情况下我们验证的是期望结果存在于Json解析后的列表中, 当设置 `has_no` 为 `True` 之后将验证期望结果不在Json解析后的列表中

`overall` 默认是关闭的状态, 若您想开启请设置为`True`, `overall`开启后的JsonPath将会失效, 函数将会把您的期望结果和实际的响应结果进行完全匹配的验证
- response: Response
- want: Any
- expr: str
- overall: bool
- has_no: bool

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

## **get_token**
可以使用此方法获取并保存响应信息中的token, 后续使用token时直接调用 `self.token` 即可
- response: Response
- expr: str

## **get_cookies**
可以使用此方法获取并保存响应中的cookies, 后续使用cookies时直接调用 `self.cookies` 即可
- response: Response
