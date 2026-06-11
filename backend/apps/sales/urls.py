from rest_framework.routers import DefaultRouter
from apps.sales.views import *

router = DefaultRouter()
router.register(r'amazon-listing', AmazonListingViewSet, basename='sales-amazon-listing')
router.register(r'listing-sku-mapping', ListingSkuMappingViewSet, basename='sales-listing-sku-mapping')
router.register(r'listing-owner', ListingOwnerViewSet, basename='sales-listing-owner')
router.register(r'listing-performance', ListingPerformanceViewSet, basename='sales-listing-performance')
router.register(r'listing-tag', ListingTagViewSet, basename='sales-listing-tag')
router.register(r'listing-price-adjust', ListingPriceAdjustViewSet, basename='sales-listing-price-adjust')
router.register(r'listing-price-queue', ListingPriceQueueViewSet, basename='sales-listing-price-queue')
router.register(r'platform-product', PlatformProductViewSet, basename='sales-platform-product')
router.register(r'alibaba-product', AlibabaProductViewSet, basename='sales-alibaba-product')
router.register(r'shopee-product', ShopeeProductViewSet, basename='sales-shopee-product')
router.register(r'ebay-product', EbayProductViewSet, basename='sales-ebay-product')
router.register(r'walmart-product', WalmartProductViewSet, basename='sales-walmart-product')
router.register(r'listing-task', ListingTaskViewSet, basename='sales-listing-task')
router.register(r'listing-template', ListingTemplateViewSet, basename='sales-listing-template')
router.register(r'listing-queue', ListingQueueViewSet, basename='sales-listing-queue')
router.register(r'inventory-sync-task', InventorySyncTaskViewSet, basename='sales-inventory-sync-task')
router.register(r'price-info', PriceInfoViewSet, basename='sales-price-info')
router.register(r'price-adjust-log', PriceAdjustLogViewSet, basename='sales-price-adjust-log')
router.register(r'temu-pricing', TemuPricingViewSet, basename='sales-temu-pricing')

urlpatterns = router.urls
