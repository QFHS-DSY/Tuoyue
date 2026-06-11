/**
 * 合规预检 composable（跨境电商版）
 * 覆盖：关键词/禁售/侵权/平台政策/图片合规
 */
import { ref, computed } from 'vue'

export function useCompliance() {
  const enabled = ref(true)

  // ==================== 合规规则配置 ====================

  /** 绝对禁售词（任何平台都不能出现） */
  const FORBIDDEN_WORDS = [
    ' counterfeit', 'fake', 'replica', 'knockoff', '克隆', '高仿',
    '水货', '走私', '违禁', '赌博', '博彩', '成人', '情色', 'sexy',
    '军火', '武器', '毒品', 'drug', '枪支', '管制刀具',
    '一比一', '原单', '跟单', '外贸原单', 'A货',
    '政治', '敏感', '台独', '藏独', '疆独',
    'R18', 'nsfw', 'xxx',
  ]

  /** 各平台禁售品类 */
  const PLATFORM_RESTRICTED = {
    tiktok: ['药品', '医疗器械', '活体动物', '电子烟', '减肥药', '增高'],
    shopee: ['二手商品', '药品', '医疗器械', '电子烟', '成人用品'],
    temu: ['食品', '化妆品', '药品', '医疗器械', '儿童玩具（含小零件）'],
    shein: ['电子产品', '食品', '药品'],
    aliexpress: ['液体', '粉末', '食品', '药品'],
    amazon: ['音像制品', '图书', '食品', '药品', '医疗器械'],
    ebay: ['药品', '医疗器械', '活体动物', '烟草'],
    lazada: ['食品', '药品', '医疗器械', '电子烟'],
    mercado: ['武器', '药品', '医疗器械'],
  }

  /** 侵权高风险词（商标/品牌） */
  const BRAND_RISK_WORDS = [
    'Nike', 'Nike', 'Adidas', 'Apple', 'Samsung', 'Gucci', 'Louis Vuitton',
    'LV', 'Prada', 'Hermès', 'Chanel', 'Cartier', 'Rolex', 'Omega',
    'Apple', 'Dell', 'HP', 'Lenovo', 'Sony', 'Nintendo', 'Disney',
    '漫威', '迪士尼', 'HelloKitty', '芭比', '变形金刚', '星球大战',
    '华为', '小米', 'OPPO', 'VIVO', '一加',
    'Supor', '苏泊尔', 'Midea', '美的', 'Joyoung', '九阳',
  ]

  /** 图片合规规则 */
  const IMAGE_FORBIDDEN = [
    '含有他人面部（未授权名人/网红）',
    '含有敏感政治/宗教符号',
    '含有未经授权的Logo（耐克/苹果/迪士尼等）',
    '图片质量过低（模糊/严重水印/马赛克）',
    '含有误导性促销信息（虚假折扣/库存）',
  ]

  /** 文字长度合规 */
  const LENGTH_RULES = {
    title: { min: 10, max: 200, target: '60-140字符' },
    description: { min: 50, max: 5000, target: '100-500字符' },
    keywords: { max: 250 },
  }

  // ==================== 预检主函数 ====================

  /**
   * 对商品信息进行跨境合规预检
   * @param {Object} goods - 商品数据 { title, name, description, images, platform, price, category }
   * @param {Array<string>} targetPlatforms - 目标平台列表 ['tiktok', 'shopee']
   * @returns {{ passed: boolean, hasError: boolean, errorCount: number, warningCount: number,
   *            errors: Array<{msg, type, severity}>, warnings: Array<{msg, type, severity}> }}
   */
  function preCheck(goods, targetPlatforms = []) {
    if (!enabled.value) {
      return { passed: true, hasError: false, errorCount: 0, warningCount: 0, errors: [], warnings: [] }
    }

    const errors = []
    const warnings = []
    const text = [
      goods.title || '',
      goods.name || '',
      goods.description || '',
      goods.features || '',
    ].join(' ').toLowerCase()

    // ── 1. 禁售词检查（ERROR）────────────────────────────
    for (const word of FORBIDDEN_WORDS) {
      if (text.includes(word.toLowerCase())) {
        errors.push({
          msg: `商品信息包含禁售词「${word}」，所有平台一律禁售`,
          type: 'forbidden_word',
          severity: 'error',
        })
      }
    }

    // ── 2. 品牌侵权检查（ERROR）─────────────────────────
    for (const brand of BRAND_RISK_WORDS) {
      const regex = new RegExp(`\\b${brand}\\b`, 'i')
      if (regex.test(text)) {
        errors.push({
          msg: `标题/描述含有品牌词「${brand}」，存在商标侵权风险`,
          type: 'brand_risk',
          severity: 'error',
        })
      }
    }

    // ── 3. 平台特定禁售检查（ERROR）──────────────────────
    const platforms = Array.isArray(targetPlatforms) ? targetPlatforms : []
    for (const platform of platforms) {
      const restricted = PLATFORM_RESTRICTED[platform] || []
      for (const keyword of restricted) {
        if (text.includes(keyword)) {
          errors.push({
            msg: `「${keyword}」在 ${getPlatformName(platform)} 属于禁售品类`,
            type: 'platform_restricted',
            severity: 'error',
          })
        }
      }
    }

    // ── 4. 图片合规检查（WARNING）───────────────────────
    if (!goods.images || goods.images.length === 0) {
      warnings.push({ msg: '商品无图片，建议至少上传3张主图', type: 'missing_images', severity: 'warning' })
    } else if (goods.images.length < 3) {
      warnings.push({ msg: `图片数量偏少（${goods.images.length}张），建议至少3张以提升转化率`, type: 'insufficient_images', severity: 'warning' })
    }

    // ── 5. 标题长度检查（WARNING）───────────────────────
    const title = (goods.title || goods.name || '').trim()
    if (title.length === 0) {
      errors.push({ msg: '商品标题不能为空', type: 'empty_title', severity: 'error' })
    } else if (title.length < LENGTH_RULES.title.min) {
      warnings.push({ msg: `标题过短（${title.length}字符），建议 ${LENGTH_RULES.title.target}`, type: 'title_too_short', severity: 'warning' })
    } else if (title.length > LENGTH_RULES.title.max) {
      warnings.push({ msg: `标题过长（${title.length}字符），可能被平台截断，建议控制在${LENGTH_RULES.title.target}`, type: 'title_too_long', severity: 'warning' })
    }

    // ── 6. 描述长度检查（WARNING）───────────────────────
    const desc = (goods.description || '').trim()
    if (desc.length > 0 && desc.length < LENGTH_RULES.description.min) {
      warnings.push({ msg: `商品描述过短（${desc.length}字符），建议 ${LENGTH_RULES.description.target}`, type: 'desc_too_short', severity: 'warning' })
    }

    // ── 7. 价格合规检查（WARNING）───────────────────────
    const price = parseFloat(goods.price || goods.cost || 0)
    if (price <= 0) {
      errors.push({ msg: '商品价格未设置或为0，无法正常上架', type: 'invalid_price', severity: 'error' })
    } else if (price < 0.5) {
      warnings.push({ msg: '商品价格过低（<$0.5），可能触发平台低价倾销审查', type: 'price_too_low', severity: 'warning' })
    }

    // ── 8. 违禁图片内容检查（WARNING）───────────────────
    if (goods.images?.some(img => img.includes('watermark') || img.includes('logo_overlay'))) {
      warnings.push({ msg: '检测到图片含有明显水印/logo遮挡，影响转化率', type: 'image_quality', severity: 'warning' })
    }

    return {
      passed: errors.length === 0,
      hasError: errors.length > 0,
      errorCount: errors.length,
      warningCount: warnings.length,
      errors,
      warnings,
    }
  }

  function setEnabled(val) {
    enabled.value = val
  }

  return { preCheck, setEnabled, enabled }
}

/** 获取平台中文名 */
function getPlatformName(id) {
  const map = {
    tiktok: 'TikTok Shop', shopee: 'Shopee', temu: 'Temu', shein: 'SHEIN',
    aliexpress: 'AliExpress', amazon: 'Amazon', ebay: 'eBay', lazada: 'Lazada',
    wish: 'Wish', mercado: 'MercadoLibre', ozon: 'Ozon', allegro: 'Allegro',
  }
  return map[id] || id
}
