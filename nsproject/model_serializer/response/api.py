from django.http import JsonResponse

from model_serializer.response.base import ResponseException
from model_serializer.response.base import Code
from model_serializer.response.pagination import get_pagination
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

    data 必须是这几种类型：
    * model 实例
    * model 实例列表（必须是同一种 Model）
    * QuerySet
    * paginator.Page
    """
    if code is None:
        code = Code.OK

    if fields or group:
        profile = LazySerializeProfile(fields=fields, group=group, **kwargs)

    return ApiResponse(
        status=200, code=code, message=message, data=data, pagination=pagination,
        serialize_profile=profile,
    )


def page(request, queryset, *, page=None, page_size=None, max_page_size=None, max_records=None, **kwargs):
    """
    构造一个分页响应

    :param request: Django HttpRequest 对象。
    :param queryset: QuerySet 或者任意可迭代对象（iterator）。
    :param message: API 响应中 message 的内容。
    :param page: 如果未指定，将自动从 request 中判断，如果指定了，则强制返回该页。
      一般用于某些输入建议的场景，只返回第一页的内容。
    :param page_size: 如果未指定，将自动从 request 中判断，如果指定了，则强制使用该大小。
      一般用于某些需要强制指定页码大小的场景。
    :param max_records: 最多返回多少记录数，默认为 1000，主要用于防止爬虫。
      若不需要限制（如管理后台接口），请赋值为 -1。
    :param **serialize_options: model 序列化时，传递给 serialize() 函数的参数。
    """
    paginator_page, _, pagination = get_pagination(
        request,
        queryset,
        page=page,
        page_size=page_size,
        max_page_size=max_page_size,
        max_records=max_records,
    )

    return ok(data=paginator_page, pagination=pagination, **kwargs)