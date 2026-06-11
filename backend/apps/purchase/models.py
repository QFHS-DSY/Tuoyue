from django.conf import settings
from django.db import models


class Supplier(models.Model):
    """供应商表"""
    code = models.CharField(max_length=50, unique=True, verbose_name='供应商编码')
    name = models.CharField(max_length=100, verbose_name='供应商名称')
    warehouse_name = models.CharField(max_length=100, blank=True, default='', verbose_name='供应商仓库')
    belong = models.CharField(max_length=50, blank=True, default='', verbose_name='所属')
    contact_name = models.CharField(max_length=50, blank=True, default='', verbose_name='联系人')
    phone = models.CharField(max_length=20, blank=True, default='', verbose_name='联系电话')
    email = models.CharField(max_length=100, blank=True, default='', verbose_name='邮箱')
    address = models.CharField(max_length=500, blank=True, default='', verbose_name='地址')
    store_account = models.CharField(max_length=100, blank=True, default='', verbose_name='门店/账号')
    settlement_method = models.CharField(max_length=50, blank=True, default='', verbose_name='结算方式')
    settlement_desc = models.CharField(max_length=500, blank=True, default='', verbose_name='结算描述')
    payment_method = models.CharField(max_length=50, blank=True, default='', verbose_name='支付方式')
    portal_enabled = models.BooleanField(default=True, verbose_name='门户启用')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name='评级')
    status = models.BooleanField(default=True, verbose_name='启用状态')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_supplier'
        verbose_name = '供应商'
        verbose_name_plural = verbose_name


class PurchasePlan(models.Model):
    """采购计划表"""
    plan_no = models.CharField(max_length=50, unique=True, verbose_name='计划编号')
    warehouse_id = models.BigIntegerField(db_index=True, verbose_name='仓库ID')
    shop_id = models.BigIntegerField(null=True, blank=True, db_index=True, verbose_name='店铺ID')
    country = models.CharField(max_length=50, blank=True, default='', verbose_name='国家/地区')
    plan_date = models.DateField(verbose_name='计划日期')
    status = models.CharField(max_length=20, default='DRAFT', db_index=True, verbose_name='状态')
    purchaser = models.CharField(max_length=50, blank=True, default='', verbose_name='采购员')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_plan'
        verbose_name = '采购计划'
        verbose_name_plural = verbose_name


class PurchasePlanItem(models.Model):
    """采购计划明细表"""
    plan = models.ForeignKey(PurchasePlan, on_delete=models.CASCADE, related_name='items', verbose_name='采购计划')
    sku_id = models.BigIntegerField(verbose_name='商品SKU ID')
    product_image = models.CharField(max_length=500, blank=True, default='', verbose_name='商品图片')
    business_identifier = models.CharField(max_length=100, blank=True, default='', verbose_name='业务标识')
    product_name = models.CharField(max_length=200, blank=True, default='', verbose_name='商品名称')
    shop_id = models.BigIntegerField(null=True, blank=True, verbose_name='店铺ID')
    country = models.CharField(max_length=50, blank=True, default='', verbose_name='国家/地区')
    fnsku = models.CharField(max_length=100, blank=True, default='', verbose_name='FNSKU')
    tags = models.CharField(max_length=500, blank=True, default='', verbose_name='标签')
    warehouse_id = models.BigIntegerField(null=True, blank=True, verbose_name='仓库ID')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='计划采购量')
    fba_suggest_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='FBA建议采购量')
    per_box_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='单箱数量')
    box_count = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='箱数')
    model_arrival_date = models.DateField(null=True, blank=True, verbose_name='模型到货时间')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='单价')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='金额')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')

    class Meta:
        db_table = 'purchase_plan_item'
        verbose_name = '采购计划明细'
        verbose_name_plural = verbose_name


