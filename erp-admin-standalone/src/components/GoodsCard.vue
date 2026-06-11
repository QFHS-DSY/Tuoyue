<template>
  <div
    :class="['goods-card', { selected: isSelected, 'drag-over': isDragOver }]"
    draggable="true"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
    @click="handleClick"
  >
    <!-- 选择checkbox（可选） -->
    <div v-if="selectable" class="card-checkbox">
      <el-checkbox
        :model-value="isSelected"
        @click.stop
        @change="$emit('select', goods)"
      />
    </div>

    <!-- 商品图片 -->
    <div class="card-image">
      <el-image
        v-if="goods.main_image"
        :src="goods.main_image"
        fit="cover"
        class="goods-img"
        :preview-src-list="[goods.main_image]"
        :initial-index="0"
      >
        <template #error>
          <div class="img-placeholder">
            <el-icon><Picture /></el-icon>
          </div>
        </template>
      </el-image>
      <div v-else class="img-placeholder">
        <el-icon><Picture /></el-icon>
      </div>

      <!-- 平台标签 -->
      <div v-if="goods.platforms && goods.platforms.length > 0" class="platform-tags">
        <el-tag
          v-for="p in goods.platforms.slice(0, 2)"
          :key="p"
          size="small"
          type="info"
        >
          {{ getPlatformName(p) }}
        </el-tag>
        <el-tag v-if="goods.platforms.length > 2" size="small" type="info">
          +{{ goods.platforms.length - 2 }}
        </el-tag>
      </div>

      <!-- 库存警告 -->
      <div v-if="goods.stock <= 0" class="stock-badge danger">缺货</div>
      <div v-else-if="goods.stock <= goods.low_stock_threshold" class="stock-badge warning">库存紧张</div>
    </div>

    <!-- 拖拽提示遮罩：移到外层，覆盖完整图片区域 -->
    <div class="drag-hint">
      <el-icon><Rank /></el-icon>
      <span>按住拖拽上货</span>
    </div>
    <div v-if="isDragging" class="drag-tip">
      <el-icon class="is-loading"><Rank /></el-icon>
      <span>放开即上货至目标平台</span>
    </div>

    <!-- 商品信息 -->
    <div class="card-info">
      <div class="goods-title" :title="goods.title">
        {{ goods.title || goods.goods_title || '未命名商品' }}
      </div>

      <!-- SKU规格（可折叠） -->
      <div v-if="goods.sku_list && goods.sku_list.length > 0" class="sku-list">
        <div
          v-for="sku in goods.sku_list.slice(0, expanded ? undefined : 2)"
          :key="sku.sku_id"
          class="sku-item"
        >
          <span class="sku-spec">{{ sku.spec || sku.sku_name || '默认规格' }}</span>
          <span class="sku-stock" :class="getStockClass(sku.stock)">
            {{ sku.stock || 0 }}件
          </span>
        </div>
        <div v-if="goods.sku_list.length > 2 && !expanded" class="sku-more" @click.stop="expanded = true">
          展开 {{ goods.sku_list.length - 2 }} 个规格
        </div>
      </div>

      <!-- 价格信息 -->
      <div class="price-row">
        <span class="price-cost">
          ¥{{ (goods.cost_price || goods.price || 0).toFixed(2) }}
        </span>
        <span v-if="goods.price && goods.cost_price" class="price-profit" :class="getProfitClass()">
          利润 ¥{{ (goods.price - goods.cost_price).toFixed(2) }}
        </span>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="card-actions" @click.stop>
      <slot name="actions">
        <el-button size="small" type="primary" @click="$emit('edit', goods)">
          编辑
        </el-button>
        <el-button size="small" @click="$emit('listing', goods)">
          上货
        </el-button>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Picture, Upload } from '@element-plus/icons-vue'
import { getPlatformName } from '@/utils/platformIcons'

