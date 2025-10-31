<template>
  <div class="crisis-room">
    <!-- Crisis Room Header -->
    <div class="crisis-header">
      <div class="crisis-status" :class="crisisLevel">
        <h1>🚨 Crisis Room - {{ crisisLevel.toUpperCase() }}</h1>
        <div class="crisis-timer">
          {{ formatDuration(crisisDuration) }}
        </div>
      </div>
    </div>

    <!-- Crisis Dashboard -->
    <div class="crisis-dashboard">
      <div class="row">
        <!-- Incident Overview -->
        <div class="col-md-4">
          <div class="crisis-card">
            <h3>🔥 Active Incident</h3>
            <div class="incident-details">
              <h4>{{ activeIncident.title }}</h4>
              <p><strong>Severity:</strong> {{ activeIncident.severity }}</p>
              <p><strong>Type:</strong> {{ activeIncident.type }}</p>
              <p><strong>Started:</strong> {{ formatTime(activeIncident.startTime) }}</p>
            </div>
          </div>
        </div>

        <!-- Response Team -->
        <div class="col-md-4">
          <div class="crisis-card">
            <h3>👥 Response Team</h3>
            <div class="team-list">
              <div v-for="member in responseTeam" :key="member.id" class="team-member">
                <div class="member-avatar">
                  <i class="fas fa-user-circle"></i>
                </div>
                <div class="member-info">
                  <strong>{{ member.name }}</strong>
                  <div class="member-role">{{ member.role }}</div>
                  <div class="member-status" :class="member.status">
                    {{ member.status }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Critical Actions -->
        <div class="col-md-4">
          <div class="crisis-card">
            <h3>⚡ Critical Actions</h3>
            <div class="action-list">
              <div v-for="action in criticalActions" :key="action.id"
                   class="action-item" :class="action.status">
                <div class="action-checkbox">
                  <input type="checkbox" v-model="action.completed"
                         @change="updateActionStatus(action)">
                </div>
                <div class="action-content">
                  <strong>{{ action.title }}</strong>
                  <div class="action-time">{{ action.deadline }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Crisis Timeline -->
    <div class="crisis-timeline">
      <h3>📅 Crisis Timeline</h3>
      <div class="timeline">
        <div v-for="event in crisisTimeline" :key="event.id" class="timeline-event">
          <div class="timeline-marker" :class="event.type"></div>
          <div class="timeline-content">
            <div class="timeline-time">{{ formatTime(event.timestamp) }}</div>
            <div class="timeline-title">{{ event.title }}</div>
            <div class="timeline-description">{{ event.description }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Crisis Communication -->
    <div class="crisis-communication">
      <h3>💬 Crisis Communication</h3>
      <div class="row">
        <div class="col-md-6">
          <div class="communication-log">
            <div v-for="message in communicationLog" :key="message.id" class="comm-message">
              <div class="message-header">
                <strong>{{ message.sender }}</strong>
                <span class="message-time">{{ formatTime(message.timestamp) }}</span>
              </div>
              <div class="message-content">{{ message.content }}</div>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="communication-controls">
            <textarea v-model="newMessage" placeholder="Emergency communication..."></textarea>
            <div class="comm-buttons">
              <button @click="sendMessage('internal')" class="btn btn-primary">
                📢 Internal Broadcast
              </button>
              <button @click="sendMessage('external')" class="btn btn-warning">
                📣 External Communication
              </button>
              <button @click="sendMessage('media')" class="btn btn-danger">
                📺 Media Statement
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CrisisRoom',
  data() {
    return {
      crisisLevel: 'high',
      crisisDuration: 0,
      activeIncident: {
        title: 'Data Center Outage',
        severity: 'Critical',
        type: 'Technology',
        startTime: new Date()
      },
      responseTeam: [
        { id: 1, name: 'John Doe', role: 'Incident Commander', status: 'active' },
        { id: 2, name: 'Jane Smith', role: 'Technical Lead', status: 'active' },
        { id: 3, name: 'Mike Johnson', role: 'Communications', status: 'standby' }
      ],
      criticalActions: [
        { id: 1, title: 'Activate backup systems', deadline: '15 min', completed: true, status: 'completed' },
        { id: 2, title: 'Notify all stakeholders', deadline: '30 min', completed: false, status: 'pending' },
        { id: 3, title: 'Prepare media statement', deadline: '1 hour', completed: false, status: 'pending' }
      ],
      crisisTimeline: [
        {
          id: 1,
          timestamp: new Date(Date.now() - 3600000),
          title: 'Crisis Declared',
          description: 'Major data center outage detected',
          type: 'critical'
        },
        {
          id: 2,
          timestamp: new Date(Date.now() - 3000000),
          title: 'Response Team Activated',
          description: 'Crisis response team assembled',
          type: 'action'
        }
      ],
      communicationLog: [
        {
          id: 1,
          sender: 'Incident Commander',
          timestamp: new Date(Date.now() - 1800000),
          content: 'All systems offline. Activating DR procedures.'
        }
      ],
      newMessage: ''
    }
  },
  methods: {
    updateActionStatus(action) {
      // Update action status
      action.status = action.completed ? 'completed' : 'pending';

      // Notify via EventBus
      this.$emit('action-updated', action);
    },

    sendMessage(type) {
      if (!this.newMessage.trim()) return;

      const message = {
        id: Date.now(),
        sender: 'Crisis Commander',
        timestamp: new Date(),
        content: this.newMessage,
        type: type
      };

      this.communicationLog.unshift(message);
      this.newMessage = '';

      // Send to notification system
      this.$emit('crisis-communication', message);
    },

    formatTime(time) {
      return new Date(time).toLocaleTimeString();
    },

    formatDuration(seconds) {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      return `${hours}h ${minutes}m`;
    }
  },

  mounted() {
    // Start crisis timer
    this.crisisTimer = setInterval(() => {
      this.crisisDuration++;
    }, 1000);

    // Connect to EventBus for real-time updates
    this.connectToEventBus();
  },

  beforeUnmount() {
    if (this.crisisTimer) {
      clearInterval(this.crisisTimer);
    }
  }
}
</script>

<style scoped>
.crisis-room {
  background: #1a1a1a;
  color: #fff;
  min-height: 100vh;
  padding: 20px;
}

.crisis-header {
  background: linear-gradient(135deg, #ff4444, #cc0000);
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.crisis-card {
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  height: 300px;
  overflow-y: auto;
}

.team-member {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding: 8px;
  border-radius: 4px;
  background: #333;
}

.action-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  padding: 6px;
  border-radius: 4px;
}

.action-item.completed {
  background: #2d5a2d;
}

.action-item.pending {
  background: #5a4d2d;
}

.timeline-event {
  display: flex;
  margin-bottom: 15px;
}

.timeline-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 15px;
  margin-top: 5px;
}

.timeline-marker.critical {
  background: #ff4444;
}

.timeline-marker.action {
  background: #44ff44;
}

.crisis-communication textarea {
  width: 100%;
  height: 100px;
  background: #333;
  border: 1px solid #666;
  color: #fff;
  padding: 10px;
  border-radius: 4px;
}

.comm-buttons {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}
</style>