from rest_framework.routers import DefaultRouter
from apps.purchase.views import *

router = DefaultRouter()
router.register(r'supplier', SupplierViewSet, basename='supplier')
router.register(r'purchase-plan', PurchasePlanViewSet, basename='purchase-plan')
router.register(r'purchase-plan-item', PurchasePlanItemViewSet, basename='purchase-plan-item')
router.register(r'purchase-order', PurchaseOrderViewSet, basename='purchase-order')
router.register(r'purchase-order-item', PurchaseOrderItemViewSet, basename='purchase-order-item')
router.register(r'outsourcing-order', OutsourcingOrderViewSet, basename='outsourcing-order')
router.register(r'outsourcing-order-item', OutsourcingOrderItemViewSet, basename='outsourcing-order-item')
router.register(r'outsourcing-material', OutsourcingMaterialViewSet, basename='outsourcing-material')
router.register(r'change-order', ChangeOrderViewSet, basename='change-order')
router.register(r'return-order', ReturnOrderViewSet, basename='return-order')
router.register(r'return-order-item', ReturnOrderItemViewSet, basename='return-order-item')
router.register(r'process-plan', ProcessPlanViewSet, basename='process-plan')
router.register(r'account-1688-auth', Account1688AuthViewSet, basename='account-1688-auth')
router.register(r'sku-1688-mapping', Sku1688MappingViewSet, basename='sku-1688-mapping')
router.register(r'order-1688', Order1688ViewSet, basename='order-1688')
router.register(r'supplier-reconciliation', SupplierReconciliationViewSet, basename='supplier-reconciliation')
router.register(r'transfer-order', TransferOrderViewSet, basename='transfer-order')
router.register(r'transfer-order-item', TransferOrderItemViewSet, basename='transfer-order-item')
router.register(r'supplier-portal-config', SupplierPortalConfigViewSet, basename='supplier-portal-config')
router.register(r'supplier-portal-account', SupplierPortalAccountViewSet, basename='supplier-portal-account')
router.register(r'supplier-message', SupplierMessageViewSet, basename='supplier-message')
router.register(r'supplier-delivery-order', SupplierDeliveryOrderViewSet, basename='supplier-delivery-order')
router.register(r'supplier-delivery-item', SupplierDeliveryItemViewSet, basename='supplier-delivery-item')

urlpatterns = router.urls
