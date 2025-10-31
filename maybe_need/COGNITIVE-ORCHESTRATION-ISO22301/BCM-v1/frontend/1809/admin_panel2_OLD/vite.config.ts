import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3001,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8069',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/web/api')
      },
      '/prometheus': {
        target: 'http://localhost:9090',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/prometheus/, '')
      },
      '/grafana': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/grafana/, '')
      },
      '/ai': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ai/, '')
      },
      '/eventbus': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/eventbus/, '')
      },
      '/modules': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/modules/, '/api/modules')
      },
      '/bia': {
        target: 'http://localhost:8082',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/bia/, '')
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // Vendor chunks
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom')) {
              return 'react-vendor';
            }
            if (id.includes('@radix-ui') || id.includes('class-variance-authority')) {
              return 'ui-vendor';
            }
            if (id.includes('lucide-react')) {
              return 'icons';
            }
            if (id.includes('recharts') || id.includes('d3')) {
              return 'charts';
            }
            if (id.includes('socket.io-client')) {
              return 'realtime';
            }
            if (id.includes('axios') || id.includes('httpx')) {
              return 'http';
            }
            return 'vendor';
          }

          // Application chunks
          if (id.includes('src/components/ui')) {
            return 'ui-components';
          }
          if (id.includes('src/services')) {
            return 'services';
          }
        },
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? chunkInfo.facadeModuleId.split('/').pop() : 'chunk';
          return `js/[name].[hash].js`;
        }
      }
    },
    // Optimize dependencies
    optimizeDeps: {
      include: ['react', 'react-dom', 'socket.io-client'],
      exclude: []
    }
  }
})