// ── Props & Emits ──────────────────────────────────────────
const props = defineProps({
  goods: {
    type: Object,
    required: true,
  },
  selectable: {
    type: Boolean,
    default: false,
  },
  selected: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['click', 'edit', 'listing', 'select', 'drag-start'])

// ── State ──────────────────────────────────────────────────
const isDragging = ref(false)
const isDragOver = ref(false)
const expanded = ref(false)

// ── 拖拽相关 ───────────────────────────────────────────────
function handleDragStart(e) {
  isDragging.value = true
  e.dataTransfer.effectAllowed = 'copy'

  // 携带完整结构化商品数据
  const payload = JSON.stringify({
    type: 'goods',
    version: '1.0',
    data: {
      id: props.goods.id,
      title: props.goods.title || props.goods.goods_title,
      sku_list: props.goods.sku_list || [],
      images: props.goods.images || [props.goods.main_image].filter(Boolean),
      price: props.goods.price,
      cost_price: props.goods.cost_price,
      category: props.goods.category,
      material: props.goods.material,
      weight: props.goods.weight,
      stock: props.goods.stock,
      source_url: props.goods.source_url,
      platforms: props.goods.platforms || [],
    }
  })

  e.dataTransfer.setData('application/json', payload)
  e.dataTransfer.setData('text/plain', props.goods.title || '')

  emit('drag-start', props.goods)
}

function handleDragEnd() {
  isDragging.value = false
}

function handleClick() {
  emit('click', props.goods)
}

// ── 工具函数 ───────────────────────────────────────────────

function getStockClass(stock) {
  if (stock <= 0) return 'stock-zero'
  if (stock <= 10) return 'stock-low'
  return 'stock-normal'
}

function getProfitClass() {
  if (!props.goods.price || !props.goods.cost_price) return ''
  const profit = props.goods.price - props.goods.cost_price
  if (profit <= 0) return 'profit-loss'
  if (profit < 10) return 'profit-low'
  return 'profit-good'
}
</script>

<style scoped>
.goods-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-extra-light);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  display: flex;
  flex-direction: column;
}

.goods-card:hover {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.goods-card.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.goods-card.drag-over {
  border-color: var(--el-color-primary);
  opacity: 0.7;
  transform: scale(1.02);
}

.goods-card[draggable="true"]:active {
  cursor: grabbing;
}

/* checkbox */
.card-checkbox {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  padding: 2px;
}

/* 图片 */
.card-image {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  background: var(--el-fill-color-light);
  overflow: hidden;
}

.goods-img {
  width: 100%;
  height: 100%;
}

.img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-placeholder);
  font-size: 32px;
}

/* 拖拽提示：移到外层，覆盖完整图片区域 */
.drag-hint {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  /* 使用 padding-bottom 撑起与 .card-image 相同的正方形高度 */
  height: 0;
  padding-bottom: 100%;
  background: linear-gradient(
    135deg,
    rgba(8, 91, 156, 0.8) 0%,
    rgba(46, 173, 62, 0.8) 100%
  );
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 700;
  opacity: 0;
  transition: opacity 0.2s ease;
  pointer-events: none;
  letter-spacing: 0.5px;
  z-index: 2;
}

.goods-card:hover .drag-hint {
  opacity: 1;
}

/* 拖拽中提示 */
.drag-tip {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 0;
  padding-bottom: 100%;
  background: linear-gradient(
    135deg,
    rgba(8, 91, 156, 0.9) 0%,
    rgba(46, 173, 62, 0.9) 100%
  );
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 700;
  z-index: 3;
}

/* 平台标签 */
.platform-tags {
  position: absolute;
  bottom: 6px;
  left: 6px;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

/* 库存徽章 */
.stock-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.stock-badge.danger {
  background: #f56c6c;
  color: white;
}

.stock-badge.warning {
  background: #e6a23c;
  color: white;
}

/* 商品信息 */
.card-info {
  padding: 10px;
  flex: 1;
}

.goods-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 6px;
  line-height: 1.3;
}

/* SKU列表 */
.sku-list {
  margin-bottom: 8px;
}

.sku-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  padding: 2px 0;
}

.sku-spec {
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 70%;
}

.sku-stock {
  font-weight: 600;
  flex-shrink: 0;
}

.stock-zero { color: #f56c6c; }
.stock-low { color: #e6a23c; }
.stock-normal { color: var(--el-color-success); }

.sku-more {
  font-size: 11px;
  color: var(--el-color-primary);
  cursor: pointer;
  padding: 2px 0;
}

/* 价格 */
.price-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.price-cost {
  font-size: 14px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.price-profit {
  font-size: 11px;
  font-weight: 600;
  padding: 1px 5px;
  border-radius: 3px;
}

.profit-good {
  background: #f0f9eb;
  color: #67c23a;
}

.profit-low {
  background: #fdf6ec;
  color: #e6a23c;
}

.profit-loss {
  background: #fef0f0;
  color: #f56c6c;
}

/* 操作按钮 */
.card-actions {
  padding: 8px 10px;
  border-top: 1px solid var(--el-border-color-extra-light);
  display: flex;
  gap: 6px;
}
</style>
