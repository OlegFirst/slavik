<template>
  <div class="loading-overlay">
    <div class="loading-content">
      <div class="spinner">
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
        <div class="spinner-ring"></div>
      </div>
      <p class="loading-text">Loading...</p>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.loading-overlay {
  @apply fixed inset-0 z-50 flex items-center justify-center;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.loading-content {
  @apply flex flex-col items-center space-y-4 bg-white dark:bg-gray-800
         rounded-lg p-8 shadow-2xl;
}

.spinner {
  @apply relative w-12 h-12;
}

.spinner-ring {
  @apply absolute border-4 border-gray-200 dark:border-gray-600 border-t-blue-600
         rounded-full animate-spin;

  &:nth-child(1) {
    @apply w-12 h-12;
    animation: spin 1.2s linear infinite;
  }

  &:nth-child(2) {
    @apply w-10 h-10 top-1 left-1 border-t-blue-500;
    animation: spin 1.2s linear infinite reverse;
    animation-delay: -0.1s;
  }

  &:nth-child(3) {
    @apply w-8 h-8 top-2 left-2 border-t-blue-400;
    animation: spin 1.2s linear infinite;
    animation-delay: -0.2s;
  }

  &:nth-child(4) {
    @apply w-6 h-6 top-3 left-3 border-t-blue-300;
    animation: spin 1.2s linear infinite reverse;
    animation-delay: -0.3s;
  }
}

.loading-text {
  @apply text-gray-700 dark:text-gray-300 font-medium;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>