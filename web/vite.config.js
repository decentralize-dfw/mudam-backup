import { defineConfig } from 'vite';

// Built into web/dist, then staged into the repository root by
// scripts/stage.mjs: index.html at the root, bundles under demo/app/.
// Model, data and images are plain files under demo/ and load at runtime.
export default defineConfig({
  base: './',
  publicDir: false,
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    assetsDir: 'demo/app',
    target: 'es2022',
    chunkSizeWarningLimit: 1200,
  },
});
