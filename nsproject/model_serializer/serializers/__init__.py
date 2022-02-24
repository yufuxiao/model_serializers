import json
import datetime
import uuid
import decimal

from collections import defaultdict

from django.db.models import QuerySet, Model
from django.core.paginator import Page as PaginatorPage
from django.utils.timezone import is_aware, make_naive

from model_serializer.serializers.model import LazySerializeProfile
from model_serializer.serializers.model import serialize_model

__all__ = [
    'LazySerializeProfile',
    'serialize_model',
    'JSONEncoder',
    'json_dumps',
]


def serialize_datetime(t=None, format=None):
    if t is None:
        return t

    if isinstance(t, datetime.datetime):
        if is_aware(t):
            t = make_naive(t)
        if not format:
            format = '%Y-%m-%d %H:%M:%S'
        return t.strftime(format)
    elif isinstance(t, datetime.date):
        if not format:
            format = '%Y-%m-%d'
        return t.strftime(format)
    elif isinstance(t, datetime.time):
        if not format:
            format = '%H:%M:%S'
        return t.strftime(format)
    else:
        raise TypeError('"t" is not valid datetime type.')


class JSONEncoder(json.JSONEncoder):
    """
    扩展默认的 json.JSONEncoder，支持序列化 Model，以及一些我们内部达成一致的通用数据类型。
    """

    def __init__(self, *, serialize_profile=None, **kwargs):
        super().__init__(**kwargs)
        self.serialize_profile = serialize_profile or defaultdict(dict)

    def default(self, o):
        if isinstance(o, (datetime.date, datetime.datetime, datetime.time)):
            return serialize_datetime(o)
        elif isinstance(o, (decimal.Decimal, uuid.UUID)):
            return str(o)
        elif isinstance(o, (PaginatorPage, QuerySet)):
            return list(o)
        elif isinstance(o, Model):
            return serialize_model(o, **self.serialize_profile[o.__class__])
        elif hasattr(o, 'Serializer'):
            return serialize_model(0, **self.serialize_profile[o.__class__])
        else:
            return super().default(o)


def json_dumps(value, *, serialize_profile=None, **kwargs):
    return json.dumps(
        value,
        cls=JSONEncoder,
        serialize_profile=serialize_profile,
        **kwargs,
    )
