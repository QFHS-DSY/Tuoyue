from django.conf import settings
from django.db import models


class AmazonListing(models.Model):
    """亚马逊Listing表"""
    msku = models.CharField(max_length=100, verbose_name='Merchant SKU')
    asin = models.CharField(max_length=50, verbose_name='ASIN')
    parent_asin = models.CharField(max_length=50, blank=True, default='', verbose_name='Parent ASIN')
    fnsku = models.CharField(max_length=50, blank=True, default='', verbose_name='FNSKU')
    shop_id = models.BigIntegerField(verbose_name='店铺ID')
    shop_name = models.CharField(max_length=100, blank=True, default='', verbose_name='店铺名称')
    country = models.CharField(max_length=10, verbose_name='站点/国家')
    title = models.CharField(max_length=500, blank=True, default='', verbose_name='商品标题')
    status = models.CharField(max_length=20, default='ACTIVE', db_index=True, verbose_name='状态')
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, verbose_name='评分')
    review_count = models.IntegerField(default=0, verbose_name='评论数')
    sales_volume = models.IntegerField(default=0, verbose_name='销量')
    category_rank = models.IntegerField(null=True, blank=True, verbose_name='大类排名')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='价格')
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='优惠价')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='总价')
    shipping = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='运费')
    points = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='积分(日本站)')
    create_time = models.DateTimeField(null=True, blank=True, verbose_name='创建时间(上架时间)')
    launch_time = models.DateTimeField(null=True, blank=True, verbose_name='开售时间')
    first_order_time = models.DateTimeField(null=True, blank=True, verbose_name='首单时间')
    remark = models.TextField(blank=True, default='', verbose_name='备注')
    fba_available = models.IntegerField(default=0, verbose_name='FBA可售库存')
    fba_pending_transfer = models.IntegerField(default=0, verbose_name='待调仓')
    fba_transferring = models.IntegerField(default=0, verbose_name='调仓中')
    fba_receiving = models.IntegerField(default=0, verbose_name='入库中')
    fba_pending_ship = models.IntegerField(default=0, verbose_name='待发货')
    fba_planned_receive = models.IntegerField(default=0, verbose_name='计划入库')
    fba_in_transit = models.IntegerField(default=0, verbose_name='在途')
    fba_unavailable = models.IntegerField(default=0, verbose_name='不可售')
    synced_at = models.DateTimeField(null=True, blank=True, verbose_name='最后同步时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sales_amazon_listing'
        verbose_name = '亚马逊Listing'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['msku'], name='idx_sales_al_msku'),
            models.Index(fields=['asin'], name='idx_sales_al_asin'),
            models.Index(fields=['shop_id'], name='idx_sales_al_shop'),
            models.Index(fields=['status'], name='idx_sales_al_status'),
        ]


class ListingSkuMapping(models.Model):
    """Listing-SKU配对表"""
    msku = models.CharField(max_length=100, verbose_name='MSKU')
    sku = models.CharField(max_length=100, verbose_name='本地SKU')
    shop_id = models.BigIntegerField(verbose_name='店铺ID')
    asin = models.CharField(max_length=50, blank=True, default='', verbose_name='ASIN')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'sales_listing_sku_mapping'
        verbose_name = 'Listing-SKU配对'
        verbose_name_plural = verbose_name


class ListingOwner(models.Model):
    """Listing负责人表"""
    shop_id = models.BigIntegerField(verbose_name='店铺ID')
    asin = models.CharField(max_length=50, verbose_name='ASIN')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='负责人')
    owner_name = models.CharField(max_length=50, verbose_name='负责人姓名')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_owners', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sales_listing_owner'
        verbose_name = 'Listing负责人'
        verbose_name_plural = verbose_name


class ListingPerformance(models.Model):
    """Listing业绩归属表"""
    shop_id = models.BigIntegerField(verbose_name='店铺ID')
    asin = models.CharField(max_length=50, verbose_name='ASIN')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='业绩归属人')
    owner_name = models.CharField(max_length=50, verbose_name='业绩归属人姓名')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_performances', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'sales_listing_performance'
        verbose_name = 'Listing业绩归属'
        verbose_name_plural = verbose_name


