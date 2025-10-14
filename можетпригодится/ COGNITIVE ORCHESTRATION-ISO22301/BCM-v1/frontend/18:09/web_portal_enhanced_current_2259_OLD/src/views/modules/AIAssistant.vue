<template>
  <div class="ai-assistant">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">AI Assistant</h1>
        <p class="page-subtitle">
          Get intelligent insights and assistance for your BCM activities
        </p>
      </div>
      <div class="header-actions">
        <Button
          variant="secondary"
          leftIcon="DocumentTextIcon"
          @click="showHelpModal = true"
        >
          Help & Examples
        </Button>
      </div>
    </div>

    <!-- Main Chat Interface -->
    <div class="chat-container">
      <Card class="chat-card" noPadding>
        <!-- Chat Messages -->
        <div class="chat-messages" ref="messagesContainer">
          <div
            v-for="message in messages"
            :key="message.id"
            class="message"
            :class="{ 'message-user': message.sender === 'user', 'message-ai': message.sender === 'ai' }"
          >
            <div class="message-avatar">
              <img
                v-if="message.sender === 'user'"
                :src="user?.avatar || '/default-avatar.png'"
                :alt="userDisplayName"
                class="avatar-image"
              />
              <div v-else class="ai-avatar">
                <SparklesIcon class="w-5 h-5" />
              </div>
            </div>

            <div class="message-content">
              <div class="message-header">
                <span class="message-sender">
                  {{ message.sender === 'user' ? userDisplayName : 'BCM AI Assistant' }}
                </span>
                <span class="message-time">{{ formatTime(message.timestamp) }}</span>
              </div>

              <div class="message-body" v-html="message.content"></div>

              <!-- Message Actions -->
              <div v-if="message.sender === 'ai'" class="message-actions">
                <button
                  @click="copyMessage(message.content)"
                  class="action-button"
                  title="Copy message"
                >
                  <ClipboardIcon class="w-4 h-4" />
                </button>
                <button
                  @click="likeMessage(message.id)"
                  class="action-button"
                  :class="{ 'liked': message.liked }"
                  title="Like message"
                >
                  <HandThumbUpIcon class="w-4 h-4" />
                </button>
                <button
                  @click="dislikeMessage(message.id)"
                  class="action-button"
                  :class="{ 'disliked': message.disliked }"
                  title="Dislike message"
                >
                  <HandThumbDownIcon class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="isTyping" class="message message-ai">
            <div class="message-avatar">
              <div class="ai-avatar">
                <SparklesIcon class="w-5 h-5" />
              </div>
            </div>
            <div class="message-content">
              <div class="typing-indicator">
                <div class="typing-dots">
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>
                <span class="typing-text">AI is thinking...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Chat Input -->
        <div class="chat-input-container">
          <div class="input-wrapper">
            <textarea
              v-model="currentMessage"
              @keydown="handleKeyDown"
              placeholder="Ask about risk assessment, BCP development, compliance, or any BCM topic..."
              class="chat-input"
              rows="1"
              ref="messageInput"
            ></textarea>

            <div class="input-actions">
              <Button
                @click="sendMessage"
                :disabled="!currentMessage.trim() || isTyping"
                :loading="isTyping"
                variant="primary"
                size="sm"
              >
                <PaperAirplaneIcon class="w-4 h-4" />
              </Button>
            </div>
          </div>

          <!-- Suggested Actions -->
          <div class="suggested-actions">
            <button
              v-for="suggestion in suggestions"
              :key="suggestion.id"
              @click="useSuggestion(suggestion.text)"
              class="suggestion-chip"
            >
              {{ suggestion.text }}
            </button>
          </div>
        </div>
      </Card>
    </div>

    <!-- Quick Actions Sidebar -->
    <div class="quick-actions">
      <Card title="Quick Actions" :icon="LightBulbIcon">
        <div class="actions-grid">
          <button
            v-for="action in quickActions"
            :key="action.id"
            @click="executeQuickAction(action)"
            class="quick-action-button"
          >
            <component :is="action.icon" class="w-6 h-6" />
            <span>{{ action.label }}</span>
          </button>
        </div>
      </Card>

      <Card title="Recent Conversations" :icon="ChatBubbleLeftRightIcon" class="mt-6">
        <div class="recent-conversations">
          <div
            v-for="conversation in recentConversations"
            :key="conversation.id"
            @click="loadConversation(conversation.id)"
            class="conversation-item"
          >
            <div class="conversation-title">{{ conversation.title }}</div>
            <div class="conversation-preview">{{ conversation.preview }}</div>
            <div class="conversation-time">{{ formatTime(conversation.timestamp) }}</div>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import {
  SparklesIcon,
  ClipboardIcon,
  HandThumbUpIcon,
  HandThumbDownIcon,
  PaperAirplaneIcon,
  LightBulbIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  ShieldExclamationIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  AcademicCapIcon
} from '@heroicons/vue/24/outline'
import Card from '@components/ui/Card.vue'
import Button from '@components/ui/Button.vue'
import { useAuthStore } from '@stores/auth'
import { formatDistanceToNow } from 'date-fns'

