from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.sales.models import *
from apps.sales.serializers import *

def _v(model, serializer, filters=None, search=None, ordering=None):
    attrs = {'queryset': model.objects.all(), 'serializer_class': serializer,
             'filter_backends': [DjangoFilterBackend, SearchFilter, OrderingFilter]}
    if filters: attrs['filterset_fields'] = filters
    if search: attrs['search_fields'] = search
    if ordering: attrs['ordering_fields'] = ordering
    return type(f'{model.__name__}ViewSet', (ModelViewSet,), attrs)

AmazonListingViewSet = _v(AmazonListing, AmazonListingSerializer, ['status', 'shop_id', 'country'], ['msku', 'asin', 'fnsku', 'title', 'shop_name'], ['id', 'sales_volume', 'rating', 'created_at'])
ListingSkuMappingViewSet = _v(ListingSkuMapping, ListingSkuMappingSerializer, ['shop_id'], ['msku', 'sku', 'asin'], ['id'])
ListingOwnerViewSet = _v(ListingOwner, ListingOwnerSerializer, ['shop_id', 'owner_id'], ['asin', 'owner_name'], ['id'])
ListingPerformanceViewSet = _v(ListingPerformance, ListingPerformanceSerializer, ['shop_id', 'owner_id'], ['asin', 'owner_name'], ['id'])
ListingTagViewSet = _v(ListingTag, ListingTagSerializer, [], ['msku', 'tag_name'], ['id'])
ListingPriceAdjustViewSet = _v(ListingPriceAdjust, ListingPriceAdjustSerializer, ['shop_id', 'status', 'adjust_type'], ['msku', 'operator_name'], ['id', 'created_at'])
ListingPriceQueueViewSet = _v(ListingPriceQueue, ListingPriceQueueSerializer, ['shop_id', 'status'], ['msku'], ['id', 'created_at'])
PlatformProductViewSet = _v(PlatformProduct, PlatformProductSerializer, ['platform', 'status', 'category', 'brand'], ['sku', 'title', 'product_no'], ['id', 'price', 'created_at'])
AlibabaProductViewSet = _v(AlibabaProduct, AlibabaProductSerializer, ['product_id'], ['alibaba_id', 'store_name'], ['id'])
ShopeeProductViewSet = _v(ShopeeProduct, ShopeeProductSerializer, ['product_id'], ['shopee_id', 'shop_name', 'item_name'], ['id'])
EbayProductViewSet = _v(EbayProduct, EbayProductSerializer, ['product_id'], ['ebay_item_id'], ['id'])
WalmartProductViewSet = _v(WalmartProduct, WalmartProductSerializer, ['product_id'], ['walmart_id', 'brand_name'], ['id'])
ListingTaskViewSet = _v(ListingTask, ListingTaskSerializer, ['platform', 'status'], ['task_no', 'title'], ['id', 'created_at'])
ListingTemplateViewSet = _v(ListingTemplate, ListingTemplateSerializer, ['platform', 'is_active'], ['name'], ['id'])
ListingQueueViewSet = _v(ListingQueue, ListingQueueSerializer, ['task_id', 'status', 'priority'], [], ['id', 'created_at'])
InventorySyncTaskViewSet = _v(InventorySyncTask, InventorySyncTaskSerializer, ['platform', 'status', 'shop_id'], ['task_no'], ['id', 'created_at'])
PriceInfoViewSet = _v(PriceInfo, PriceInfoSerializer, ['platform'], [], ['id', 'updated_at'])
PriceAdjustLogViewSet = _v(PriceAdjustLog, PriceAdjustLogSerializer, ['platform', 'adjust_type', 'product_id'], [], ['id', 'operated_at'])
TemuPricingViewSet = _v(TemuPricing, TemuPricingSerializer, ['status', 'product_id'], [], ['id', 'created_at'])

__all__ = [k for k in dir() if k.endswith('ViewSet')]