class ListingTag(models.Model):
    """Listing标签表"""
    msku = models.CharField(max_length=100, verbose_name='MSKU')
    tag_id = models.BigIntegerField(verbose_name='标签ID')
    tag_name = models.CharField(max_length=50, verbose_name='标签名称')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'sales_listing_tag'
        verbose_name = 'Listing标签'
        verbose_name_plural = verbose_name


class ListingPriceAdjust(models.Model):
    """Listing调价记录表"""
    msku = models.CharField(max_length=100, verbose_name='MSKU')
    shop_id = models.BigIntegerField(verbose_name='店铺ID')
    before_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='调整前价格')
    after_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='调整后价格')
    before_sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='调整前优惠价')
    after_sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='调整后优惠价')
    sale_start_date = models.DateField(null=True, blank=True, verbose_name='优惠开始日期')
    sale_end_date = models.DateField(null=True, blank=True, verbose_name='优惠结束日期')
    adjust_type = models.CharField(max_length=20, verbose_name='调整类型')
    adjust_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='调整幅度(%)')
    estimated_profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='预估毛利润')
    estimated_profit_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='预估毛利率(%)')
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='操作人')
    operator_name = models.CharField(max_length=50, verbose_name='操作人姓名')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    error_message = models.TextField(blank=True, default='', verbose_name='错误信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'sales_listing_price_adjust'
        verbose_name = 'Listing调价记录'
        verbose_name_plural = verbose_name


class ListingPriceQueue(models.Model):
    """Listing调价队列表"""
    adjust = models.ForeignKey(ListingPriceAdjust, on_delete=models.CASCADE, verbose_name='调价记录')
    msku = models.CharField(max_length=100, verbose_name='MSKU')
    shop_id = models.BigIntegerField(verbose_name='店铺ID')
    status = models.CharField(max_length=20, default='QUEUED', db_index=True, verbose_name='状态')
    retry_count = models.IntegerField(default=0, verbose_name='重试次数')
    error_message = models.TextField(blank=True, default='', verbose_name='错误信息')
    executed_at = models.DateTimeField(null=True, blank=True, verbose_name='执行时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'sales_listing_price_queue'
        verbose_name = 'Listing调价队列'
        verbose_name_plural = verbose_name


class PlatformProduct(models.Model):
    """平台商品主表"""
    product_no = models.CharField(max_length=50, unique=True, verbose_name='商品编号')
    platform = models.CharField(max_length=30, db_index=True, verbose_name='平台类型')
    sku = models.CharField(max_length=100, verbose_name='商品SKU')
    title = models.CharField(max_length=500, verbose_name='商品标题')
    description = models.TextField(blank=True, default='', verbose_name='商品描述')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='原价')
    currency = models.CharField(max_length=10, default='USD', verbose_name='货币类型')
    stock_qty = models.IntegerField(default=0, verbose_name='库存数量')
    available_qty = models.IntegerField(default=0, verbose_name='可售数量')
    status = models.CharField(max_length=20, default='ACTIVE', db_index=True, verbose_name='商品状态')
    image_urls = models.TextField(blank=True, default='', verbose_name='商品图片(JSON)')
    category = models.CharField(max_length=100, blank=True, default='', verbose_name='商品类目')
    brand = models.CharField(max_length=100, blank=True, default='', verbose_name='品牌')
    attributes = models.TextField(blank=True, default='', verbose_name='商品属性(JSON)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sales_platform_product'
        verbose_name = '平台商品'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['platform', 'sku'], name='idx_sales_pp_pl_sku'),
        ]


class AlibabaProduct(models.Model):
    """阿里国际站商品表"""
    product = models.ForeignKey(PlatformProduct, on_delete=models.CASCADE, verbose_name='平台商品')
    alibaba_id = models.CharField(max_length=100, unique=True, verbose_name='阿里商品ID')
    store_name = models.CharField(max_length=100, blank=True, default='', verbose_name='店铺名称')
    store_id = models.CharField(max_length=50, blank=True, default='', verbose_name='店铺ID')
    product_type = models.CharField(max_length=50, blank=True, default='', verbose_name='产品类型')
    min_order_qty = models.IntegerField(default=1, verbose_name='最小起订量')
    moq_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='MOQ价格')
    shelf_life = models.CharField(max_length=50, blank=True, default='', verbose_name='有效期')
    weight = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='重量(kg)')
    package_size = models.CharField(max_length=100, blank=True, default='', verbose_name='包装尺寸')
    hs_code = models.CharField(max_length=50, blank=True, default='', verbose_name='HS编码')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sales_alibaba_product'
        verbose_name = '阿里国际站商品'
        verbose_name_plural = verbose_name


