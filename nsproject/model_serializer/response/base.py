from enum import unique, IntEnum


@unique
class Code(IntEnum):
    """
    这里使用的 Code 是 API 响应中的 code 值，原则上：
    * 除 OK 以外，其他含义、代码与 HTTP 相同
    * 对于 BAD_REQUEST，Code 可以自定义
    """
    OK = 0

    PERMANENT_REDIRECT = 301
    TEMPORARY_REDIRECT = 302
    SEE_OTHER = 303

    BAD_REQUEST = 400
    NOT_AUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405

    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501


class ResponseException(Exception):
    """
    为了方便在任何地方返回 HTTP 响应，我们可以使用 raise 抛出该异常
    """
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)