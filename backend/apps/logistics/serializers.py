from rest_framework import serializers
from apps.logistics.models import *

def _m(cls): return type(f'{cls.__name__}Serializer', (serializers.ModelSerializer,), {
    'Meta': type('Meta', (), {'model': cls, 'fields': '__all__', 'read_only_fields': ['id', 'created_at', 'updated_at']})
})

LogisticsProviderSerializer = _m(LogisticsProvider)
LogisticsChannelSerializer = _m(LogisticsChannel)
ShippingOrderSerializer = _m(ShippingOrder)
HeadOrderSerializer = _m(HeadOrder)
AddressBookSerializer = _m(AddressBook)
FreightTemplateSerializer = _m(FreightTemplate)
DeclarationRuleSerializer = _m(DeclarationRule)
TrackingNumberPoolSerializer = _m(TrackingNumberPool)
LogisticsNumberPoolSerializer = _m(LogisticsNumberPool)
HeadReconciliationSerializer = _m(HeadReconciliation)
LogisticsReconciliationSerializer = _m(LogisticsReconciliation)

__all__ = [k for k in dir() if k.endswith('Serializer')]
