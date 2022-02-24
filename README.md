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
    class Tasks(models.Model):
        """任务"""
        task_topo = models.OneToOneField("TasksTopo", related_name="tasks", on_delete=models.DO_NOTHING, null=True)
        task_name = models.IntegerField("任务名称")
        test_list = JSONField()
        test_char = models.TextField()

        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        
        # 也允许自定义 serialize_{field}() 开头的序列化方案
        def serialize_app(self):
            return "xxxx"

        class Serializer:
            default_fields = ["task_name", "test_list", "test_char"]
            field_groups = {
                "list": ["task_topo", "task_name", "test_list", "test_char", "app", "report"]
            }
            
        注意：id、 created_at、updated_at 默认序列化，不需要加入序列化组
 
            
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
