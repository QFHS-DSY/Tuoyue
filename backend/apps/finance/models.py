from django.conf import settings
from django.db import models


class PaymentRequestPool(models.Model):
    """请款池表"""
    pool_type = models.CharField(max_length=20, verbose_name='请款池类型')
    source_type = models.CharField(max_length=20, verbose_name='来源类型')
    source_no = models.CharField(max_length=50, db_index=True, verbose_name='来源单据号')
    related_no = models.CharField(max_length=50, blank=True, default='', verbose_name='关联单据号')
    supplier_id = models.BigIntegerField(null=True, blank=True, db_index=True, verbose_name='供应商/物流商ID')
    supplier_name = models.CharField(max_length=100, blank=True, default='', verbose_name='供应商/物流商名称')
    payee_object = models.CharField(max_length=100, blank=True, default='', verbose_name='应付对象')
    payee_object_type = models.CharField(max_length=20, blank=True, default='', verbose_name='应付对象类型')
    purchase_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='采购金额')
    goods_value = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='货值')
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='运费')
    other_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='其他费用')
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='折扣金额')
    payable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='应付金额')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='已付金额')
    received_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='已收金额')
    real_paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='实付金额')
    unapplied_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='未申请金额')
    applying_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='申请中金额')
    prepay_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='预付比例(%)')
    currency = models.CharField(max_length=10, default='CNY', verbose_name='币种')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='汇率')
    exchange_rate_type = models.CharField(max_length=20, default='PAYMENT', verbose_name='汇率类型')
    apply_dimension = models.CharField(max_length=20, blank=True, default='', verbose_name='请款维度')
    status = models.CharField(max_length=20, default='UNAPPLIED', db_index=True, verbose_name='状态')
    purchase_order_status = models.CharField(max_length=20, blank=True, default='', verbose_name='采购单状态')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_payment_request_pool'
        verbose_name = '请款池'
        verbose_name_plural = verbose_name


class PaymentRequest(models.Model):
    """请款单表"""
    request_no = models.CharField(max_length=50, unique=True, verbose_name='请款单号')
    supplier_id = models.BigIntegerField(db_index=True, verbose_name='供应商ID')
    supplier_name = models.CharField(max_length=100, verbose_name='供应商名称')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='请款总金额')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='已付款金额')
    currency = models.CharField(max_length=10, default='CNY', verbose_name='币种')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='汇率')
    exchange_rate_type = models.CharField(max_length=20, default='REQUEST', verbose_name='汇率类型')
    status = models.CharField(max_length=20, default='PENDING_APPROVAL', db_index=True, verbose_name='状态')
    approval_level = models.IntegerField(default=1, verbose_name='当前审批级别')
    max_approval_level = models.IntegerField(default=1, verbose_name='最大审批级别')
    payable_type = models.CharField(max_length=20, verbose_name='应付费用类型')
    remark = models.TextField(blank=True, default='', verbose_name='备注')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_payment_request'
        verbose_name = '请款单'
        verbose_name_plural = verbose_name


class PaymentRequestItem(models.Model):
    """请款单明细表"""
    request = models.ForeignKey(PaymentRequest, on_delete=models.CASCADE, related_name='items', verbose_name='请款单')
    source_type = models.CharField(max_length=20, verbose_name='来源类型')
    source_no = models.CharField(max_length=50, verbose_name='来源单据号')
    item_name = models.CharField(max_length=200, verbose_name='项目名称')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='数量')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='单价')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='金额')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')

    class Meta:
        db_table = 'finance_payment_request_item'
        verbose_name = '请款单明细'
        verbose_name_plural = verbose_name


class PaymentRecord(models.Model):
    """付款记录表"""
    request = models.ForeignKey(PaymentRequest, on_delete=models.CASCADE, related_name='payment_records', verbose_name='请款单')
    pay_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='付款金额')
    pay_currency = models.CharField(max_length=10, default='CNY', verbose_name='付款币种')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='付款时汇率')
    pay_method = models.CharField(max_length=20, blank=True, default='', verbose_name='付款方式')
    pay_date = models.DateField(verbose_name='付款日期')
    payer_id = models.BigIntegerField(null=True, blank=True, verbose_name='付款人ID')
    payer_name = models.CharField(max_length=50, blank=True, default='', verbose_name='付款人名称')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_payment_record'
        verbose_name = '付款记录'
        verbose_name_plural = verbose_name