class PurchaseOrder(models.Model):
    """采购单表"""
    order_no = models.CharField(max_length=50, unique=True, verbose_name='订单编号')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='供应商')
    warehouse_id = models.BigIntegerField(verbose_name='收货仓库ID')
    shop_id = models.BigIntegerField(null=True, blank=True, verbose_name='店铺ID')
    logistics_provider_id = models.BigIntegerField(null=True, blank=True, verbose_name='物流商ID')
    order_type = models.CharField(max_length=20, default='NORMAL', verbose_name='采购类型')
    account_1688_id = models.BigIntegerField(null=True, blank=True, verbose_name='1688账号ID')
    receiver_address = models.CharField(max_length=500, blank=True, default='', verbose_name='收货地址')
    platform_order_type = models.CharField(max_length=20, blank=True, default='', verbose_name='订单类型')
    trade_method = models.CharField(max_length=50, blank=True, default='', verbose_name='交易方式')
    settlement_date = models.DateField(null=True, blank=True, verbose_name='结算日期')
    fnsku_status = models.CharField(max_length=20, default='PENDING', verbose_name='1688状态')
    fnsku_order_no = models.CharField(max_length=100, blank=True, default='', verbose_name='1688订单号')
    fnsku_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='1688应付金额')
    fnsku_shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='1688运费')
    seller_message = models.CharField(max_length=500, blank=True, default='', verbose_name='卖家留言')
    order_date = models.DateField(verbose_name='订单日期')
    delivery_date = models.DateField(null=True, blank=True, verbose_name='预计交货日期')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='订单总金额')
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='税额合计')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='已付金额')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')
    auditor = models.CharField(max_length=50, blank=True, default='', verbose_name='审核人')
    audit_time = models.DateTimeField(null=True, blank=True, verbose_name='审核时间')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_order'
        verbose_name = '采购单'
        verbose_name_plural = verbose_name


class PurchaseOrderItem(models.Model):
    """采购单明细表"""
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items', verbose_name='采购单')
    sku_id = models.BigIntegerField(verbose_name='商品SKU ID')
    product_image = models.CharField(max_length=500, blank=True, default='', verbose_name='商品图片')
    business_identifier = models.CharField(max_length=100, blank=True, default='', verbose_name='业务标识')
    product_name = models.CharField(max_length=200, blank=True, default='', verbose_name='商品名称')
    shop_id = models.BigIntegerField(null=True, blank=True, verbose_name='店铺ID')
    msku = models.CharField(max_length=100, blank=True, default='', verbose_name='MSKU')
    fnsku = models.CharField(max_length=100, blank=True, default='', verbose_name='FNSKU')
    tags = models.CharField(max_length=500, blank=True, default='', verbose_name='标签')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='单价')
    stock_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='备货单价')
    supplier_quote_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='供应商报价')
    retail_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='零售价')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='采购量')
    received_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='到货量')
    pending_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='待到货量')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='金额')
    estimated_arrival_date = models.DateField(null=True, blank=True, verbose_name='预计到货时间')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')

    class Meta:
        db_table = 'purchase_order_item'
        verbose_name = '采购单明细'
        verbose_name_plural = verbose_name


class OutsourcingOrder(models.Model):
    """委外订单表"""
    order_no = models.CharField(max_length=50, unique=True, verbose_name='委外单号')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='加工商')
    warehouse_id = models.BigIntegerField(verbose_name='收货仓库ID')
    shop_id = models.BigIntegerField(null=True, blank=True, verbose_name='店铺ID')
    logistics_provider_id = models.BigIntegerField(null=True, blank=True, verbose_name='物流商ID')
    order_date = models.DateField(verbose_name='订单日期')
    delivery_date = models.DateField(null=True, blank=True, verbose_name='预计交货日期')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='订单总金额')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    purchaser = models.CharField(max_length=50, blank=True, default='', verbose_name='采购员')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_outsourcing_order'
        verbose_name = '委外订单'
        verbose_name_plural = verbose_name


