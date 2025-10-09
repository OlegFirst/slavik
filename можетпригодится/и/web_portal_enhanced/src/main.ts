import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Toast from 'vue-toastification'
import FloatingVue from 'floating-vue'

import App from './App.vue'
import router from './router'

// Import global styles
import './styles/main.scss'
import 'vue-toastification/dist/index.css'
import 'floating-vue/dist/style.css'

// Create Vue app
const app = createApp(App)

// Configure Pinia
const pinia = createPinia()

// Configure Toast notifications
const toastOptions = {
  position: 'top-right' as const,
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
  icon: true,
  rtl: false
}

// Use plugins
app.use(pinia)
app.use(router)
app.use(Toast, toastOptions)
app.use(FloatingVue)

// Global properties
app.config.globalProperties.$appName = 'BCM Platform v2'
app.config.globalProperties.$version = '2.0.0'

// Error handling
app.config.errorHandler = (err: any, vm: any, info: string) => {
  console.error('Vue Error:', err)
  console.error('Vue Info:', info)
  // You can add error reporting service here
}

// Mount the app
app.mount('#app')