from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.product_sys.models import *
from apps.product_sys.serializers import *

def _v(model, serializer, filters=None, search=None, ordering=None):
    attrs = {'queryset': model.objects.all(), 'serializer_class': serializer,
             'filter_backends': [DjangoFilterBackend, SearchFilter, OrderingFilter]}
    if filters: attrs['filterset_fields'] = filters
    if search: attrs['search_fields'] = search
    if ordering: attrs['ordering_fields'] = ordering
    return type(f'{model.__name__}ViewSet', (ModelViewSet,), attrs)

ProductViewSet = _v(Product, ProductSerializer, ['status', 'brand_id', 'category_id'], ['name', 'product_no'], ['id', 'created_at'])
ProductSkuViewSet = _v(ProductSku, ProductSkuSerializer, ['product_id'], ['sku'], ['id'])
ProductSpecViewSet = _v(ProductSpec, ProductSpecSerializer, ['product_id'], ['spec_name', 'spec_value'], ['id'])
SpuInfoViewSet = _v(SpuInfo, SpuInfoSerializer, ['status', 'brand_id', 'category_id'], ['spu_code', 'spu_name'], ['id', 'created_at'])
SpuSkuRelationViewSet = _v(SpuSkuRelation, SpuSkuRelationSerializer, ['spu_id'], ['sku'], ['id'])
SpuAttributeViewSet = _v(SpuAttribute, SpuAttributeSerializer, ['spu_id'], ['attribute_name'], ['id'])
DevelopmentTaskViewSet = _v(DevelopmentTask, DevelopmentTaskSerializer, ['status', 'country', 'category_id'], ['task_no', 'demand_name', 'processor_name'], ['id', 'created_at'])
BundleProductViewSet = _v(BundleProduct, BundleProductSerializer, ['status'], ['bundle_sku', 'name'], ['id'])
BundleProductItemViewSet = _v(BundleProductItem, BundleProductItemSerializer, ['bundle_id'], ['child_sku'], ['id'])
AccessoryViewSet = _v(Accessory, AccessorySerializer, ['status'], ['name', 'code'], ['id'])
UpcCodeViewSet = _v(UpcCode, UpcCodeSerializer, ['status', 'code_type'], ['code'], ['id', 'created_at'])
TransparencyAccountViewSet = _v(TransparencyAccount, TransparencyAccountSerializer, ['status'], ['account_name'], ['id'])
TransparencyProductViewSet = _v(TransparencyProduct, TransparencyProductSerializer, ['account_id', 'label_status'], ['asin', 'msku', 'title'], ['id'])
TransparencyTcodeViewSet = _v(TransparencyTcode, TransparencyTcodeSerializer, ['product_id', 'status'], ['tcode', 'batch_no'], ['id'])
BrandViewSet = _v(Brand, BrandSerializer, ['status'], ['name', 'code'], ['id'])
CategoryViewSet = _v(Category, CategorySerializer, ['status', 'parent_id', 'level'], ['name', 'code'], ['id', 'sort_order'])
ProductImageViewSet = _v(ProductImage, ProductImageSerializer, ['product_id', 'is_main'], [], ['id', 'sort_order'])
AttributeViewSet = _v(Attribute, AttributeSerializer, ['category_id', 'required'], ['name', 'code'], ['id', 'sort_order'])
AttributeValueViewSet = _v(AttributeValue, AttributeValueSerializer, ['product_id', 'attribute_id'], ['value'], ['id'])
QualityTemplateViewSet = _v(QualityTemplate, QualityTemplateSerializer, ['status', 'category_id'], ['name'], ['id'])
ProductQualityInfoViewSet = _v(ProductQualityInfo, ProductQualityInfoSerializer, ['template_id'], ['sku'], ['id'])
PlatformMatchViewSet = _v(PlatformMatch, PlatformMatchSerializer, ['platform', 'status', 'product_id'], ['platform_sku', 'platform_id'], ['id'])
MatchRuleViewSet = _v(MatchRule, MatchRuleSerializer, ['platform', 'status', 'match_type'], ['name'], ['id', 'priority'])
AlibabaMatchViewSet = _v(AlibabaMatch, AlibabaMatchSerializer, ['product_id'], ['alibaba_id', 'alibaba_sku', 'supplier_name'], ['id'])

__all__ = [k for k in dir() if k.endswith('ViewSet')]