class ReceiptOrder(models.Model):
    """收款单表"""
    receipt_no = models.CharField(max_length=50, unique=True, verbose_name='收款单号')
    customer_id = models.BigIntegerField(null=True, blank=True, verbose_name='客户ID')
    customer_name = models.CharField(max_length=100, verbose_name='客户名称')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='收款总金额')
    received_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='已收款金额')
    currency = models.CharField(max_length=10, default='CNY', verbose_name='币种')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    remark = models.TextField(blank=True, default='', verbose_name='备注')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_receipt_order'
        verbose_name = '收款单'
        verbose_name_plural = verbose_name


class ReceiptOrderItem(models.Model):
    """收款单明细表"""
    receipt = models.ForeignKey(ReceiptOrder, on_delete=models.CASCADE, related_name='items', verbose_name='收款单')
    source_no = models.CharField(max_length=50, blank=True, default='', verbose_name='来源单据号')
    item_name = models.CharField(max_length=200, verbose_name='项目名称')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='金额')
    received_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='已收金额')

    class Meta:
        db_table = 'finance_receipt_order_item'
        verbose_name = '收款单明细'
        verbose_name_plural = verbose_name


class TransactionFlow(models.Model):
    """往来流水表"""
    flow_no = models.CharField(max_length=50, unique=True, verbose_name='流水号')
    transaction_type = models.CharField(max_length=20, verbose_name='交易类型(收款/付款)')
    source_type = models.CharField(max_length=20, verbose_name='来源类型')
    source_no = models.CharField(max_length=50, db_index=True, verbose_name='来源单据号')
    related_no = models.CharField(max_length=50, blank=True, default='', verbose_name='关联单据号')
    counterparty_id = models.BigIntegerField(null=True, blank=True, verbose_name='交易对方ID')
    counterparty_name = models.CharField(max_length=100, verbose_name='交易对方名称')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='金额(收款为负,付款为正)')
    currency = models.CharField(max_length=10, default='CNY', verbose_name='币种')
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='汇率')
    original_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='原币金额')
    balance_before = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='交易前余额')
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='交易后余额')
    pay_method = models.CharField(max_length=20, blank=True, default='', verbose_name='付款方式')
    pay_account = models.CharField(max_length=100, blank=True, default='', verbose_name='付款账户')
    transaction_date = models.DateField(db_index=True, verbose_name='交易日期')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_transaction_flow'
        verbose_name = '往来流水'
        verbose_name_plural = verbose_name


class OrderProfit(models.Model):
    """订单利润表"""
    order_id = models.CharField(max_length=50, verbose_name='订单ID')
    msku = models.CharField(max_length=100, verbose_name='MSKU')
    sku = models.CharField(max_length=100, blank=True, default='', verbose_name='SKU')
    sales_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='销售额')
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='采购成本')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='头程费用')
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='平台费')
    fba_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='FBA费用')
    advertising_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='广告费')
    profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='利润')
    profit_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='利润率')
    settlement_month = models.CharField(max_length=7, db_index=True, verbose_name='结算月份(YYYY-MM)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_order_profit'
        verbose_name = '订单利润'
        verbose_name_plural = verbose_name


class SettlementProfit(models.Model):
    """结算利润表"""
    settlement_month = models.CharField(max_length=7, unique=True, verbose_name='结算月份(YYYY-MM)')
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='总销售额')
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='总成本')
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='总利润')
    profit_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='利润率')
    order_count = models.IntegerField(default=0, verbose_name='订单数量')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_settlement_profit'
        verbose_name = '结算利润'
        verbose_name_plural = verbose_name


class BillDetail(models.Model):
    """账单明细表"""
    bill_no = models.CharField(max_length=50, verbose_name='账单号')
    platform = models.CharField(max_length=20, verbose_name='平台')
    account_id = models.BigIntegerField(verbose_name='店铺/账户ID')
    transaction_date = models.DateField(verbose_name='交易日期')
    transaction_type = models.CharField(max_length=50, verbose_name='交易类型')
    description = models.CharField(max_length=500, blank=True, default='', verbose_name='描述')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='金额')
    currency = models.CharField(max_length=10, default='USD', verbose_name='币种')
    order_id = models.CharField(max_length=50, blank=True, default='', verbose_name='订单ID')
    msku = models.CharField(max_length=100, blank=True, default='', verbose_name='MSKU')
    settlement_month = models.CharField(max_length=7, db_index=True, verbose_name='结算月份')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_bill_detail'
        verbose_name = '账单明细'
        verbose_name_plural = verbose_name