class OutsourcingOrderItem(models.Model):
    """委外订单明细表"""
    order = models.ForeignKey(OutsourcingOrder, on_delete=models.CASCADE, related_name='items', verbose_name='委外订单')
    product_sku_id = models.BigIntegerField(verbose_name='加工品SKU ID')
    product_image = models.CharField(max_length=500, blank=True, default='', verbose_name='商品图片')
    product_name = models.CharField(max_length=200, blank=True, default='', verbose_name='商品名称')
    shop_id = models.BigIntegerField(null=True, blank=True, verbose_name='店铺ID')
    msku = models.CharField(max_length=100, blank=True, default='', verbose_name='MSKU')
    fnsku = models.CharField(max_length=100, blank=True, default='', verbose_name='FNSKU')
    tags = models.CharField(max_length=500, blank=True, default='', verbose_name='标签')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='委外数量')
    received_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='到货量')
    pending_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='待到货量')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='加工单价')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='金额')
    purchase_plan_no = models.CharField(max_length=50, blank=True, default='', verbose_name='采购计划号')
    process_plan_no = models.CharField(max_length=50, blank=True, default='', verbose_name='加工计划号')
    estimated_arrival_date = models.DateField(null=True, blank=True, verbose_name='预计到货时间')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')

    class Meta:
        db_table = 'purchase_outsourcing_order_item'
        verbose_name = '委外订单明细'
        verbose_name_plural = verbose_name


class OutsourcingMaterial(models.Model):
    """委外原材料表"""
    order = models.ForeignKey(OutsourcingOrder, on_delete=models.CASCADE, related_name='materials', verbose_name='委外订单')
    order_item = models.ForeignKey(OutsourcingOrderItem, on_delete=models.CASCADE, null=True, blank=True, verbose_name='关联明细')
    sku_id = models.BigIntegerField(verbose_name='原材料SKU ID')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='数量')
    issued_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='已发数量')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')

    class Meta:
        db_table = 'purchase_outsourcing_material'
        verbose_name = '委外原材料'
        verbose_name_plural = verbose_name


class ChangeOrder(models.Model):
    """变更单表"""
    change_no = models.CharField(max_length=50, unique=True, verbose_name='变更单号')
    order_type = models.CharField(max_length=20, verbose_name='订单类型')
    order_id = models.BigIntegerField(verbose_name='关联订单ID')
    change_type = models.CharField(max_length=20, verbose_name='变更类型')
    change_reason = models.CharField(max_length=500, blank=True, default='', verbose_name='变更原因')
    before_data = models.TextField(blank=True, default='', verbose_name='变更前数据(JSON)')
    after_data = models.TextField(blank=True, default='', verbose_name='变更后数据(JSON)')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'purchase_change_order'
        verbose_name = '变更单'
        verbose_name_plural = verbose_name


class ReturnOrder(models.Model):
    """退货单表"""
    return_no = models.CharField(max_length=50, unique=True, verbose_name='退货单号')
    order_type = models.CharField(max_length=20, verbose_name='订单类型')
    purchase_order_id = models.BigIntegerField(null=True, blank=True, verbose_name='关联采购单ID')
    outsourcing_order_id = models.BigIntegerField(null=True, blank=True, verbose_name='关联委外订单ID')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='供应商')
    warehouse_id = models.BigIntegerField(verbose_name='退货仓库ID')
    shop_id = models.BigIntegerField(null=True, blank=True, verbose_name='店铺ID')
    logistics_provider_id = models.BigIntegerField(null=True, blank=True, verbose_name='物流商ID')
    return_type = models.CharField(max_length=20, verbose_name='退货类型')
    return_date = models.DateField(verbose_name='退货日期')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='退货金额')
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='税额合计')
    deduct_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='扣款金额')
    refundable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='可退款金额')
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='退款金额')
    outbound_order_id = models.BigIntegerField(null=True, blank=True, verbose_name='关联出库单ID')
    receipt_order_id = models.BigIntegerField(null=True, blank=True, verbose_name='关联收款单ID')
    return_reason = models.CharField(max_length=200, blank=True, default='', verbose_name='退货原因')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_return_order'
        verbose_name = '退货单'
        verbose_name_plural = verbose_name


