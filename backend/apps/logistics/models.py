from django.conf import settings
from django.db import models


class LogisticsProvider(models.Model):
    """物流商表"""
    name = models.CharField(max_length=100, verbose_name='物流商名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='物流商编码')
    type = models.CharField(max_length=20, blank=True, default='', verbose_name='类型')
    settlement_method = models.CharField(max_length=20, blank=True, default='', verbose_name='结算方式')
    contact = models.CharField(max_length=50, blank=True, default='', verbose_name='联系人')
    phone = models.CharField(max_length=20, blank=True, default='', verbose_name='联系电话')
    email = models.CharField(max_length=100, blank=True, default='', verbose_name='邮箱')
    address = models.CharField(max_length=500, blank=True, default='', verbose_name='地址')
    api_config = models.TextField(blank=True, default='', verbose_name='API对接配置(JSON)')
    api_status = models.BooleanField(default=False, verbose_name='API状态')
    description = models.CharField(max_length=500, blank=True, default='', verbose_name='备注说明')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    status = models.BooleanField(default=True, db_index=True, verbose_name='启用状态')

    class Meta:
        db_table = 'logistics_provider'
        verbose_name = '物流商'
        verbose_name_plural = verbose_name


class LogisticsChannel(models.Model):
    """物流渠道表"""
    provider = models.ForeignKey(LogisticsProvider, on_delete=models.CASCADE, related_name='channels', verbose_name='物流商')
    name = models.CharField(max_length=100, verbose_name='渠道名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='渠道编码')
    channel_type = models.CharField(max_length=20, blank=True, default='', verbose_name='渠道类型')
    base_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='基础费用')
    weight_fee = models.DecimalField(max_digits=10, decimal_places=4, default=0, verbose_name='每公斤费用')
    min_weight = models.DecimalField(max_digits=10, decimal_places=4, default=0, verbose_name='最低重量(kg)')
    max_weight = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='最高重量(kg)')
    origin = models.CharField(max_length=100, blank=True, default='', verbose_name='起运地')
    destination = models.CharField(max_length=100, blank=True, default='', verbose_name='目的国家/地区')
    estimated_days = models.IntegerField(null=True, blank=True, verbose_name='预计时效(天)')
    is_tax_included = models.BooleanField(default=False, verbose_name='是否含税')
    price_calculation = models.CharField(max_length=50, blank=True, default='', verbose_name='计价方式')
    settlement_type = models.CharField(max_length=20, blank=True, default='', verbose_name='结算方式')
    source = models.CharField(max_length=50, blank=True, default='', verbose_name='来源')
    price_track_enabled = models.BooleanField(default=False, verbose_name='是否启用价格跟踪')
    status = models.BooleanField(default=True, db_index=True, verbose_name='启用状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'logistics_channel'
        verbose_name = '物流渠道'
        verbose_name_plural = verbose_name


class ShippingOrder(models.Model):
    """自发货订单表"""
    order_no = models.CharField(max_length=50, unique=True, verbose_name='订单编号')
    channel = models.ForeignKey(LogisticsChannel, on_delete=models.PROTECT, verbose_name='物流渠道')
    address = models.ForeignKey('AddressBook', on_delete=models.PROTECT, verbose_name='收货地址')
    weight = models.DecimalField(max_digits=10, decimal_places=4, verbose_name='重量(kg)')
    volume_weight = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='体积重量(kg)')
    fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='运费')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    tracking_no = models.CharField(max_length=100, blank=True, default='', verbose_name='跟踪号')
    logistics_no = models.CharField(max_length=100, blank=True, default='', verbose_name='物流单号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='发货时间')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='签收时间')

    class Meta:
        db_table = 'logistics_shipping_order'
        verbose_name = '自发货订单'
        verbose_name_plural = verbose_name


class HeadOrder(models.Model):
    """头程订单表"""
    order_no = models.CharField(max_length=50, unique=True, verbose_name='运单号')
    transport_type = models.CharField(max_length=20, blank=True, default='', verbose_name='运输方式')
    provider = models.ForeignKey(LogisticsProvider, on_delete=models.PROTECT, verbose_name='物流商')
    channel = models.ForeignKey(LogisticsChannel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='物流渠道')
    from_warehouse_id = models.BigIntegerField(null=True, blank=True, verbose_name='发货仓库ID')
    to_warehouse_id = models.BigIntegerField(null=True, blank=True, verbose_name='收货仓库ID')
    destination_country = models.CharField(max_length=50, blank=True, default='', verbose_name='收货国家')
    related_order_no = models.CharField(max_length=100, blank=True, default='', verbose_name='关联单据号')
    estimated_weight = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='预估重量(kg)')
    actual_weight = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='实际重量(kg)')
    estimated_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='预估费用')
    actual_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='实际费用')
    estimated_days = models.IntegerField(null=True, blank=True, verbose_name='预计时效(天)')
    actual_days = models.IntegerField(null=True, blank=True, verbose_name='实际时效(天)')
    logistics_status = models.CharField(max_length=20, blank=True, default='', verbose_name='物流状态')
    logistics_status_time = models.DateTimeField(null=True, blank=True, verbose_name='物流状态时间')
    settlement_type = models.CharField(max_length=20, blank=True, default='', verbose_name='结算方式')
    internal_note = models.CharField(max_length=500, blank=True, default='', verbose_name='内部备注')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    tracking_no = models.CharField(max_length=100, blank=True, default='', verbose_name='跟踪号')
    origin = models.CharField(max_length=100, blank=True, default='', verbose_name='起运地')
    destination = models.CharField(max_length=100, blank=True, default='', verbose_name='目的地')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='发货时间')
    arrived_at = models.DateTimeField(null=True, blank=True, verbose_name='到达时间')

    class Meta:
        db_table = 'logistics_head_order'
        verbose_name = '头程订单'
        verbose_name_plural = verbose_name


