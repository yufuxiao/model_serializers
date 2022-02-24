from model_serializer.models import Tasks
from model_serializer.response import api


def test(request):
    """
    usage:
        Model 对象：
            tasks = Tasks.objects.get(id=5)
            return api.ok(tasks, group="xx")

        QuerySet:
            qs = Tasks.objects.all()
            return api.page(request, qs, group="xx")

    """
    # tasks = Tasks.objects.get(id=5)
    # return api.ok(tasks, group="list")
    qs = Tasks.objects.all()
    return api.page(request, qs, group="list")