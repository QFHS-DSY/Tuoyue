from rest_framework.routers import DefaultRouter
from apps.tools.views import *

router = DefaultRouter()
router.register(r'walmart-monitor', WalmartMonitorViewSet, basename='tools-walmart-monitor')
router.register(r'logistics-query', LogisticsQueryViewSet, basename='tools-logistics-query')
router.register(r'ai-model-task', AiModelTaskViewSet, basename='tools-ai-model-task')
router.register(r'ai-cutout-task', AiCutoutTaskViewSet, basename='tools-ai-cutout-task')
router.register(r'ai-generate-task', AiGenerateTaskViewSet, basename='tools-ai-generate-task')
router.register(r'approval-type', ApprovalTypeViewSet, basename='tools-approval-type')
router.register(r'approval-task', ApprovalTaskViewSet, basename='tools-approval-task')
router.register(r'approval-record', ApprovalRecordViewSet, basename='tools-approval-record')
router.register(r'ai-product-copy', AiProductCopyViewSet, basename='tools-ai-product-copy')
router.register(r'alert-rule', AlertRuleViewSet, basename='tools-alert-rule')
router.register(r'alert-message', AlertMessageViewSet, basename='tools-alert-message')
router.register(r'price-adjust-task', PriceAdjustTaskViewSet, basename='tools-price-adjust-task')
router.register(r'price-adjust-rule', PriceAdjustRuleViewSet, basename='tools-price-adjust-rule')
router.register(r'price-adjust-log', PriceAdjustLogViewSet, basename='tools-price-adjust-log')

urlpatterns = router.urls
