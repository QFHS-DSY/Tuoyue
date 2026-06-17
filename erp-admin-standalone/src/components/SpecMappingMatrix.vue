<template>
  <!-- 1688 规格映射矩阵 — 多级合并表头 -->
  <div class="spec-mapping-matrix">
    <div class="matrix-header">
      <div class="matrix-title">
        <el-icon><Operation /></el-icon>
        规格映射矩阵
      </div>
      <div class="matrix-actions">
        <el-button size="small" @click="autoMapSpecs" :loading="autoMapping">
          <el-icon><MagicStick /></el-icon>
          智能映射
        </el-button>
        <el-button size="small" type="primary" @click="$emit('confirm', mappings)" :disabled="mappings.length === 0">
          确认映射
        </el-button>
      </div>
    </div>

    <div class="matrix-desc">
      左侧展示 1688 原始规格（颜色、尺码、起批量等），右侧选择目标平台对应的规格值
    </div>

    <!-- 多级合并表头 el-table -->
    <el-table
      :data="mappingRows"
      border
      stripe
      size="small"
      class="spec-matrix-table"
      :header-cell-style="{ background: '#f5f7fa', fontWeight: 600 }"
    >
      <!-- ====== 多级表头第一层：1688 原始规格（合并列） ====== -->
      <el-table-column
        v-for="spec in specs"
        :key="'src_' + spec.name"
        :label="spec.name"
        :width="spec.values.length > 3 ? 180 : 130"
      >
        <template #default="{ row }">
          <div class="spec-cell-value">
            <el-tag size="small" effect="plain" type="info">{{ row[spec.name] }}</el-tag>
          </div>
        </template>
      </el-table-column>

      <!-- ====== 分隔列 ====== -->
      <el-table-column width="60" align="center">
        <template #header>
          <el-icon color="#909399"><ArrowRight /></el-icon>
        </template>
        <template #default>
          <el-icon color="#c0c4cc"><ArrowRight /></el-icon>
        </template>
      </el-table-column>

      <!-- ====== 多级表头第二层：目标平台规格映射（每个 spec 一列，带下拉选择） ====== -->
      <el-table-column
        v-for="(spec, specIdx) in specs"
        :key="'tgt_' + spec.name"
        :label="'目标 ' + spec.name"
        :width="spec.values.length > 3 ? 180 : 150"
      >
        <template #default="{ row, $index }">
          <el-select
            :model-value="getMapping($index, spec.name)"
            @update:model-value="(val) => setMapping($index, spec.name, val)"
            placeholder="选择目标值"
            size="small"
            filterable
            allow-create
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="val in spec.values"
              :key="val"
              :label="val"
              :value="val"
            />
            <el-option
              v-for="val in suggestedValues[spec.name] || []"
              :key="'sug_' + val"
              :label="val + ' (推荐)'"
              :value="val"
            />
          </el-select>
        </template>
      </el-table-column>

      <!-- 价格列 -->
      <el-table-column label="采购价" width="100">
        <template #default="{ row }">
          <span class="price-cell">¥{{ row.price }}</span>
        </template>
      </el-table-column>

      <!-- 库存列 -->
      <el-table-column label="库存" width="80">
        <template #default="{ row }">
          {{ row.stock || '-' }}
        </template>
      </el-table-column>

      <!-- 起批量列 -->
      <el-table-column label="起批量" width="90">
        <template #default="{ row }">
          <el-popover
            v-if="row.price_tiers && row.price_tiers.length > 1"
            placement="bottom"
            :width="200"
            trigger="hover"
          >
            <template #reference>
              <el-tag size="small" type="warning">{{ row.min_order }}件起</el-tag>
            </template>
            <div class="price-tier-popover">
              <div class="ptp-title">阶梯价格</div>
              <div v-for="(tier, ti) in row.price_tiers" :key="ti" class="ptp-item">
                <span>{{ tier.min_qty }}{{ tier.max_qty ? '-' + tier.max_qty : '+' }}件</span>
                <span class="ptp-price">¥{{ tier.price }}</span>
              </div>
            </div>
          </el-popover>
          <span v-else>{{ row.min_order || 1 }}件</span>
        </template>
      </el-table-column>
    </el-table>

    <!-- 底部汇总 -->
    <div v-if="mappingStats.total > 0" class="matrix-summary">
      <span class="summary-item">
        <el-icon><Check /></el-icon>
        已映射 {{ mappingStats.mapped }}/{{ mappingStats.total }}
      </span>
      <span v-if="mappingStats.unmapped > 0" class="summary-item unmapped">
        <el-icon color="#f59e0b"><Warning /></el-icon>
        未映射 {{ mappingStats.unmapped }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { Operation, ArrowRight, MagicStick, Check, Warning } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  /** 1688 原始规格定义 [{ name: '颜色', values: ['黑色','白色'] }, ...] */
  specs: {
    type: Array,
    default: () => [],
  },
  /** 1688 SKU 列表 [{ properties:{颜色:'黑色',尺码:'XL'}, price:12, stock:100, price_tiers:[] }, ...] */
  skus: {
    type: Array,
    default: () => [],
  },
  /** 目标平台（用于智能映射推荐） */
  targetPlatform: {
    type: String,
    default: 'shein',
  },
})