class CollectionDetail(models.Model):
    """回款明细表"""
    order_id = models.CharField(max_length=50, verbose_name='订单ID')
    msku = models.CharField(max_length=100, blank=True, default='', verbose_name='MSKU')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='回款金额')
    currency = models.CharField(max_length=10, default='USD', verbose_name='币种')
    expected_date = models.DateField(null=True, blank=True, verbose_name='预计回款日期')
    actual_date = models.DateField(null=True, blank=True, verbose_name='实际回款日期')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    settlement_month = models.CharField(max_length=7, db_index=True, verbose_name='结算月份')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_collection_detail'
        verbose_name = '回款明细'
        verbose_name_plural = verbose_name


class ExpenseRecord(models.Model):
    """费用记录表"""
    expense_no = models.CharField(max_length=50, unique=True, verbose_name='费用单号')
    expense_type = models.CharField(max_length=20, verbose_name='费用类型')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='金额')
    currency = models.CharField(max_length=10, default='CNY', verbose_name='币种')
    related_object_id = models.BigIntegerField(null=True, blank=True, verbose_name='关联对象ID')
    related_object_type = models.CharField(max_length=20, blank=True, default='', verbose_name='关联对象类型')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_expense_record'
        verbose_name = '费用记录'
        verbose_name_plural = verbose_name


class CostDiagnosis(models.Model):
    """成本诊断表"""
    sku = models.CharField(max_length=100, verbose_name='SKU')
    msku = models.CharField(max_length=100, blank=True, default='', verbose_name='MSKU')
    diagnosis_type = models.CharField(max_length=20, verbose_name='诊断类型')
    abnormal_desc = models.CharField(max_length=500, blank=True, default='', verbose_name='异常描述')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    source_doc_no = models.CharField(max_length=50, blank=True, default='', verbose_name='源头单据号')
    cost_source = models.CharField(max_length=50, blank=True, default='', verbose_name='成本取值来源')
    settlement_month = models.CharField(max_length=7, db_index=True, verbose_name='结算月份')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_cost_diagnosis'
        verbose_name = '成本诊断'
        verbose_name_plural = verbose_name


class CostResetRecord(models.Model):
    """成本重置记录表"""
    batch_no = models.CharField(max_length=50, unique=True, verbose_name='重置批次号')
    sku = models.CharField(max_length=100, verbose_name='SKU')
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='重置采购成本')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='重置头程费用')
    settlement_month = models.CharField(max_length=7, db_index=True, verbose_name='结算月份')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_cost_reset_record'
        verbose_name = '成本重置记录'
        verbose_name_plural = verbose_name


class CostValuation(models.Model):
    """成本计价表"""
    sku = models.CharField(max_length=100, verbose_name='SKU')
    msku = models.CharField(max_length=100, blank=True, default='', verbose_name='MSKU')
    source_doc_no = models.CharField(max_length=50, blank=True, default='', verbose_name='源头单据号')
    cost_source = models.CharField(max_length=50, blank=True, default='', verbose_name='成本取值来源')
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='采购成本')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='头程费用')
    valuation_month = models.CharField(max_length=7, db_index=True, verbose_name='计价月份')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_cost_valuation'
        verbose_name = '成本计价'
        verbose_name_plural = verbose_name