class ReturnOrderItem(models.Model):
    """退货单明细表"""
    return_order = models.ForeignKey(ReturnOrder, on_delete=models.CASCADE, related_name='items', verbose_name='退货单')
    purchase_order_item_id = models.BigIntegerField(null=True, blank=True, verbose_name='关联采购明细ID')
    sku_id = models.BigIntegerField(verbose_name='商品SKU ID')
    product_image = models.CharField(max_length=500, blank=True, default='', verbose_name='商品图片')
    business_identifier = models.CharField(max_length=100, blank=True, default='', verbose_name='业务标识')
    product_name = models.CharField(max_length=200, blank=True, default='', verbose_name='商品名称')
    shop_id = models.BigIntegerField(null=True, blank=True, verbose_name='店铺ID')
    msku = models.CharField(max_length=100, blank=True, default='', verbose_name='MSKU')
    fnsku = models.CharField(max_length=100, blank=True, default='', verbose_name='FNSKU')
    tags = models.CharField(max_length=500, blank=True, default='', verbose_name='标签')
    purchase_order_no = models.CharField(max_length=50, blank=True, default='', verbose_name='采购单号')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='退货数量')
    pending_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='待审核数量')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='单价')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='金额')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')

    class Meta:
        db_table = 'purchase_return_order_item'
        verbose_name = '退货单明细'
        verbose_name_plural = verbose_name


class ProcessPlan(models.Model):
    """加工计划表"""
    plan_no = models.CharField(max_length=50, unique=True, verbose_name='计划编号')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='供应商')
    shop_id = models.BigIntegerField(null=True, blank=True, verbose_name='店铺ID')
    warehouse_id = models.BigIntegerField(null=True, blank=True, verbose_name='仓库ID')
    country = models.CharField(max_length=50, blank=True, default='', verbose_name='国家/地区')
    purchase_batch_no = models.CharField(max_length=50, blank=True, default='', verbose_name='采购批次号')
    purchase_plan_no = models.CharField(max_length=50, blank=True, default='', verbose_name='采购计划号')
    plan_date = models.DateField(verbose_name='计划日期')
    expected_arrival_date = models.DateField(null=True, blank=True, verbose_name='期望到货时间')
    status = models.CharField(max_length=20, default='DRAFT', db_index=True, verbose_name='状态')
    plan_purchase_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='计划采购量')
    plan_process_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='计划加工量')
    processable_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='可加工数量')
    processing_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='加工中数量')
    processed_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='已加工数量')
    expected_available_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='期望可用库存')
    product_tags = models.CharField(max_length=500, blank=True, default='', verbose_name='产品标签')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_process_plan'
        verbose_name = '加工计划'
        verbose_name_plural = verbose_name


class Account1688Auth(models.Model):
    """1688账号授权表"""
    account_name = models.CharField(max_length=100, verbose_name='账号名称')
    account_type = models.CharField(max_length=20, verbose_name='账号类型')
    auth_token = models.CharField(max_length=500, blank=True, default='', verbose_name='授权令牌')
    refresh_token = models.CharField(max_length=500, blank=True, default='', verbose_name='刷新令牌')
    token_expire_time = models.DateTimeField(null=True, blank=True, verbose_name='令牌过期时间')
    user_id = models.CharField(max_length=100, blank=True, default='', verbose_name='1688用户ID')
    user_name = models.CharField(max_length=100, blank=True, default='', verbose_name='1688用户名')
    status = models.BooleanField(default=True, verbose_name='启用状态')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_account_1688_auth'
        verbose_name = '1688账号授权'
        verbose_name_plural = verbose_name


