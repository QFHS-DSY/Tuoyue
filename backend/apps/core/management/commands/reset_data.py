import random
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from apps.core.models import (
    Product, ProductVariant, Order, InventoryAdjustment, OrderRemark,
    InventorySyncLog, Shop, Warehouse, PlatformToken
)
from apps.sku_mgt.models import Sku


class Command(BaseCommand):
    help = "清空并重置精简测试数据"

    def handle(self, *args, **options):
        now = timezone.now()

        # 清空
        for m in [OrderRemark, InventoryAdjustment, ProductVariant, Order, Product,
                  InventorySyncLog, Sku, PlatformToken]:
            m.objects.all().delete()
        self.stdout.write("旧数据已清空")

        # 仓库
        for wd in [{"code":"SZ-001","name":"Shenzhen WH","status":"active"},
                   {"code":"GZ-001","name":"Guangzhou WH","status":"active"},
                   {"code":"UK-001","name":"UK Overseas WH","status":"active"}]:
            Warehouse.objects.get_or_create(code=wd["code"], defaults=wd)
        self.stdout.write(f"Warehouses: {Warehouse.objects.count()}")

        # 店铺
        for sd in [{"platform":"tiktok","external_shop_id":"TK001","name":"TikTok Flagship","status":"active"},
                   {"platform":"amazon","external_shop_id":"AMZ001","name":"Amazon Global","status":"active"},
                   {"platform":"1688","external_shop_id":"1688001","name":"1688 Direct","status":"active"},
                   {"platform":"tiktok","external_shop_id":"TK002","name":"TikTok Fashion","status":"active"}]:
            Shop.objects.get_or_create(external_shop_id=sd["external_shop_id"], defaults=sd)
        self.stdout.write(f"Shops: {Shop.objects.count()}")

        # 80 个商品
        prefixes = ["New","Hot","Premium","Simple","Style","Classic","Fashion"]
        items = ["T-Shirt","Dress","Earphone","Powerbank","Case","Sweater","Shoes",
                 "Watch","Bag","Hat","Scarf","Lamp","Cup","Box","Poster"]
        products = []
        for i in range(1, 81):
            stock = 0 if i > 75 else random.randint(0, 80)
            products.append(Product(
                platform=random.choice(["tiktok","amazon","1688"]),
                platform_product_id=f"SKU-TEST-{i:04d}",
                title=f"{random.choice(prefixes)} {random.choice(items)}",
                price=random.randint(15, 9999) + 0.99,
                stock=stock,
                images=[],
                attributes={"warehouse": random.choice(["Shenzhen WH","Guangzhou WH","UK Overseas WH"])},
                created_at=now - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23)),
            ))
        Product.objects.bulk_create(products, batch_size=2000)
        self.stdout.write(f"Products: {Product.objects.count()}")

        # 20 个订单
        statuses = ["pending","paid","shipped","signed","completed","cancelled"]
        weights = [3, 3, 4, 2, 5, 3]
        names = ["Zhang Wei","Li Na","Wang Fang","Liu Yang","Chen Jing","Yang Lei","Zhao Min","Huang Jie"]
        orders = []
        for i in range(1, 21):
            created = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            status = random.choices(statuses, weights=weights, k=1)[0]
            city = random.choice(["Los Angeles","London","Tokyo","Berlin","Sydney"])
            orders.append(Order(
                platform=random.choice(["tiktok","amazon","1688"]),
                order_no=f"ORD-{now.strftime('%Y%m%d')}-{i:04d}",
                buyer_name=random.choice(names),
                status=status,
                amount=random.randint(500, 500000) / 100,
                recipient_name=random.choice(names),
                recipient_phone=f"+86{random.randint(13800000000, 13999999999)}",
                shipping_address={"country": random.choice(["US","UK","JP","DE","AU"]),
                                  "city": city, "street": f"{random.randint(1,999)} {city} St"},
                created_at=created,
            ))
        Order.objects.bulk_create(orders, batch_size=2000)
        status_counts = {s: Order.objects.filter(status=s).count() for s in statuses}
        self.stdout.write(f"Orders: {Order.objects.count()} ({status_counts})")

        self.stdout.write(self.style.SUCCESS("=== Data reset complete ==="))