class WfsCost(models.Model):
    """WFS成本计价表"""
    sku = models.CharField(max_length=100, verbose_name='SKU')
    fnsku = models.CharField(max_length=50, blank=True, default='', verbose_name='FNSKU')
    cost_method = models.CharField(max_length=20, default='FIFO', verbose_name='计价方法')
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='单位成本')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='数量')
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='总成本')
    valuation_date = models.DateField(db_index=True, verbose_name='计价日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_wfs_cost'
        verbose_name = 'WFS成本计价'
        verbose_name_plural = verbose_name


class ApprovalFlow(models.Model):
    """审批流程表"""
    document_type = models.CharField(max_length=20, verbose_name='单据类型')
    document_id = models.BigIntegerField(db_index=True, verbose_name='单据ID')
    level = models.IntegerField(verbose_name='审批级别(1-3)')
    approver_id = models.BigIntegerField(verbose_name='审批人ID')
    approver_name = models.CharField(max_length=50, verbose_name='审批人名称')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='审批状态')
    comment = models.TextField(blank=True, default='', verbose_name='审批意见')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_approval_flow'
        verbose_name = '审批流程'
        verbose_name_plural = verbose_name


class AmazonSummaryReport(models.Model):
    """亚马逊Summary报表表"""
    report_no = models.CharField(max_length=50, verbose_name='报表编号')
    account_id = models.BigIntegerField(verbose_name='店铺ID')
    settlement_month = models.CharField(max_length=7, db_index=True, verbose_name='结算月份')
    income_data = models.TextField(blank=True, default='', verbose_name='收入数据(JSON)')
    expense_data = models.TextField(blank=True, default='', verbose_name='支出数据(JSON)')
    tax_data = models.TextField(blank=True, default='', verbose_name='税费数据(JSON)')
    transfer_data = models.TextField(blank=True, default='', verbose_name='转账数据(JSON)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_amazon_summary_report'
        verbose_name = '亚马逊Summary报表'
        verbose_name_plural = verbose_name


class ClosingPeriod(models.Model):
    """结账期间表"""
    period_month = models.CharField(max_length=7, unique=True, verbose_name='结账月份(YYYY-MM)')
    cost_closed = models.BooleanField(default=False, verbose_name='成本是否已结账')
    profit_closed = models.BooleanField(default=False, verbose_name='利润是否已结账')
    cost_closed_at = models.DateTimeField(null=True, blank=True, verbose_name='成本结账时间')
    profit_closed_at = models.DateTimeField(null=True, blank=True, verbose_name='利润结账时间')
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='结账人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_closing_period'
        verbose_name = '结账期间'
        verbose_name_plural = verbose_name


class ClosingLog(models.Model):
    """结账日志表"""
    period_month = models.CharField(max_length=7, verbose_name='结账月份')
    closing_type = models.CharField(max_length=20, verbose_name='结账类型(COST/PROFIT)')
    action = models.CharField(max_length=20, verbose_name='操作(CLOSE/REVERSE)')
    result = models.BooleanField(default=True, verbose_name='操作结果')
    message = models.TextField(blank=True, default='', verbose_name='操作信息')
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='操作人')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_closing_log'
        verbose_name = '结账日志'
        verbose_name_plural = verbose_name


class ClosingSetting(models.Model):
    """自动结账设置表"""
    auto_cost_closing = models.BooleanField(default=False, verbose_name='自动成本结账')
    auto_profit_closing = models.BooleanField(default=False, verbose_name='自动利润结账')
    closing_day = models.IntegerField(default=1, verbose_name='结账日期')
    closing_hour = models.IntegerField(default=0, verbose_name='结账时间(0-23)')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_closing_setting'
        verbose_name = '自动结账设置'
        verbose_name_plural = verbose_name


class AdInvoiceHeader(models.Model):
    """广告发票头表"""
    invoice_no = models.CharField(max_length=50, unique=True, verbose_name='发票编号')
    platform = models.CharField(max_length=20, verbose_name='平台')
    account_id = models.BigIntegerField(verbose_name='店铺ID')
    invoice_date = models.DateField(verbose_name='发票日期')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='总金额')
    currency = models.CharField(max_length=10, default='USD', verbose_name='币种')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_ad_invoice_header'
        verbose_name = '广告发票头'
        verbose_name_plural = verbose_name


class AdInvoiceDetail(models.Model):
    """广告发票明细表"""
    header = models.ForeignKey(AdInvoiceHeader, on_delete=models.CASCADE, related_name='details', verbose_name='发票头')
    campaign_name = models.CharField(max_length=200, blank=True, default='', verbose_name='广告活动名称')
    ad_group = models.CharField(max_length=200, blank=True, default='', verbose_name='广告组')
    cost_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='花费金额')
    clicks = models.IntegerField(default=0, verbose_name='点击量')
    impressions = models.IntegerField(default=0, verbose_name='展示量')
    orders = models.IntegerField(default=0, verbose_name='订单数')
    sales = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='销售额')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_ad_invoice_detail'
        verbose_name = '广告发票明细'
        verbose_name_plural = verbose_name


