from django.db import models
from django.db.models import JSONField


class TasksTopo(models.Model):
    """任务拓扑"""
    bk_biz_id = models.IntegerField(verbose_name="业务id")
    bk_obj_id = models.CharField(max_length=50, verbose_name="拓扑类型")
    bk_inst_id = models.IntegerField(verbose_name="集群id")
    bk_inst_name = models.CharField(max_length=255, verbose_name="节点名称")
    path = models.TextField(verbose_name="拓扑路径")

    class Serializer:
        default_fields = ["bk_biz_id", "bk_obj_id", "bk_inst_id"]
        field_groups = {
            "list": ["tasks"]
        }


class Tasks(models.Model):
    """任务"""
    task_topo = models.OneToOneField("TasksTopo", related_name="tasks", on_delete=models.DO_NOTHING, null=True)
    task_name = models.IntegerField("任务名称")
    test_list = JSONField()
    test_char = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def serialize_app(self):
        return "xxxx"

    class Serializer:
        default_fields = ["task_name", "test_list", "test_char"]
        field_groups = {
            "list": ["task_topo", "task_name", "test_list", "test_char", "app", "report"]
        }


class Reports(models.Model):
    """报告"""
    STATE = (
        ("wait", "等待"),
        ("run", "进行中"),
        ("finish", "完成"),
    )
    task_id = models.ForeignKey(Tasks, on_delete=models.DO_NOTHING, db_constraint=False, related_name='report')
    task_name = models.CharField("任务名称，与报告名称相同", max_length=32)
    task_type = models.CharField("任务类型", max_length=32)
    name = models.CharField("报告名称", max_length=32)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Serializer:
        default_fields = ["task_name", "name", "task_type"]
        field_groups = {
            "list": ["task_id"]
        }