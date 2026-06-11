from django.conf import settings
from django.db import models


class WarehouseWms(models.Model):
    """仓库表"""
    name = models.CharField(max_length=100, verbose_name='仓库名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='仓库编码')
    address = models.CharField(max_length=500, blank=True, default='', verbose_name='仓库地址')
    status = models.BooleanField(default=True, verbose_name='启用状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'wms_warehouse'
        verbose_name = '仓库'
        verbose_name_plural = verbose_name


class Inventory(models.Model):
    """库存表"""
    warehouse = models.ForeignKey(WarehouseWms, on_delete=models.PROTECT, related_name='inventories', verbose_name='仓库')
    sku = models.CharField(max_length=100, verbose_name='商品SKU')
    sku_name = models.CharField(max_length=200, blank=True, default='', verbose_name='商品名称')
    quantity = models.DecimalField(max_digits=18, decimal_places=4, default=0, verbose_name='可用库存')
    locked_qty = models.DecimalField(max_digits=18, decimal_places=4, default=0, verbose_name='锁定库存')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'wms_inventory'
        verbose_name = '库存'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['warehouse', 'sku'], name='idx_wms_ivt_wh_sku'),
        ]


class InventoryBatch(models.Model):
    """库存批次表"""
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='batches', verbose_name='库存')
    batch_no = models.CharField(max_length=100, verbose_name='批次号')
    expiry_date = models.DateField(null=True, blank=True, verbose_name='有效期')
    quantity = models.DecimalField(max_digits=18, decimal_places=4, default=0, verbose_name='批次数量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'wms_inventory_batch'
        verbose_name = '库存批次'
        verbose_name_plural = verbose_name


class ReceiptOrder(models.Model):
    """收货单表"""
    order_no = models.CharField(max_length=50, unique=True, verbose_name='单据编号')
    warehouse = models.ForeignKey(WarehouseWms, on_delete=models.PROTECT, verbose_name='收货仓库')
    source_type = models.CharField(max_length=50, blank=True, default='', verbose_name='来源类型')
    source_id = models.BigIntegerField(null=True, blank=True, verbose_name='来源单据ID')
    status = models.IntegerField(default=0, db_index=True, verbose_name='状态(0待审核1已审核2已完成3已驳回)')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'wms_receipt_order'
        verbose_name = '收货单'
        verbose_name_plural = verbose_name


class ReceiptOrderItem(models.Model):
    """收货单明细表"""
    order = models.ForeignKey(ReceiptOrder, on_delete=models.CASCADE, related_name='items', verbose_name='收货单')
    sku = models.CharField(max_length=100, verbose_name='商品SKU')
    sku_name = models.CharField(max_length=200, blank=True, default='', verbose_name='商品名称')
    fnsku = models.CharField(max_length=100, blank=True, default='', verbose_name='FNSKU')
    expected_qty = models.DecimalField(max_digits=18, decimal_places=4, verbose_name='预期收货数量')
    actual_qty = models.DecimalField(max_digits=18, decimal_places=4, default=0, verbose_name='实际收货数量')
    qualified_qty = models.DecimalField(max_digits=18, decimal_places=4, default=0, verbose_name='合格品数量')
    defective_qty = models.DecimalField(max_digits=18, decimal_places=4, default=0, verbose_name='不合格品数量')
    unit_cost = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True, verbose_name='单位成本')
    batch_no = models.CharField(max_length=100, blank=True, default='', verbose_name='批次号')
    expiry_date = models.DateField(null=True, blank=True, verbose_name='有效期')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')

    class Meta:
        db_table = 'wms_receipt_order_item'
        verbose_name = '收货单明细'
        verbose_name_plural = verbose_name


class DeliveryOrder(models.Model):
    """出库单表"""
    order_no = models.CharField(max_length=50, unique=True, verbose_name='单据编号')
    warehouse = models.ForeignKey(WarehouseWms, on_delete=models.PROTECT, verbose_name='出库仓库')
    source_type = models.CharField(max_length=50, blank=True, default='', verbose_name='来源类型')
    source_id = models.BigIntegerField(null=True, blank=True, verbose_name='来源单据ID')
    wave_no = models.CharField(max_length=50, blank=True, default='', verbose_name='波次号')
    status = models.IntegerField(default=0, db_index=True, verbose_name='状态(0待审核1已审核2拣货中3已发货)')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'wms_delivery_order'
        verbose_name = '出库单'
        verbose_name_plural = verbose_name


