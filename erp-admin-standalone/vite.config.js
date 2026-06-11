import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 加载 .env 文件（Vite config 中必须用 loadEnv，不能用 import.meta.env）
  const env = loadEnv(mode, process.cwd(), '')

  // vite-plugin-vue-devtools 内部 birpc 通信在某些场景下会抛出
  // "[birpc] function not found" 警告，干扰开发体验
  // 默认关闭，需要调试时在 .env 设置 VITE_ENABLE_VUE_DEVTOOLS=true 后重启
  const enableDevTools = env.VITE_ENABLE_VUE_DEVTOOLS === 'true'

  return {
    plugins: [
      vue(),
      ...(enableDevTools ? [vueDevTools()] : []),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    server: {
      host: '0.0.0.0',
      port: 1101,
      strictPort: true,
      // 允许 localtunnel 等内网穿透工具访问
      allowedHosts: ['.loca.lt', '.ngrok-free.app', '.ngrok.io', 'www.tuoyue-tch.com', '.tuoyue-tch.com'],
      // 开发环境代理：所有 /api 请求转发到后端
      // target 优先从 .env 的 VITE_API_BASE_URL 读取
      // ⚠️ 必须使用 127.0.0.1（而非 localhost），否则 Node 17+ 会解析为 IPv6 ::1 导致转发失败
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://127.0.0.1:1102',
          changeOrigin: true,
          // Django URL 本身含 api 前缀，不 rewrite
        },
        // 拓岳AI代理：解决跨域问题
        '/ai-api': {
          target: 'https://api.tuoyue-tech.shop',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/ai-api/, '/v1'),
          secure: true,
        },
      },
    },
  }
})
