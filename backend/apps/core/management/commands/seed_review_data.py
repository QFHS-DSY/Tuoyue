import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Shop, Product, Order, LogisticsShipment
from apps.creator_mgt.models import Creator, CreatorEcomProfile, Invitation


class Command(BaseCommand):
    help = "一键生成评审用高逼真演示数据"

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 开始通过 Django 后端生成评审演示数据...\n")
        now = timezone.now()

        # 1. 生成店铺 (Shop)
        shop_tiktok, _ = Shop.objects.get_or_create(
            external_shop_id="TK_US_001",
            defaults={"platform": "tiktok", "name": "TikTok 美区自营旗舰店", "status": "active"},
        )
        shop_amazon, _ = Shop.objects.get_or_create(
            external_shop_id="AMZ_NA_002",
            defaults={"platform": "amazon", "name": "Amazon 北美精品店", "status": "active"},
        )
        self.stdout.write("✅ 店铺数据生成完毕")

        # 2. 生成核心商品 (Product)
        products_data = [
            {"platform_product_id": "P_001", "title": "幻影 RK3588 自动化控制终端", "price": "1299.00", "stock": 500},
            {"platform_product_id": "P_002", "title": "重型地下铲运机 1:50 仿真合金模型", "price": "299.50", "stock": 200},
            {"platform_product_id": "P_003", "title": "跨境爆款 智能感应夜灯", "price": "19.90", "stock": 5000},
        ]
        for pd in products_data:
            Product.objects.get_or_create(
                platform="tiktok",
                platform_product_id=pd["platform_product_id"],
                defaults={"title": pd["title"], "price": Decimal(pd["price"]), "stock": pd["stock"]},
            )
        self.stdout.write("✅ 商品数据生成完毕")

        # 3. 生成订单与物流 (Order & Logistics)
        statuses = ["pending", "paid", "shipped", "signed", "completed"]
        buyers = ["Lv Hongyan", "Zhang Dachuan", "Michael Smith", "Emily Chen"]
        locations = [
            {"name": "US", "addr": {"country": "US", "city": "Los Angeles"}},
            {"name": "UK", "addr": {"country": "UK", "city": "London"}},
            {"name": "SG", "addr": {"country": "SG", "city": "Singapore"}},
        ]

        created_orders = 0
        for i in range(1, 81):
            random_days_ago = random.randint(0, 30)
            order_date = now - timedelta(days=random_days_ago)
            status = random.choice(statuses)

            order, _ = Order.objects.get_or_create(
                platform="tiktok",
                order_no=f"ORD-TK-{order_date.strftime('%Y%m%d')}-{i:04d}",
                defaults={
                    "buyer_name": random.choice(buyers),
                    "status": status,
                    "amount": Decimal(random.uniform(15.0, 1500.0)).quantize(Decimal("0.00")),
                    "shipping_address": random.choice(locations)["addr"],
                },
            )

            # 强制修改时间戳以支撑趋势图
            Order.objects.filter(id=order.id).update(created_at=order_date)

            if status in ["shipped", "signed", "completed"]:
                LogisticsShipment.objects.get_or_create(
                    order=order,
                    waybill_no=f"WB{order.id}{i}",
                    defaults={
                        "carrier": "FedEx",
                        "status": "in_transit" if status == "shipped" else "delivered",
                    },
                )
            created_orders += 1

        self.stdout.write(f"✅ 订单与物流大盘数据生成完毕 (共 {created_orders} 条)")

        # 4. 生成达人与邀约 (Creator & Invitation)
        creators_info = [
            ("Tech_DengGe", "US", "A"),
            ("Hardware_Ming", "UK", "A"),
            ("Jiarui_Dev", "SG", "B"),
            ("Zehua_Service", "US", "C"),
        ]
        for handle, region, tier in creators_info:
            c, _ = Creator.objects.get_or_create(
                platform_uid=f"UID_{handle}",
                defaults={"handle": handle, "region": region, "tier": tier, "timezone": "America/Los_Angeles"},
            )
            CreatorEcomProfile.objects.get_or_create(
                creator=c,
                defaults={
                    "tiktok_shop_gpm": Decimal(random.uniform(50.0, 300.0)).quantize(Decimal("0.00"))
                },
            )
            if random.choice([True, False]):
                Invitation.objects.get_or_create(
                    creator=c,
                    channel="email",
                    defaults={
                        "pitch_text": "您好，诚邀您合作测评我们的最新产品！",
                        "status": random.choice(["draft", "sent"]),
                    },
                )
        self.stdout.write("✅ 达人与邀约数据生成完毕")

        self.stdout.write(self.style.SUCCESS("🎉 所有评审演示数据通过 Django 注入成功！"))
