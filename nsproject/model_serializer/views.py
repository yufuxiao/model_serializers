from model_serializer.models import Tasks, Reports, TasksTopo
from model_serializer.response import api


def test(request):
    # tasks = Tasks.objects.get(id=5)
    # reports = Reports.objects.get(id=10)
    tasks_topo = TasksTopo.objects.get(id=1)
    return api.ok(tasks_topo, group="list")