class AdInvoiceAllocation(models.Model):
    """广告发票分摊表"""
    detail = models.ForeignKey(AdInvoiceDetail, on_delete=models.CASCADE, related_name='allocations', verbose_name='发票明细')
    allocation_type = models.CharField(max_length=20, verbose_name='分摊类型')
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='分摊金额')
    allocated_to = models.CharField(max_length=100, verbose_name='分摊对象')
    settlement_month = models.CharField(max_length=7, db_index=True, verbose_name='结算月份')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_ad_invoice_allocation'
        verbose_name = '广告发票分摊'
        verbose_name_plural = verbose_name


class DelayedSettlement(models.Model):
    """延迟结算表"""
    settlement_no = models.CharField(max_length=50, unique=True, verbose_name='结算编号')
    account_id = models.BigIntegerField(verbose_name='店铺ID')
    settlement_month = models.CharField(max_length=7, db_index=True, verbose_name='结算月份')
    expected_settlement_date = models.DateField(null=True, blank=True, verbose_name='预计结算日期')
    actual_settlement_date = models.DateField(null=True, blank=True, verbose_name='实际结算日期')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='金额')
    currency = models.CharField(max_length=10, default='USD', verbose_name='币种')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_delayed_settlement'
        verbose_name = '延迟结算'
        verbose_name_plural = verbose_name


class DelayedSettlementSetting(models.Model):
    """预结算设置表"""
    account_id = models.BigIntegerField(unique=True, verbose_name='店铺ID')
    pre_settlement_enabled = models.BooleanField(default=False, verbose_name='是否启用预结算')
    days_offset = models.IntegerField(default=14, verbose_name='偏移天数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_delayed_settlement_setting'
        verbose_name = '预结算设置'
        verbose_name_plural = verbose_name


class DelayedSettlementAdjustment(models.Model):
    """延迟结算冲销表"""
    settlement = models.ForeignKey(DelayedSettlement, on_delete=models.CASCADE, related_name='adjustments', verbose_name='延迟结算')
    adjustment_type = models.CharField(max_length=20, verbose_name='冲销类型')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='冲销金额')
    reason = models.TextField(blank=True, default='', verbose_name='冲销原因')
    adjusted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='冲销人')
    adjusted_at = models.DateTimeField(auto_now_add=True, verbose_name='冲销时间')

    class Meta:
        db_table = 'finance_delayed_settlement_adjustment'
        verbose_name = '延迟结算冲销'
        verbose_name_plural = verbose_name


class ProfitReportConfig(models.Model):
    """利润报表配置表"""
    config_key = models.CharField(max_length=100, unique=True, verbose_name='配置键')
    config_value = models.TextField(blank=True, default='', verbose_name='配置值(JSON)')
    description = models.CharField(max_length=500, blank=True, default='', verbose_name='配置描述')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_profit_report_config'
        verbose_name = '利润报表配置'
        verbose_name_plural = verbose_name


class ExpenseAllocationRule(models.Model):
    """费用分摊规则表"""
    rule_name = models.CharField(max_length=100, verbose_name='规则名称')
    allocation_method = models.CharField(max_length=20, verbose_name='分摊方式')
    allocation_params = models.TextField(blank=True, default='', verbose_name='分摊参数(JSON)')
    status = models.CharField(max_length=20, default='ACTIVE', db_index=True, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_expense_allocation_rule'
        verbose_name = '费用分摊规则'
        verbose_name_plural = verbose_name


class ProfitReportVersion(models.Model):
    """利润报表版本表"""
    settlement_month = models.CharField(max_length=7, verbose_name='结算月份')
    version_no = models.IntegerField(default=1, verbose_name='版本号')
    report_data = models.TextField(blank=True, default='', verbose_name='报表数据(JSON)')
    is_current = models.BooleanField(default=False, db_index=True, verbose_name='是否当前版本')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_profit_report_version'
        verbose_name = '利润报表版本'
        verbose_name_plural = verbose_name


class PerformanceReport(models.Model):
    """业绩报表表"""
    report_month = models.CharField(max_length=7, db_index=True, verbose_name='报表月份')
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='员工')
    employee_name = models.CharField(max_length=50, verbose_name='员工姓名')
    department_id = models.BigIntegerField(null=True, blank=True, verbose_name='部门ID')
    department_name = models.CharField(max_length=100, blank=True, default='', verbose_name='部门名称')
    sales_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='销售额')
    profit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='利润额')
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='提成金额')
    remark = models.TextField(blank=True, default='', verbose_name='备注')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_reports', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_performance_report'
        verbose_name = '业绩报表'
        verbose_name_plural = verbose_name


