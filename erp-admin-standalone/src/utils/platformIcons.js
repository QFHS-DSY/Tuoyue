/**
 * 平台 SVG Logo 映射表
 * 图标来源: D:\试验场\ERP\图标\ (已复制到 public/platform-icons/)
 * 使用方式: import { PLATFORM_ICONS } from '@/utils/platformIcons'
 *
 * 每个平台包含:
 * - icon:   相对于 /platform-icons/ 的 SVG 文件路径
 * - color:  品牌主色调（用于标签背景等场景）
 * - name:   显示名称
 */

export const PLATFORM_ICONS = {
  '1688': {
    icon: '/platform-icons/1688.svg',
    color: '#ff6a00',
    name: '1688',
  },
  taobao: {
    icon: '/platform-icons/taobao.svg',
    color: '#ff5000',
    name: '淘宝',
  },
  pdd: {
    icon: '/platform-icons/pdd.svg',
    color: '#e53e30',
    name: '拼多多',
  },
  tmall: {
    icon: '/platform-icons/tmall.svg',
    color: '#c01111',
    name: '天猫',
  },
  shopee: {
    icon: '/platform-icons/shopee.svg',
    color: '#EE4D2D',
    name: 'Shopee',
  },
  temu: {
    icon: '/platform-icons/temu.svg',
    color: '#FF6B00',
    name: 'Temu',
  },
  shein: {
    icon: '/platform-icons/shein.svg',
    color: '#000000',
    name: 'SHEIN',
  },
  tiktok: {
    icon: '/platform-icons/tiktok.svg',
    color: '#000000',
    name: 'TikTok Shop',
  },
  aliexpress: {
    icon: '/platform-icons/aliexpress.svg',
    color: '#FF4747',
    name: '速卖通',
  },
  amazon: {
    icon: '/platform-icons/amazon.svg',
    color: '#FF9900',
    name: 'Amazon',
  },
  ebay: {
    icon: '/platform-icons/ebay.svg',
    color: '#E53238',
    name: 'eBay',
  },
  lazada: {
    icon: '/platform-icons/lazada.svg',
    color: '#0B94D5',
    name: 'Lazada',
  },
  wish: {
    icon: '/platform-icons/wish.svg',
    color: '#2A80C4',
    name: 'Wish',
  },
  mercado: {
    icon: '/platform-icons/mercado.svg',
    color: '#FFE600',
    name: 'Mercado',
  },
  ozon: {
    icon: '/platform-icons/ozon.svg',
    color: '#005BFF',
    name: 'Ozon',
  },
}

/** 核心平台（小白模式展示） */
export const CORE_PLATFORMS = ['shopee', 'temu', 'shein', 'tiktok']

/** 全部平台列表 */
export const ALL_PLATFORMS = Object.keys(PLATFORM_ICONS)

/**
 * 标准化平台 key（小写 + 去除空格）
 * 兼容 "TikTok", "tiktok", "Shopee", "shopee" 等各种格式
 */
function normalizeKey(key) {
  return (key || '').toLowerCase().replace(/\s+/g, '')
}

/**
 * 根据 key 获取平台 Logo 的 <img> src
 * @param {string} key
 * @returns {string} img src URL
 */
export function getPlatformIcon(key) {
  return PLATFORM_ICONS[normalizeKey(key)]?.icon || ''
}

/**
 * 根据 key 获取平台主色调
 * @param {string} key
 * @returns {string} hex color
 */
export function getPlatformColor(key) {
  return PLATFORM_ICONS[normalizeKey(key)]?.color || '#999999'
}

/**
 * 根据 key 获取平台名称
 * @param {string} key
 * @returns {string}
 */
export function getPlatformName(key) {
  return PLATFORM_ICONS[normalizeKey(key)]?.name || key
}
