"""设置系统 Serializers"""
from rest_framework import serializers
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


# ========== 组织与账号模块 ==========

class DepartmentSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_children(self, obj):
        if hasattr(obj, 'children') and obj.children.exists():
            return DepartmentSerializer(obj.children.all(), many=True).data
        return []


class DepartmentSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'parent', 'level']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class PermissionSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = '__all__'
        read_only_fields = ['created_at']

    def get_children(self, obj):
        if hasattr(obj, 'children') and obj.children.exists():
            return PermissionSerializer(obj.children.all(), many=True).data
        return []


class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = '__all__'


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'


class UserDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDepartment
        fields = '__all__'


class DataPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataPermission
        fields = '__all__'


class DataPermissionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataPermissionRule
        fields = '__all__'


class UserDataPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDataPermission
        fields = '__all__'


class HandoverRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HandoverRecord
        fields = '__all__'
        read_only_fields = ['created_at']


class BatchImportLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchImportLog
        fields = '__all__'
        read_only_fields = ['created_at']


class OperationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationLog
        fields = '__all__'
        read_only_fields = ['created_at']


# ========== 仓库与参数配置 ==========

class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class TagRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagRule
        fields = '__all__'


class WarehouseConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseConfig
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ThirdPartyWarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThirdPartyWarehouse
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class WarehouseMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseMapping
        fields = '__all__'


class WarehouseFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseFeature
        fields = '__all__'


# ========== 授权模块 ==========

class PlatformConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformConfig
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class PlatformAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformAuth
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ShopAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopAuth
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AdAccountAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdAccountAuth
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class EmailBindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailBinding
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AuthRefreshLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthRefreshLog
        fields = '__all__'
        read_only_fields = ['created_at']


# ========== 拓岳助手 ==========

class AssistantTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantTask
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AssistantTaskConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantTaskConfig
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# ========== 安全与系统 ==========

class ApiTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiToken
        fields = '__all__'
        read_only_fields = ['token_hash', 'created_at']


class SSOConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSOConfig
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SensitiveConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensitiveConfig
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['created_at']


class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSetting
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