const emit = defineEmits(['confirm'])

// ── 映射数据结构：mappings[idx][specName] = targetValue ──
const mappings = reactive([])

// 映射行数据（el-table 数据源）
const mappingRows = computed(() => {
  return props.skus.map((sku, idx) => ({
    ...(sku.properties || {}),
    price: sku.price,
    stock: sku.stock,
    min_order: sku.price_tiers?.[0]?.min_qty || 1,
    price_tiers: sku.price_tiers || [],
  }))
})

// 智能推荐的目标值
const suggestedValues = computed(() => {
  const result = {}
  props.specs.forEach(spec => {
    result[spec.name] = spec.values.map(v => {
      // 根据目标平台推荐翻译
      if (props.targetPlatform === 'shein' || props.targetPlatform === 'amazon') {
        return translateSpecValue(v)
      }
      return v
    })
  })
  return result
})

// 简单的中→英规格值翻译映射
const translationMap = {
  '黑色': 'Black', '白色': 'White', '红色': 'Red', '蓝色': 'Blue', '绿色': 'Green',
  '黄色': 'Yellow', '粉色': 'Pink', '紫色': 'Purple', '灰色': 'Gray', '棕色': 'Brown',
  '橙色': 'Orange', '金色': 'Gold', '银色': 'Silver', '米色': 'Beige',
  'S': 'S', 'M': 'M', 'L': 'L', 'XL': 'XL', 'XXL': 'XXL', 'XXXL': 'XXXL',
  '均码': 'One Size', '小码': 'S', '中码': 'M', '大码': 'L',
  '加大码': 'XL', '加加大码': 'XXL',
}

function translateSpecValue(chineseVal) {
  return translationMap[chineseVal] || chineseVal
}

// ── 映射读取/设置 ──
function getMapping(rowIdx, specName) {
  return mappings[rowIdx]?.[specName] || ''
}

function setMapping(rowIdx, specName, value) {
  if (!mappings[rowIdx]) {
    mappings[rowIdx] = {}
  }
  mappings[rowIdx][specName] = value
}

// ── 映射统计 ──
const mappingStats = computed(() => {
  let total = 0, mapped = 0
  props.skus.forEach((_, idx) => {
    props.specs.forEach(spec => {
      total++
      if (mappings[idx]?.[spec.name]) mapped++
    })
  })
  return { total, mapped, unmapped: total - mapped }
})

// ── 自动智能映射 ──
const autoMapping = ref(false)

function autoMapSpecs() {
  autoMapping.value = true
  // 模拟 AI 智能映射
  setTimeout(() => {
    props.skus.forEach((sku, idx) => {
      if (!mappings[idx]) mappings[idx] = {}
      props.specs.forEach(spec => {
        const srcVal = sku.properties?.[spec.name] || ''
        if (srcVal) {
          // 根据目标平台决定是否翻译
          if (props.targetPlatform === 'shein' || props.targetPlatform === 'amazon') {
            mappings[idx][spec.name] = translateSpecValue(srcVal)
          } else {
            mappings[idx][spec.name] = srcVal
          }
        }
      })
    })
    autoMapping.value = false
    ElMessage.success(`智能映射完成，共映射 ${props.skus.length * props.specs.length} 项`)
  }, 600)
}

// ── 数据变化时重置映射 ──
watch(() => props.skus, () => {
  mappings.length = 0
}, { deep: true })
</script>

<style scoped>
.spec-mapping-matrix {
  margin-top: 16px;
}

.matrix-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.matrix-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.matrix-actions {
  display: flex;
  gap: 8px;
}

.matrix-desc {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
}

.spec-matrix-table {
  margin-bottom: 12px;
}

.spec-cell-value {
  padding: 2px 0;
}

.price-cell {
  color: #059669;
  font-weight: 600;
}

/* 阶梯价格弹出 */
.price-tier-popover {
  font-size: 12px;
}

.ptp-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #1e293b;
}

.ptp-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
}

.ptp-item:last-child {
  border-bottom: none;
}

.ptp-price {
  color: #e6a23c;
  font-weight: 500;
}

/* 底部汇总 */
.matrix-summary {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 16px;
  background: #f9fafb;
  border-radius: 8px;
  font-size: 13px;
  color: #606266;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.summary-item.unmapped {
  color: #f59e0b;
}

/* 多级表头样式 */
:deep(.spec-matrix-table thead th) {
  text-align: center;
}

:deep(.spec-matrix-table .el-table__header-wrapper) {
  border-bottom: 2px solid #e5e7eb;
}
</style>
