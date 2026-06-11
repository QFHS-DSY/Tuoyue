import uuid
import random
from datetime import timedelta
from rest_framework.validators import UniqueTogetherValidator

from django.utils import timezone
from rest_framework import serializers

from .models import (
    PhoneRebindAppeal,
    CollectionTask,
    InventorySyncLog,
    LogisticsRateCard,
    LogisticsShipment,
    Order,
    PlatformToken,
    Product,
    ProductVariant,
    SmsDispatchLog,
    Shop,
    SyncRule,
)


class CollectionTaskCreateSerializer(serializers.Serializer):
    platform = serializers.ChoiceField(choices=["tiktok", "amazon", "shein", "1688"])
    target_ids = serializers.ListField(child=serializers.CharField(), allow_empty=False)


class Collect1688SingleSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=500)
    source = serializers.ChoiceField(choices=["1688"], default="1688")


class Collect1688BatchSerializer(serializers.Serializer):
    urls = serializers.ListField(child=serializers.URLField(max_length=500), allow_empty=False)
    source = serializers.ChoiceField(choices=["1688"], default="1688")


class GoodsListingSerializer(serializers.Serializer):
    goods_id = serializers.IntegerField()
    platform = serializers.ChoiceField(choices=["tiktok", "amazon", "shein", "1688"])
    shop_id = serializers.CharField(required=False, allow_blank=True)


class GoodsBatchListingSerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.DictField(), allow_empty=False)
    platform = serializers.ChoiceField(choices=["tiktok", "amazon", "shein", "1688"])


class CollectionTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionTask
        fields = "__all__"


class PlatformTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformToken
        fields = ["id", "platform", "account_id", "expires_at", "updated_at", "created_at"]


class SyncRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncRule
        fields = "__all__"


class InventorySyncLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventorySyncLog
        fields = "__all__"


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    # ── 可读写字段（前端表单真实输入，通过 source 映射到模型字段）──
    name = serializers.CharField(source='title', required=False, allow_blank=True)
    skuId = serializers.CharField(source='platform_product_id', required=False, allow_blank=True)

    # ── 只写字段（前端传入，存入 attributes JSON，不出现在响应中）──
    warehouse_type = serializers.CharField(write_only=True, required=False)

    # ── 只读计算字段（由 SerializerMethodField 响应时动态生成）──
    warehouse = serializers.SerializerMethodField()
    safeStock = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()
    locked = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    statusType = serializers.SerializerMethodField()
    statusLabel = serializers.SerializerMethodField()
    lastIn = serializers.SerializerMethodField()
    lastOut = serializers.SerializerMethodField()
    alarmDays = serializers.SerializerMethodField()
    variants = ProductVariantSerializer(many=True, read_only=True)

    def get_safeStock(self, obj):
        # 从 attributes 读取用户设置的安全库存，默认 10
        return int(obj.attributes.get("safe_stock", 10)) if obj.attributes else 10

    def get_warehouse(self, obj):
        """返回格式：深圳仓 (本地仓)"""
        wh_name = obj.attributes.get("warehouse", "深圳仓") if obj.attributes else "深圳仓"
        wh_type = obj.attributes.get("warehouse_type") if obj.attributes else None
        return f"{wh_name} ({wh_type})" if wh_type else wh_name

    def get_available(self, obj): return max(int(obj.stock) - 2, 0)
    def get_locked(self, obj): return 2
    def get_status(self, obj):
        s = obj.stock
        safe = self.get_safeStock(obj)
        if s <= 0:
            return "out"
        if s <= safe:
            return "low"
        return "normal"
    def get_statusType(self, obj):
        return {"out": "danger", "low": "warning", "normal": "success"}.get(self.get_status(obj), "info")
    def get_statusLabel(self, obj):
        return {"out": "缺货", "low": "预警", "normal": "正常"}.get(self.get_status(obj), "未知")
    def get_lastIn(self, obj): return obj.created_at.strftime("%m-%d") if obj.created_at else ""
    def get_lastOut(self, obj): return obj.updated_at.strftime("%m-%d") if obj.updated_at else ""
    def get_alarmDays(self, obj): return 0

    def create(self, validated_data):
        # 提取前端传来的仓库类型，塞入 attributes JSON
        warehouse_type = validated_data.pop('warehouse_type', None)
        attrs = validated_data.get('attributes', {}) or {}
        if warehouse_type:
            attrs['warehouse_type'] = warehouse_type
        if attrs:
            validated_data['attributes'] = attrs
        return super().create(validated_data)

    class Meta:
        model = Product
        fields = "__all__"
        # 显式定义 UniqueTogetherValidator，避免 DRF 自动发现时
        # 因 skuId(source='platform_product_id') 和 platform_product_id 映射冲突而断言失败
        validators = [
            UniqueTogetherValidator(
                queryset=Product.objects.all(),
                fields=['platform', 'platform_product_id']
            )
        ]


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    can_manual_edit_address = serializers.SerializerMethodField()
    order_time = serializers.SerializerMethodField()
    pay_time = serializers.SerializerMethodField()
    status_text = serializers.SerializerMethodField()
    buyer = serializers.SerializerMethodField()
    shipping = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    operation_logs = serializers.SerializerMethodField()
    buyer_message = serializers.SerializerMethodField()

    def get_can_manual_edit_address(self, obj):
        request = self.context.get("request")
        if not request or not getattr(request, "user", None):
            return False
        user = request.user
        if not user.is_authenticated:
            return False
        return user.is_superuser or user.has_perm("core.order_edit")

    def get_order_time(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M") if obj.created_at else ""

    def get_pay_time(self, obj):
        if obj.status in ("paid", "shipped", "signed", "completed"):
            return obj.created_at.strftime("%Y-%m-%d %H:%M") if obj.created_at else ""
        return None

    _STATUS_LABEL_MAP = {
        "pending": "待审核", "paid": "待发货", "shipped": "已发货",
        "signed": "已签收", "completed": "已完成", "cancelled": "已取消",
    }

    def get_status_text(self, obj):
        return self._STATUS_LABEL_MAP.get(obj.status, obj.status)

    def get_buyer(self, obj):
        return {"name": obj.buyer_name, "phone": obj.recipient_phone}

    def get_shipping(self, obj):
        shipment = obj.shipments.first() if hasattr(obj, "shipments") else None
        addr = obj.shipping_address
        if isinstance(addr, dict):
            addr_str = addr.get("city", "") or addr.get("country", "") or ""
        else:
            addr_str = str(addr) if addr else ""
        return {
            "address": addr_str,
            "waybill_no": shipment.waybill_no if shipment else None,
            "carrier": shipment.carrier if shipment else None,
        }

    def get_products(self, obj):
        return [{
            "name": f"商品 #{obj.id}",
            "sku": f"SKU-{obj.order_no[:8]}",
            "price": float(obj.amount),
            "quantity": 1,
            "image": None,
        }]

    def get_items(self, obj):
        return self.get_products(obj)

    def get_operation_logs(self, obj):
        status_flow = ["pending", "paid", "shipped", "signed", "completed"]
        idx = status_flow.index(obj.status) if obj.status in status_flow else -1
        logs = []
        if idx >= 0:
            logs.append({"time": obj.created_at.strftime("%Y-%m-%d %H:%M"), "action": "下单", "operator": "system", "type": "primary"})
        if idx >= 1:
            logs.append({"time": obj.created_at.strftime("%Y-%m-%d %H:%M"), "action": "付款", "operator": "system", "type": "success"})
        if idx >= 2:
            s = obj.shipments.first()
            if s:
                logs.append({"time": s.created_at.strftime("%Y-%m-%d %H:%M"), "action": f"发货（{s.carrier}）", "operator": "system", "type": "warning"})
        if idx >= 4:
            logs.append({"time": obj.updated_at.strftime("%Y-%m-%d %H:%M"), "action": "完成交易", "operator": "system", "type": "success"})
        return logs

    def get_buyer_message(self, obj):
        return ""

    class Meta:
        model = Order
        fields = "__all__"


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[s[0] for s in Order.STATUS_CHOICES])


