from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.wms.models import *
from apps.wms.serializers import *

def _v(model, serializer, filters=None, search=None, ordering=None):
    attrs = {'queryset': model.objects.all(), 'serializer_class': serializer,
             'filter_backends': [DjangoFilterBackend, SearchFilter, OrderingFilter]}
    if filters: attrs['filterset_fields'] = filters
    if search: attrs['search_fields'] = search
    if ordering: attrs['ordering_fields'] = ordering
    return type(f'{model.__name__}ViewSet', (ModelViewSet,), attrs)

WarehouseWmsViewSet = _v(WarehouseWms, WarehouseWmsSerializer, ['status'], ['name', 'code'], ['id', 'name', 'created_at'])
InventoryViewSet = _v(Inventory, InventorySerializer, ['warehouse_id'], ['sku', 'sku_name'], ['id', 'quantity', 'updated_at'])
InventoryBatchViewSet = _v(InventoryBatch, InventoryBatchSerializer, ['inventory_id'], ['batch_no'], ['id'])
ReceiptOrderViewSet = _v(ReceiptOrder, ReceiptOrderSerializer, ['warehouse_id', 'status', 'source_type'], ['order_no', 'creator'], ['id', 'created_at'])
ReceiptOrderItemViewSet = _v(ReceiptOrderItem, ReceiptOrderItemSerializer, ['order_id'], ['sku', 'sku_name', 'fnsku'], ['id'])
DeliveryOrderViewSet = _v(DeliveryOrder, DeliveryOrderSerializer, ['warehouse_id', 'status', 'source_type'], ['order_no', 'wave_no', 'creator'], ['id', 'created_at'])
DeliveryOrderItemViewSet = _v(DeliveryOrderItem, DeliveryOrderItemSerializer, ['order_id'], ['sku', 'sku_name', 'fnsku'], ['id'])
TransferOrderViewSet = _v(TransferOrder, TransferOrderSerializer, ['from_warehouse_id', 'to_warehouse_id', 'status'], ['order_no', 'creator'], ['id', 'created_at'])
TransferOrderItemViewSet = _v(TransferOrderItem, TransferOrderItemSerializer, ['order_id'], ['sku', 'sku_name'], ['id'])
InventoryCheckViewSet = _v(InventoryCheck, InventoryCheckSerializer, ['warehouse_id', 'status'], ['order_no', 'creator'], ['id', 'created_at'])
InventoryCheckItemViewSet = _v(InventoryCheckItem, InventoryCheckItemSerializer, ['order_id'], ['sku', 'sku_name'], ['id'])
StockFlowViewSet = _v(StockFlow, StockFlowSerializer, ['inventory_id', 'flow_type'], ['order_no', 'sku'], ['id', 'created_at'])
WaveViewSet = _v(Wave, WaveSerializer, ['warehouse_id', 'status'], ['wave_no'], ['id', 'created_at'])
WaveOrderViewSet = _v(WaveOrder, WaveOrderSerializer, ['wave_id'], ['order_no'], ['id'])
PackingTaskViewSet = _v(PackingTask, PackingTaskSerializer, ['warehouse_id', 'status'], ['task_no'], ['id', 'created_at'])
PackingItemViewSet = _v(PackingItem, PackingItemSerializer, ['task_id'], ['box_no', 'sku'], ['id'])
ProductViewSet = _v(Product, ProductSerializer, ['product_status', 'category', 'brand'], ['sku', 'sku_name', 'asin', 'msku', 'fnsku'], ['id', 'created_at'])
OverseasStockingViewSet = _v(OverseasStocking, OverseasStockingSerializer, ['warehouse_id', 'status'], ['order_no'], ['id', 'created_at'])

__all__ = [k for k in dir() if k.endswith('ViewSet')]
