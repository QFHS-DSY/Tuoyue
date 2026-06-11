from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.purchase.models import *
from apps.purchase.serializers import *

def _v(model, serializer, filters=None, search=None, ordering=None):
    attrs = {'queryset': model.objects.all(), 'serializer_class': serializer,
             'filter_backends': [DjangoFilterBackend, SearchFilter, OrderingFilter]}
    if filters: attrs['filterset_fields'] = filters
    if search: attrs['search_fields'] = search
    if ordering: attrs['ordering_fields'] = ordering
    return type(f'{model.__name__}ViewSet', (ModelViewSet,), attrs)

SupplierViewSet = _v(Supplier, SupplierSerializer, ['status', 'settlement_method'], ['name', 'code', 'contact_name'], ['id', 'name', 'created_at'])
PurchasePlanViewSet = _v(PurchasePlan, PurchasePlanSerializer, ['status', 'warehouse_id', 'shop_id'], ['plan_no', 'purchaser'], ['id', 'plan_date', 'created_at'])
PurchasePlanItemViewSet = _v(PurchasePlanItem, PurchasePlanItemSerializer, ['plan_id', 'sku_id'], ['product_name', 'fnsku'], ['id'])
PurchaseOrderViewSet = _v(PurchaseOrder, PurchaseOrderSerializer, ['status', 'supplier_id', 'warehouse_id', 'order_type'], ['order_no', 'creator'], ['id', 'order_date', 'total_amount', 'created_at'])
PurchaseOrderItemViewSet = _v(PurchaseOrderItem, PurchaseOrderItemSerializer, ['order_id', 'sku_id'], ['product_name', 'msku', 'fnsku'], ['id'])
OutsourcingOrderViewSet = _v(OutsourcingOrder, OutsourcingOrderSerializer, ['status', 'supplier_id'], ['order_no', 'purchaser'], ['id', 'order_date', 'created_at'])
OutsourcingOrderItemViewSet = _v(OutsourcingOrderItem, OutsourcingOrderItemSerializer, ['order_id'], ['product_name', 'msku', 'fnsku'], ['id'])
OutsourcingMaterialViewSet = _v(OutsourcingMaterial, OutsourcingMaterialSerializer, ['order_id'], [], ['id'])
ChangeOrderViewSet = _v(ChangeOrder, ChangeOrderSerializer, ['order_type', 'order_id', 'status', 'change_type'], ['change_no'], ['id', 'created_at'])
ReturnOrderViewSet = _v(ReturnOrder, ReturnOrderSerializer, ['status', 'supplier_id', 'return_type'], ['return_no', 'creator'], ['id', 'return_date', 'created_at'])
ReturnOrderItemViewSet = _v(ReturnOrderItem, ReturnOrderItemSerializer, ['return_order_id', 'sku_id'], ['product_name', 'msku', 'fnsku'], ['id'])
ProcessPlanViewSet = _v(ProcessPlan, ProcessPlanSerializer, ['status', 'supplier_id', 'warehouse_id'], ['plan_no', 'purchase_batch_no'], ['id', 'plan_date', 'created_at'])
Account1688AuthViewSet = _v(Account1688Auth, Account1688AuthSerializer, ['status', 'account_type'], ['account_name', 'user_name'], ['id'])
Sku1688MappingViewSet = _v(Sku1688Mapping, Sku1688MappingSerializer, ['sku_id', 'supplier_id', 'status'], ['product_name', 'product_id'], ['id'])
Order1688ViewSet = _v(Order1688, Order1688Serializer, ['status', 'supplier_id', 'platform_status', 'synced', 'purchase_order_created'], ['order_no', 'product_name', 'supplier_name'], ['id', 'order_date', 'created_at'])
SupplierReconciliationViewSet = _v(SupplierReconciliation, SupplierReconciliationSerializer, ['status', 'supplier_id'], ['bill_no'], ['id', 'period_start', 'created_at'])
TransferOrderViewSet = _v(TransferOrder, TransferOrderSerializer, ['status', 'from_warehouse_id', 'to_warehouse_id'], ['transfer_no'], ['id', 'transfer_date', 'created_at'])
TransferOrderItemViewSet = _v(TransferOrderItem, TransferOrderItemSerializer, ['transfer_order_id', 'sku_id'], ['product_name', 'msku', 'fnsku'], ['id'])
SupplierPortalConfigViewSet = _v(SupplierPortalConfig, SupplierPortalConfigSerializer, ['supplier_id', 'status'], [], ['id'])
SupplierPortalAccountViewSet = _v(SupplierPortalAccount, SupplierPortalAccountSerializer, ['supplier_id', 'status'], ['phone', 'username'], ['id'])
SupplierMessageViewSet = _v(SupplierMessage, SupplierMessageSerializer, ['supplier_id', 'read_status', 'message_type'], ['title'], ['id', 'created_at'])
SupplierDeliveryOrderViewSet = _v(SupplierDeliveryOrder, SupplierDeliveryOrderSerializer, ['supplier_id', 'status'], ['delivery_no'], ['id', 'delivery_date', 'created_at'])
SupplierDeliveryItemViewSet = _v(SupplierDeliveryItem, SupplierDeliveryItemSerializer, ['delivery_order_id', 'sku_id'], ['product_name'], ['id'])

__all__ = [k for k in dir() if k.endswith('ViewSet')]
