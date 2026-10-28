import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
    plugins: [vue()],
    server: {
      proxy: {
        "/api": {
          target: env.API_PROXY_TARGET || "http://127.0.0.1:8000",
          changeOrigin: true,
        },
      },
    },
    test: {
      environment: "jsdom",
      include: ["tests/**/*.test.js"],
      restoreMocks: true,
      coverage: {
        provider: "v8",
        include: [
          "src/api/adapters.js",
          "src/api/client.js",
          "src/auth.js",
          "src/domain/**/*.js",
        ],
        reporter: ["text", "lcov"],
        thresholds: { lines: 60, statements: 60, functions: 60, branches: 40 },
      },
      // 路由测试会懒加载真实页面组件，Windows 上首次加载 element-plus 可能超过 5 秒默认上限
      testTimeout: 20000,
      hookTimeout: 20000,
    },
  };
});
