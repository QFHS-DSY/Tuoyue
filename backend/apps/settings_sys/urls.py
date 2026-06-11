"""设置系统 URL 路由"""
from rest_framework.routers import DefaultRouter
from apps.settings_sys.views import (
    DepartmentViewSet, UserProfileViewSet, RoleViewSet, PermissionViewSet,
    RolePermissionViewSet, UserRoleViewSet, UserDepartmentViewSet,
    DataPermissionViewSet, DataPermissionRuleViewSet, UserDataPermissionViewSet,
    HandoverRecordViewSet, BatchImportLogViewSet, OperationLogViewSet,
    SystemConfigViewSet, TagViewSet, TagRuleViewSet,
    WarehouseConfigViewSet, ThirdPartyWarehouseViewSet,
    WarehouseMappingViewSet, WarehouseFeatureViewSet,
    PlatformConfigViewSet, PlatformAuthViewSet, ShopAuthViewSet,
    AdAccountAuthViewSet, EmailBindingViewSet, AuthRefreshLogViewSet,
    AssistantTaskViewSet, AssistantTaskConfigViewSet,
    ApiTokenViewSet, SSOConfigViewSet, SensitiveConfigViewSet,
    AuditLogViewSet, NotificationSettingViewSet,
)

router = DefaultRouter()

# 组织与账号模块
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'user-profiles', UserProfileViewSet, basename='user-profile')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'role-permissions', RolePermissionViewSet, basename='role-permission')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')
router.register(r'user-departments', UserDepartmentViewSet, basename='user-department')
router.register(r'data-permissions', DataPermissionViewSet, basename='data-permission')
router.register(r'data-permission-rules', DataPermissionRuleViewSet, basename='data-permission-rule')
router.register(r'user-data-permissions', UserDataPermissionViewSet, basename='user-data-permission')
router.register(r'handover-records', HandoverRecordViewSet, basename='handover-record')
router.register(r'batch-import-logs', BatchImportLogViewSet, basename='batch-import-log')
router.register(r'operation-logs', OperationLogViewSet, basename='operation-log')

# 仓库与参数配置
router.register(r'system-configs', SystemConfigViewSet, basename='system-config')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'tag-rules', TagRuleViewSet, basename='tag-rule')
router.register(r'warehouse-configs', WarehouseConfigViewSet, basename='warehouse-config')
router.register(r'third-party-warehouses', ThirdPartyWarehouseViewSet, basename='third-party-warehouse')
router.register(r'warehouse-mappings', WarehouseMappingViewSet, basename='warehouse-mapping')
router.register(r'warehouse-features', WarehouseFeatureViewSet, basename='warehouse-feature')

# 授权模块
router.register(r'platform-configs', PlatformConfigViewSet, basename='platform-config')
router.register(r'platform-auths', PlatformAuthViewSet, basename='platform-auth')
router.register(r'shop-auths', ShopAuthViewSet, basename='shop-auth')
router.register(r'ad-account-auths', AdAccountAuthViewSet, basename='ad-account-auth')
router.register(r'email-bindings', EmailBindingViewSet, basename='email-binding')
router.register(r'auth-refresh-logs', AuthRefreshLogViewSet, basename='auth-refresh-log')

# 拓岳助手
router.register(r'assistant-tasks', AssistantTaskViewSet, basename='assistant-task')
router.register(r'assistant-task-configs', AssistantTaskConfigViewSet, basename='assistant-task-config')

# 安全与系统
router.register(r'api-tokens', ApiTokenViewSet, basename='api-token')
router.register(r'sso-configs', SSOConfigViewSet, basename='sso-config')
router.register(r'sensitive-configs', SensitiveConfigViewSet, basename='sensitive-config')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'notification-settings', NotificationSettingViewSet, basename='notification-setting')

urlpatterns = router.urls
