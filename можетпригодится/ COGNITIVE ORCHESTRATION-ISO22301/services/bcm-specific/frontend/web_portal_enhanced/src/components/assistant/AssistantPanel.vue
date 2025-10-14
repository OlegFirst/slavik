<template>
  <div class="assistant-panel">
    <div class="assistant-header">
      <h3>AI Assistant</h3>
      <p class="assistant-subtitle">Get help with BCM processes</p>
    </div>

    <div class="assistant-content">
      <div class="chat-container">
        <div class="messages">
          <div class="message assistant-message">
            <div class="message-content">
              Hello! I'm your BCM AI Assistant. How can I help you today?
            </div>
          </div>
        </div>

        <div class="input-container">
          <input
            type="text"
            placeholder="Ask me anything about business continuity..."
            class="chat-input"
            @keyup.enter="sendMessage"
            v-model="currentMessage"
          >
          <button class="send-button" @click="sendMessage">
            <span>Send</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const currentMessage = ref('')

const sendMessage = () => {
  if (currentMessage.value.trim()) {
    // Handle message sending logic here
    console.log('Sending message:', currentMessage.value)
    currentMessage.value = ''
  }
}
</script>

<style lang="scss" scoped>
.assistant-panel {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-height: 500px;
  display: flex;
  flex-direction: column;
}

.assistant-header {
  border-bottom: 1px solid #e5e5e5;
  padding-bottom: 16px;
  margin-bottom: 16px;

  h3 {
    margin: 0;
    color: #1f2937;
    font-size: 18px;
    font-weight: 600;
  }

  .assistant-subtitle {
    margin: 4px 0 0 0;
    color: #6b7280;
    font-size: 14px;
  }
}

.assistant-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 16px;
  min-height: 200px;
}

.message {
  margin-bottom: 12px;

  &.assistant-message {
    .message-content {
      background: #f3f4f6;
      color: #374151;
      border-radius: 12px 12px 12px 4px;
    }
  }

  &.user-message {
    text-align: right;

    .message-content {
      background: #3b82f6;
      color: white;
      border-radius: 12px 12px 4px 12px;
      display: inline-block;
    }
  }
}

.message-content {
  padding: 12px 16px;
  max-width: 80%;
  word-wrap: break-word;
}

.input-container {
  display: flex;
  gap: 8px;
  align-items: center;
}

.chat-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;

  &:focus {
    border-color: #3b82f6;
  }

  &::placeholder {
    color: #9ca3af;
  }
}

.send-button {
  padding: 12px 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background: #2563eb;
  }

  &:active {
    background: #1d4ed8;
  }
}
</style>