import random
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from apps.core.models import (
    Product, ProductVariant, Order, InventoryAdjustment, OrderRemark,
    InventorySyncLog, Shop, Warehouse, PlatformToken
)
from apps.sku_mgt.models import Sku

# ── 清空旧数据 ──
print("清空旧数据...")
for m in [OrderRemark, InventoryAdjustment, ProductVariant, Order, Product,
          InventorySyncLog, Sku, PlatformToken]:
    m.objects.all().delete()
print("  OK - 旧数据已清空")

# ── 创建默认仓库 ──
warehouses_data = [
    {"code": "SZ-001", "name": "深圳前海仓", "status": "active"},
    {"code": "GZ-001", "name": "广州白云仓", "status": "active"},
    {"code": "UK-001", "name": "海外仓(英国)", "status": "active"},
]
for wd in warehouses_data:
    Warehouse.objects.get_or_create(code=wd["code"], defaults=wd)
print(f"  OK - 仓库 {len(warehouses_data)} 个")

# ── 创建模拟店铺 ──
shops_data = [
    {"platform": "tiktok", "external_shop_id": "TK001", "name": "TikTok 旗舰店", "status": "active"},
    {"platform": "amazon", "external_shop_id": "AMZ001", "name": "Amazon 全球店", "status": "active"},
    {"platform": "1688",   "external_shop_id": "1688001",  "name": "1688 诚信通", "status": "active"},
    {"platform": "tiktok", "external_shop_id": "TK002", "name": "TikTok 女装专营店", "status": "active"},
]
for sd in shops_data:
    Shop.objects.get_or_create(external_shop_id=sd["external_shop_id"], defaults=sd)
print(f"  OK - 店铺 {len(shops_data)} 个")

# ── 生成 80 个商品 ──
print("生成 80 个商品...")
platforms = ["tiktok", "amazon", "1688"]
prefixes = ["新款", "热销", "爆款", "精品", "高端", "轻奢", "简约"]
items = ["T恤", "连衣裙", "蓝牙耳机", "充电宝", "手机壳", "卫衣", "运动鞋",
         "手表", "背包", "帽子", "围巾", "台灯", "水杯", "收纳盒", "挂画"]
now = timezone.now()
products = []
for i in range(1, 81):
    stock = 0 if i > 75 else random.randint(0, 80)
    key = f"SKU-TEST-{i:04d}"
    products.append(Product(
        platform=random.choice(platforms),
        platform_product_id=key,
        title=f"{random.choice(prefixes)}{random.choice(items)}",
        price=random.randint(15, 9999) + 0.99,
        stock=stock,
        images=[],
        attributes={"warehouse": random.choice(["深圳前海仓", "广州白云仓", "海外仓(英国)"])},
        created_at=now - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23)),
    ))
Product.objects.bulk_create(products, batch_size=2000)
print(f"  OK - 商品 80 个（库存>0: 75个, 预警/断货: 5个）")

# ── 生成 20 个订单 ──
print("生成 20 个订单...")
statuses = ["pending", "paid", "shipped", "signed", "completed", "cancelled"]
weights = [3, 3, 4, 2, 5, 3]  # 分布权重
orders = []
for i in range(1, 21):
    created = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
    status = random.choices(statuses, weights=weights, k=1)[0]
    orders.append(Order(
        platform=random.choice(platforms),
        order_no=f"ORD-{now.strftime('%Y%m%d')}-{i:04d}",
        buyer_name=random.choice(["张伟","李娜","王芳","刘洋","陈静","杨磊","赵敏","黄杰"]),
        status=status,
        amount=random.randint(500, 500000) / 100,
        recipient_name=random.choice(["张伟","李娜","王芳","刘洋"]),
        recipient_phone=f"+86{random.randint(13800000000, 13999999999)}",
        shipping_address={
            "country": random.choice(["United States","United Kingdom","Japan","Germany","Australia"]),
            "city": random.choice(["Los Angeles","London","Tokyo","Berlin","Sydney"]),
            "street": f"{random.randint(1,999)} Main St"
        },
        created_at=created,
    ))
Order.objects.bulk_create(orders, batch_size=2000)
print(f"  OK - 订单 20 个（状态分布: " +
      ", ".join(f"{s}={Order.objects.filter(status=s).count()}" for s in statuses) + "）")

# ── 汇总 ──
print(f"\n========================")
print(f"商品: {Product.objects.count()}")
print(f"订单: {Order.objects.count()}")
print(f"店铺: {Shop.objects.count()}")
print(f"仓库: {Warehouse.objects.count()}")
print(f"=========================")