// Store
const authStore = useAuthStore()

// Refs
const messagesContainer = ref<HTMLDivElement>()
const messageInput = ref<HTMLTextAreaElement>()

// Reactive data
const showHelpModal = ref(false)
const currentMessage = ref('')
const isTyping = ref(false)

const messages = ref([
  {
    id: 1,
    sender: 'ai',
    content: 'Hello! I\'m your BCM AI Assistant. I can help you with risk assessments, business continuity planning, compliance questions, and more. How can I assist you today?',
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
    liked: false,
    disliked: false
  }
])

const suggestions = ref([
  { id: 1, text: 'How do I conduct a BIA?' },
  { id: 2, text: 'What are ISO 22301 requirements?' },
  { id: 3, text: 'Risk assessment best practices' },
  { id: 4, text: 'Create incident response plan' }
])

const quickActions = ref([
  {
    id: 1,
    label: 'Risk Analysis',
    icon: ShieldExclamationIcon,
    action: 'risk-analysis'
  },
  {
    id: 2,
    label: 'BIA Guidance',
    icon: ChartBarIcon,
    action: 'bia-guidance'
  },
  {
    id: 3,
    label: 'Crisis Scenarios',
    icon: ExclamationTriangleIcon,
    action: 'crisis-scenarios'
  },
  {
    id: 4,
    label: 'Training Content',
    icon: AcademicCapIcon,
    action: 'training-content'
  }
])

const recentConversations = ref([
  {
    id: 1,
    title: 'Risk Assessment Process',
    preview: 'How to identify and evaluate operational risks...',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000)
  },
  {
    id: 2,
    title: 'ISO 22301 Compliance',
    preview: 'Requirements for business continuity management...',
    timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000)
  }
])

// Computed
const user = computed(() => authStore.user)
const userDisplayName = computed(() => {
  if (!user.value) return 'User'
  return `${user.value.firstName} ${user.value.lastName}`
})

// Methods
async function sendMessage(): Promise<void> {
  if (!currentMessage.value.trim() || isTyping.value) return

  const userMessage = {
    id: Date.now(),
    sender: 'user' as const,
    content: currentMessage.value,
    timestamp: new Date()
  }

  messages.value.push(userMessage)
  const messageText = currentMessage.value
  currentMessage.value = ''

  // Auto-resize textarea
  if (messageInput.value) {
    messageInput.value.style.height = 'auto'
  }

  // Scroll to bottom
  await nextTick()
  scrollToBottom()

  // Show typing indicator
  isTyping.value = true

  // Simulate AI response
  setTimeout(() => {
    const aiResponse = {
      id: Date.now() + 1,
      sender: 'ai' as const,
      content: generateAIResponse(messageText),
      timestamp: new Date(),
      liked: false,
      disliked: false
    }

    messages.value.push(aiResponse)
    isTyping.value = false

    nextTick(() => {
      scrollToBottom()
    })
  }, 1500 + Math.random() * 1000)
}

function generateAIResponse(message: string): string {
  // Simple response generation - in real app, this would call an AI service
  const responses = [
    'Based on ISO 22301 standards, here are the key steps for your BCM process...',
    'I can help you with that. Let me break down the risk assessment methodology...',
    'For business continuity planning, you should consider these critical factors...',
    'Here\'s a comprehensive approach to incident management...'
  ]

  return responses[Math.floor(Math.random() * responses.length)]
}

