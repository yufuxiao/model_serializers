from django.http import JsonResponse

from model_serializer.response.base import ResponseException
from model_serializer.response.base import Code
from model_serializer.serializers import JSONEncoder
from model_serializer.serializers import LazySerializeProfile


class ApiResponse(JsonResponse, ResponseException):

    def __init__(self,
                 *,
                 status: int = 200,
                 code: Code = Code.OK,
                 message: str = "",
                 data=None,
                 serialize_profile=None,
                 pagination=None,
                 ):
        content = dict(code=code, message=message, data=data)
        if pagination is not None:
            content["pagination"] = pagination

        JsonResponse.__init__(self,
                              status=status, data=content,
                              encoder=JSONEncoder, safe=False,
                              json_dumps_params=dict(serialize_profile=serialize_profile),
                              )
        ResponseException.__init__(self, f'<ApiResponse status={status} code={code} message="{message}">')

def ok(data=None,
       *,
       message='ok', code=None, pagination=None,
       profile=None, fields=None, group=None,
       **kwargs
       ):
    """
    构造一个 OK 响应

    :param data: API 响应中 data 的内容，支持任何可以 JSON 序列化的数据类型，具体见 `ApiResponse` 中的说明。
    :param message: API 响应中 message 的内容。
    :param code: API 响应中 code 的值，默认为 Code.OK。原则上不应该使用其他值。
    :param pagination: 如果是分页响应，可以提供 pagination 对象。
    :param profile: 序列化方案配置。
    :param fields: 需要序列化的字段。
    :param group: 需要序列化的字段组。
    :param **kwargs: 序列化时需要额外使用的参数。
    """
    if code is None:
        code = Code.OK

    if fields or group:
        profile = LazySerializeProfile(fields=fields, group=group, **kwargs)

    return ApiResponse(
        status=200, code=code, message=message, data=data, pagination=pagination,
        serialize_profile=profile,
    )