class DeliveryOrderItem(models.Model):
    """出库单明细表"""
    order = models.ForeignKey(DeliveryOrder, on_delete=models.CASCADE, related_name='items', verbose_name='出库单')
    sku = models.CharField(max_length=100, verbose_name='商品SKU')
    sku_name = models.CharField(max_length=200, blank=True, default='', verbose_name='商品名称')
    fnsku = models.CharField(max_length=100, blank=True, default='', verbose_name='FNSKU')
    order_qty = models.DecimalField(max_digits=18, decimal_places=4, verbose_name='出库数量')
    picked_qty = models.DecimalField(max_digits=18, decimal_places=4, default=0, verbose_name='已拣货数量')
    shipped_qty = models.DecimalField(max_digits=18, decimal_places=4, default=0, verbose_name='已发货数量')
    batch_no = models.CharField(max_length=100, blank=True, default='', verbose_name='批次号')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')

    class Meta:
        db_table = 'wms_delivery_order_item'
        verbose_name = '出库单明细'
        verbose_name_plural = verbose_name


class TransferOrder(models.Model):
    """调拨单表"""
    order_no = models.CharField(max_length=50, unique=True, verbose_name='单据编号')
    from_warehouse = models.ForeignKey(WarehouseWms, on_delete=models.PROTECT, related_name='transfers_out', verbose_name='调出仓库')
    to_warehouse = models.ForeignKey(WarehouseWms, on_delete=models.PROTECT, related_name='transfers_in', verbose_name='调入仓库')
    status = models.IntegerField(default=0, db_index=True, verbose_name='状态(0待审核1已审核2已出库3已入库)')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'wms_transfer_order'
        verbose_name = '调拨单'
        verbose_name_plural = verbose_name


class TransferOrderItem(models.Model):
    """调拨单明细表"""
    order = models.ForeignKey(TransferOrder, on_delete=models.CASCADE, related_name='items', verbose_name='调拨单')
    sku = models.CharField(max_length=100, verbose_name='商品SKU')
    sku_name = models.CharField(max_length=200, blank=True, default='', verbose_name='商品名称')
    qty = models.DecimalField(max_digits=18, decimal_places=4, verbose_name='调拨数量')
    batch_no = models.CharField(max_length=100, blank=True, default='', verbose_name='批次号')

    class Meta:
        db_table = 'wms_transfer_order_item'
        verbose_name = '调拨单明细'
        verbose_name_plural = verbose_name


class InventoryCheck(models.Model):
    """盘点单表"""
    order_no = models.CharField(max_length=50, unique=True, verbose_name='单据编号')
    warehouse = models.ForeignKey(WarehouseWms, on_delete=models.PROTECT, verbose_name='盘点仓库')
    status = models.IntegerField(default=0, db_index=True, verbose_name='状态(0待盘点1盘点中2已完成)')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'wms_inventory_check'
        verbose_name = '盘点单'
        verbose_name_plural = verbose_name


class InventoryCheckItem(models.Model):
    """盘点单明细表"""
    order = models.ForeignKey(InventoryCheck, on_delete=models.CASCADE, related_name='items', verbose_name='盘点单')
    sku = models.CharField(max_length=100, verbose_name='商品SKU')
    sku_name = models.CharField(max_length=200, blank=True, default='', verbose_name='商品名称')
    system_qty = models.DecimalField(max_digits=18, decimal_places=4, verbose_name='系统库存')
    actual_qty = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True, verbose_name='实际盘点数量')
    diff_qty = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True, verbose_name='差异数量')
    batch_no = models.CharField(max_length=100, blank=True, default='', verbose_name='批次号')

    class Meta:
        db_table = 'wms_inventory_check_item'
        verbose_name = '盘点单明细'
        verbose_name_plural = verbose_name


class StockFlow(models.Model):
    """库存流水表"""
    inventory = models.ForeignKey(Inventory, on_delete=models.PROTECT, verbose_name='库存')
    flow_type = models.CharField(max_length=50, verbose_name='流水类型(IN/OUT/ADJUST)')
    change_qty = models.DecimalField(max_digits=18, decimal_places=4, verbose_name='变动数量')
    before_qty = models.DecimalField(max_digits=18, decimal_places=4, verbose_name='变动前数量')
    after_qty = models.DecimalField(max_digits=18, decimal_places=4, verbose_name='变动后数量')
    order_no = models.CharField(max_length=50, blank=True, default='', verbose_name='关联单据号')
    remark = models.CharField(max_length=500, blank=True, default='', verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')

    class Meta:
        db_table = 'wms_stock_flow'
        verbose_name = '库存流水'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['inventory'], name='idx_wms_sf_inventory'),
            models.Index(fields=['created_at'], name='idx_wms_sf_created'),
        ]


