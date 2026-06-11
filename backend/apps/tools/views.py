from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.tools.models import *
from apps.tools.serializers import *

def _v(model, serializer, filters=None, search=None, ordering=None):
    attrs = {'queryset': model.objects.all(), 'serializer_class': serializer,
             'filter_backends': [DjangoFilterBackend, SearchFilter, OrderingFilter]}
    if filters: attrs['filterset_fields'] = filters
    if search: attrs['search_fields'] = search
    if ordering: attrs['ordering_fields'] = ordering
    return type(f'{model.__name__}ViewSet', (ModelViewSet,), attrs)

WalmartMonitorViewSet = _v(WalmartMonitor, WalmartMonitorSerializer, ['monitor_status', 'follow_status', 'shop_id'], ['product_id', 'msku', 'tag'], ['id', 'start_time', 'created_at'])
LogisticsQueryViewSet = _v(LogisticsQuery, LogisticsQuerySerializer, ['query_type'], ['tracking_number', 'logistics_provider'], ['id', 'query_time'])
AiModelTaskViewSet = _v(AiModelTask, AiModelTaskSerializer, ['status', 'model_type'], ['task_no'], ['id', 'created_at'])
AiCutoutTaskViewSet = _v(AiCutoutTask, AiCutoutTaskSerializer, ['status'], ['task_no'], ['id', 'created_at'])
AiGenerateTaskViewSet = _v(AiGenerateTask, AiGenerateTaskSerializer, ['status'], ['task_no'], ['id', 'created_at'])
ApprovalTypeViewSet = _v(ApprovalType, ApprovalTypeSerializer, [], ['name', 'code'], ['id'])
ApprovalTaskViewSet = _v(ApprovalTask, ApprovalTaskSerializer, ['status', 'type_id'], ['task_no', 'title', 'applicant_name', 'approver_name'], ['id', 'created_at'])
ApprovalRecordViewSet = _v(ApprovalRecord, ApprovalRecordSerializer, ['task_id', 'action'], ['approver_name'], ['id', 'created_at'])
AiProductCopyViewSet = _v(AiProductCopy, AiProductCopySerializer, ['status', 'language'], ['task_no', 'product_type'], ['id', 'created_at'])
AlertRuleViewSet = _v(AlertRule, AlertRuleSerializer, ['dimension', 'is_enabled'], ['rule_name', 'alert_model'], ['id', 'created_at'])
AlertMessageViewSet = _v(AlertMessage, AlertMessageSerializer, ['rule_id', 'read_status', 'process_status'], ['title'], ['id', 'created_at'])
PriceAdjustTaskViewSet = _v(PriceAdjustTask, PriceAdjustTaskSerializer, ['platform', 'status', 'is_enabled'], ['task_name'], ['id', 'created_at'])
PriceAdjustRuleViewSet = _v(PriceAdjustRule, PriceAdjustRuleSerializer, ['task_id', 'rule_type'], [], ['id', 'sort_order'])
PriceAdjustLogViewSet = _v(PriceAdjustLog, PriceAdjustLogSerializer, ['task_id', 'platform', 'status'], [], ['id', 'created_at'])

__all__ = [k for k in dir() if k.endswith('ViewSet')]