class OrderAddressUpdateSerializer(serializers.Serializer):
    recipient_name = serializers.CharField(max_length=128, required=False, allow_blank=True)
    recipient_phone = serializers.CharField(max_length=32, required=False, allow_blank=True)
    shipping_address = serializers.JSONField(required=False)


class LogisticsShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogisticsShipment
        fields = "__all__"


class FreightEstimateSerializer(serializers.Serializer):
    destination = serializers.CharField(max_length=64)
    weight_kg = serializers.FloatField(min_value=0.01)
    length_cm = serializers.FloatField(min_value=0.01)
    width_cm = serializers.FloatField(min_value=0.01)
    height_cm = serializers.FloatField(min_value=0.01)


class LogisticsRateCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogisticsRateCard
        fields = "__all__"


class FreightEstimateQuerySerializer(serializers.Serializer):
    length_cm = serializers.DecimalField(max_digits=10, decimal_places=2)
    width_cm = serializers.DecimalField(max_digits=10, decimal_places=2)
    height_cm = serializers.DecimalField(max_digits=10, decimal_places=2)
    actual_weight_kg = serializers.DecimalField(max_digits=10, decimal_places=3)
    destination_country = serializers.CharField(max_length=8)
    carrier = serializers.CharField(required=False, allow_blank=True, max_length=64)


class SmsCodeSendSerializer(serializers.Serializer):
    phone = serializers.RegexField(regex=r"^\d{6,20}$")
    country_code = serializers.RegexField(regex=r"^\d{1,4}$", required=False, default="86")
    voice = serializers.BooleanField(required=False, default=False)
    captcha_id = serializers.CharField(required=False, allow_blank=True)
    captcha_answer = serializers.CharField(required=False, allow_blank=True)


class SmsCodeVerifySerializer(serializers.Serializer):
    phone = serializers.RegexField(regex=r"^\+?\d{6,20}$")
    code = serializers.RegexField(regex=r"^\d{4,6}$")


class MobileAuthSerializer(serializers.Serializer):
    mobile = serializers.RegexField(regex=r"^\d{6,20}$")
    country_code = serializers.RegexField(regex=r"^\d{1,4}$", required=False, default="86")
    code = serializers.RegexField(regex=r"^\d{4,6}$")
    agreed_privacy = serializers.BooleanField(required=True)


class AccountDeleteSerializer(serializers.Serializer):
    code = serializers.RegexField(regex=r"^\d{4,6}$")
    reason = serializers.CharField(required=False, allow_blank=True, max_length=255)


class CarrierOneTapSerializer(serializers.Serializer):
    mobile = serializers.RegexField(regex=r"^\d{6,20}$")
    country_code = serializers.RegexField(regex=r"^\d{1,4}$", required=False, default="86")
    token = serializers.CharField()
    carrier = serializers.CharField(required=False, allow_blank=True)


class PhoneRebindAppealSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneRebindAppeal
        fields = "__all__"
        read_only_fields = ["user", "status", "reviewer", "review_note", "created_at", "updated_at"]


class SmsChannelStatsQuerySerializer(serializers.Serializer):
    days = serializers.IntegerField(min_value=1, max_value=30, required=False, default=7)


class SmsDispatchLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmsDispatchLog
        fields = "__all__"