class Wave(models.Model):
    """波次表"""
    wave_no = models.CharField(max_length=50, unique=True, verbose_name='波次编号')
    warehouse = models.ForeignKey(WarehouseWms, on_delete=models.PROTECT, verbose_name='仓库')
    status = models.IntegerField(default=0, db_index=True, verbose_name='状态(0待分配1拣货中2已完成)')
    order_count = models.IntegerField(default=0, verbose_name='包含订单数')
    item_count = models.IntegerField(default=0, verbose_name='包含商品项数')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'wms_wave'
        verbose_name = '波次'
        verbose_name_plural = verbose_name


class WaveOrder(models.Model):
    """波次订单关联表"""
    wave = models.ForeignKey(Wave, on_delete=models.CASCADE, verbose_name='波次')
    order_id = models.BigIntegerField(verbose_name='出库单ID')
    order_no = models.CharField(max_length=50, verbose_name='订单编号')

    class Meta:
        db_table = 'wms_wave_order'
        verbose_name = '波次订单关联'
        verbose_name_plural = verbose_name


class PackingTask(models.Model):
    """装箱任务表"""
    task_no = models.CharField(max_length=50, unique=True, verbose_name='任务编号')
    warehouse = models.ForeignKey(WarehouseWms, on_delete=models.PROTECT, verbose_name='仓库')
    status = models.IntegerField(default=0, db_index=True, verbose_name='状态(0待执行1装箱中2已完成)')
    box_count = models.IntegerField(default=0, verbose_name='箱子数量')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'wms_packing_task'
        verbose_name = '装箱任务'
        verbose_name_plural = verbose_name


class PackingItem(models.Model):
    """装箱明细表"""
    task = models.ForeignKey(PackingTask, on_delete=models.CASCADE, related_name='items', verbose_name='装箱任务')
    box_no = models.CharField(max_length=50, verbose_name='箱号')
    sku = models.CharField(max_length=100, verbose_name='商品SKU')
    qty = models.DecimalField(max_digits=18, decimal_places=4, verbose_name='装箱数量')
    barcode = models.CharField(max_length=100, blank=True, default='', verbose_name='条码')

    class Meta:
        db_table = 'wms_packing_item'
        verbose_name = '装箱明细'
        verbose_name_plural = verbose_name


class Product(models.Model):
    """商品表"""
    sku = models.CharField(max_length=100, unique=True, verbose_name='商品SKU')
    sku_name = models.CharField(max_length=200, verbose_name='商品名称')
    fnsku = models.CharField(max_length=100, blank=True, default='', verbose_name='FNSKU')
    msku = models.CharField(max_length=100, blank=True, default='', verbose_name='MSKU')
    asin = models.CharField(max_length=50, blank=True, default='', verbose_name='ASIN')
    upc = models.CharField(max_length=50, blank=True, default='', verbose_name='UPC')
    category = models.CharField(max_length=100, blank=True, default='', verbose_name='商品分类')
    brand = models.CharField(max_length=100, blank=True, default='', verbose_name='品牌')
    weight = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name='重量(kg)')
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='长度(cm)')
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='宽度(cm)')
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='高度(cm)')
    image_url = models.CharField(max_length=500, blank=True, default='', verbose_name='商品图片URL')
    product_status = models.CharField(max_length=20, default='ACTIVE', verbose_name='商品状态')
    listing_owner = models.CharField(max_length=50, blank=True, default='', verbose_name='Listing负责人')
    product_owner = models.CharField(max_length=50, blank=True, default='', verbose_name='产品负责人')
    tags = models.CharField(max_length=500, blank=True, default='', verbose_name='商品标签')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'wms_product'
        verbose_name = '商品'
        verbose_name_plural = verbose_name


class OverseasStocking(models.Model):
    """海外仓备货单表"""
    order_no = models.CharField(max_length=50, unique=True, verbose_name='单据编号')
    warehouse = models.ForeignKey(WarehouseWms, on_delete=models.PROTECT, verbose_name='海外仓')
    status = models.IntegerField(default=0, db_index=True, verbose_name='状态(0待审核1已审核2已发货3已入库)')
    creator = models.CharField(max_length=50, blank=True, default='', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'wms_overseas_stocking'
        verbose_name = '海外仓备货单'
        verbose_name_plural = verbose_name
