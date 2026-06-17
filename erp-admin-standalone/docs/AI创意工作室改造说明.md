# AI创意工作室改造说明

## 一、完成情况

本次在当前仓库内完成的是 **前端项目的 AI 创意工作室配套改造**，重点围绕接口接入、交互约束、降级处理和积分展示展开。

### 1. AI 接口层统一

- 调整了 [`src/utils/request.js`](F:\Github\Tuoyue\src\utils\request.js)，将默认请求超时统一为 `60s`，并对 `/api/ai/` 请求自动提升为 `120s`。
- 调整了 [`src/api/ai.js`](F:\Github\Tuoyue\src\api\ai.js)，补齐标题生成、描述生成、翻译、卖点提炼等接口的参数结构，使其更贴近任务书要求。
- 调整了 [`src/api/aiImage.js`](F:\Github\Tuoyue\src\api\aiImage.js)，统一文生图、图生图、微调、视频生成的前端请求入口。
- 新增了 [`src/utils/aiStudio.js`](F:\Github\Tuoyue\src\utils\aiStudio.js)，集中管理 AI 超时、积分换算、图片大小限制、视频开关等规则。

### 2. AI 创意工作室页面改造

- 调整了 [`src/views/skillhub/AIToolsCenter.vue`](F:\Github\Tuoyue\src\views\skillhub\AIToolsCenter.vue)：
  - 增加图片输入规范提示；
  - 工具卡片显示预计积分消耗；
  - 视频工具支持“待开通”禁用态和提示；
  - 接通图片类工具的预览弹窗联动。
- 调整了 `skillhub/panels` 下多个子面板：
  - [`ProductImageGen.vue`](F:\Github\Tuoyue\src\views\skillhub\panels\ProductImageGen.vue)
  - [`SceneReplace.vue`](F:\Github\Tuoyue\src\views\skillhub\panels\SceneReplace.vue)
  - [`ModelDress.vue`](F:\Github\Tuoyue\src\views\skillhub\panels\ModelDress.vue)
  - [`EffectRender.vue`](F:\Github\Tuoyue\src\views\skillhub\panels\EffectRender.vue)
  - [`SmartEdit.vue`](F:\Github\Tuoyue\src\views\skillhub\panels\SmartEdit.vue)
  - [`VideoGen.vue`](F:\Github\Tuoyue\src\views\skillhub\panels\VideoGen.vue)
  - [`TitleGen.vue`](F:\Github\Tuoyue\src\views\skillhub\panels\TitleGen.vue)
  - [`DescriptionGen.vue`](F:\Github\Tuoyue\src\views\skillhub\panels\DescriptionGen.vue)
  - [`FeaturesGen.vue`](F:\Github\Tuoyue\src\views\skillhub\panels\FeaturesGen.vue)
  - [`TranslateTool.vue`](F:\Github\Tuoyue\src\views\skillhub\panels\TranslateTool.vue)

实现内容包括：

- 所有图片上传入口增加图片类型与大小校验；
- 单张图片按文档要求提示“不要超过 20MB，建议压缩至 5MB 以内”；
- 视频功能改为走后端 `/api/ai/video/generate/`，并在后端能力未开通时前端禁用；
- 文案类工具补齐目标语言、风格、平台等必要参数；
- 修复了部分已有实现问题，例如模特换装面板中的背景变量引用错误。

### 3. 全局积分展示

- 调整了 [`src/App.vue`](F:\Github\Tuoyue\src\App.vue)：
  - 在顶栏新增“我的剩余积分”入口；
  - 支持优先读取 `points`，若无则按 `balance * 10000` 换算积分；
  - 在弹层中展示文案工具、图片工具、渲染工具的预计可用次数；
  - 增加充值/明细占位入口。

### 4. 配置与验证

- 调整了 [`vite.config.js`](F:\Github\Tuoyue\vite.config.js)，移除前端直连 `/ai-api` 的代理配置，统一改为后端代理思路。
- 调整了 [`.env.example`](F:\Github\Tuoyue\.env.example)，去掉前端暴露 AI Key 的引导配置，改为只保留视频功能开关。
- 执行了 `npm ci` 安装依赖。
- 执行了 `npm run build`，构建通过。

## 二、遇到的问题（是否解决）

### 1. 当前仓库不是任务书中提到的 Django 后端仓库

- 问题：任务书里提到的后端路径（如 `backend/apps/core/views.py`）在当前仓库中不存在，当前仓库实际是 Vue 前端项目。
- 是否解决：**部分解决**。
- 处理结果：本次完成了前端侧全部可落地的改造；真正的 Django 后端代理、AI 转发、兜底返回、视频接口实现，仍需在后端仓库中完成。

### 2. 前端存在直接走 `/ai-api` 的视频调用方式

- 问题：`VideoGen.vue` 原本直接 `fetch('/ai-api/video/generate')`，不符合“统一走后端代理”的要求。
- 是否解决：**已解决**。
- 处理结果：已改为封装到 `src/api/aiImage.js` 中，通过 `/api/ai/video/generate/` 访问，并增加前端禁用态与待开通提示。

### 3. 文档要求前端不要暴露 AI Key

- 问题：环境模板中原先仍保留 `VITE_AI_API_KEY`、`VITE_TUOYUE_API_KEY` 等前端可见字段，和任务书要求冲突。
- 是否解决：**已解决**。
- 处理结果：已从示例配置中去掉这类前端 AI Key 引导，改为强调统一通过后端代理接入。

### 4. 图片输入规范与大小限制未统一

- 问题：多个图片面板上传逻辑分散，大小限制和提示不一致。
- 是否解决：**已解决**。
- 处理结果：已抽出统一校验逻辑，并在多个上传入口复用，同时补上 20MB 上限和 5MB 建议提示。

### 5. 构建前本地缺少依赖

- 问题：首次执行 `npm run build` 时，环境中没有可用的 `vite`，导致无法直接验证。
- 是否解决：**已解决**。
- 处理结果：执行 `npm ci` 安装依赖后重新构建，构建通过。

### 6. 视频能力是否真正可用依赖后端接口

- 问题：即使前端已接好入口，视频生成是否能真正返回结果，仍取决于后端是否实现 `/api/ai/video/generate/`，以及拓岳侧是否提供对应能力。
- 是否解决：**未在当前仓库内彻底解决**。
- 处理结果：前端已做好能力开关、禁用态和友好提示；待后端完成后可直接联调启用。
