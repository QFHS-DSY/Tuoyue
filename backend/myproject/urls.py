from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

from apps.common.metrics import metrics_view

# OpenAPI / 文档页必须匿名可访问，便于前端 B 拉取契约（不受 DEFAULT_PERMISSION_CLASSES 影响）
_SCHEMA_AUTH = {"permission_classes": [AllowAny], "authentication_classes": []}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(**_SCHEMA_AUTH), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema", **_SCHEMA_AUTH), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema", **_SCHEMA_AUTH), name="redoc"),
    path("metrics", metrics_view, name="metrics"),
    path("api/sku/", include("apps.sku_mgt.urls")),
    # 核心业务 API（含 _common_urls / _v1_real_urls / _demo_urls / _business_auth_urls）
    # 生成路径示例：/api/orders/、/api/v1/goods/list、/api/dashboard/stats
    path("api/", include("apps.core.urls")),
    # 达人管理（独占 /api/creators/ 等前缀，不与 core 重叠）
    path("api/", include("apps.creator_mgt.urls")),
    # SKU 管理（独占 /api/sku/ 前缀）
    path("api/sku/", include("apps.sku_mgt.urls")),
    # 任务管理（仅含 /api/tasks/ 路由）
    path("api/", include("apps.task_mgt.urls")),
    # 选品引擎（独占 /api/selection/ 前缀）
    path("api/", include("apps.selection_engine.urls")),
    # =========================================================================
    # ERP 系统新增模块（财务/采购/仓库/产品/工具/物流/销售）
    # =========================================================================
    path("api/finance/", include("apps.finance.urls")),
    path("api/purchase/", include("apps.purchase.urls")),
    path("api/wms/", include("apps.wms.urls")),
    path("api/product-sys/", include("apps.product_sys.urls")),
    path("api/tools/", include("apps.tools.urls")),
    path("api/logistics/", include("apps.logistics.urls")),
    path("api/sales/", include("apps.sales.urls")),
    # =========================================================================
    # ERP 设置系统（部门/角色权限/仓库对接/平台授权/助手/系统安全）
    # =========================================================================
    path("api/settings/", include("apps.settings_sys.urls")),
]
