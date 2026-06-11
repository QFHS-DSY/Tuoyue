from rest_framework import serializers
from apps.product_sys.models import *

def _m(cls): return type(f'{cls.__name__}Serializer', (serializers.ModelSerializer,), {
    'Meta': type('Meta', (), {'model': cls, 'fields': '__all__', 'read_only_fields': ['id', 'created_at', 'updated_at']})
})

ProductSerializer = _m(Product)
ProductSkuSerializer = _m(ProductSku)
ProductSpecSerializer = _m(ProductSpec)
SpuInfoSerializer = _m(SpuInfo)
SpuSkuRelationSerializer = _m(SpuSkuRelation)
SpuAttributeSerializer = _m(SpuAttribute)
DevelopmentTaskSerializer = _m(DevelopmentTask)
BundleProductSerializer = _m(BundleProduct)
BundleProductItemSerializer = _m(BundleProductItem)
AccessorySerializer = _m(Accessory)
UpcCodeSerializer = _m(UpcCode)
TransparencyAccountSerializer = _m(TransparencyAccount)
TransparencyProductSerializer = _m(TransparencyProduct)
TransparencyTcodeSerializer = _m(TransparencyTcode)
BrandSerializer = _m(Brand)
CategorySerializer = _m(Category)
ProductImageSerializer = _m(ProductImage)
AttributeSerializer = _m(Attribute)
AttributeValueSerializer = _m(AttributeValue)
QualityTemplateSerializer = _m(QualityTemplate)
ProductQualityInfoSerializer = _m(ProductQualityInfo)
PlatformMatchSerializer = _m(PlatformMatch)
MatchRuleSerializer = _m(MatchRule)
AlibabaMatchSerializer = _m(AlibabaMatch)

__all__ = [k for k in dir() if k.endswith('Serializer')]
