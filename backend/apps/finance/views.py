from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.finance.models import *
from apps.finance.serializers import *

def _v(model, serializer, filters=None, search=None, ordering=None):
    """Factory for a standard ModelViewSet."""
    attrs = {'queryset': model.objects.all(), 'serializer_class': serializer,
             'filter_backends': [DjangoFilterBackend, SearchFilter, OrderingFilter]}
    if filters: attrs['filterset_fields'] = filters
    if search: attrs['search_fields'] = search
    if ordering: attrs['ordering_fields'] = ordering
    return type(f'{model.__name__}ViewSet', (ModelViewSet,), attrs)

PaymentRequestPoolViewSet = _v(PaymentRequestPool, PaymentRequestPoolSerializer,
    ['pool_type', 'source_type', 'status', 'supplier_id'], ['source_no', 'supplier_name', 'payee_object'], ['id', 'created_at'])
PaymentRequestViewSet = _v(PaymentRequest, PaymentRequestSerializer,
    ['status', 'supplier_id', 'payable_type'], ['request_no', 'supplier_name'], ['id', 'created_at', 'total_amount'])
PaymentRequestItemViewSet = _v(PaymentRequestItem, PaymentRequestItemSerializer,
    ['request_id', 'source_type'], ['item_name', 'source_no'], ['id'])
PaymentRecordViewSet = _v(PaymentRecord, PaymentRecordSerializer,
    ['request_id', 'pay_method'], ['payer_name'], ['id', 'pay_date'])
ReceiptOrderViewSet = _v(ReceiptOrder, ReceiptOrderSerializer,
    ['status', 'customer_id'], ['receipt_no', 'customer_name'], ['id', 'created_at'])
ReceiptOrderItemViewSet = _v(ReceiptOrderItem, ReceiptOrderItemSerializer,
    ['receipt_id'], ['item_name', 'source_no'], ['id'])
TransactionFlowViewSet = _v(TransactionFlow, TransactionFlowSerializer,
    ['transaction_type', 'source_type', 'counterparty_id'], ['flow_no', 'counterparty_name'], ['id', 'transaction_date'])
OrderProfitViewSet = _v(OrderProfit, OrderProfitSerializer,
    ['settlement_month', 'msku'], ['order_id', 'msku', 'sku'], ['id', 'profit'])
SettlementProfitViewSet = _v(SettlementProfit, SettlementProfitSerializer,
    ['settlement_month'], ['settlement_month'], ['id', 'total_profit'])
BillDetailViewSet = _v(BillDetail, BillDetailSerializer,
    ['platform', 'account_id', 'settlement_month'], ['bill_no', 'order_id', 'msku'], ['id', 'transaction_date'])
CollectionDetailViewSet = _v(CollectionDetail, CollectionDetailSerializer,
    ['status', 'settlement_month'], ['order_id', 'msku'], ['id', 'expected_date'])
ExpenseRecordViewSet = _v(ExpenseRecord, ExpenseRecordSerializer,
    ['expense_type'], ['expense_no'], ['id', 'created_at'])
CostDiagnosisViewSet = _v(CostDiagnosis, CostDiagnosisSerializer,
    ['status', 'diagnosis_type', 'settlement_month'], ['sku', 'msku'], ['id', 'created_at'])
CostResetRecordViewSet = _v(CostResetRecord, CostResetRecordSerializer,
    ['settlement_month'], ['batch_no', 'sku'], ['id', 'created_at'])
CostValuationViewSet = _v(CostValuation, CostValuationSerializer,
    ['valuation_month'], ['sku', 'msku'], ['id', 'created_at'])
WfsCostViewSet = _v(WfsCost, WfsCostSerializer,
    ['valuation_date', 'cost_method'], ['sku', 'fnsku'], ['id'])
ApprovalFlowViewSet = _v(ApprovalFlow, ApprovalFlowSerializer,
    ['document_type', 'document_id', 'status'], ['approver_name'], ['id'])
AmazonSummaryReportViewSet = _v(AmazonSummaryReport, AmazonSummaryReportSerializer,
    ['account_id', 'settlement_month'], ['report_no'], ['id'])
ClosingPeriodViewSet = _v(ClosingPeriod, ClosingPeriodSerializer,
    ['period_month', 'cost_closed', 'profit_closed'], ['period_month'], ['id'])
ClosingLogViewSet = _v(ClosingLog, ClosingLogSerializer,
    ['period_month', 'closing_type', 'action'], [], ['id', 'created_at'])
ClosingSettingViewSet = _v(ClosingSetting, ClosingSettingSerializer,
    [], [], ['id'])
AdInvoiceHeaderViewSet = _v(AdInvoiceHeader, AdInvoiceHeaderSerializer,
    ['platform', 'account_id', 'status'], ['invoice_no'], ['id', 'invoice_date'])
AdInvoiceDetailViewSet = _v(AdInvoiceDetail, AdInvoiceDetailSerializer,
    ['header_id'], ['campaign_name', 'ad_group'], ['id'])
AdInvoiceAllocationViewSet = _v(AdInvoiceAllocation, AdInvoiceAllocationSerializer,
    ['detail_id', 'settlement_month'], ['allocation_type', 'allocated_to'], ['id'])
DelayedSettlementViewSet = _v(DelayedSettlement, DelayedSettlementSerializer,
    ['account_id', 'settlement_month', 'status'], ['settlement_no'], ['id'])
DelayedSettlementSettingViewSet = _v(DelayedSettlementSetting, DelayedSettlementSettingSerializer,
    ['account_id'], [], ['id'])
DelayedSettlementAdjustmentViewSet = _v(DelayedSettlementAdjustment, DelayedSettlementAdjustmentSerializer,
    ['settlement_id'], [], ['id'])
ProfitReportConfigViewSet = _v(ProfitReportConfig, ProfitReportConfigSerializer,
    [], ['config_key'], ['id'])
ExpenseAllocationRuleViewSet = _v(ExpenseAllocationRule, ExpenseAllocationRuleSerializer,
    ['status'], ['rule_name'], ['id'])
ProfitReportVersionViewSet = _v(ProfitReportVersion, ProfitReportVersionSerializer,
    ['settlement_month', 'is_current'], [], ['id'])
PerformanceReportViewSet = _v(PerformanceReport, PerformanceReportSerializer,
    ['report_month', 'employee_id', 'department_id'], ['employee_name', 'department_name'], ['id'])
EmployeeDepartmentRelViewSet = _v(EmployeeDepartmentRel, EmployeeDepartmentRelSerializer,
    ['department_id'], ['department_name'], ['id'])
TurnoverHandoverViewSet = _v(TurnoverHandover, TurnoverHandoverSerializer,
    [], ['from_employee_name', 'to_employee_name'], ['id', 'handover_date'])
ExpenseTypeViewSet = _v(ExpenseType, ExpenseTypeSerializer,
    ['status'], ['type_name', 'type_code'], ['id'])
ExpenseOrderViewSet = _v(ExpenseOrder, ExpenseOrderSerializer,
    ['status', 'expense_type_id'], ['order_no'], ['id', 'created_at'])
ExpenseTemplateViewSet = _v(ExpenseTemplate, ExpenseTemplateSerializer,
    ['expense_type_id'], ['template_name'], ['id'])
ProfitCheckRuleViewSet = _v(ProfitCheckRule, ProfitCheckRuleSerializer,
    ['is_enabled'], ['rule_name'], ['id'])

__all__ = [k for k in dir() if k.endswith('ViewSet')]