class ShopeeProduct(models.Model):
    """Shopee商品表"""
    product = models.ForeignKey(PlatformProduct, on_delete=models.CASCADE, verbose_name='平台商品')
    shopee_id = models.CharField(max_length=100, unique=True, verbose_name='Shopee商品ID')
    shop_id = models.CharField(max_length=50, verbose_name='店铺ID')
    shop_name = models.CharField(max_length=100, blank=True, default='', verbose_name='店铺名称')
    item_name = models.CharField(max_length=500, blank=True, default='', verbose_name='商品名称')
    description = models.TextField(blank=True, default='', verbose_name='商品描述')
    category_id = models.CharField(max_length=50, blank=True, default='', verbose_name='类目ID')
    category_name = models.CharField(max_length=100, blank=True, default='', verbose_name='类目名称')
    variation_info = models.TextField(blank=True, default='', verbose_name='变体信息(JSON)')
    stock_location = models.CharField(max_length=100, blank=True, default='', verbose_name='库存位置')
    logistics_info = models.TextField(blank=True, default='', verbose_name='物流信息(JSON)')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sales_shopee_product'
        verbose_name = 'Shopee商品'
        verbose_name_plural = verbose_name


class EbayProduct(models.Model):
    """eBay商品表"""
    product = models.ForeignKey(PlatformProduct, on_delete=models.CASCADE, verbose_name='平台商品')
    ebay_item_id = models.CharField(max_length=50, unique=True, verbose_name='eBay商品ID')
    listing_type = models.CharField(max_length=20, blank=True, default='', verbose_name='刊登类型')
    condition = models.CharField(max_length=20, blank=True, default='', verbose_name='商品状态')
    listing_duration = models.IntegerField(null=True, blank=True, verbose_name='刊登时长(天)')
    hit_count = models.IntegerField(default=0, verbose_name='浏览次数')
    watch_count = models.IntegerField(default=0, verbose_name='关注次数')
    bid_count = models.IntegerField(default=0, verbose_name='出价次数')
    start_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='起拍价')
    reserve_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='保留价')
    buy_it_now_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='一口价')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sales_ebay_product'
        verbose_name = 'eBay商品'
        verbose_name_plural = verbose_name


class WalmartProduct(models.Model):
    """Walmart商品表"""
    product = models.ForeignKey(PlatformProduct, on_delete=models.CASCADE, verbose_name='平台商品')
    walmart_id = models.CharField(max_length=100, unique=True, verbose_name='Walmart商品ID')
    gtin = models.CharField(max_length=50, blank=True, default='', verbose_name='GTIN编码')
    upc = models.CharField(max_length=50, blank=True, default='', verbose_name='UPC编码')
    brand_name = models.CharField(max_length=100, blank=True, default='', verbose_name='品牌名称')
    product_category = models.CharField(max_length=200, blank=True, default='', verbose_name='产品类目')
    item_type = models.CharField(max_length=50, blank=True, default='', verbose_name='商品类型')
    fulfillment_type = models.CharField(max_length=20, blank=True, default='', verbose_name='配送类型')
    weight = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, verbose_name='重量(lb)')
    dimensions = models.CharField(max_length=100, blank=True, default='', verbose_name='尺寸')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sales_walmart_product'
        verbose_name = 'Walmart商品'
        verbose_name_plural = verbose_name


class ListingTask(models.Model):
    """刊登任务表"""
    task_no = models.CharField(max_length=50, unique=True, verbose_name='任务编号')
    platform = models.CharField(max_length=30, verbose_name='目标平台')
    product_id = models.BigIntegerField(null=True, blank=True, verbose_name='关联商品ID')
    template_id = models.BigIntegerField(null=True, blank=True, verbose_name='关联模板ID')
    title = models.CharField(max_length=500, verbose_name='商品标题')
    description = models.TextField(blank=True, default='', verbose_name='商品描述')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='销售价格')
    stock_qty = models.IntegerField(default=0, verbose_name='库存数量')
    images = models.TextField(blank=True, default='', verbose_name='图片URL(JSON)')
    attributes = models.TextField(blank=True, default='', verbose_name='属性信息(JSON)')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    error_message = models.TextField(blank=True, default='', verbose_name='错误信息')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sales_listing_task'
        verbose_name = '刊登任务'
        verbose_name_plural = verbose_name


