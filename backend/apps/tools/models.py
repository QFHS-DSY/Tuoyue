from django.conf import settings
from django.db import models


class WalmartMonitor(models.Model):
    """Walmart跟卖监控表"""
    product_id = models.CharField(max_length=100, verbose_name='商品ID')
    msku = models.CharField(max_length=100, verbose_name='MSKU')
    tag = models.CharField(max_length=100, blank=True, default='', verbose_name='标签')
    shop_id = models.BigIntegerField(null=True, blank=True, verbose_name='店铺ID')
    shop_name = models.CharField(max_length=100, blank=True, default='', verbose_name='店铺名称')
    has_buybox = models.BooleanField(default=False, verbose_name='是否获得BuyBox')
    seller_count = models.IntegerField(default=0, verbose_name='跟卖卖家数量')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='当前价格')
    buybox_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='BuyBox价格')
    monitor_status = models.CharField(max_length=20, default='ACTIVE', db_index=True, verbose_name='监控状态')
    follow_status = models.CharField(max_length=20, default='NO_FOLLOW', verbose_name='跟卖状态')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始监控时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='监控结束时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tools_walmart_monitor'
        verbose_name = 'Walmart跟卖监控'
        verbose_name_plural = verbose_name


class LogisticsQuery(models.Model):
    """物流查询记录表"""
    tracking_number = models.CharField(max_length=100, verbose_name='物流单号')
    logistics_provider = models.CharField(max_length=100, blank=True, default='', verbose_name='物流商')
    query_type = models.CharField(max_length=20, default='FAST', verbose_name='查询类型')
    status = models.CharField(max_length=50, blank=True, default='', verbose_name='物流状态')
    details = models.TextField(blank=True, default='', verbose_name='物流详情(JSON)')
    query_time = models.DateTimeField(auto_now_add=True, verbose_name='查询时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tools_logistics_query'
        verbose_name = '物流查询记录'
        verbose_name_plural = verbose_name


class AiModelTask(models.Model):
    """AI模特任务表"""
    task_no = models.CharField(max_length=50, unique=True, verbose_name='任务编号')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    original_image = models.CharField(max_length=500, verbose_name='原图路径')
    model_type = models.CharField(max_length=20, verbose_name='模特类型(human/mannequin)')
    model_id = models.BigIntegerField(null=True, blank=True, verbose_name='模特ID')
    skin_color = models.CharField(max_length=50, blank=True, default='', verbose_name='肤色')
    size = models.CharField(max_length=20, blank=True, default='', verbose_name='尺码')
    style = models.CharField(max_length=50, blank=True, default='', verbose_name='风格')
    result_image = models.CharField(max_length=500, blank=True, default='', verbose_name='结果图路径')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    error_message = models.TextField(blank=True, default='', verbose_name='错误信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tools_ai_model_task'
        verbose_name = 'AI模特任务'
        verbose_name_plural = verbose_name


class AiCutoutTask(models.Model):
    """AI抠图任务表"""
    task_no = models.CharField(max_length=50, unique=True, verbose_name='任务编号')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    original_image = models.CharField(max_length=500, verbose_name='原图路径')
    result_image = models.CharField(max_length=500, blank=True, default='', verbose_name='结果图路径')
    background_image = models.CharField(max_length=500, blank=True, default='', verbose_name='背景图路径')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    error_message = models.TextField(blank=True, default='', verbose_name='错误信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tools_ai_cutout_task'
        verbose_name = 'AI抠图任务'
        verbose_name_plural = verbose_name


class AiGenerateTask(models.Model):
    """AI生图任务表"""
    task_no = models.CharField(max_length=50, unique=True, verbose_name='任务编号')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    prompt = models.TextField(verbose_name='描述文本')
    style = models.CharField(max_length=50, blank=True, default='', verbose_name='风格')
    width = models.IntegerField(default=512, verbose_name='图片宽度')
    height = models.IntegerField(default=512, verbose_name='图片高度')
    result_image = models.CharField(max_length=500, blank=True, default='', verbose_name='结果图路径')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    error_message = models.TextField(blank=True, default='', verbose_name='错误信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tools_ai_generate_task'
        verbose_name = 'AI生图任务'
        verbose_name_plural = verbose_name


class ApprovalType(models.Model):
    """审批类型表"""
    name = models.CharField(max_length=50, verbose_name='类型名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='类型编码')
    description = models.CharField(max_length=500, blank=True, default='', verbose_name='类型描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tools_approval_type'
        verbose_name = '审批类型'
        verbose_name_plural = verbose_name


class ApprovalTask(models.Model):
    """审批任务表"""
    task_no = models.CharField(max_length=50, unique=True, verbose_name='审批编号')
    type = models.ForeignKey(ApprovalType, on_delete=models.PROTECT, verbose_name='审批类型')
    title = models.CharField(max_length=200, verbose_name='审批标题')
    summary = models.TextField(blank=True, default='', verbose_name='审批摘要')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='applied_tasks', verbose_name='申请人')
    applicant_name = models.CharField(max_length=50, blank=True, default='', verbose_name='申请人姓名')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_tasks', verbose_name='审批人')
    approver_name = models.CharField(max_length=50, blank=True, default='', verbose_name='审批人姓名')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tools_approval_task'
        verbose_name = '审批任务'
        verbose_name_plural = verbose_name


class ApprovalRecord(models.Model):
    """审批记录表"""
    task = models.ForeignKey(ApprovalTask, on_delete=models.CASCADE, related_name='records', verbose_name='审批任务')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='审批人')
    approver_name = models.CharField(max_length=50, blank=True, default='', verbose_name='审批人姓名')
    action = models.CharField(max_length=20, verbose_name='操作(APPROVE/REJECT)')
    comment = models.TextField(blank=True, default='', verbose_name='审批意见')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tools_approval_record'
        verbose_name = '审批记录'
        verbose_name_plural = verbose_name


class AiProductCopy(models.Model):
    """AI商品文案任务表"""
    task_no = models.CharField(max_length=50, unique=True, verbose_name='任务编号')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户')
    product_type = models.CharField(max_length=200, blank=True, default='', verbose_name='商品类型')
    target_audience = models.CharField(max_length=200, blank=True, default='', verbose_name='目标人群')
    brand_model = models.CharField(max_length=200, blank=True, default='', verbose_name='品牌&型号')
    language = models.CharField(max_length=20, blank=True, default='', verbose_name='语言')
    title = models.CharField(max_length=500, blank=True, default='', verbose_name='生成的标题')
    bullet_points = models.TextField(blank=True, default='', verbose_name='生成的要点')
    description = models.TextField(blank=True, default='', verbose_name='生成的商品描述')
    keywords = models.CharField(max_length=500, blank=True, default='', verbose_name='关键词')
    status = models.CharField(max_length=20, default='DRAFT', db_index=True, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tools_ai_product_copy'
        verbose_name = 'AI商品文案'
        verbose_name_plural = verbose_name


class AlertRule(models.Model):
    """预警规则表"""
    rule_name = models.CharField(max_length=100, unique=True, verbose_name='规则名称')
    dimension = models.CharField(max_length=20, verbose_name='维度')
    alert_model = models.CharField(max_length=50, blank=True, default='', verbose_name='预警模型')
    alert_objects = models.TextField(blank=True, default='', verbose_name='预警对象(JSON)')
    monitor_rules = models.TextField(blank=True, default='', verbose_name='监控规则(JSON)')
    recipients = models.TextField(blank=True, default='', verbose_name='消息接收人(JSON)')
    notify_methods = models.TextField(blank=True, default='', verbose_name='通知方式(JSON)')
    is_enabled = models.BooleanField(default=False, verbose_name='是否开启')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tools_alert_rule'
        verbose_name = '预警规则'
        verbose_name_plural = verbose_name


class AlertMessage(models.Model):
    """预警消息表"""
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, verbose_name='预警规则')
    title = models.CharField(max_length=200, blank=True, default='', verbose_name='消息标题')
    content = models.TextField(blank=True, default='', verbose_name='消息内容')
    level = models.CharField(max_length=20, blank=True, default='', verbose_name='消息级别')
    read_status = models.BooleanField(default=False, verbose_name='已读状态')
    process_status = models.CharField(max_length=20, default='UNPROCESSED', verbose_name='处理状态')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tools_alert_message'
        verbose_name = '预警消息'
        verbose_name_plural = verbose_name


class PriceAdjustTask(models.Model):
    """调价任务表"""
    task_name = models.CharField(max_length=100, verbose_name='任务名称')
    platform = models.CharField(max_length=30, verbose_name='平台')
    adjust_type = models.CharField(max_length=20, verbose_name='调价类型')
    adjust_scope = models.TextField(blank=True, default='', verbose_name='调价范围(JSON)')
    adjust_rules = models.TextField(blank=True, default='', verbose_name='调价规则(JSON)')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    is_enabled = models.BooleanField(default=True, verbose_name='是否开启')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tools_price_adjust_task'
        verbose_name = '调价任务'
        verbose_name_plural = verbose_name


class PriceAdjustRule(models.Model):
    """调价规则表"""
    task = models.ForeignKey(PriceAdjustTask, on_delete=models.CASCADE, related_name='rules', verbose_name='调价任务')
    rule_type = models.CharField(max_length=50, verbose_name='规则类型')
    rule_params = models.TextField(blank=True, default='', verbose_name='规则参数(JSON)')
    sort_order = models.IntegerField(default=0, verbose_name='排序号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tools_price_adjust_rule'
        verbose_name = '调价规则'
        verbose_name_plural = verbose_name


class PriceAdjustLog(models.Model):
    """调价日志表"""
    task = models.ForeignKey(PriceAdjustTask, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='调价任务')
    product_id = models.BigIntegerField(verbose_name='商品ID')
    platform = models.CharField(max_length=30, verbose_name='平台')
    before_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='调整前价格')
    after_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='调整后价格')
    adjust_type = models.CharField(max_length=20, verbose_name='调整类型')
    status = models.CharField(max_length=20, db_index=True, verbose_name='状态')
    message = models.TextField(blank=True, default='', verbose_name='结果信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tools_price_adjust_log'
        verbose_name = '调价日志'
        verbose_name_plural = verbose_name
