<template>
  <header class="header">
    <div class="header-content">
      <!-- Left Section -->
      <div class="header-left">
        <!-- Mobile Menu Button -->
        <button
          @click="$emit('toggle-sidebar')"
          class="menu-button lg:hidden"
          type="button"
        >
          <Bars3Icon class="w-6 h-6" />
        </button>

        <!-- Desktop Menu Button -->
        <button
          @click="$emit('toggle-sidebar')"
          class="menu-button hidden lg:flex"
          type="button"
        >
          <Bars3Icon v-if="sidebarCollapsed" class="w-6 h-6" />
          <XMarkIcon v-else class="w-6 h-6" />
        </button>

        <!-- Page Title -->
        <div class="page-title">
          <h1 class="title-text">{{ currentPageTitle }}</h1>
          <p v-if="currentPageSubtitle" class="subtitle-text">
            {{ currentPageSubtitle }}
          </p>
        </div>
      </div>

      <!-- Right Section -->
      <div class="header-right">
        <!-- Search -->
        <div class="search-container hidden md:flex">
          <div class="search-input-wrapper">
            <MagnifyingGlassIcon class="search-icon" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search..."
              class="search-input"
              @keydown.enter="handleSearch"
            />
          </div>
        </div>

        <!-- Notifications -->
        <div class="relative">
          <button
            @click="toggleNotifications"
            class="icon-button"
            type="button"
          >
            <BellIcon class="w-6 h-6" />
            <span
              v-if="unreadCount > 0"
              class="notification-badge"
            >
              {{ unreadCount > 99 ? '99+' : unreadCount }}
            </span>
          </button>

          <!-- Notifications Dropdown -->
          <Transition name="dropdown">
            <NotificationDropdown
              v-if="showNotifications"
              @close="showNotifications = false"
            />
          </Transition>
        </div>

        <!-- Theme Toggle -->
        <button
          @click="toggleTheme"
          class="icon-button"
          type="button"
        >
          <SunIcon v-if="isDarkMode" class="w-6 h-6" />
          <MoonIcon v-else class="w-6 h-6" />
        </button>

        <!-- User Menu -->
        <div class="relative">
          <Menu as="div" class="relative">
            <MenuButton class="user-menu-button">
              <img
                :src="user?.avatar || '/default-avatar.png'"
                :alt="userDisplayName"
                class="user-avatar"
              />
              <div class="user-info hidden sm:block">
                <p class="user-name">{{ userDisplayName }}</p>
                <p class="user-role">{{ user?.role || 'User' }}</p>
              </div>
              <ChevronDownIcon class="chevron-icon" />
            </MenuButton>

            <Transition name="menu">
              <MenuItems class="user-dropdown">
                <MenuItem v-slot="{ active }">
                  <router-link
                    to="/profile"
                    :class="[active ? 'menu-item-active' : '', 'menu-item']"
                  >
                    <UserIcon class="menu-item-icon" />
                    Profile
                  </router-link>
                </MenuItem>
                <MenuItem v-slot="{ active }">
                  <router-link
                    to="/settings"
                    :class="[active ? 'menu-item-active' : '', 'menu-item']"
                  >
                    <CogIcon class="menu-item-icon" />
                    Settings
                  </router-link>
                </MenuItem>
                <MenuItem v-slot="{ active }">
                  <button
                    @click="handleLogout"
                    :class="[active ? 'menu-item-active' : '', 'menu-item w-full']"
                  >
                    <ArrowRightOnRectangleIcon class="menu-item-icon" />
                    Sign Out
                  </button>
                </MenuItem>
              </MenuItems>
            </Transition>
          </Menu>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Menu, MenuButton, MenuItems, MenuItem } from '@headlessui/vue'