class AddressBook(models.Model):
    """地址簿表"""
    address_name = models.CharField(max_length=100, verbose_name='地址名称')
    address_type = models.CharField(max_length=20, blank=True, default='', verbose_name='地址类型')
    company_name = models.CharField(max_length=100, blank=True, default='', verbose_name='公司名称')
    contact_name = models.CharField(max_length=50, verbose_name='联系人姓名')
    phone = models.CharField(max_length=20, verbose_name='联系电话')
    country = models.CharField(max_length=50, verbose_name='国家/地区')
    province = models.CharField(max_length=100, blank=True, default='', verbose_name='省/州')
    city = models.CharField(max_length=100, blank=True, default='', verbose_name='城市')
    district = models.CharField(max_length=100, blank=True, default='', verbose_name='区')
    address_line1 = models.CharField(max_length=200, blank=True, default='', verbose_name='详细地址1')
    address_line2 = models.CharField(max_length=200, blank=True, default='', verbose_name='详细地址2')
    zip_code = models.CharField(max_length=20, blank=True, default='', verbose_name='邮编')
    email = models.CharField(max_length=100, blank=True, default='', verbose_name='邮箱')
    is_default = models.BooleanField(default=False, verbose_name='是否默认地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'logistics_address_book'
        verbose_name = '地址簿'
        verbose_name_plural = verbose_name


class FreightTemplate(models.Model):
    """运费模板表"""
    name = models.CharField(max_length=100, verbose_name='模板名称')
    description = models.CharField(max_length=500, blank=True, default='', verbose_name='描述')
    valid_from = models.DateTimeField(null=True, blank=True, verbose_name='生效开始时间')
    valid_to = models.DateTimeField(null=True, blank=True, verbose_name='生效结束时间')
    warehouse_types = models.CharField(max_length=200, blank=True, default='', verbose_name='应用仓库类型(JSON)')
    logistics_types = models.CharField(max_length=200, blank=True, default='', verbose_name='应用物流类型(JSON)')
    rules = models.TextField(blank=True, default='', verbose_name='计费规则(JSON)')
    operator = models.CharField(max_length=50, blank=True, default='', verbose_name='操作人')
    status = models.BooleanField(default=True, verbose_name='启用状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'logistics_freight_template'
        verbose_name = '运费模板'
        verbose_name_plural = verbose_name


class DeclarationRule(models.Model):
    """申报规则表"""
    name = models.CharField(max_length=100, verbose_name='规则名称')
    hs_code = models.CharField(max_length=50, blank=True, default='', verbose_name='HS编码')
    category = models.CharField(max_length=100, blank=True, default='', verbose_name='商品类别')
    declared_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='申报价值')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='税率')
    status = models.BooleanField(default=True, verbose_name='启用状态')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'logistics_declaration_rule'
        verbose_name = '申报规则'
        verbose_name_plural = verbose_name


class TrackingNumberPool(models.Model):
    """跟踪号码池表"""
    tracking_no = models.CharField(max_length=100, unique=True, verbose_name='跟踪号码')
    provider = models.ForeignKey(LogisticsProvider, on_delete=models.CASCADE, verbose_name='所属物流商')
    status = models.BooleanField(default=False, verbose_name='使用状态(0未使用1已使用)')
    order_id = models.BigIntegerField(null=True, blank=True, verbose_name='关联订单ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='使用时间')

    class Meta:
        db_table = 'logistics_tracking_number_pool'
        verbose_name = '跟踪号码池'
        verbose_name_plural = verbose_name


class LogisticsNumberPool(models.Model):
    """物流号码池表"""
    logistics_no = models.CharField(max_length=100, unique=True, verbose_name='物流号码')
    provider = models.ForeignKey(LogisticsProvider, on_delete=models.CASCADE, verbose_name='所属物流商')
    status = models.BooleanField(default=False, verbose_name='使用状态')
    order_id = models.BigIntegerField(null=True, blank=True, verbose_name='关联订单ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='使用时间')

    class Meta:
        db_table = 'logistics_number_pool'
        verbose_name = '物流号码池'
        verbose_name_plural = verbose_name


class HeadReconciliation(models.Model):
    """头程对账单表"""
    bill_no = models.CharField(max_length=50, unique=True, verbose_name='账单编号')
    provider = models.ForeignKey(LogisticsProvider, on_delete=models.PROTECT, verbose_name='物流商')
    period_start = models.DateField(verbose_name='账单周期开始')
    period_end = models.DateField(verbose_name='账单周期结束')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='账单金额')
    matched_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='已匹配金额')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    reconciled_at = models.DateTimeField(null=True, blank=True, verbose_name='对账完成时间')

    class Meta:
        db_table = 'logistics_head_reconciliation'
        verbose_name = '头程对账单'
        verbose_name_plural = verbose_name


class LogisticsReconciliation(models.Model):
    """物流对账单表"""
    bill_no = models.CharField(max_length=50, unique=True, verbose_name='账单编号')
    provider = models.ForeignKey(LogisticsProvider, on_delete=models.PROTECT, verbose_name='物流商')
    period_start = models.DateField(verbose_name='账单周期开始')
    period_end = models.DateField(verbose_name='账单周期结束')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='账单金额')
    matched_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='已匹配金额')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    reconciled_at = models.DateTimeField(null=True, blank=True, verbose_name='对账完成时间')

    class Meta:
        db_table = 'logistics_reconciliation'
        verbose_name = '物流对账单'
        verbose_name_plural = verbose_name
