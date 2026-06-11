from rest_framework.routers import DefaultRouter
from apps.wms.views import *

router = DefaultRouter()
router.register(r'warehouse', WarehouseWmsViewSet, basename='wms-warehouse')
router.register(r'inventory', InventoryViewSet, basename='wms-inventory')
router.register(r'inventory-batch', InventoryBatchViewSet, basename='wms-inventory-batch')
router.register(r'receipt', ReceiptOrderViewSet, basename='wms-receipt')
router.register(r'receipt-item', ReceiptOrderItemViewSet, basename='wms-receipt-item')
router.register(r'delivery', DeliveryOrderViewSet, basename='wms-delivery')
router.register(r'delivery-item', DeliveryOrderItemViewSet, basename='wms-delivery-item')
router.register(r'transfer', TransferOrderViewSet, basename='wms-transfer')
router.register(r'transfer-item', TransferOrderItemViewSet, basename='wms-transfer-item')
router.register(r'inventory-check', InventoryCheckViewSet, basename='wms-inventory-check')
router.register(r'inventory-check-item', InventoryCheckItemViewSet, basename='wms-inventory-check-item')
router.register(r'stock-flow', StockFlowViewSet, basename='wms-stock-flow')
router.register(r'wave', WaveViewSet, basename='wms-wave')
router.register(r'wave-order', WaveOrderViewSet, basename='wms-wave-order')
router.register(r'packing-task', PackingTaskViewSet, basename='wms-packing-task')
router.register(r'packing-item', PackingItemViewSet, basename='wms-packing-item')
router.register(r'product', ProductViewSet, basename='wms-product')
router.register(r'overseas-stocking', OverseasStockingViewSet, basename='wms-overseas-stocking')

urlpatterns = router.urls
