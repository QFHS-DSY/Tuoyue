from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, permissions

from apps.common.responses import success_response

from .models import Task
from .pagination import TaskPagePagination
from .permissions import IsOwner
from .serializers import TaskSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TaskPagePagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "updated_at", "due_date", "priority"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Task.objects.filter(creator=self.request.user).only(
            "id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "creator_id",
            "created_at",
            "updated_at",
        )
        status_value = self.request.query_params.get("status")
        if status_value:
            queryset = queryset.filter(status=status_value)
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @extend_schema(summary="任务列表（分页+状态筛选）")
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return success_response(data=response.data)

    @extend_schema(summary="创建任务")
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return success_response(data=response.data, status_code=201)


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Task.objects.filter(creator=self.request.user)

    @extend_schema(summary="任务详情")
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return success_response(data=response.data)

    @extend_schema(summary="更新任务")
    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        return success_response(data=response.data)

    @extend_schema(summary="部分更新任务")
    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        return success_response(data=response.data)

    @extend_schema(summary="删除任务")
    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return success_response(data=None, message="deleted")
