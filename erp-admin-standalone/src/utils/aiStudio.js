export const AI_DEFAULT_TIMEOUT_MS = 60_000
export const AI_LONG_TIMEOUT_MS = 120_000

export const AI_POINTS_EXCHANGE_RATE = 10_000
export const AI_IMAGE_MAX_SIZE_MB = 20
export const AI_IMAGE_RECOMMENDED_SIZE_MB = 5

export const AI_IMAGE_INPUT_HINT =
  `单张图片请勿超过 ${AI_IMAGE_MAX_SIZE_MB}MB，建议压缩至 ${AI_IMAGE_RECOMMENDED_SIZE_MB}MB 以内以提高响应速度。`

export const AI_VIDEO_ENABLED = import.meta.env.VITE_AI_VIDEO_ENABLED === 'true'
export const AI_VIDEO_UNAVAILABLE_MESSAGE =
  'AI 视频生成正在等待后端代理能力开通，当前请先使用文案与图片工具。'

export const AI_TOOL_META = {
  'title-gen': {
    points: 1,
    costLabel: '预计消耗 1 积分 / 次',
    category: 'copy',
  },
  'desc-gen': {
    points: 1,
    costLabel: '预计消耗 1 积分 / 次',
    category: 'copy',
  },
  'features-gen': {
    points: 1,
    costLabel: '预计消耗 1 积分 / 次',
    category: 'copy',
  },
  translate: {
    points: 1,
    costLabel: '预计消耗 1 积分 / 次',
    category: 'copy',
  },
  'product-image': {
    points: 10,
    costLabel: '预计消耗 10 积分 / 张',
    category: 'image',
  },
  'scene-replace': {
    points: 10,
    costLabel: '预计消耗 10 积分 / 张',
    category: 'image',
  },
  'smart-edit': {
    points: 10,
    costLabel: '预计消耗 10 积分 / 张',
    category: 'image',
  },
  'model-dress': {
    points: 20,
    costLabel: '预计消耗 20 积分 / 张',
    category: 'image',
  },
  'effect-render': {
    points: 20,
    costLabel: '预计消耗 20 积分 / 张',
    category: 'image',
  },
  'video-gen': {
    points: 100,
    costLabel: '预计消耗 100 积分 / 条',
    category: 'video',
  },
}

export function getAiToolMeta(toolId) {
  return AI_TOOL_META[toolId] || {
    points: 1,
    costLabel: '预计消耗 1 积分 / 次',
    category: 'copy',
  }
}

export function validateAiImageFile(file) {
  if (!file) {
    return { valid: false, severity: 'error', message: '未读取到图片文件，请重新选择' }
  }

  if (file.type && !file.type.startsWith('image/')) {
    return { valid: false, severity: 'error', message: '仅支持上传图片文件，请重新选择' }
  }

  const sizeInMb = file.size / 1024 / 1024
  if (sizeInMb > AI_IMAGE_MAX_SIZE_MB) {
    return {
      valid: false,
      severity: 'error',
      message: `单张图片请勿超过 ${AI_IMAGE_MAX_SIZE_MB}MB，当前约 ${sizeInMb.toFixed(1)}MB。`,
    }
  }

  if (sizeInMb > AI_IMAGE_RECOMMENDED_SIZE_MB) {
    return {
      valid: true,
      severity: 'warning',
      message: `当前图片约 ${sizeInMb.toFixed(1)}MB，建议压缩至 ${AI_IMAGE_RECOMMENDED_SIZE_MB}MB 以内以提升响应速度。`,
    }
  }

  return { valid: true, severity: 'success', message: '' }
}

function toFiniteNumber(value) {
  const number = Number(value)
  return Number.isFinite(number) ? number : null
}

function pickFirstNumber(source, keys) {
  for (const key of keys) {
    const value = toFiniteNumber(source?.[key])
    if (value !== null) return value
  }
  return null
}

export function resolveUserCredits(user) {
  const points = pickFirstNumber(user, ['points', 'credit_points', 'wallet_points'])
  const balance = pickFirstNumber(user, ['balance', 'wallet_balance', 'account_balance', 'credit_balance'])

  if (points !== null) {
    return { points: Math.max(0, Math.round(points)), balance }
  }

  if (balance !== null) {
    return {
      points: Math.max(0, Math.round(balance * AI_POINTS_EXCHANGE_RATE)),
      balance,
    }
  }

  return { points: null, balance: null }
}

export function formatPoints(points) {
  if (!Number.isFinite(points)) return '--'
  return new Intl.NumberFormat('zh-CN', { maximumFractionDigits: 0 }).format(points)
}

export function formatBalance(balance) {
  if (!Number.isFinite(balance)) return '--'
  return new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(balance)
}

export function estimateRemainingUses(points, toolId) {
  if (!Number.isFinite(points)) return null
  const meta = getAiToolMeta(toolId)
  return meta.points > 0 ? Math.floor(points / meta.points) : null
}
