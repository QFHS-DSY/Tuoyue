from rest_framework import serializers
from apps.sales.models import *

def _m(cls): return type(f'{cls.__name__}Serializer', (serializers.ModelSerializer,), {
    'Meta': type('Meta', (), {'model': cls, 'fields': '__all__', 'read_only_fields': ['id', 'created_at', 'updated_at']})
})

AmazonListingSerializer = _m(AmazonListing)
ListingSkuMappingSerializer = _m(ListingSkuMapping)
ListingOwnerSerializer = _m(ListingOwner)
ListingPerformanceSerializer = _m(ListingPerformance)
ListingTagSerializer = _m(ListingTag)
ListingPriceAdjustSerializer = _m(ListingPriceAdjust)
ListingPriceQueueSerializer = _m(ListingPriceQueue)
PlatformProductSerializer = _m(PlatformProduct)
AlibabaProductSerializer = _m(AlibabaProduct)
ShopeeProductSerializer = _m(ShopeeProduct)
EbayProductSerializer = _m(EbayProduct)
WalmartProductSerializer = _m(WalmartProduct)
ListingTaskSerializer = _m(ListingTask)
ListingTemplateSerializer = _m(ListingTemplate)
ListingQueueSerializer = _m(ListingQueue)
InventorySyncTaskSerializer = _m(InventorySyncTask)
PriceInfoSerializer = _m(PriceInfo)
PriceAdjustLogSerializer = _m(PriceAdjustLog)
TemuPricingSerializer = _m(TemuPricing)

__all__ = [k for k in dir() if k.endswith('Serializer')]
