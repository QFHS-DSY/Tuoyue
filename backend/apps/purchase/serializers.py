from rest_framework import serializers
from apps.purchase.models import *

def _m(cls): return type(f'{cls.__name__}Serializer', (serializers.ModelSerializer,), {
    'Meta': type('Meta', (), {'model': cls, 'fields': '__all__', 'read_only_fields': ['id', 'created_at', 'updated_at']})
})

SupplierSerializer = _m(Supplier)
PurchasePlanSerializer = _m(PurchasePlan)
PurchasePlanItemSerializer = _m(PurchasePlanItem)
PurchaseOrderSerializer = _m(PurchaseOrder)
PurchaseOrderItemSerializer = _m(PurchaseOrderItem)
OutsourcingOrderSerializer = _m(OutsourcingOrder)
OutsourcingOrderItemSerializer = _m(OutsourcingOrderItem)
OutsourcingMaterialSerializer = _m(OutsourcingMaterial)
ChangeOrderSerializer = _m(ChangeOrder)
ReturnOrderSerializer = _m(ReturnOrder)
ReturnOrderItemSerializer = _m(ReturnOrderItem)
ProcessPlanSerializer = _m(ProcessPlan)
Account1688AuthSerializer = _m(Account1688Auth)
Sku1688MappingSerializer = _m(Sku1688Mapping)
Order1688Serializer = _m(Order1688)
SupplierReconciliationSerializer = _m(SupplierReconciliation)
TransferOrderSerializer = _m(TransferOrder)
TransferOrderItemSerializer = _m(TransferOrderItem)
SupplierPortalConfigSerializer = _m(SupplierPortalConfig)
SupplierPortalAccountSerializer = _m(SupplierPortalAccount)
SupplierMessageSerializer = _m(SupplierMessage)
SupplierDeliveryOrderSerializer = _m(SupplierDeliveryOrder)
SupplierDeliveryItemSerializer = _m(SupplierDeliveryItem)

__all__ = [k for k in dir() if k.endswith('Serializer')]