class Sku1688Mapping(models.Model):
    """1688商品配对表"""
    sku_id = models.BigIntegerField(verbose_name='系统SKU ID')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='供应商')
    product_id = models.CharField(max_length=100, verbose_name='1688商品ID')
    product_name = models.CharField(max_length=200, blank=True, default='', verbose_name='1688商品名称')
    product_url = models.CharField(max_length=500, blank=True, default='', verbose_name='1688商品链接')
    product_attribute = models.CharField(max_length=500, blank=True, default='', verbose_name='1688商品属性')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='参考单价')
    min_order_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name='起订量')
    status = models.BooleanField(default=True, verbose_name='启用状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_sku_1688_mapping'
        verbose_name = '1688商品配对'
        verbose_name_plural = verbose_name


class Order1688(models.Model):
    """1688订单表"""
    order_no = models.CharField(max_length=50, unique=True, verbose_name='1688订单编号')
    platform_order_no = models.CharField(max_length=100, verbose_name='平台订单号')
    supplier_id = models.BigIntegerField(null=True, blank=True, verbose_name='供应商ID')
    supplier_name = models.CharField(max_length=100, blank=True, default='', verbose_name='供应商名称')
    product_name = models.CharField(max_length=200, blank=True, default='', verbose_name='1688商品名称')
    product_image = models.CharField(max_length=500, blank=True, default='', verbose_name='商品图片')
    product_attribute = models.CharField(max_length=500, blank=True, default='', verbose_name='1688属性')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='单价')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='数量')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='订单金额')
    order_date = models.DateTimeField(verbose_name='下单日期')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    platform_status = models.CharField(max_length=50, blank=True, default='', verbose_name='1688订单状态')
    logistics_no = models.CharField(max_length=100, blank=True, default='', verbose_name='物流单号')
    logistics_status = models.CharField(max_length=50, blank=True, default='', verbose_name='物流状态')
    synced = models.BooleanField(default=False, verbose_name='是否已同步')
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name='同步时间')
    purchase_order_id = models.BigIntegerField(null=True, blank=True, verbose_name='关联采购单ID')
    purchase_order_created = models.BooleanField(default=False, verbose_name='是否已生成采购单')
    release_status = models.CharField(max_length=20, default='PENDING', verbose_name='收款放行状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_order_1688'
        verbose_name = '1688订单'
        verbose_name_plural = verbose_name


class SupplierReconciliation(models.Model):
    """供应商对账单表"""
    bill_no = models.CharField(max_length=50, unique=True, verbose_name='账单编号')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='供应商')
    period_start = models.DateField(verbose_name='账单周期开始')
    period_end = models.DateField(verbose_name='账单周期结束')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='账单金额')
    matched_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='已匹配金额')
    unmatched_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='未匹配金额')
    difference_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='差异金额')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='已付金额')
    unpaid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='未付金额')
    payable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='应付金额')
    actual_paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='实付金额')
    return_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='退货金额')
    profit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='预估利润')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_supplier_reconciliation'
        verbose_name = '供应商对账单'
        verbose_name_plural = verbose_name


class TransferOrder(models.Model):
    """调拨单表"""
    transfer_no = models.CharField(max_length=50, unique=True, verbose_name='调拨单号')
    from_warehouse_id = models.BigIntegerField(verbose_name='源仓库ID')
    to_warehouse_id = models.BigIntegerField(verbose_name='目标仓库ID')
    shop_id = models.BigIntegerField(null=True, blank=True, verbose_name='店铺ID')
    logistics_provider_id = models.BigIntegerField(null=True, blank=True, verbose_name='物流商ID')
    transfer_date = models.DateField(verbose_name='调拨日期')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_transfer_order'
        verbose_name = '调拨单'
        verbose_name_plural = verbose_name


class TransferOrderItem(models.Model):
    """调拨单明细表"""
    transfer_order = models.ForeignKey(TransferOrder, on_delete=models.CASCADE, related_name='items', verbose_name='调拨单')
    sku_id = models.BigIntegerField(verbose_name='商品SKU ID')
    product_image = models.CharField(max_length=500, blank=True, default='', verbose_name='商品图片')
    product_name = models.CharField(max_length=200, blank=True, default='', verbose_name='商品名称')
    shop_id = models.BigIntegerField(null=True, blank=True, verbose_name='店铺ID')
    msku = models.CharField(max_length=100, blank=True, default='', verbose_name='MSKU')
    fnsku = models.CharField(max_length=100, blank=True, default='', verbose_name='FNSKU')
    tags = models.CharField(max_length=500, blank=True, default='', verbose_name='标签')
    available_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='可用商品数量')
    transfer_quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='本次调拨数量')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')

    class Meta:
        db_table = 'purchase_transfer_order_item'
        verbose_name = '调拨单明细'
        verbose_name_plural = verbose_name


