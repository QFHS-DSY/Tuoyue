"""设置系统 ViewSets — 完整 CRUD API"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from apps.settings_sys.models import (
    Department, UserProfile, Role, Permission, RolePermission, UserRole,
    UserDepartment, DataPermission, DataPermissionRule, UserDataPermission,
    HandoverRecord, BatchImportLog, OperationLog,
    SystemConfig, Tag, TagRule, WarehouseConfig, ThirdPartyWarehouse,
    WarehouseMapping, WarehouseFeature,
    PlatformConfig, PlatformAuth, ShopAuth, AdAccountAuth, EmailBinding, AuthRefreshLog,
    AssistantTask, AssistantTaskConfig,
    ApiToken, SSOConfig, SensitiveConfig, AuditLog, NotificationSetting,
)
from apps.settings_sys.serializers import (
    DepartmentSerializer, DepartmentSimpleSerializer, UserProfileSerializer,
    RoleSerializer, PermissionSerializer, RolePermissionSerializer,
    UserRoleSerializer, UserDepartmentSerializer,
    DataPermissionSerializer, DataPermissionRuleSerializer, UserDataPermissionSerializer,
    HandoverRecordSerializer, BatchImportLogSerializer, OperationLogSerializer,
    SystemConfigSerializer, TagSerializer, TagRuleSerializer,
    WarehouseConfigSerializer, ThirdPartyWarehouseSerializer,
    WarehouseMappingSerializer, WarehouseFeatureSerializer,
    PlatformConfigSerializer, PlatformAuthSerializer, ShopAuthSerializer,
    AdAccountAuthSerializer, EmailBindingSerializer, AuthRefreshLogSerializer,
    AssistantTaskSerializer, AssistantTaskConfigSerializer,
    ApiTokenSerializer, SSOConfigSerializer, SensitiveConfigSerializer,
    AuditLogSerializer, NotificationSettingSerializer,
)


# ========================= 组织与账号模块 =========================

class DepartmentViewSet(viewsets.ModelViewSet):
    """部门管理 — 支持树形结构"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'status', 'parent']
    search_fields = ['name', 'code']
    ordering_fields = ['sort_order', 'id', 'created_at']

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """返回完整部门树"""
        roots = Department.objects.filter(parent__isnull=True).prefetch_related('children')
        serializer = DepartmentSerializer(roots, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def simple(self, request):
        """返回部门列表（用于下拉选择）"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = DepartmentSimpleSerializer(queryset, many=True)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user_id']
    search_fields = ['phone', 'employee_no', 'position']


class RoleViewSet(viewsets.ModelViewSet):
    """角色管理"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_system']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['sort_order', 'id', 'created_at']

    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """获取角色拥有的权限"""
        role = self.get_object()
        perm_ids = RolePermission.objects.filter(role=role).values_list('permission_id', flat=True)
        return Response(list(perm_ids))

    @action(detail=True, methods=['post'])
    def set_permissions(self, request, pk=None):
        """设置角色权限（批量）"""
        role = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        RolePermission.objects.filter(role=role).delete()
        for perm_id in permission_ids:
            RolePermission.objects.create(role=role, permission_id=perm_id)
        return Response({'status': 'success', 'count': len(permission_ids)})


class PermissionViewSet(viewsets.ModelViewSet):
    """权限管理 — 支持树形结构"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['perm_type', 'status', 'parent']
    search_fields = ['name', 'code', 'resource_path']
    ordering_fields = ['sort_order', 'id']

    @action(detail=False, methods=['get'])
    def tree(self, request):
        roots = Permission.objects.filter(parent__isnull=True).prefetch_related('children')
        serializer = PermissionSerializer(roots, many=True)
        return Response(serializer.data)


class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role', 'permission']


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'role']


class UserDepartmentViewSet(viewsets.ModelViewSet):
    queryset = UserDepartment.objects.all()
    serializer_class = UserDepartmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'department']


class DataPermissionViewSet(viewsets.ModelViewSet):
    queryset = DataPermission.objects.all()
    serializer_class = DataPermissionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['dimension', 'status']
    search_fields = ['name', 'code']


class DataPermissionRuleViewSet(viewsets.ModelViewSet):
    queryset = DataPermissionRule.objects.all()
    serializer_class = DataPermissionRuleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['data_permission']


class UserDataPermissionViewSet(viewsets.ModelViewSet):
    queryset = UserDataPermission.objects.all()
    serializer_class = UserDataPermissionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'data_permission']


class HandoverRecordViewSet(viewsets.ModelViewSet):
    """离职交接记录"""
    queryset = HandoverRecord.objects.all()
    serializer_class = HandoverRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['from_user', 'status', 'handover_type']
    search_fields = ['remark']
    ordering_fields = ['created_at', 'handover_date']


class BatchImportLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BatchImportLog.objects.all()
    serializer_class = BatchImportLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['import_type', 'status']
    search_fields = ['file_name']
    ordering_fields = ['created_at']


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'module', 'action', 'response_code']
    search_fields = ['target_type', 'request_path', 'ip_address']
    ordering_fields = ['created_at', 'duration_ms']


# ========================= 仓库与参数配置 =========================

class SystemConfigViewSet(viewsets.ModelViewSet):
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['config_group', 'is_encrypted']
    search_fields = ['config_key', 'description']

    @action(detail=False, methods=['get'])
    def by_group(self, request):
        group = request.query_params.get('group', 'GENERAL')
        queryset = SystemConfig.objects.filter(config_group=group)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tag_type', 'status', 'is_auto']
    search_fields = ['name', 'code']


class TagRuleViewSet(viewsets.ModelViewSet):
    queryset = TagRule.objects.all()
    serializer_class = TagRuleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tag', 'target_type', 'is_enabled']


class WarehouseConfigViewSet(viewsets.ModelViewSet):
    """仓库配置（拓岳WMS）"""
    queryset = WarehouseConfig.objects.all()
    serializer_class = WarehouseConfigSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['warehouse_type', 'status', 'country']
    search_fields = ['warehouse_name', 'warehouse_code']


class ThirdPartyWarehouseViewSet(viewsets.ModelViewSet):
    """第三方海外仓配置"""
    queryset = ThirdPartyWarehouse.objects.all()
    serializer_class = ThirdPartyWarehouseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['provider_code', 'status', 'country']
    search_fields = ['name', 'provider_name', 'warehouse_code']


class WarehouseMappingViewSet(viewsets.ModelViewSet):
    queryset = WarehouseMapping.objects.all()
    serializer_class = WarehouseMappingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['source_warehouse', 'target_warehouse', 'mapping_type', 'status']


class WarehouseFeatureViewSet(viewsets.ModelViewSet):
    queryset = WarehouseFeature.objects.all()
    serializer_class = WarehouseFeatureSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['warehouse_config', 'feature_code', 'is_enabled']


# ========================= 授权模块 =========================

class PlatformConfigViewSet(viewsets.ModelViewSet):
    queryset = PlatformConfig.objects.all()
    serializer_class = PlatformConfigSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'auth_type']
    search_fields = ['platform_name', 'platform_code']


class PlatformAuthViewSet(viewsets.ModelViewSet):
    queryset = PlatformAuth.objects.all()
    serializer_class = PlatformAuthSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['platform', 'auth_status']
    search_fields = ['account_name', 'account_id']
    ordering_fields = ['created_at', 'token_expires_at']

    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        """手动刷新Token"""
        auth = self.get_object()
        # 这里应调用 celery 异步任务执行实际刷新
        return Response({'status': 'queued', 'message': 'Token刷新任务已排入队列'})


class ShopAuthViewSet(viewsets.ModelViewSet):
    queryset = ShopAuth.objects.all()
    serializer_class = ShopAuthSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['platform_auth', 'status', 'country']
    search_fields = ['shop_name', 'shop_id']


class AdAccountAuthViewSet(viewsets.ModelViewSet):
    queryset = AdAccountAuth.objects.all()
    serializer_class = AdAccountAuthSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['platform_auth', 'status']
    search_fields = ['ad_account_name', 'ad_account_id']


class EmailBindingViewSet(viewsets.ModelViewSet):
    queryset = EmailBinding.objects.all()
    serializer_class = EmailBindingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'email_type', 'status']
    search_fields = ['email_address']


class AuthRefreshLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuthRefreshLog.objects.all()
    serializer_class = AuthRefreshLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['platform_auth', 'success']
    ordering_fields = ['created_at']


# ========================= 拓岳助手 =========================

class AssistantTaskViewSet(viewsets.ModelViewSet):
    queryset = AssistantTask.objects.all()
    serializer_class = AssistantTaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['task_type', 'status']
    search_fields = ['task_name', 'task_no']
    ordering_fields = ['created_at', 'priority']

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """手动触发任务"""
        task = self.get_object()
        return Response({'status': 'queued', 'task_no': task.task_no})

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """启用/禁用任务"""
        task = self.get_object()
        task.status = 'IDLE' if task.status == 'DISABLED' else 'DISABLED'
        task.save()
        return Response({'status': task.status})


class AssistantTaskConfigViewSet(viewsets.ModelViewSet):
    queryset = AssistantTaskConfig.objects.all()
    serializer_class = AssistantTaskConfigSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task']


# ========================= 安全与系统 =========================

class ApiTokenViewSet(viewsets.ModelViewSet):
    queryset = ApiToken.objects.all()
    serializer_class = ApiTokenSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'is_active']
    search_fields = ['token_name']

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """吊销Token"""
        token = self.get_object()
        token.is_active = False
        token.save()
        return Response({'status': 'revoked'})


class SSOConfigViewSet(viewsets.ModelViewSet):
    queryset = SSOConfig.objects.all()
    serializer_class = SSOConfigSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['sso_provider', 'status']
    search_fields = ['sso_name']


class SensitiveConfigViewSet(viewsets.ModelViewSet):
    queryset = SensitiveConfig.objects.all()
    serializer_class = SensitiveConfigSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['config_type']
    search_fields = ['config_key', 'description']


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'audit_type', 'result']
    search_fields = ['action', 'target', 'ip_address']
    ordering_fields = ['created_at']


class NotificationSettingViewSet(viewsets.ModelViewSet):
    queryset = NotificationSetting.objects.all()
    serializer_class = NotificationSettingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']
