from rest_framework import serializers
from apps.tools.models import *

def _m(cls): return type(f'{cls.__name__}Serializer', (serializers.ModelSerializer,), {
    'Meta': type('Meta', (), {'model': cls, 'fields': '__all__', 'read_only_fields': ['id', 'created_at', 'updated_at']})
})

WalmartMonitorSerializer = _m(WalmartMonitor)
LogisticsQuerySerializer = _m(LogisticsQuery)
AiModelTaskSerializer = _m(AiModelTask)
AiCutoutTaskSerializer = _m(AiCutoutTask)
AiGenerateTaskSerializer = _m(AiGenerateTask)
ApprovalTypeSerializer = _m(ApprovalType)
ApprovalTaskSerializer = _m(ApprovalTask)
ApprovalRecordSerializer = _m(ApprovalRecord)
AiProductCopySerializer = _m(AiProductCopy)
AlertRuleSerializer = _m(AlertRule)
AlertMessageSerializer = _m(AlertMessage)
PriceAdjustTaskSerializer = _m(PriceAdjustTask)
PriceAdjustRuleSerializer = _m(PriceAdjustRule)
PriceAdjustLogSerializer = _m(PriceAdjustLog)

__all__ = [k for k in dir() if k.endswith('Serializer')]