import {
  Bars3Icon,
  XMarkIcon,
  MagnifyingGlassIcon,
  BellIcon,
  SunIcon,
  MoonIcon,
  UserIcon,
  CogIcon,
  ChevronDownIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/vue/24/outline'
import { useAuthStore } from '@stores/auth'
import { useAppStore } from '@stores/app'
import NotificationDropdown from '@components/ui/NotificationDropdown.vue'

// Emits
defineEmits<{
  'toggle-sidebar': []
}>()

// Router
const router = useRouter()
const route = useRoute()

// Stores
const authStore = useAuthStore()
const appStore = useAppStore()

// Reactive data
const searchQuery = ref('')
const showNotifications = ref(false)

// Computed
const user = computed(() => authStore.user)
const sidebarCollapsed = computed(() => appStore.sidebarCollapsed)
const isDarkMode = computed(() => appStore.isDarkMode)
const unreadCount = computed(() => appStore.unreadNotificationsCount)

const userDisplayName = computed(() => {
  if (!user.value) return 'Guest'
  return `${user.value.firstName} ${user.value.lastName}`
})

const currentPageTitle = computed(() => {
  return route.meta?.title as string || 'Dashboard'
})

const currentPageSubtitle = computed(() => {
  return route.meta?.subtitle as string || ''
})

// Methods
function toggleNotifications(): void {
  showNotifications.value = !showNotifications.value
}

function toggleTheme(): void {
  const newTheme = isDarkMode.value ? 'light' : 'dark'
  appStore.setTheme(newTheme)
}

function handleSearch(): void {
  if (searchQuery.value.trim()) {
    router.push(`/search?q=${encodeURIComponent(searchQuery.value)}`)
    searchQuery.value = ''
  }
}

async function handleLogout(): Promise<void> {
  await authStore.logout()
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.header {
  @apply h-16 flex items-center px-4 sm:px-6 lg:px-8;
}

.header-content {
  @apply w-full flex items-center justify-between;
}

.header-left {
  @apply flex items-center space-x-4;
}

.header-right {
  @apply flex items-center space-x-4;
}

.menu-button {
  @apply p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100
         dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700
         transition-colors duration-200;
}

.page-title {
  @apply hidden sm:block;
}

.title-text {
  @apply text-xl font-semibold text-gray-900 dark:text-white;
}

.subtitle-text {
  @apply text-sm text-gray-500 dark:text-gray-400;
}

.search-container {
  @apply relative;
}

.search-input-wrapper {
  @apply relative;
}

.search-icon {
  @apply absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400;
}

.search-input {
  @apply w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg
         focus:ring-2 focus:ring-blue-500 focus:border-blue-500
         dark:bg-gray-700 dark:border-gray-600 dark:text-white
         dark:focus:ring-blue-400 dark:focus:border-blue-400
         transition-colors duration-200;
}

.icon-button {
  @apply relative p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100
         dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700
         transition-colors duration-200;
}

.notification-badge {
  @apply absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold
         rounded-full h-6 w-6 flex items-center justify-center;
}

.user-menu-button {
  @apply flex items-center space-x-3 p-2 rounded-lg
         hover:bg-gray-100 dark:hover:bg-gray-700
         transition-colors duration-200;
}

.user-avatar {
  @apply w-8 h-8 rounded-full object-cover;
}

.user-info {
  @apply text-left;
}

.user-name {
  @apply text-sm font-medium text-gray-900 dark:text-white;
}

.user-role {
  @apply text-xs text-gray-500 dark:text-gray-400 capitalize;
}

.chevron-icon {
  @apply w-4 h-4 text-gray-400;
}

.user-dropdown {
  @apply absolute right-0 top-full mt-2 w-56 bg-white dark:bg-gray-800
         rounded-lg shadow-lg border border-gray-200 dark:border-gray-700
         py-2 z-50;
}

.menu-item {
  @apply flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300
         hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200;
}

.menu-item-active {
  @apply bg-gray-100 dark:bg-gray-700;
}

.menu-item-icon {
  @apply w-4 h-4 mr-3;
}

// Transitions
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.menu-enter-active,
.menu-leave-active {
  transition: all 0.2s ease;
}

.menu-enter-from,
.menu-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>