class EmployeeDepartmentRel(models.Model):
    """员工部门关系表"""
    employee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='department_rel', verbose_name='员工')
    department_id = models.BigIntegerField(verbose_name='部门ID')
    department_name = models.CharField(max_length=100, verbose_name='部门名称')
    joined_at = models.DateField(null=True, blank=True, verbose_name='入职日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_employee_department_rel'
        verbose_name = '员工部门关系'
        verbose_name_plural = verbose_name


class TurnoverHandover(models.Model):
    """离职业绩交接表"""
    from_employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='handovers_from', verbose_name='离职员工')
    to_employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='handovers_to', verbose_name='接手员工')
    from_employee_name = models.CharField(max_length=50, verbose_name='离职员工姓名')
    to_employee_name = models.CharField(max_length=50, verbose_name='接手员工姓名')
    handover_date = models.DateField(verbose_name='交接日期')
    remark = models.TextField(blank=True, default='', verbose_name='备注')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_handovers', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_turnover_handover'
        verbose_name = '离职业绩交接'
        verbose_name_plural = verbose_name


class ExpenseType(models.Model):
    """费用类型表"""
    type_name = models.CharField(max_length=100, unique=True, verbose_name='类型名称')
    type_code = models.CharField(max_length=50, unique=True, verbose_name='类型编码')
    description = models.CharField(max_length=500, blank=True, default='', verbose_name='描述')
    is_system = models.BooleanField(default=False, verbose_name='是否系统内置')
    status = models.CharField(max_length=20, default='ACTIVE', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finance_expense_type'
        verbose_name = '费用类型'
        verbose_name_plural = verbose_name


class ExpenseOrder(models.Model):
    """费用单表"""
    order_no = models.CharField(max_length=50, unique=True, verbose_name='费用单号')
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT, verbose_name='费用类型')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='金额')
    currency = models.CharField(max_length=10, default='CNY', verbose_name='币种')
    allocation_method = models.CharField(max_length=20, blank=True, default='', verbose_name='分摊方式')
    allocation_dimension = models.CharField(max_length=20, blank=True, default='', verbose_name='分摊维度')
    status = models.CharField(max_length=20, default='DRAFT', db_index=True, verbose_name='状态')
    related_object_id = models.BigIntegerField(null=True, blank=True, verbose_name='关联对象ID')
    related_object_type = models.CharField(max_length=20, blank=True, default='', verbose_name='关联对象类型')
    remark = models.TextField(blank=True, default='', verbose_name='备注')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_expense_order'
        verbose_name = '费用单'
        verbose_name_plural = verbose_name


class ExpenseTemplate(models.Model):
    """费用模板表"""
    template_name = models.CharField(max_length=100, verbose_name='模板名称')
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='费用类型')
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='金额')
    allocation_method = models.CharField(max_length=20, blank=True, default='', verbose_name='分摊方式')
    allocation_dimension = models.CharField(max_length=20, blank=True, default='', verbose_name='分摊维度')
    template_data = models.TextField(blank=True, default='', verbose_name='模板数据(JSON)')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_expense_template'
        verbose_name = '费用模板'
        verbose_name_plural = verbose_name


class ProfitCheckRule(models.Model):
    """利润核对规则表"""
    rule_name = models.CharField(max_length=100, verbose_name='规则名称')
    check_type = models.CharField(max_length=20, verbose_name='核对类型')
    check_params = models.TextField(blank=True, default='', verbose_name='核对参数(JSON)')
    is_enabled = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'finance_profit_check_rule'
        verbose_name = '利润核对规则'
        verbose_name_plural = verbose_name
