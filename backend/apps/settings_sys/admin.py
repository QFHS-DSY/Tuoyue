from django.contrib import admin
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

admin.site.register(Department)
admin.site.register(UserProfile)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(RolePermission)
admin.site.register(UserRole)
admin.site.register(UserDepartment)
admin.site.register(DataPermission)
admin.site.register(DataPermissionRule)
admin.site.register(UserDataPermission)
admin.site.register(HandoverRecord)
admin.site.register(BatchImportLog)
admin.site.register(OperationLog)
admin.site.register(SystemConfig)
admin.site.register(Tag)
admin.site.register(TagRule)
admin.site.register(WarehouseConfig)
admin.site.register(ThirdPartyWarehouse)
admin.site.register(WarehouseMapping)
admin.site.register(WarehouseFeature)
admin.site.register(PlatformConfig)
admin.site.register(PlatformAuth)
admin.site.register(ShopAuth)
admin.site.register(AdAccountAuth)
admin.site.register(EmailBinding)
admin.site.register(AuthRefreshLog)
admin.site.register(AssistantTask)
admin.site.register(AssistantTaskConfig)
admin.site.register(ApiToken)
admin.site.register(SSOConfig)
admin.site.register(SensitiveConfig)
admin.site.register(AuditLog)
admin.site.register(NotificationSetting)