class SupplierPortalConfig(models.Model):
    """供应商门户配置表"""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='供应商')
    purchase_order_view = models.BooleanField(default=False, verbose_name='采购单查看权限')
    purchase_order_export = models.BooleanField(default=False, verbose_name='采购单导出权限')
    purchase_order_print_contract = models.BooleanField(default=False, verbose_name='打印采购合同权限')
    purchase_order_print_barcode = models.BooleanField(default=False, verbose_name='打印产品条码权限')
    purchase_order_print_fnsku = models.BooleanField(default=False, verbose_name='打印FNSKU条码权限')
    receipt_order_view = models.BooleanField(default=False, verbose_name='收货单查看权限')
    receipt_order_add = models.BooleanField(default=False, verbose_name='收货单添加权限')
    receipt_order_edit = models.BooleanField(default=False, verbose_name='收货单编辑权限')
    receipt_order_delete = models.BooleanField(default=False, verbose_name='收货单删除权限')
    barcode_template_id = models.BigIntegerField(null=True, blank=True, verbose_name='打印模板ID')
    contract_template_id = models.BigIntegerField(null=True, blank=True, verbose_name='合同模板ID')
    status = models.CharField(max_length=20, default='DISABLED', db_index=True, verbose_name='门户状态')
    invitation_code = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='邀请码')
    invitation_url = models.CharField(max_length=500, blank=True, default='', verbose_name='邀请链接')
    invitation_message = models.TextField(blank=True, default='', verbose_name='邀请语')
    purchase_company_name = models.CharField(max_length=200, blank=True, default='', verbose_name='采购方展示名称')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_supplier_portal_config'
        verbose_name = '供应商门户配置'
        verbose_name_plural = verbose_name


class SupplierPortalAccount(models.Model):
    """供应商门户账号表"""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='关联供应商')
    phone = models.CharField(max_length=20, unique=True, verbose_name='注册手机号')
    password = models.CharField(max_length=200, verbose_name='密码(加密)')
    username = models.CharField(max_length=50, blank=True, default='', verbose_name='用户名')
    status = models.CharField(max_length=20, default='ACTIVE', verbose_name='账号状态')
    last_login_at = models.DateTimeField(null=True, blank=True, verbose_name='最后登录时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_supplier_portal_account'
        verbose_name = '供应商门户账号'
        verbose_name_plural = verbose_name


class SupplierMessage(models.Model):
    """供应商消息表"""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='供应商')
    message_type = models.CharField(max_length=20, blank=True, default='', verbose_name='消息类型')
    title = models.CharField(max_length=200, blank=True, default='', verbose_name='消息标题')
    content = models.TextField(blank=True, default='', verbose_name='消息内容')
    order_id = models.BigIntegerField(null=True, blank=True, verbose_name='关联订单ID')
    read_status = models.BooleanField(default=False, verbose_name='已读状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'purchase_supplier_message'
        verbose_name = '供应商消息'
        verbose_name_plural = verbose_name


class SupplierDeliveryOrder(models.Model):
    """供应商送货单表"""
    delivery_no = models.CharField(max_length=50, unique=True, verbose_name='送货单号')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='供应商')
    purchase_order_id = models.BigIntegerField(null=True, blank=True, verbose_name='关联采购单ID')
    warehouse_id = models.BigIntegerField(verbose_name='收货仓库ID')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    delivery_date = models.DateField(null=True, blank=True, verbose_name='送货日期')
    creator_type = models.CharField(max_length=20, blank=True, default='', verbose_name='创建类型')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_supplier_delivery_order'
        verbose_name = '供应商送货单'
        verbose_name_plural = verbose_name


class SupplierDeliveryItem(models.Model):
    """供应商送货单明细表"""
    delivery_order = models.ForeignKey(SupplierDeliveryOrder, on_delete=models.CASCADE, related_name='items', verbose_name='送货单')
    sku_id = models.BigIntegerField(verbose_name='商品SKU ID')
    product_name = models.CharField(max_length=200, blank=True, default='', verbose_name='商品名称')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='送货数量')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')

    class Meta:
        db_table = 'purchase_supplier_delivery_item'
        verbose_name = '供应商送货单明细'
        verbose_name_plural = verbose_name
