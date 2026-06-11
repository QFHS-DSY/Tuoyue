"""
设置系统 (Settings System) - 完整数据模型
============================================
涵盖：组织架构、角色权限RBAC、仓库对接、平台授权、拓岳助手、系统安全
共计 33 张业务表
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


# =============================================================================
# 一、组织与账号模块 (Organization & Account) — 13 张表
# =============================================================================

class Department(models.Model):
    """部门表 — 支持最多9级树形结构"""
    name = models.CharField('部门名称', max_length=100)
    code = models.CharField('部门编码', max_length=50, unique=True, db_index=True)
    parent = models.ForeignKey(
        'self', verbose_name='上级部门', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='children'
    )
    level = models.IntegerField('层级', default=1, validators=[MinValueValidator(1), MaxValueValidator(9)])
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='负责人', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='managed_departments'
    )
    sort_order = models.IntegerField('排序', default=0)
    status = models.BooleanField('启用', default=True)
    description = models.CharField('描述', max_length=500, blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='创建人', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='created_departments'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_department'
        verbose_name = '部门'
        verbose_name_plural = '部门'
        ordering = ['sort_order', 'id']
        indexes = [
            models.Index(fields=['parent_id', 'status']),
            models.Index(fields=['level']),
        ]

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """用户扩展资料表"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, verbose_name='用户', on_delete=models.CASCADE,
        related_name='profile'
    )
    phone = models.CharField('手机号', max_length=20, blank=True, default='')
    avatar_url = models.CharField('头像', max_length=500, blank=True, default='')
    employee_no = models.CharField('工号', max_length=50, blank=True, default='', db_index=True)
    position = models.CharField('职位', max_length=100, blank=True, default='')
    entry_date = models.DateField('入职日期', null=True, blank=True)
    leave_date = models.DateField('离职日期', null=True, blank=True)
    is_online = models.BooleanField('在线状态', default=False)
    last_login_ip = models.CharField('最后登录IP', max_length=50, blank=True, default='')
    remark = models.CharField('备注', max_length=500, blank=True, default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_user_profile'
        verbose_name = '用户扩展资料'
        verbose_name_plural = '用户扩展资料'

    def __str__(self):
        return f'{self.user.username} Profile'


class Role(models.Model):
    """角色表"""
    name = models.CharField('角色名称', max_length=100, unique=True)
    code = models.CharField('角色编码', max_length=50, unique=True, db_index=True)
    description = models.CharField('描述', max_length=500, blank=True, default='')
    is_system = models.BooleanField('系统内置', default=False)
    status = models.BooleanField('启用', default=True)
    sort_order = models.IntegerField('排序', default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='创建人', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_role'
        verbose_name = '角色'
        verbose_name_plural = '角色'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class Permission(models.Model):
    """权限表"""
    PERM_TYPE_CHOICES = [
        ('MENU', '菜单权限'),
        ('API', '接口权限'),
        ('DATA', '数据权限'),
        ('BUTTON', '按钮权限'),
    ]
    name = models.CharField('权限名称', max_length=100)
    code = models.CharField('权限编码', max_length=100, unique=True, db_index=True)
    perm_type = models.CharField('权限类型', max_length=20, choices=PERM_TYPE_CHOICES, default='API')
    parent = models.ForeignKey(
        'self', verbose_name='上级权限', null=True, blank=True,
        on_delete=models.CASCADE, related_name='children'
    )
    resource_path = models.CharField('资源路径', max_length=200, blank=True, default='')
    icon = models.CharField('图标', max_length=100, blank=True, default='')
    sort_order = models.IntegerField('排序', default=0)
    status = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_permission'
        verbose_name = '权限'
        verbose_name_plural = '权限'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'{self.get_perm_type_display()} - {self.name}'


class RolePermission(models.Model):
    """角色权限关联表"""
    role = models.ForeignKey(Role, verbose_name='角色', on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, verbose_name='权限', on_delete=models.CASCADE)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_role_permission'
        verbose_name = '角色权限关联'
        verbose_name_plural = '角色权限关联'
        unique_together = [['role', 'permission']]


class UserRole(models.Model):
    """用户角色关联表"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='用户', on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(Role, verbose_name='角色', on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='分配人', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='assigned_roles'
    )
    assigned_at = models.DateTimeField('分配时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_user_role'
        verbose_name = '用户角色关联'
        verbose_name_plural = '用户角色关联'
        unique_together = [['user', 'role']]


class UserDepartment(models.Model):
    """用户部门关联表（支持一人多部门）"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='用户', on_delete=models.CASCADE,
        related_name='user_departments'
    )
    department = models.ForeignKey(Department, verbose_name='部门', on_delete=models.CASCADE)
    is_primary = models.BooleanField('主部门', default=False)
    assigned_at = models.DateTimeField('分配时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_user_department'
        verbose_name = '用户部门关联'
        verbose_name_plural = '用户部门关联'
        unique_together = [['user', 'department']]


class DataPermission(models.Model):
    """数据权限表"""
    DIMENSION_CHOICES = [
        ('SKU', 'SKU权限'),
        ('DOCUMENT', '单据权限'),
        ('LISTING', 'Listing权限'),
        ('DEPARTMENT', '部门权限'),
        ('WAREHOUSE', '仓库权限'),
        ('SHOP', '店铺权限'),
    ]
    name = models.CharField('数据权限名称', max_length=100)
    code = models.CharField('数据权限编码', max_length=100, unique=True, db_index=True)
    dimension = models.CharField('权限维度', max_length=20, choices=DIMENSION_CHOICES)
    description = models.CharField('描述', max_length=500, blank=True, default='')
    status = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_data_permission'
        verbose_name = '数据权限'
        verbose_name_plural = '数据权限'

    def __str__(self):
        return f'{self.get_dimension_display()} - {self.name}'


class DataPermissionRule(models.Model):
    """数据权限规则表"""
    data_permission = models.ForeignKey(
        DataPermission, verbose_name='数据权限', on_delete=models.CASCADE,
        related_name='rules'
    )
    rule_type = models.CharField('规则类型', max_length=50)  # include/exclude/range
    rule_params = models.JSONField('规则参数', default=dict)
    priority = models.IntegerField('优先级', default=1)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_data_permission_rule'
        verbose_name = '数据权限规则'
        verbose_name_plural = '数据权限规则'


class UserDataPermission(models.Model):
    """用户数据权限关联表"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='用户', on_delete=models.CASCADE,
        related_name='data_permissions'
    )
    data_permission = models.ForeignKey(DataPermission, verbose_name='数据权限', on_delete=models.CASCADE)
    rule_params = models.JSONField('规则参数覆盖', default=dict, blank=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='分配人', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    assigned_at = models.DateTimeField('分配时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_user_data_permission'
        verbose_name = '用户数据权限关联'
        verbose_name_plural = '用户数据权限关联'
        unique_together = [['user', 'data_permission']]


class HandoverRecord(models.Model):
    """离职交接记录表"""
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='离职人', on_delete=models.CASCADE,
        related_name='sys_handovers_from'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='交接人', on_delete=models.CASCADE,
        related_name='sys_handovers_to'
    )
    handover_type = models.CharField('交接类型', max_length=50)  # SKU/DOCUMENT/LISTING/ALL
    handover_data = models.JSONField('交接数据', default=dict)
    status = models.CharField('状态', max_length=20, default='PENDING')  # PENDING/PROCESSING/COMPLETED/FAILED
    handover_date = models.DateTimeField('交接日期', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    error_message = models.TextField('错误信息', blank=True, default='')
    remark = models.CharField('备注', max_length=500, blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='操作人', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='sys_created_handovers'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_handover_record'
        verbose_name = '离职交接记录'
        verbose_name_plural = '离职交接记录'
        indexes = [
            models.Index(fields=['from_user_id', 'status']),
            models.Index(fields=['status']),
        ]


class BatchImportLog(models.Model):
    """批量导入日志表"""
    IMPORT_TYPE_CHOICES = [
        ('USER', '批量导入用户'),
        ('SKU', '批量导入SKU'),
        ('LISTING', '批量导入Listing'),
    ]
    import_type = models.CharField('导入类型', max_length=20, choices=IMPORT_TYPE_CHOICES)
    file_name = models.CharField('文件名', max_length=200)
    total_count = models.IntegerField('总条数', default=0)
    success_count = models.IntegerField('成功条数', default=0)
    failed_count = models.IntegerField('失败条数', default=0)
    error_detail = models.JSONField('错误详情', default=list, blank=True)
    status = models.CharField('状态', max_length=20, default='PENDING')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='操作人', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)

    class Meta:
        db_table = 'sys_batch_import_log'
        verbose_name = '批量导入日志'
        verbose_name_plural = '批量导入日志'


class OperationLog(models.Model):
    """操作日志表"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='操作人', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    module = models.CharField('操作模块', max_length=100)
    action = models.CharField('操作动作', max_length=50)
    target_type = models.CharField('目标类型', max_length=50, blank=True, default='')
    target_id = models.BigIntegerField('目标ID', null=True, blank=True)
    request_method = models.CharField('请求方法', max_length=10, blank=True, default='')
    request_path = models.CharField('请求路径', max_length=500, blank=True, default='')
    request_body = models.JSONField('请求体', default=dict, blank=True)
    response_code = models.IntegerField('响应码', null=True, blank=True)
    ip_address = models.CharField('IP地址', max_length=50, blank=True, default='')
    user_agent = models.CharField('User-Agent', max_length=500, blank=True, default='')
    duration_ms = models.IntegerField('耗时(毫秒)', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'sys_operation_log'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'


# =============================================================================
# 二、仓库与参数配置 (Warehouse & Parameters) — 7 张表
# =============================================================================

class SystemConfig(models.Model):
    """系统配置表"""
    config_key = models.CharField('配置键', max_length=100, unique=True, db_index=True)
    config_value = models.JSONField('配置值', default=dict)
    config_group = models.CharField('配置分组', max_length=50, default='GENERAL')
    description = models.CharField('描述', max_length=500, blank=True, default='')
    is_encrypted = models.BooleanField('是否加密', default=False)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='更新人', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_config'
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'

    def __str__(self):
        return self.config_key


class Tag(models.Model):
    """全局标签表"""
    name = models.CharField('标签名称', max_length=50)
    code = models.CharField('标签编码', max_length=50, unique=True, db_index=True)
    tag_type = models.CharField('标签类型', max_length=50)  # SKU/ORDER/LISTING/SUPPLIER/WAREHOUSE
    color = models.CharField('标签颜色', max_length=20, default='#409EFF')
    description = models.CharField('描述', max_length=200, blank=True, default='')
    is_auto = models.BooleanField('是否自动', default=False)
    status = models.BooleanField('启用', default=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_tag'
        verbose_name = '全局标签'
        verbose_name_plural = '全局标签'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class TagRule(models.Model):
    """自动打标签规则表"""
    tag = models.ForeignKey(Tag, verbose_name='标签', on_delete=models.CASCADE, related_name='rules')
    rule_name = models.CharField('规则名称', max_length=100)
    target_type = models.CharField('目标类型', max_length=50)  # SKU/ORDER/LISTING
    conditions = models.JSONField('条件规则', default=dict)
    priority = models.IntegerField('优先级', default=1)
    is_enabled = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_tag_rule'
        verbose_name = '自动打标签规则'
        verbose_name_plural = '自动打标签规则'


class WarehouseConfig(models.Model):
    """仓库配置表（拓岳WMS）"""
    warehouse_name = models.CharField('仓库名称', max_length=100)
    warehouse_code = models.CharField('仓库编码', max_length=50, unique=True, db_index=True)
    warehouse_type = models.CharField('仓库类型', max_length=50)  # SELF/THIRD_PARTY/FBA
    address = models.CharField('仓库地址', max_length=500, blank=True, default='')
    contact_name = models.CharField('联系人', max_length=50, blank=True, default='')
    contact_phone = models.CharField('联系电话', max_length=20, blank=True, default='')
    country = models.CharField('国家', max_length=50, blank=True, default='')
    api_endpoint = models.CharField('API地址', max_length=500, blank=True, default='')
    api_key = models.CharField('API密钥(加密)', max_length=500, blank=True, default='')
    api_secret = models.CharField('API Secret(加密)', max_length=500, blank=True, default='')
    status = models.BooleanField('启用', default=True)
    config_params = models.JSONField('扩展参数', default=dict, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_warehouse_config'
        verbose_name = '仓库配置'
        verbose_name_plural = '仓库配置'

    def __str__(self):
        return self.warehouse_name


class ThirdPartyWarehouse(models.Model):
    """第三方海外仓配置表（谷仓/万邑通等）"""
    name = models.CharField('海外仓名称', max_length=100)
    provider_code = models.CharField('服务商编码', max_length=50)  # GUCANG/WANYITONG/4PX
    provider_name = models.CharField('服务商名称', max_length=100)
    warehouse_code = models.CharField('仓库编码', max_length=100)
    country = models.CharField('国家', max_length=50)
    api_endpoint = models.CharField('API地址', max_length=500)
    api_app_key = models.CharField('AppKey(加密)', max_length=500, blank=True, default='')
    api_app_secret = models.CharField('AppSecret(加密)', max_length=500, blank=True, default='')
    api_token = models.CharField('Token(加密)', max_length=500, blank=True, default='')
    status = models.BooleanField('启用', default=True)
    config_params = models.JSONField('扩展参数', default=dict, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_third_party_warehouse'
        verbose_name = '第三方海外仓配置'
        verbose_name_plural = '第三方海外仓配置'

    def __str__(self):
        return f'{self.provider_name} - {self.name}'


class WarehouseMapping(models.Model):
    """仓库配对映射表"""
    source_warehouse = models.ForeignKey(
        WarehouseConfig, verbose_name='拓岳仓库', on_delete=models.CASCADE,
        related_name='mappings'
    )
    target_warehouse = models.ForeignKey(
        ThirdPartyWarehouse, verbose_name='第三方仓库', on_delete=models.CASCADE,
        related_name='mappings'
    )
    mapping_type = models.CharField('映射类型', max_length=50)  # SKU/ORDER/INVENTORY
    mapping_params = models.JSONField('映射参数', default=dict, blank=True)
    is_auto_sync = models.BooleanField('自动同步', default=False)
    sync_interval = models.IntegerField('同步间隔(分钟)', default=60)
    last_sync_at = models.DateTimeField('最后同步时间', null=True, blank=True)
    status = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_warehouse_mapping'
        verbose_name = '仓库配对映射'
        verbose_name_plural = '仓库配对映射'


class WarehouseFeature(models.Model):
    """仓库功能配置表"""
    warehouse_config = models.ForeignKey(
        WarehouseConfig, verbose_name='仓库', on_delete=models.CASCADE,
        related_name='features'
    )
    feature_name = models.CharField('功能名称', max_length=100)  # RECEIVE/SHIP/INVENTORY/TRANSFER
    feature_code = models.CharField('功能编码', max_length=50)
    is_enabled = models.BooleanField('启用', default=True)
    config_params = models.JSONField('功能参数', default=dict, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_warehouse_feature'
        verbose_name = '仓库功能配置'
        verbose_name_plural = '仓库功能配置'
        unique_together = [['warehouse_config', 'feature_code']]


# =============================================================================
# 三、授权模块 (Authorization) — 6 张表
# =============================================================================

class PlatformConfig(models.Model):
    """平台配置表"""
    platform_name = models.CharField('平台名称', max_length=50)  # AMAZON/1688/EBAY/SHOPEE/WALMART/TEMU
    platform_code = models.CharField('平台编码', max_length=30, unique=True, db_index=True)
    auth_type = models.CharField('授权方式', max_length=50)  # OAUTH2/TOKEN/API_KEY/SP_API
    auth_url = models.CharField('授权地址', max_length=500, blank=True, default='')
    token_url = models.CharField('Token地址', max_length=500, blank=True, default='')
    api_base_url = models.CharField('API基础地址', max_length=500, blank=True, default='')
    client_id = models.CharField('ClientID', max_length=200, blank=True, default='')
    client_secret = models.CharField('ClientSecret(加密)', max_length=500, blank=True, default='')
    redirect_uri = models.CharField('回调地址', max_length=500, blank=True, default='')
    scope = models.CharField('授权范围', max_length=500, blank=True, default='')
    status = models.BooleanField('启用', default=True)
    config_params = models.JSONField('扩展参数', default=dict, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_platform_config'
        verbose_name = '平台配置'
        verbose_name_plural = '平台配置'

    def __str__(self):
        return self.platform_name


class PlatformAuth(models.Model):
    """平台授权表（Amazon/1688 等 OAuth/Token）"""
    platform = models.ForeignKey(PlatformConfig, verbose_name='平台', on_delete=models.CASCADE, related_name='auths')
    account_name = models.CharField('账户名称', max_length=100)
    account_id = models.CharField('平台账户ID', max_length=100, db_index=True)
    access_token = models.CharField('AccessToken(加密)', max_length=2000, blank=True, default='')
    refresh_token = models.CharField('RefreshToken(加密)', max_length=1000, blank=True, default='')
    token_expires_at = models.DateTimeField('Token过期时间', null=True, blank=True)
    auth_status = models.CharField('授权状态', max_length=20, default='ACTIVE')  # ACTIVE/EXPIRED/REVOKED
    auth_scope = models.CharField('授权范围', max_length=500, blank=True, default='')
    extra_data = models.JSONField('额外数据', default=dict, blank=True)
    authorized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='授权人', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    authorized_at = models.DateTimeField('授权时间', null=True, blank=True)
    last_refresh_at = models.DateTimeField('最后刷新时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_platform_auth'
        verbose_name = '平台授权'
        verbose_name_plural = '平台授权'
        indexes = [
            models.Index(fields=['platform_id', 'auth_status']),
            models.Index(fields=['token_expires_at']),
        ]

    def __str__(self):
        return f'{self.platform} - {self.account_name}'


class ShopAuth(models.Model):
    """店铺授权表"""
    platform_auth = models.ForeignKey(
        PlatformAuth, verbose_name='平台授权', on_delete=models.CASCADE,
        related_name='shop_auths'
    )
    shop_id = models.CharField('店铺ID', max_length=100, db_index=True)
    shop_name = models.CharField('店铺名称', max_length=200)
    marketplace_id = models.CharField('市场ID', max_length=50, blank=True, default='')
    country = models.CharField('国家', max_length=10, blank=True, default='')
    currency = models.CharField('货币', max_length=10, default='USD')
    status = models.BooleanField('启用', default=True)
    sync_settings = models.JSONField('同步设置', default=dict, blank=True)
    last_sync_at = models.DateTimeField('最后同步时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_shop_auth'
        verbose_name = '店铺授权'
        verbose_name_plural = '店铺授权'
        unique_together = [['platform_auth', 'shop_id']]

    def __str__(self):
        return self.shop_name


class AdAccountAuth(models.Model):
    """广告账户授权表"""
    platform_auth = models.ForeignKey(
        PlatformAuth, verbose_name='平台授权', on_delete=models.CASCADE,
        related_name='ad_auths'
    )
    ad_account_id = models.CharField('广告账户ID', max_length=200)
    ad_account_name = models.CharField('广告账户名称', max_length=200)
    ad_platform = models.CharField('广告平台', max_length=50)  # AMAZON_ADS/GOOGLE_ADS/FACEBOOK_ADS
    access_token = models.CharField('AccessToken(加密)', max_length=2000, blank=True, default='')
    refresh_token = models.CharField('RefreshToken(加密)', max_length=1000, blank=True, default='')
    token_expires_at = models.DateTimeField('Token过期时间', null=True, blank=True)
    status = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_ad_account_auth'
        verbose_name = '广告账户授权'
        verbose_name_plural = '广告账户授权'

    def __str__(self):
        return self.ad_account_name


class EmailBinding(models.Model):
    """邮箱绑定表"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='用户', on_delete=models.CASCADE,
        related_name='email_bindings'
    )
    email_address = models.EmailField('邮箱地址', max_length=200)
    email_type = models.CharField('邮箱类型', max_length=50)  # NOTIFICATION/ORDER/SUPPLIER/PLATFORM
    smtp_host = models.CharField('SMTP主机', max_length=200, blank=True, default='')
    smtp_port = models.IntegerField('SMTP端口', null=True, blank=True)
    smtp_username = models.CharField('SMTP用户名', max_length=200, blank=True, default='')
    smtp_password = models.CharField('SMTP密码(加密)', max_length=500, blank=True, default='')
    is_verified = models.BooleanField('已验证', default=False)
    is_default = models.BooleanField('默认', default=False)
    status = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_email_binding'
        verbose_name = '邮箱绑定'
        verbose_name_plural = '邮箱绑定'

    def __str__(self):
        return self.email_address


class AuthRefreshLog(models.Model):
    """授权续期日志表"""
    platform_auth = models.ForeignKey(
        PlatformAuth, verbose_name='平台授权', on_delete=models.CASCADE,
        related_name='refresh_logs'
    )
    refresh_type = models.CharField('续期类型', max_length=50)  # TOKEN_REFRESH/REAUTH
    success = models.BooleanField('成功', default=True)
    error_message = models.TextField('错误信息', blank=True, default='')
    old_expires_at = models.DateTimeField('旧过期时间', null=True, blank=True)
    new_expires_at = models.DateTimeField('新过期时间', null=True, blank=True)
    ip_address = models.CharField('IP地址', max_length=50, blank=True, default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_auth_refresh_log'
        verbose_name = '授权续期日志'
        verbose_name_plural = '授权续期日志'
        indexes = [
            models.Index(fields=['platform_auth_id', 'success']),
        ]


# =============================================================================
# 四、拓岳助手模块 (Tuoyue Assistant) — 2 张表
# =============================================================================

class AssistantTask(models.Model):
    """助手任务表"""
    task_no = models.CharField('任务编号', max_length=50, unique=True, db_index=True)
    task_name = models.CharField('任务名称', max_length=200)
    task_type = models.CharField('任务类型', max_length=50)  # SYNC/COLLECT/MONITOR/REPORT/BACKUP
    task_params = models.JSONField('任务参数', default=dict)
    cron_expression = models.CharField('Cron表达式', max_length=100, blank=True, default='')
    status = models.CharField('状态', max_length=20, default='IDLE')  # IDLE/RUNNING/SUCCESS/FAILED/DISABLED
    priority = models.IntegerField('优先级', default=1)
    retry_count = models.IntegerField('重试次数', default=0)
    max_retry = models.IntegerField('最大重试', default=3)
    last_run_at = models.DateTimeField('上次运行', null=True, blank=True)
    next_run_at = models.DateTimeField('下次运行', null=True, blank=True)
    last_result = models.JSONField('上次结果', default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='创建人', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_assistant_task'
        verbose_name = '助手任务'
        verbose_name_plural = '助手任务'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['task_type']),
        ]

    def __str__(self):
        return self.task_name


class AssistantTaskConfig(models.Model):
    """助手任务配置表"""
    task = models.OneToOneField(
        AssistantTask, verbose_name='任务', on_delete=models.CASCADE,
        related_name='config'
    )
    notify_on_success = models.BooleanField('成功通知', default=False)
    notify_on_failure = models.BooleanField('失败通知', default=True)
    notify_users = models.JSONField('通知用户', default=list, blank=True)
    notify_channels = models.JSONField('通知渠道', default=list, blank=True)  # EMAIL/SMS/SYSTEM
    timeout_seconds = models.IntegerField('超时(秒)', default=3600)
    concurrent_limit = models.IntegerField('并发限制', default=1)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_assistant_task_config'
        verbose_name = '助手任务配置'
        verbose_name_plural = '助手任务配置'

    def __str__(self):
        return f'{self.task.task_name} Config'


# =============================================================================
# 五、安全与系统模块 (Security & System) — 5 张表
# =============================================================================

class ApiToken(models.Model):
    """API Token管理表"""
    token_name = models.CharField('Token名称', max_length=100)
    token_key = models.CharField('Token前缀', max_length=20, unique=True, db_index=True)
    token_hash = models.CharField('Token哈希', max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='所属用户', on_delete=models.CASCADE,
        related_name='api_tokens'
    )
    scopes = models.JSONField('权限范围', default=list)
    last_used_at = models.DateTimeField('最后使用', null=True, blank=True)
    expires_at = models.DateTimeField('过期时间', null=True, blank=True)
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_api_token'
        verbose_name = 'API Token'
        verbose_name_plural = 'API Token'

    def __str__(self):
        return self.token_name


class SSOConfig(models.Model):
    """SSO单点登录配置表"""
    sso_name = models.CharField('SSO名称', max_length=100)
    sso_provider = models.CharField('提供商', max_length=50)  # JWT/LDAP/OAUTH2/SAML
    issuer = models.CharField('签发者', max_length=200)
    audience = models.CharField('接收者', max_length=200, blank=True, default='')
    signing_algorithm = models.CharField('签名算法', max_length=20, default='HS256')
    signing_secret = models.CharField('签名密钥(加密)', max_length=500, blank=True, default='')
    public_key = models.TextField('公钥', blank=True, default='')
    token_lifetime_hours = models.IntegerField('Token有效期(小时)', default=24)
    auto_create_user = models.BooleanField('自动创建用户', default=False)
    default_role = models.ForeignKey(
        Role, verbose_name='默认角色', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    status = models.BooleanField('启用', default=False)
    config_params = models.JSONField('扩展参数', default=dict, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_sso_config'
        verbose_name = 'SSO配置'
        verbose_name_plural = 'SSO配置'

    def __str__(self):
        return self.sso_name


class SensitiveConfig(models.Model):
    """敏感配置表（加密存储）"""
    config_key = models.CharField('配置键', max_length=100, unique=True, db_index=True)
    config_value_encrypted = models.TextField('加密值')
    config_type = models.CharField('配置类型', max_length=50)  # SMTP/SMS/API_KEY/PAYMENT
    description = models.CharField('描述', max_length=500, blank=True, default='')
    encryption_method = models.CharField('加密方式', max_length=50, default='AES256')
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='更新人', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_sensitive_config'
        verbose_name = '敏感配置'
        verbose_name_plural = '敏感配置'

    def __str__(self):
        return f'{self.get_config_type_display()} - {self.config_key}'


class AuditLog(models.Model):
    """审计日志表"""
    AUDIT_TYPE_CHOICES = [
        ('LOGIN', '登录'),
        ('LOGOUT', '登出'),
        ('PERM_CHANGE', '权限变更'),
        ('ROLE_CHANGE', '角色变更'),
        ('CONFIG_CHANGE', '配置变更'),
        ('DATA_EXPORT', '数据导出'),
        ('SECURITY', '安全事件'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='用户', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    audit_type = models.CharField('审计类型', max_length=20, choices=AUDIT_TYPE_CHOICES)
    action = models.CharField('动作', max_length=100)
    target = models.CharField('目标', max_length=200, blank=True, default='')
    detail = models.JSONField('详情', default=dict, blank=True)
    ip_address = models.CharField('IP地址', max_length=50, blank=True, default='')
    user_agent = models.CharField('User-Agent', max_length=500, blank=True, default='')
    result = models.CharField('结果', max_length=20, default='SUCCESS')  # SUCCESS/FAILURE
    created_at = models.DateTimeField('创建时间', auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'sys_audit_log'
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        indexes = [
            models.Index(fields=['audit_type', 'created_at']),
            models.Index(fields=['user_id', 'created_at']),
        ]


class NotificationSetting(models.Model):
    """通知设置表"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, verbose_name='用户', on_delete=models.CASCADE,
        related_name='notification_setting'
    )
    email_enabled = models.BooleanField('邮件通知', default=True)
    sms_enabled = models.BooleanField('短信通知', default=False)
    system_enabled = models.BooleanField('系统通知', default=True)
    notify_types = models.JSONField('通知类型', default=list)  # 订单/库存/审批/系统
    quiet_hours_start = models.TimeField('免打扰开始', null=True, blank=True)
    quiet_hours_end = models.TimeField('免打扰结束', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_notification_setting'
        verbose_name = '通知设置'
        verbose_name_plural = '通知设置'

    def __str__(self):
        return f'{self.user.username} Notification'
