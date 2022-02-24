from django.core.paginator import Paginator


def get_pagination(request, queryset, *, page=None, page_size=None, max_page_size=None, max_records=None):
    """
    :param request: HttpRequest 对象。
    :param queryset: QuerySet 或者任意可迭代对象
    :param page: 页码，如果提供了该参数，则使用指定值，否则使用 querystring 中page 的值，默认 1
    :param page_size: 每页展示的数量，如果提供了该参数，则使用指定值，否则使用 querystring 中 page_size 的值，默认为 10。
    :param max_page_size: 每页展示的最大数量，默认为 100
    :param max_records: 最多返回多少条记录数，防止恶意获取数据，默认 1000

    返回一个三元组：page，paginator，pagination
    page: django.core.paginator.Page 对象
    paginator: django.core.paginator.paginator 对象
    pagination: 一个字典，字段格式如下：
      {
        'total': int, 条目总数
        'page': int, 当前页码（页码从1开始）
        'page_size': int, 每页条目数量
        'last_page': int, 最后一页的页码
        'form': int, 当前页第一个元素的编号（编号从1开始，下同）
        'to': int, 当前页最后一个元素的编号
      }
    """
    max_page_size = max_page_size or 100
    max_records = max_records or 1000

    if page_size and page_size > max_page_size:
        raise ValueError(f"超过了最大允许的值{max_page_size},如有需求请提供 max_page_size 参数")

    if max_page_size > max_records > 0:
        raise ValueError(f"max_page_size 不能大于 max_records")

    if page is None:
        page = get_int(request, "page", 1)
    if page_size is None:
        page_size = get_int(request, "page_size", 10)
        if page_size > max_page_size:
            page_size = max_page_size
    if max_records is None:
        max_records = 1000

    if page * page_size > max_records > 0:
        page = max_records // page_size

    paginator = Paginator(queryset, page_size)
    paginator_page = paginator.get_page(page)
    pagination = dict(
        total=paginator.count,
        page=paginator_page.number,
        page_size=page_size,
        last_page=paginator.num_pages,
        form=paginator_page.start_index(),
        to=paginator_page.end_index(),
    )
    return paginator_page, paginator, pagination


def get_int(request, name, default=None, raise_on_value_error=False):
    """获取一个 int 类型的字符串参数"""
    value = request.GET.get(name)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError as e:
        if raise_on_value_error:
            raise e
        return default