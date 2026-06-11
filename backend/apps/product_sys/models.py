from django.conf import settings
from django.db import models


class Product(models.Model):
    """产品主表"""
    product_no = models.CharField(max_length=50, unique=True, verbose_name='产品编号')
    name = models.CharField(max_length=200, verbose_name='产品名称')
    brand_id = models.BigIntegerField(null=True, blank=True, verbose_name='品牌ID')
    category_id = models.BigIntegerField(null=True, blank=True, verbose_name='分类ID')
    short_desc = models.CharField(max_length=500, blank=True, default='', verbose_name='简短描述')
    description = models.TextField(blank=True, default='', verbose_name='详细描述')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='成本价')
    weight = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='重量(kg)')
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='长度(cm)')
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='宽度(cm)')
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='高度(cm)')
    status = models.CharField(max_length=20, default='ACTIVE', db_index=True, verbose_name='状态')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_product'
        verbose_name = '产品'
        verbose_name_plural = verbose_name


class ProductSku(models.Model):
    """产品SKU表"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='skus', verbose_name='产品')
    sku = models.CharField(max_length=100, unique=True, verbose_name='SKU编码')
    variant_info = models.TextField(blank=True, default='', verbose_name='变体信息(JSON)')
    barcode = models.CharField(max_length=50, blank=True, default='', verbose_name='条形码')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='成本价')
    stock_qty = models.IntegerField(default=0, verbose_name='库存数量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_product_sku'
        verbose_name = '产品SKU'
        verbose_name_plural = verbose_name


class ProductSpec(models.Model):
    """产品规格表"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specs', verbose_name='产品')
    spec_name = models.CharField(max_length=50, verbose_name='规格名称')
    spec_value = models.CharField(max_length=200, verbose_name='规格值')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'product_sys_product_spec'
        verbose_name = '产品规格'
        verbose_name_plural = verbose_name


class SpuInfo(models.Model):
    """SPU信息表"""
    spu_code = models.CharField(max_length=100, unique=True, verbose_name='SPU编码')
    spu_name = models.CharField(max_length=200, verbose_name='SPU名称')
    style_name = models.CharField(max_length=100, blank=True, default='', verbose_name='款名')
    category_id = models.BigIntegerField(null=True, blank=True, verbose_name='分类ID')
    brand_id = models.BigIntegerField(null=True, blank=True, verbose_name='品牌ID')
    short_desc = models.CharField(max_length=500, blank=True, default='', verbose_name='简短描述')
    description = models.TextField(blank=True, default='', verbose_name='详细描述')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='参考成本价')
    weight = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='重量(kg)')
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='长度(cm)')
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='宽度(cm)')
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='高度(cm)')
    status = models.CharField(max_length=20, default='ACTIVE', verbose_name='状态')
    sku_count = models.IntegerField(default=0, verbose_name='关联SKU数量')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_spu_info'
        verbose_name = 'SPU信息'
        verbose_name_plural = verbose_name


