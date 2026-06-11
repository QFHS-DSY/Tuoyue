from rest_framework.routers import DefaultRouter
from apps.logistics.views import *

router = DefaultRouter()
router.register(r'provider', LogisticsProviderViewSet, basename='logistics-provider')
router.register(r'channel', LogisticsChannelViewSet, basename='logistics-channel')
router.register(r'shipping-order', ShippingOrderViewSet, basename='logistics-shipping-order')
router.register(r'head-order', HeadOrderViewSet, basename='logistics-head-order')
router.register(r'address-book', AddressBookViewSet, basename='logistics-address-book')
router.register(r'freight-template', FreightTemplateViewSet, basename='logistics-freight-template')
router.register(r'declaration-rule', DeclarationRuleViewSet, basename='logistics-declaration-rule')
router.register(r'tracking-pool', TrackingNumberPoolViewSet, basename='logistics-tracking-pool')
router.register(r'logistics-pool', LogisticsNumberPoolViewSet, basename='logistics-number-pool')
router.register(r'head-reconciliation', HeadReconciliationViewSet, basename='logistics-head-reconciliation')
router.register(r'reconciliation', LogisticsReconciliationViewSet, basename='logistics-reconciliation')

urlpatterns = router.urls
