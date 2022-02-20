import warnings
import inspect

from django.db.models import Model
from django.core.exceptions import FieldDoesNotExist


class LazySerializeProfile:
    """
    用于简化版的序列化方式: api.ok(data, fields=xx, group=xx)
    """

    def __init__(self, fields=None, group=None, **serialize_kwargs):
        self.fields = fields
        self.group = group
        self.serialize_kwargs = serialize_kwargs
        # 当第一次被使用时，会记录其 model_class
        self.model_class = None
        self.mapping = dict()

    def __getitem__(self, model_class):
        if self.model_class is None:
            self.model_class = model_class
            self.mapping[model_class] = dict(fields=self.fields, group=self.group)

        if model_class in self.mapping:
            return {**self.mapping[model_class], **self.serialize_kwargs}
        else:
            return {}


def serialize_model(model: Model, *, fields=None, group=None, **kwargs):
    if hasattr(model.__class__, 'Serializer'):
        model._serializer = make_model_serializer(model.__class__)  # type: ignore
        return model._serializer.serialize(model, fields=fields, group=group, **kwargs)  # type: ignore

    # 对于既没有定义 Serializer，也没有 serialize() 的情况，我们添加一个默认的 Serialize
    class DefaultSerializer:
        INCLUDE_PRIMARY_KEY = True
        INCLUDE_TIMESTAMP = False

    warnings.warn(
        f'{model.__class__.__name__} 没有定义序列化方式，将默认只序列化 primary_key 字段'
    )
    model._serializer = make_model_serializer(model.__class__, DefaultSerializer)
    return model._serializer.serialize(model, fields=None, group=None, **kwargs)


