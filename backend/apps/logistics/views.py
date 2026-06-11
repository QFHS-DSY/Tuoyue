from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.logistics.models import *
from apps.logistics.serializers import *

def _v(model, serializer, filters=None, search=None, ordering=None):
    attrs = {'queryset': model.objects.all(), 'serializer_class': serializer,
             'filter_backends': [DjangoFilterBackend, SearchFilter, OrderingFilter]}
    if filters: attrs['filterset_fields'] = filters
    if search: attrs['search_fields'] = search
    if ordering: attrs['ordering_fields'] = ordering
    return type(f'{model.__name__}ViewSet', (ModelViewSet,), attrs)

LogisticsProviderViewSet = _v(LogisticsProvider, LogisticsProviderSerializer, ['status', 'type', 'settlement_method', 'api_status'], ['name', 'code', 'contact', 'phone'], ['id', 'name', 'created_at'])
LogisticsChannelViewSet = _v(LogisticsChannel, LogisticsChannelSerializer, ['provider_id', 'status', 'channel_type', 'is_tax_included'], ['name', 'code', 'destination'], ['id', 'estimated_days'])
ShippingOrderViewSet = _v(ShippingOrder, ShippingOrderSerializer, ['channel_id', 'status'], ['order_no', 'tracking_no', 'logistics_no'], ['id', 'created_at', 'shipped_at'])
HeadOrderViewSet = _v(HeadOrder, HeadOrderSerializer, ['provider_id', 'status', 'transport_type', 'destination_country'], ['order_no', 'tracking_no', 'related_order_no'], ['id', 'created_at', 'shipped_at', 'arrived_at'])
AddressBookViewSet = _v(AddressBook, AddressBookSerializer, ['address_type', 'country', 'is_default'], ['address_name', 'contact_name', 'phone', 'company_name'], ['id', 'created_at'])
FreightTemplateViewSet = _v(FreightTemplate, FreightTemplateSerializer, ['status'], ['name'], ['id', 'created_at'])
DeclarationRuleViewSet = _v(DeclarationRule, DeclarationRuleSerializer, ['status'], ['name', 'hs_code', 'category'], ['id'])
TrackingNumberPoolViewSet = _v(TrackingNumberPool, TrackingNumberPoolSerializer, ['provider_id', 'status'], ['tracking_no'], ['id', 'created_at'])
LogisticsNumberPoolViewSet = _v(LogisticsNumberPool, LogisticsNumberPoolSerializer, ['provider_id', 'status'], ['logistics_no'], ['id', 'created_at'])
HeadReconciliationViewSet = _v(HeadReconciliation, HeadReconciliationSerializer, ['provider_id', 'status'], ['bill_no'], ['id', 'period_start', 'created_at'])
LogisticsReconciliationViewSet = _v(LogisticsReconciliation, LogisticsReconciliationSerializer, ['provider_id', 'status'], ['bill_no'], ['id', 'period_start', 'created_at'])

__all__ = [k for k in dir() if k.endswith('ViewSet')]
