import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  define: {
    'process.env': {},
    'process.env.NEXT_PUBLIC_GATEWAY_URL': JSON.stringify('http://localhost:8888'),
    'process.env.NEXT_PUBLIC_API_GATEWAY_URL': JSON.stringify('http://localhost:8777')
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3001,
    host: true,
    proxy: {
      // AI Platform Services
      '/api/orchestrator': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/orchestrator/, '')
      },
      '/api/workflow': {
        target: 'http://localhost:8003',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/workflow/, '')
      },
      '/api/community': {
        target: 'http://localhost:8004',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/community/, '')
      },
      '/api/predictive': {
        target: 'http://localhost:8005',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/predictive/, '')
      },
      '/api/analytics': {
        target: 'http://localhost:8051',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/analytics/, '/api/v1/analytics')
      },
      // Infrastructure Services
      '/api/eventbus': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/eventbus/, '')
      },
      '/api/gateway': {
        target: 'http://localhost:8777',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/gateway/, '')
      },
      // Observability
      '/prometheus': {
        target: 'http://localhost:9090',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/prometheus/, '')
      },
      '/grafana': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/grafana/, '')
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
