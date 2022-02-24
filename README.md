### model_serializers
  提供两种类型的序列化方案
   1. model 对象
   2. queryset

### projects tree

    │  ├─response
    │  │  └─api        // 构造一个 api 响应，如：ok、bad_request、page 等
    │  │  └─base       // 封装 api 响应中的 code 值
    │  │  └─pagination // 一个分页结构
    │  └─serializers
    │  │  └─__init__   // 扩展 json.JSONEncoder，支持序列化 Model
    │  │  └─model      // Model 序列化主逻辑

### usage
    Model 对象：
        tasks = Tasks.objects.get(id=5)
        return api.ok(tasks, group="xx")

    QuerySet:
        qs = Tasks.objects.all()
        return api.page(request, qs, group="xx")

### django version
  Django3.1

### python version
  Python3.7

### database
  pip install migrate