class SpuSkuRelation(models.Model):
    """SPU-SKU关联表"""
    spu = models.ForeignKey(SpuInfo, on_delete=models.CASCADE, related_name='sku_relations', verbose_name='SPU')
    sku = models.CharField(max_length=100, verbose_name='SKU编码')
    attribute_value = models.TextField(blank=True, default='', verbose_name='属性值(JSON)')
    sort_order = models.IntegerField(default=0, verbose_name='排序号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'product_sys_spu_sku_relation'
        verbose_name = 'SPU-SKU关联'
        verbose_name_plural = verbose_name


class SpuAttribute(models.Model):
    """SPU属性表"""
    spu = models.ForeignKey(SpuInfo, on_delete=models.CASCADE, related_name='attributes', verbose_name='SPU')
    attribute_id = models.BigIntegerField(verbose_name='属性ID')
    attribute_name = models.CharField(max_length=50, verbose_name='属性名称')
    option_values = models.TextField(blank=True, default='', verbose_name='可选值(JSON)')
    sort_order = models.IntegerField(default=0, verbose_name='排序号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'product_sys_spu_attribute'
        verbose_name = 'SPU属性'
        verbose_name_plural = verbose_name


class DevelopmentTask(models.Model):
    """新品开发任务表"""
    task_no = models.CharField(max_length=50, unique=True, verbose_name='需求编号')
    demand_name = models.CharField(max_length=200, verbose_name='需求名称')
    image_url = models.CharField(max_length=500, blank=True, default='', verbose_name='目标新品图片')
    country = models.CharField(max_length=10, verbose_name='目标国家/站点')
    level = models.CharField(max_length=20, blank=True, default='', verbose_name='级别')
    category_id = models.BigIntegerField(null=True, blank=True, verbose_name='分类ID')
    brand_id = models.BigIntegerField(null=True, blank=True, verbose_name='品牌ID')
    status = models.CharField(max_length=20, default='PROCESSING', db_index=True, verbose_name='状态')
    current_node = models.CharField(max_length=50, blank=True, default='', verbose_name='当前节点')
    processor_id = models.BigIntegerField(null=True, blank=True, verbose_name='当前处理人ID')
    processor_name = models.CharField(max_length=50, blank=True, default='', verbose_name='当前处理人姓名')
    linked_sku = models.TextField(blank=True, default='', verbose_name='关联产品SKU列表(JSON)')
    basic_info = models.TextField(blank=True, default='', verbose_name='基础信息(JSON)')
    pricing_profit = models.TextField(blank=True, default='', verbose_name='定价利润试算数据(JSON)')
    style_attributes = models.TextField(blank=True, default='', verbose_name='款式属性(JSON)')
    supplier_quotes = models.TextField(blank=True, default='', verbose_name='供应商报价(JSON)')
    competitor_asins = models.TextField(blank=True, default='', verbose_name='竞品ASIN列表(JSON)')
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='预估成本')
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='实际成本')
    remark = models.TextField(blank=True, default='', verbose_name='备注')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_development_task'
        verbose_name = '新品开发任务'
        verbose_name_plural = verbose_name


class BundleProduct(models.Model):
    """捆绑产品表"""
    bundle_sku = models.CharField(max_length=100, unique=True, verbose_name='捆绑产品SKU')
    name = models.CharField(max_length=200, verbose_name='捆绑名称')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='采购成本')
    status = models.CharField(max_length=20, default='ACTIVE', verbose_name='状态')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_bundle_product'
        verbose_name = '捆绑产品'
        verbose_name_plural = verbose_name


