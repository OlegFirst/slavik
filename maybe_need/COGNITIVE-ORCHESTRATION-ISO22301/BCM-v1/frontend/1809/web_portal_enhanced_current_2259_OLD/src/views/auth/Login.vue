<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Login Card -->
      <div class="login-card">
        <!-- Header -->
        <div class="login-header">
          <div class="logo-section">
            <img src="/logo.svg" alt="BCM Platform" class="logo" />
            <h1 class="app-title">BCM Platform</h1>
          </div>
          <div class="welcome-text">
            <h2 class="welcome-title">Welcome back</h2>
            <p class="welcome-subtitle">
              Sign in to your Business Continuity Management portal
            </p>
          </div>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleSubmit" class="login-form">
          <div class="form-group">
            <label for="email" class="form-label">Email address</label>
            <div class="input-wrapper">
              <EnvelopeIcon class="input-icon" />
              <input
                id="email"
                v-model="form.email"
                type="email"
                required
                class="form-input"
                placeholder="Enter your email"
                :disabled="isLoading"
                autocomplete="email"
              />
            </div>
            <div v-if="errors.email" class="error-text">{{ errors.email }}</div>
          </div>

          <div class="form-group">
            <label for="password" class="form-label">Password</label>
            <div class="input-wrapper">
              <LockClosedIcon class="input-icon" />
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="form-input"
                placeholder="Enter your password"
                :disabled="isLoading"
                autocomplete="current-password"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="password-toggle"
              >
                <EyeIcon v-if="!showPassword" class="w-5 h-5" />
                <EyeSlashIcon v-else class="w-5 h-5" />
              </button>
            </div>
            <div v-if="errors.password" class="error-text">{{ errors.password }}</div>
          </div>

          <div class="form-options">
            <label class="checkbox-wrapper">
              <input
                v-model="form.rememberMe"
                type="checkbox"
                class="checkbox"
              />
              <span class="checkbox-label">Remember me</span>
            </label>

            <router-link to="/forgot-password" class="forgot-link">
              Forgot password?
            </router-link>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            :loading="isLoading"
            :disabled="isLoading"
            block
          >
            Sign in
          </Button>

          <div v-if="errors.general" class="error-text text-center mt-4">
            {{ errors.general }}
          </div>
        </form>

        <!-- Footer -->
        <div class="login-footer">
          <p class="footer-text">
            Don't have an account?
            <router-link to="/register" class="register-link">
              Contact administrator
            </router-link>
          </p>
        </div>
      </div>

      <!-- Features Section -->
      <div class="features-section">
        <div class="features-content">
          <h3 class="features-title">Enterprise BCM Platform</h3>
          <p class="features-subtitle">
            Comprehensive Business Continuity Management solution
          </p>

          <div class="features-list">
            <div
              v-for="feature in features"
              :key="feature.id"
              class="feature-item"
            >
              <div class="feature-icon">
                <component :is="feature.icon" class="w-6 h-6" />
              </div>
              <div class="feature-content">
                <h4 class="feature-title">{{ feature.title }}</h4>
                <p class="feature-description">{{ feature.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import {
  EnvelopeIcon,
  LockClosedIcon,
  EyeIcon,
  EyeSlashIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  DocumentTextIcon,
  CogIcon
} from '@heroicons/vue/24/outline'
import Button from '@components/ui/Button.vue'
import { useAuthStore } from '@stores/auth'
import { useToast } from 'vue-toastification'

// Router
const router = useRouter()

// Store & Toast
const authStore = useAuthStore()
const toast = useToast()

// Reactive data
const isLoading = ref(false)
const showPassword = ref(false)

const form = reactive({
  email: '',
  password: '',
  rememberMe: false
})

const errors = reactive({
  email: '',
  password: '',
  general: ''
})

const features = ref([
  {
    id: 1,
    title: 'Risk Management',
    description: 'Comprehensive risk assessment and mitigation strategies',
    icon: ShieldCheckIcon
  },
  {
    id: 2,
    title: 'Business Impact Analysis',
    description: 'Detailed analysis of business process dependencies',
    icon: ChartBarIcon
  },
  {
    id: 3,
    title: 'Continuity Planning',
    description: 'Structured business continuity plan development',
    icon: DocumentTextIcon
  },
  {
    id: 4,
    title: 'Automated Workflows',
    description: 'Streamlined processes with intelligent automation',
    icon: CogIcon
  }
])

// Methods
function clearErrors(): void {
  errors.email = ''
  errors.password = ''
  errors.general = ''
}

function validateForm(): boolean {
  clearErrors()
  let isValid = true

  if (!form.email) {
    errors.email = 'Email is required'
    isValid = false
  } else if (!/\S+@\S+\.\S+/.test(form.email)) {
    errors.email = 'Please enter a valid email address'
    isValid = false
  }

  if (!form.password) {
    errors.password = 'Password is required'
    isValid = false
  } else if (form.password.length < 6) {
    errors.password = 'Password must be at least 6 characters'
    isValid = false
  }

  return isValid
}

async function handleSubmit(): Promise<void> {
  if (!validateForm()) return

  isLoading.value = true
  clearErrors()

  try {
    const success = await authStore.login({
      email: form.email,
      password: form.password,
      rememberMe: form.rememberMe
    })

    if (success) {
      router.push('/dashboard')
    } else {
      errors.general = 'Invalid email or password'
    }
  } catch (error: any) {
    console.error('Login error:', error)
    errors.general = error.message || 'An error occurred during login'
  } finally {
    isLoading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  @apply min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100
         dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4;
}

.login-container {
  @apply w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8
         lg:gap-12 items-center;
}

.login-card {
  @apply bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-8 w-full max-w-md mx-auto
         border border-gray-200 dark:border-gray-700;
}

.login-header {
  @apply space-y-6 text-center mb-8;
}

.logo-section {
  @apply flex flex-col items-center space-y-3;
}

.logo {
  @apply w-16 h-16 object-contain;
}

.app-title {
  @apply text-2xl font-bold text-gray-900 dark:text-white;
}

.welcome-text {
  @apply space-y-2;
}

.welcome-title {
  @apply text-xl font-semibold text-gray-900 dark:text-white;
}

.welcome-subtitle {
  @apply text-gray-600 dark:text-gray-400;
}

.login-form {
  @apply space-y-6;
}

.form-group {
  @apply space-y-2;
}

.form-label {
  @apply block text-sm font-medium text-gray-700 dark:text-gray-300;
}

.input-wrapper {
  @apply relative;
}

.input-icon {
  @apply absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400;
}

.form-input {
  @apply w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600
         rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500
         dark:bg-gray-700 dark:text-white transition-colors duration-200
         disabled:opacity-50 disabled:cursor-not-allowed;
}

.password-toggle {
  @apply absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400
         hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-200;
}

.form-options {
  @apply flex items-center justify-between;
}

.checkbox-wrapper {
  @apply flex items-center space-x-2 cursor-pointer;
}

.checkbox {
  @apply w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded
         focus:ring-blue-500 dark:bg-gray-700;
}

.checkbox-label {
  @apply text-sm text-gray-700 dark:text-gray-300;
}

.forgot-link {
  @apply text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400
         dark:hover:text-blue-300 transition-colors duration-200;
}

.error-text {
  @apply text-sm text-red-600 dark:text-red-400;
}

.login-footer {
  @apply mt-8 pt-6 border-t border-gray-200 dark:border-gray-700 text-center;
}

.footer-text {
  @apply text-sm text-gray-600 dark:text-gray-400;
}

.register-link {
  @apply text-blue-600 hover:text-blue-700 dark:text-blue-400
         dark:hover:text-blue-300 font-medium transition-colors duration-200;
}

.features-section {
  @apply hidden lg:block;
}

.features-content {
  @apply space-y-8;
}

.features-title {
  @apply text-3xl font-bold text-gray-900 dark:text-white;
}

.features-subtitle {
  @apply text-lg text-gray-600 dark:text-gray-400;
}

.features-list {
  @apply space-y-6;
}

.feature-item {
  @apply flex items-start space-x-4;
}

.feature-icon {
  @apply flex-shrink-0 w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-lg
         flex items-center justify-center text-blue-600 dark:text-blue-400;
}

.feature-content {
  @apply space-y-1;
}

.feature-title {
  @apply font-semibold text-gray-900 dark:text-white;
}

.feature-description {
  @apply text-gray-600 dark:text-gray-400;
}
</style>