class ListingTemplate(models.Model):
    """刊登模板表"""
    name = models.CharField(max_length=100, verbose_name='模板名称')
    platform = models.CharField(max_length=30, verbose_name='适用平台')
    title_template = models.CharField(max_length=500, blank=True, default='', verbose_name='标题模板')
    description_template = models.TextField(blank=True, default='', verbose_name='描述模板')
    category_id = models.CharField(max_length=50, blank=True, default='', verbose_name='类目ID')
    attributes = models.TextField(blank=True, default='', verbose_name='属性模板(JSON)')
    image_settings = models.TextField(blank=True, default='', verbose_name='图片设置(JSON)')
    pricing_rules = models.TextField(blank=True, default='', verbose_name='定价规则(JSON)')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sales_listing_template'
        verbose_name = '刊登模板'
        verbose_name_plural = verbose_name


class ListingQueue(models.Model):
    """刊登队列表"""
    task = models.ForeignKey(ListingTask, on_delete=models.CASCADE, verbose_name='刊登任务')
    priority = models.IntegerField(default=1, verbose_name='优先级(1-5)')
    status = models.CharField(max_length=20, default='QUEUED', db_index=True, verbose_name='状态')
    retry_count = models.IntegerField(default=0, verbose_name='重试次数')
    error_message = models.TextField(blank=True, default='', verbose_name='错误信息')
    scheduled_time = models.DateTimeField(null=True, blank=True, verbose_name='计划执行时间')
    executed_at = models.DateTimeField(null=True, blank=True, verbose_name='实际执行时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'sales_listing_queue'
        verbose_name = '刊登队列'
        verbose_name_plural = verbose_name


class InventorySyncTask(models.Model):
    """库存同步任务表"""
    task_no = models.CharField(max_length=50, unique=True, verbose_name='任务编号')
    platform = models.CharField(max_length=30, verbose_name='目标平台')
    shop_id = models.BigIntegerField(null=True, blank=True, verbose_name='店铺ID')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    sync_count = models.IntegerField(default=0, verbose_name='同步商品数量')
    success_count = models.IntegerField(default=0, verbose_name='成功数量')
    failed_count = models.IntegerField(default=0, verbose_name='失败数量')
    error_message = models.TextField(blank=True, default='', verbose_name='错误信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')

    class Meta:
        db_table = 'sales_inventory_sync_task'
        verbose_name = '库存同步任务'
        verbose_name_plural = verbose_name


class PriceInfo(models.Model):
    """价格信息表"""
    product_id = models.BigIntegerField(verbose_name='商品ID')
    platform = models.CharField(max_length=30, verbose_name='平台类型')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='当前价格')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='基础价格')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='成本价格')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='运费')
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='利润率(%)')
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='最低价格限制')
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='最高价格限制')
    price_strategy = models.CharField(max_length=50, blank=True, default='', verbose_name='定价策略')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='更新人')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sales_price_info'
        verbose_name = '价格信息'
        verbose_name_plural = verbose_name


class PriceAdjustLog(models.Model):
    """价格调整记录表"""
    product_id = models.BigIntegerField(verbose_name='商品ID')
    platform = models.CharField(max_length=30, verbose_name='平台类型')
    before_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='调整前价格')
    after_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='调整后价格')
    adjust_type = models.CharField(max_length=20, verbose_name='调整类型')
    adjust_reason = models.CharField(max_length=200, blank=True, default='', verbose_name='调整原因')
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='操作人')
    operated_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        db_table = 'sales_price_adjust_log'
        verbose_name = '价格调整记录'
        verbose_name_plural = verbose_name


class TemuPricing(models.Model):
    """Temu核价表"""
    product_id = models.BigIntegerField(verbose_name='商品ID')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='成本价格')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='运费')
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='平台费用')
    other_costs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='其他费用')
    target_profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='目标利润')
    target_profit_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='目标利润率(%)')
    calculated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='核算价格')
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='建议售价')
    status = models.CharField(max_length=20, default='PENDING', db_index=True, verbose_name='状态')
    review_comment = models.TextField(blank=True, default='', verbose_name='审核意见')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='审核人')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='审核时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'sales_temu_pricing'
        verbose_name = 'Temu核价'
        verbose_name_plural = verbose_name
