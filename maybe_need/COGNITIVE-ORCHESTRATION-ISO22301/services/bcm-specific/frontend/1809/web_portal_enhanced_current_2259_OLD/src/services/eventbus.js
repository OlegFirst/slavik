/**
 * Event Bus - Simple event emitter for component communication
 * Based on Vue 3 patterns
 */

import { reactive } from 'vue'

class EventBus {
  constructor() {
    this.events = reactive({})
  }

  // Emit an event
  emit(event, data) {
    if (this.events[event]) {
      this.events[event].forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`Error in event handler for '${event}':`, error)
        }
      })
    }
  }

  // Listen to an event
  on(event, callback) {
    if (!this.events[event]) {
      this.events[event] = []
    }
    this.events[event].push(callback)
  }

  // Remove event listener
  off(event, callback) {
    if (this.events[event]) {
      const index = this.events[event].indexOf(callback)
      if (index > -1) {
        this.events[event].splice(index, 1)
      }
    }
  }

  // Remove all listeners for an event
  removeAllListeners(event) {
    if (this.events[event]) {
      this.events[event] = []
    }
  }

  // Get all listeners for an event
  getListeners(event) {
    return this.events[event] || []
  }
}

// Create and export singleton instance
const eventBus = new EventBus()

export default eventBus