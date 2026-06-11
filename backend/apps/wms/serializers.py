from rest_framework import serializers
from apps.wms.models import *

def _m(cls): return type(f'{cls.__name__}Serializer', (serializers.ModelSerializer,), {
    'Meta': type('Meta', (), {'model': cls, 'fields': '__all__', 'read_only_fields': ['id', 'created_at', 'updated_at']})
})

WarehouseWmsSerializer = _m(WarehouseWms)
InventorySerializer = _m(Inventory)
InventoryBatchSerializer = _m(InventoryBatch)
ReceiptOrderSerializer = _m(ReceiptOrder)
ReceiptOrderItemSerializer = _m(ReceiptOrderItem)
DeliveryOrderSerializer = _m(DeliveryOrder)
DeliveryOrderItemSerializer = _m(DeliveryOrderItem)
TransferOrderSerializer = _m(TransferOrder)
TransferOrderItemSerializer = _m(TransferOrderItem)
InventoryCheckSerializer = _m(InventoryCheck)
InventoryCheckItemSerializer = _m(InventoryCheckItem)
StockFlowSerializer = _m(StockFlow)
WaveSerializer = _m(Wave)
WaveOrderSerializer = _m(WaveOrder)
PackingTaskSerializer = _m(PackingTask)
PackingItemSerializer = _m(PackingItem)
ProductSerializer = _m(Product)
OverseasStockingSerializer = _m(OverseasStocking)

__all__ = [k for k in dir() if k.endswith('Serializer')]