def make_model_serializer(ModelClass, SerializerClass=None):
    Serializer = SerializerClass or ModelClass.Serializer

    if hasattr(Serializer, "_instance"):
        return Serializer._instance

    if hasattr(ModelClass, "serialize"):
        warnings.warn(
            f"{ModelClass.__name__} 同时定义了 Serializer 和 serialize()，serialize() 函数将被忽略"
        )

    if hasattr(Serializer, "serialize"):
        raise ValueError(
            '请勿在 Serializer 类上定义 serialize 函数或属性：'
            f'{ModelClass.__name__}.Serializer'
        )

    class CompiledSerializer(Serializer):
        def __init__(self):
            cls = self.__class__

            if not hasattr(cls, 'default_fields'):
                cls.default_fields = []
            if not hasattr(cls, 'optional_fields'):
                cls.optional_fields = []
            if not hasattr(cls, 'field_groups'):
                cls.field_groups = {}

            # 如果 INCLUDE_PRIMARY_KEY 为 True，则自动加入 pk
            if getattr(cls, 'INCLUDE_PRIMARY_KEY', True):
                cls.default_fields.append(ModelClass._meta.pk.name)

            # 如果 INCLUDE_TIMESTAMP 为 True，则自动加入时间戳字段
            if getattr(cls, 'INCLUDE_TIMESTAMP', True):
                # 分两种情况，一种是用户没有提供 TIMESTAMP_FIELDS，则自动检测是否存在
                # created_at, updated_at，如果不存在，不会报错。
                # 另一种情况是用户提供了 TIMESTAMP_FIELDS，则相应的字段必须存在。
                if hasattr(cls, 'TIMESTAMP_FIELDS'):
                    cls.default_fields.extend(cls.TIMESTAMP_FIELDS)
                    TIMESTAMP_FIELDS_AUTO = []
                else:
                    TIMESTAMP_FIELDS_AUTO = ['created_at', 'updated_at']
            else:
                TIMESTAMP_FIELDS_AUTO = []

            # 计算所有可能的字段
            fields = set()
            fields.update(cls.default_fields)
            fields.update(cls.optional_fields)
            for v in cls.field_groups.values():
                fields.update(v)

            # 检查这些字段是否存在，并生成一个字典，key 为字段值，value 为 serialize() 函数
            cls.fields = dict()

            def attribute_serializer(attr):
                def getter(obj, **kwargs):
                    return getattr(obj, attr)
                return getter

            for field in fields:
                # 有些情况下，一个字段需要根据不同场合使用不同的序列化方式，我们可以为其指定一个函数，
                # 函数名格式没有限制，但是建议为 serialize_{field}_{variant}()
                # 字段名声明格式为：{field}@{method}
                if '@' in field:
                    raw_field, method_name = field.split('@', 1)
                    if not hasattr(ModelClass, method_name):
                        raise ValueError(
                            f'字段 {field} 没有实现相应的序列化方法：{method_name}'
                        )
                    cls.fields[field] = self._create_method_serializer(ModelClass, method_name)
                    continue

                # 如果存在 serialize_field() 方法，则使用该方法
                if hasattr(ModelClass, f'serialize_{field}'):
                    method_name = f'serialize_{field}'
                    cls.fields[field] = self._create_method_serializer(ModelClass, method_name)
                    continue

                try:
                    f = ModelClass._meta.get_field(field)
                    if f.many_to_many or f.one_to_many:
                        # ManyToManyField, ForeignKey 的反向引用，需要使用 .all() 来访问
                        cls.fields[field] = self._create_many_relation_serializer(field)
                    else:
                        # 其他则直接返回值本身
                        cls.fields[field] = self._create_attribute_serializer(field)
                    continue
                except FieldDoesNotExist:
                    pass

                if hasattr(ModelClass, field):
                    # 否则看 ModelClass 上是否存在相应的 property
                    cls.fields[field] = self._create_attribute_serializer(field)
                    continue

                raise Exception(f'{ModelClass.__name__} 无法序列化该字段：{field}')

            for field in TIMESTAMP_FIELDS_AUTO:
                # 对于时间戳字段，也允许自定义 serialize_{field}()，以便在特定场景下使用自定义的格式
                if hasattr(Model, f'serialize_{field}'):
                    method_name = f'serialize_{field}'
                    cls.default_fields.append(field)
                    cls.fields[field] = self._create_method_serializer(Model, method_name)

                elif hasattr(ModelClass, field):
                    cls.default_fields.append(field)
                    cls.fields[field] = self._create_attribute_serializer(field)

        def _create_method_serializer(self, Model, method_name):
            method = getattr(Model, method_name)
            parameters = inspect.signature(method).parameters

            keyword_args = []
            takes_var_args = False

            for name, param in parameters.items():
                if name == 'self':
                    continue
                if param.kind == param.POSITIONAL_ONLY or param.kind == param.VAR_POSITIONAL:
                    raise ValueError(
                        '序列化函数不允许接受 positional only 和 var positional 参数：'
                        f'{Model.__name__}.{method_name}(): {name}'
                    )
                if param.kind == param.VAR_KEYWORD:
                    takes_var_args = True
                    continue
                keyword_args.append(name)

            def serializer(instance, **kwargs):
                if takes_var_args:
                    return method(instance, **kwargs)
                else:
                    args = {key: kwargs.pop(key) for key in keyword_args if key in kwargs}
                    return method(instance, **args)

            return serializer

        def _create_attribute_serializer(self, attr_name):
            def serializer(instance, **kwargs):
                return getattr(instance, attr_name)

            return serializer

        def _create_many_relation_serializer(self, field_name):
            def serializer(instance, **kwargs):
                return getattr(instance, field_name).all()

            return serializer

        def serialize(self, instance: Model, fields=None, group=None, **kwargs):
            # serialize_fields 为实际需要返回的字段集合
            # 包括：
            #   * Serializer.default_fields 指定的字段
            #   * 参数 fields 指定的字段
            #   * 参数 groups 指定的字段
            serialize_fields = set(self.default_fields)

            if fields:
                for field in fields:
                    if field not in self.fields:
                        raise ValueError(f'指定的 field 不存在或不允许序列化：{field}')
                    serialize_fields.add(field)

            if group:
                if group not in self.field_groups:
                    raise ValueError(f'指定的 group 不存在：{group}')
                serialize_fields.update(self.field_groups[group])

            result = {}
            for field in serialize_fields:
                data = self.fields[field](instance, **kwargs)

                if '@' in field:
                    raw_field, _ = field.split('@', 1)
                    result[raw_field] = data
                else:
                    result[field] = data

            return result

    Serializer._instance = CompiledSerializer()
    return Serializer._instance