class BundleProductItem(models.Model):
    """捆绑子产品表"""
    bundle = models.ForeignKey(BundleProduct, on_delete=models.CASCADE, related_name='items', verbose_name='捆绑产品')
    child_sku = models.CharField(max_length=100, verbose_name='子产品SKU')
    child_type = models.CharField(max_length=20, verbose_name='子产品类型')
    quantity = models.IntegerField(default=1, verbose_name='子产品数量')
    sort_order = models.IntegerField(default=0, verbose_name='排序号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'product_sys_bundle_product_item'
        verbose_name = '捆绑子产品'
        verbose_name_plural = verbose_name


class Accessory(models.Model):
    """辅料表"""
    name = models.CharField(max_length=100, verbose_name='辅料名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='辅料编码')
    unit = models.CharField(max_length=20, verbose_name='单位')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='成本价')
    stock_qty = models.IntegerField(default=0, verbose_name='库存数量')
    min_stock = models.IntegerField(default=0, verbose_name='最低库存')
    status = models.CharField(max_length=20, default='ACTIVE', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_accessory'
        verbose_name = '辅料'
        verbose_name_plural = verbose_name


class UpcCode(models.Model):
    """UPC编码表"""
    code = models.CharField(max_length=20, unique=True, verbose_name='UPC/EAN/ISBN编码')
    code_type = models.CharField(max_length=20, verbose_name='编码类型(UPC/EAN/ISBN)')
    status = models.CharField(max_length=20, default='UNUSED', db_index=True, verbose_name='使用状态')
    used_by = models.CharField(max_length=100, blank=True, default='', verbose_name='使用对象')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='使用时间')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_upc_code'
        verbose_name = 'UPC编码'
        verbose_name_plural = verbose_name


class TransparencyAccount(models.Model):
    """透明计划账号表"""
    account_name = models.CharField(max_length=100, verbose_name='账号名称')
    client_id = models.CharField(max_length=200, verbose_name='Client ID')
    client_secret = models.CharField(max_length=200, verbose_name='Client Secret')
    party_id = models.CharField(max_length=100, blank=True, default='', verbose_name='Party ID')
    status = models.CharField(max_length=20, default='ACTIVE', verbose_name='状态')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_transparency_account'
        verbose_name = '透明计划账号'
        verbose_name_plural = verbose_name


class TransparencyProduct(models.Model):
    """透明计划商品表"""
    asin = models.CharField(max_length=50, verbose_name='ASIN')
    msku = models.CharField(max_length=100, blank=True, default='', verbose_name='MSKU')
    title = models.CharField(max_length=500, blank=True, default='', verbose_name='商品标题')
    gtin = models.CharField(max_length=50, verbose_name='GTIN编码')
    brand_name = models.CharField(max_length=100, blank=True, default='', verbose_name='品牌名称')
    status = models.CharField(max_length=20, blank=True, default='', verbose_name='状态')
    account = models.ForeignKey(TransparencyAccount, on_delete=models.PROTECT, verbose_name='透明计划账号')
    label_status = models.CharField(max_length=20, default='UNPRINTED', verbose_name='标签状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_transparency_product'
        verbose_name = '透明计划商品'
        verbose_name_plural = verbose_name


class TransparencyTcode(models.Model):
    """T-Code表"""
    product = models.ForeignKey(TransparencyProduct, on_delete=models.CASCADE, related_name='tcodes', verbose_name='透明计划商品')
    tcode = models.CharField(max_length=100, unique=True, verbose_name='T-Code编码')
    status = models.CharField(max_length=20, default='UNUSED', db_index=True, verbose_name='使用状态')
    batch_no = models.CharField(max_length=100, blank=True, default='', verbose_name='批次号')
    batch_type = models.CharField(max_length=20, blank=True, default='', verbose_name='批次号类型')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='使用时间')
    applied_at = models.DateTimeField(null=True, blank=True, verbose_name='申请时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_transparency_tcode'
        verbose_name = 'T-Code'
        verbose_name_plural = verbose_name


class Brand(models.Model):
    """品牌表"""
    name = models.CharField(max_length=100, verbose_name='品牌名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='品牌编码')
    logo_url = models.CharField(max_length=500, blank=True, default='', verbose_name='Logo地址')
    description = models.CharField(max_length=500, blank=True, default='', verbose_name='品牌描述')
    status = models.CharField(max_length=20, default='ACTIVE', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_brand'
        verbose_name = '品牌'
        verbose_name_plural = verbose_name


class Category(models.Model):
    """分类表"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='分类编码')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', verbose_name='父分类')
    level = models.IntegerField(default=1, verbose_name='分类层级')
    sort_order = models.IntegerField(default=0, verbose_name='排序号')
    status = models.CharField(max_length=20, default='ACTIVE', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_category'
        verbose_name = '分类'
        verbose_name_plural = verbose_name


class ProductImage(models.Model):
    """产品图片表"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='产品')
    sku_id = models.BigIntegerField(null=True, blank=True, verbose_name='SKU ID')
    image_url = models.CharField(max_length=500, verbose_name='图片地址')
    thumbnail_url = models.CharField(max_length=500, blank=True, default='', verbose_name='缩略图地址')
    sort_order = models.IntegerField(default=0, verbose_name='排序号')
    is_main = models.BooleanField(default=False, verbose_name='是否主图')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'product_sys_product_image'
        verbose_name = '产品图片'
        verbose_name_plural = verbose_name


class Attribute(models.Model):
    """属性表"""
    name = models.CharField(max_length=50, verbose_name='属性名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='属性编码')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='所属分类')
    input_type = models.CharField(max_length=20, default='text', verbose_name='输入类型')
    options = models.TextField(blank=True, default='', verbose_name='可选值(JSON)')
    required = models.BooleanField(default=False, verbose_name='是否必填')
    sort_order = models.IntegerField(default=0, verbose_name='排序号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'product_sys_attribute'
        verbose_name = '属性'
        verbose_name_plural = verbose_name


class AttributeValue(models.Model):
    """属性值表"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attribute_values', verbose_name='产品')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, verbose_name='属性')
    value = models.CharField(max_length=200, verbose_name='属性值')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'product_sys_attribute_value'
        verbose_name = '属性值'
        verbose_name_plural = verbose_name


class QualityTemplate(models.Model):
    """质检模板表"""
    name = models.CharField(max_length=100, unique=True, verbose_name='模板名称')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='适用分类')
    items = models.TextField(verbose_name='质检项(JSON)')
    status = models.CharField(max_length=20, default='ACTIVE', verbose_name='状态')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_quality_template'
        verbose_name = '质检模板'
        verbose_name_plural = verbose_name


class ProductQualityInfo(models.Model):
    """产品质检信息表"""
    sku = models.CharField(max_length=100, verbose_name='产品SKU')
    template = models.ForeignKey(QualityTemplate, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='质检模板')
    default_inspection_type = models.CharField(max_length=20, blank=True, default='', verbose_name='默认质检方式')
    custom_items = models.TextField(blank=True, default='', verbose_name='自定义质检项(JSON)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_product_quality_info'
        verbose_name = '产品质检信息'
        verbose_name_plural = verbose_name


class PlatformMatch(models.Model):
    """平台配对表"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='产品')
    sku_id = models.BigIntegerField(null=True, blank=True, verbose_name='SKU ID')
    platform = models.CharField(max_length=30, verbose_name='平台类型')
    platform_sku = models.CharField(max_length=100, verbose_name='平台SKU')
    platform_id = models.CharField(max_length=100, blank=True, default='', verbose_name='平台商品ID')
    status = models.CharField(max_length=20, default='ACTIVE', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_platform_match'
        verbose_name = '平台配对'
        verbose_name_plural = verbose_name


class MatchRule(models.Model):
    """配对规则表"""
    name = models.CharField(max_length=100, verbose_name='规则名称')
    platform = models.CharField(max_length=30, verbose_name='适用平台')
    match_type = models.CharField(max_length=20, verbose_name='匹配类型')
    conditions = models.TextField(blank=True, default='', verbose_name='匹配条件(JSON)')
    priority = models.IntegerField(default=1, verbose_name='优先级')
    status = models.CharField(max_length=20, default='ACTIVE', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_match_rule'
        verbose_name = '配对规则'
        verbose_name_plural = verbose_name


class AlibabaMatch(models.Model):
    """1688配对表"""
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='产品')
    sku_id = models.BigIntegerField(null=True, blank=True, verbose_name='SKU ID')
    alibaba_id = models.CharField(max_length=100, verbose_name='1688商品ID')
    alibaba_sku = models.CharField(max_length=100, blank=True, default='', verbose_name='1688规格')
    supplier_id = models.CharField(max_length=50, blank=True, default='', verbose_name='供应商ID')
    supplier_name = models.CharField(max_length=100, blank=True, default='', verbose_name='供应商名称')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='单价')
    moq = models.IntegerField(default=1, verbose_name='最小起订量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sys_alibaba_match'
        verbose_name = '1688配对'
        verbose_name_plural = verbose_name
