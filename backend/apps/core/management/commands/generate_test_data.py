"""
生成跨境电商测试数据（商品 + 订单）

用法：
  python manage.py generate_test_data         # 默认 1 万条
  python manage.py generate_test_data 5000     # 指定数量

使用 Django ORM 的 bulk_create 批量插入，不产生 N+1 查询。
依赖：pip install faker（可选，缺失时会降级为随机数生成）
"""
import random
import string
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Order, Product, ProductVariant

try:
    from faker import Faker

    fake = Faker("zh_CN")
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False

PLATFORMS = ["tiktok", "amazon", "1688"]
ORDER_STATUSES = ["pending", "paid", "shipped", "signed", "completed", "cancelled"]


def _random_sku(index: int) -> str:
    """生成唯一 SKU"""
    return f"SKU-{index:06d}"


def _random_platform_id() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=16))


def _fake_title() -> str:
    """生成模拟商品名"""
    prefixes = ["新款", "热销", "爆款", "精品", "高端", "轻奢", "简约", "ins风"]
    items = ["T恤", "连衣裙", "蓝牙耳机", "充电宝", "手机壳", "卫衣", "运动鞋",
             "手表", "背包", "帽子", "围巾", "台灯", "水杯", "收纳盒", "挂画"]
    return f"{random.choice(prefixes)}{random.choice(items)}"


def _fake_buyer_name() -> str:
    if FAKER_AVAILABLE:
        return fake.name()
    first = ["张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴", "徐", "孙", "马", "朱"]
    second = ["伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "洋", "勇", "军", "杰", "娟", "艳", "涛", "明", "超", "秀兰", "霞", "平", "刚", "桂英"]
    return random.choice(first) + random.choice(second)


def _fake_address() -> dict:
    cities = [
        ("Los Angeles", "United States"), ("New York", "United States"),
        ("London", "United Kingdom"), ("Tokyo", "Japan"),
        ("Seoul", "South Korea"), ("Singapore", "Singapore"),
        ("Sydney", "Australia"), ("Berlin", "Germany"),
        ("Paris", "France"), ("Mumbai", "India"),
        ("Shanghai", "China"), ("Shenzhen", "China"),
        ("Guangzhou", "China"),
    ]
    city, country = random.choice(cities)
    return {"country": country, "city": city, "street": f"{random.randint(1,999)} {city} St"}


class Command(BaseCommand):
    help = "批量生成跨境商品 + 订单测试数据（使用 bulk_create）"

    def add_arguments(self, parser):
        parser.add_argument("count", nargs="?", type=int, default=10000,
                            help="生成数据条数（默认 10000）")

    def handle(self, *args, **options):
        total = options["count"]
        now = timezone.now()

        # ── 1. 生成商品 ──
        self.stdout.write(f"正在生成 {total} 条商品数据...")
        products = []
        for i in range(1, total + 1):
            stock = random.randint(0, 500)
            products.append(Product(
                platform=random.choice(PLATFORMS),
                platform_product_id=_random_platform_id(),
                title=_fake_title(),
                price=random.randint(10, 9999) + 0.99,
                stock=stock,
                images=[],
                attributes={"warehouse": random.choice(["深圳仓", "广州仓", "海外仓(英国)"])},
                created_at=now - timedelta(days=random.randint(0, 90), hours=random.randint(0, 23)),
            ))
        Product.objects.bulk_create(products, batch_size=2000)
        self.stdout.write(self.style.SUCCESS(f"  [OK] 商品 {total} 条已插入"))

        # ── 2. 给部分商品生成 Variant ──
        self.stdout.write("正在生成商品变体（SKU）...")
        product_ids = list(Product.objects.values_list("id", flat=True)[:total])
        variants = []
        for pid in product_ids[:total // 10]:  # 约 10% 商品有变体
            for v in range(random.randint(1, 3)):
                variants.append(ProductVariant(
                    product_id=pid,
                    sku=_random_sku(random.randint(100000, 999999)),
                    title=_fake_title(),
                    price=random.randint(5, 500) + 0.99,
                    stock=random.randint(0, 200),
                ))
        ProductVariant.objects.bulk_create(variants, batch_size=2000)
        self.stdout.write(self.style.SUCCESS(f"  [OK] 变体 {len(variants)} 条已插入"))

        # ── 3. 生成订单 ──
        self.stdout.write(f"正在生成 {total} 条订单数据...")
        orders = []
        for i in range(1, total + 1):
            created = now - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))
            status = random.choice(ORDER_STATUSES)
            addr = _fake_address()
            orders.append(Order(
                platform=random.choice(PLATFORMS),
                order_no=f"ORD-{now.strftime('%Y%m%d')}-{i:06d}",
                buyer_name=_fake_buyer_name(),
                status=status,
                amount=random.randint(500, 500000) / 100,
                recipient_name=_fake_buyer_name(),
                recipient_phone=f"+86{random.randint(13800000000, 19999999999)}",
                shipping_address=addr,
                created_at=created,
            ))
        Order.objects.bulk_create(orders, batch_size=2000)
        self.stdout.write(self.style.SUCCESS(f"  [OK] 订单 {total} 条已插入"))

        # ── 汇总统计 ──
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("数据生成完毕！"))
        self.stdout.write(f"  商品:   {Product.objects.count()}")
        self.stdout.write(f"  变体:   {ProductVariant.objects.count()}")
        self.stdout.write(f"  订单:   {Order.objects.count()}")
        self.stdout.write("=" * 50)