function handleKeyDown(event: KeyboardEvent): void {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

function useSuggestion(text: string): void {
  currentMessage.value = text
  sendMessage()
}

function executeQuickAction(action: any): void {
  const actionMessages: Record<string, string> = {
    'risk-analysis': 'Help me create a comprehensive risk analysis framework',
    'bia-guidance': 'I need guidance on conducting a Business Impact Analysis',
    'crisis-scenarios': 'Generate crisis scenarios for my organization',
    'training-content': 'Help me develop BCM training materials'
  }

  currentMessage.value = actionMessages[action.action] || `Help me with ${action.label}`
  sendMessage()
}

function formatTime(date: Date): string {
  return formatDistanceToNow(date, { addSuffix: true })
}

function scrollToBottom(): void {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function copyMessage(content: string): void {
  navigator.clipboard.writeText(content.replace(/<[^>]*>/g, ''))
}

function likeMessage(messageId: number): void {
  const message = messages.value.find(m => m.id === messageId)
  if (message) {
    message.liked = !message.liked
    message.disliked = false
  }
}

function dislikeMessage(messageId: number): void {
  const message = messages.value.find(m => m.id === messageId)
  if (message) {
    message.disliked = !message.disliked
    message.liked = false
  }
}

function loadConversation(conversationId: number): void {
  console.log('Loading conversation:', conversationId)
}

// Lifecycle
onMounted(() => {
  scrollToBottom()
})
</script>

<style lang="scss" scoped>
.ai-assistant {
  @apply flex gap-6 h-full;
}

.page-header {
  @apply col-span-2 flex items-center justify-between mb-6;
}

.header-content {
  @apply space-y-1;
}

.page-title {
  @apply text-2xl font-bold text-gray-900 dark:text-white;
}

.page-subtitle {
  @apply text-gray-600 dark:text-gray-400;
}

.header-actions {
  @apply flex items-center space-x-3;
}

.chat-container {
  @apply flex-1;
}

.chat-card {
  @apply h-[600px] flex flex-col;
}

.chat-messages {
  @apply flex-1 overflow-y-auto p-4 space-y-4;
}

.message {
  @apply flex items-start space-x-3;

  &.message-user {
    @apply flex-row-reverse space-x-reverse;

    .message-content {
      @apply bg-blue-600 text-white;
    }
  }

  &.message-ai {
    .message-content {
      @apply bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white;
    }
  }
}

.message-avatar {
  @apply flex-shrink-0;
}

.avatar-image {
  @apply w-8 h-8 rounded-full object-cover;
}

.ai-avatar {
  @apply w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-purple-600
         flex items-center justify-center text-white;
}

.message-content {
  @apply max-w-xs sm:max-w-md lg:max-w-lg rounded-lg p-3 space-y-2;
}

.message-header {
  @apply flex items-center justify-between text-xs opacity-75;
}

.message-sender {
  @apply font-medium;
}

.message-time {
  @apply text-xs;
}

.message-body {
  @apply text-sm leading-relaxed;
}

.message-actions {
  @apply flex items-center space-x-2 pt-2 border-t border-gray-200 dark:border-gray-600;
}

.action-button {
  @apply p-1 rounded text-gray-500 hover:text-gray-700 hover:bg-gray-200
         dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-600
         transition-colors duration-200;

  &.liked {
    @apply text-blue-600 bg-blue-100 dark:bg-blue-900/50;
  }

  &.disliked {
    @apply text-red-600 bg-red-100 dark:bg-red-900/50;
  }
}

.typing-indicator {
  @apply flex items-center space-x-2;
}

.typing-dots {
  @apply flex space-x-1;
}

.dot {
  @apply w-2 h-2 bg-gray-400 rounded-full animate-bounce;

  &:nth-child(2) {
    animation-delay: 0.1s;
  }

  &:nth-child(3) {
    animation-delay: 0.2s;
  }
}

.typing-text {
  @apply text-sm text-gray-500;
}

.chat-input-container {
  @apply p-4 border-t border-gray-200 dark:border-gray-700 space-y-3;
}

.input-wrapper {
  @apply flex items-end space-x-3;
}

.chat-input {
  @apply flex-1 min-h-[40px] max-h-32 px-3 py-2 border border-gray-300 dark:border-gray-600
         rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
         dark:bg-gray-700 dark:text-white;
}

.input-actions {
  @apply flex-shrink-0;
}

.suggested-actions {
  @apply flex flex-wrap gap-2;
}

.suggestion-chip {
  @apply px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600
         rounded-full transition-colors duration-200;
}

.quick-actions {
  @apply w-80 space-y-6;
}

.actions-grid {
  @apply grid grid-cols-2 gap-3;
}

.quick-action-button {
  @apply p-3 border border-gray-200 dark:border-gray-700 rounded-lg
         hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-md
         transition-all duration-200 flex flex-col items-center space-y-2
         text-sm font-medium text-gray-700 dark:text-gray-300;
}

.recent-conversations {
  @apply space-y-3;
}

.conversation-item {
  @apply p-3 border border-gray-200 dark:border-gray-700 rounded-lg
         hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-sm
         transition-all duration-200 cursor-pointer;
}

.conversation-title {
  @apply font-medium text-gray-900 dark:text-white text-sm;
}

.conversation-preview {
  @apply text-gray-500 dark:text-gray-400 text-xs mt-1 truncate;
}

.conversation-time {
  @apply text-gray-400 text-xs mt-2;
}
</style>