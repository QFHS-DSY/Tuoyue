/**
 * 图片/文件上传 API
 *
 * 接口约定（供嘉瑞开发）：
 *   POST /api/v1/upload/image/
 *   Content-Type: multipart/form-data
 *   Body: { file: Binary }
 *   返回: { url: "https://cdn.xxx.com/xxx.jpg" }
 */

import request from '@/utils/request'

// ==================== 配置 ====================
const MAX_FILE_SIZE_MB = 5
const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif']

// ==================== 工具函数 ====================

/**
 * 图片压缩（使用 Canvas）
 * @param {File} file - 原始文件
 * @param {number} maxWidth - 最大宽度，默认 1920
 * @param {number} quality - 压缩质量 0~1，默认 0.85
 * @returns {Promise<Blob>} 压缩后的 Blob
 */
export function compressImage(file, maxWidth = 1920, quality = 0.85) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const url = URL.createObjectURL(file)

    img.onload = () => {
      URL.revokeObjectURL(url)

      let { width, height } = img
      if (width > maxWidth) {
        height = Math.round((height * maxWidth) / width)
        width = maxWidth
      }

      const canvas = document.createElement('canvas')
      canvas.width = width
      canvas.height = height

      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0, width, height)

      canvas.toBlob(
        (blob) => {
          if (blob) {
            resolve(blob)
          } else {
            reject(new Error('图片压缩失败'))
          }
        },
        file.type || 'image/jpeg',
        quality
      )
    }

    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error('图片加载失败'))
    }

    img.src = url
  })
}

/**
 * 将 File/Blob 转为 base64
 */
export function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

// ==================== 上传函数 ====================

/**
 * 上传单张图片（对接后端真实接口）
 *
 * @param {File} file - 图片文件
 * @param {Function} onProgress - 上传进度回调 (0-100)
 * @returns {Promise<string>} 返回图片 URL
 */
export async function uploadImage(file, onProgress) {
  // ── 前置校验 ─────────────────────────────────
  if (!ALLOWED_TYPES.includes(file.type)) {
    throw new Error(`不支持的图片格式，请上传 ${ALLOWED_TYPES.map(t => t.split('/')[1].toUpperCase()).join('、')} 格式`)
  }

  const maxBytes = MAX_FILE_SIZE_MB * 1024 * 1024
  if (file.size > maxBytes) {
    if (file.size > 50 * 1024 * 1024) {
      throw new Error('图片体积过大（超过50MB），请先手动压缩')
    }
    file = await compressImage(file)
  }

  // ── 调用上传接口 ─────────────────────────────────
  const formData = new FormData()
  formData.append('file', file)

  const res = await request.post('/api/v1/upload/image/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total) {
        onProgress?.(Math.round((e.loaded / e.total) * 100))
      }
    },
  })

  // 兼容多种返回结构
  return res.url || res.data?.url || res.path || res.fileUrl
}

/**
 * 批量上传图片
 *
 * @param {File[]} files - 图片文件数组
 * @param {Function} onProgress - 全局进度回调 (loaded, total)
 * @returns {Promise<string[]>} 返回图片 URL 数组
 */
export async function uploadImages(files, onProgress) {
  const results = []
  for (let i = 0; i < files.length; i++) {
    results.push(
      await uploadImage(files[i], (p) => onProgress?.(i, p))
    )
  }
  return results
}
