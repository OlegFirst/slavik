# BCM Community Forum

Knowledge sharing and collaboration platform for BCM Platform users, providing forums, discussions, and community-driven knowledge exchange for business continuity management.

## 🏗️ Architecture

```
BCM Platform → Community Forum → Knowledge Exchange
     ↓              ↓                    ↓
User Interaction → Topic Creation → Discussion Threads
     ↓              ↓                    ↓
Real-time Updates → Notifications → Reputation System
```

## 🚀 Features

### ✅ Forum Management
- **Multi-category forums** - Organized discussion spaces
- **Topic and post management** - Threaded discussions
- **Rich text editor** - Markdown support with syntax highlighting
- **File attachments** - Document and image sharing
- **Search functionality** - Full-text search across content

### ✅ User Engagement
- **User profiles** - Reputation and activity tracking
- **Reaction system** - Like, helpful, solved reactions
- **Mention system** - @username notifications
- **Subscription system** - Follow topics and categories
- **Real-time notifications** - WebSocket-powered updates

### ✅ Collaboration Features
- **Knowledge base** - FAQ and documentation sections
- **Polls and surveys** - Community decision making
- **Expert system** - Verified experts and badges
- **Content moderation** - Community-driven quality control
- **Discussion analytics** - Engagement metrics

### ✅ BCM Integration
- **User synchronization** - BCM Platform user integration
- **Company-based access** - Multi-tenant forum spaces
- **BCM topic categories** - ISO 22301 aligned discussions
- **Expert verification** - BCM professional validation
- **Knowledge tagging** - BCM-specific content organization

## 📦 Components

### 1. Forum Service (`forum_service.py`)
- FastAPI-based REST API and WebSocket service
- User authentication and authorization
- Topic, post, and reaction management
- Real-time communication and notifications

### 2. Background Worker (`worker.py`)
- Asynchronous task processing with Redis
- Notification delivery and digest generation
- User reputation updates and data synchronization
- Maintenance and cleanup tasks

### 3. Analytics Service
- Discussion metrics and engagement tracking
- User activity analytics and reporting
- Content performance analysis
- Community health monitoring

### 4. Database Layer
- PostgreSQL with comprehensive forum schema
- User profiles, topics, posts, and reactions
- Notification and subscription management
- Analytics and reporting data

## 🛠️ Setup & Deployment

### Prerequisites
- Docker & Docker Compose
- 2GB+ RAM for optimal performance
- PostgreSQL 15+ and Redis 7+

### 1. Environment Configuration
```bash
# Copy and configure environment
cp .env.example .env

# Required variables
FORUM_API_KEY=your_secure_forum_api_key
FORUM_JWT_SECRET=your_jwt_secret_key
FORUM_DB_PASSWORD=secure_forum_db_password
FORUM_REDIS_PASSWORD=secure_redis_password
BCM_API_KEY=your_bcm_platform_api_key

# Optional features
SMTP_SERVER=smtp.example.com
SMTP_USERNAME=forum@example.com
SMTP_PASSWORD=email_password
```

### 2. Deploy Forum Service
```bash
# Start core forum service
docker-compose up -d

# Start with storage service
docker-compose --profile storage up -d

# Start with search capabilities
docker-compose --profile search up -d

# Start with worker and analytics
docker-compose --profile worker --profile analytics up -d
```

### 3. Verify Deployment
```bash
# Check service health
curl http://localhost:8006/health

# Test forum API
curl -X GET -H "Authorization: Bearer your_api_key" \
  http://localhost:8006/api/v1/categories

# Test WebSocket connection
wscat -c ws://localhost:8006/ws?token=your_jwt_token
```

## 🔧 API Usage

### User Authentication
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "secure_password"
}
```

### Create Category
```bash
POST /api/v1/categories
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "name": "Business Continuity Planning",
  "description": "Discussion about BCP development and maintenance",
  "slug": "bcp-planning",
  "is_public": true
}
```

### Create Topic
```bash
POST /api/v1/topics
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "category_id": "cat_123",
  "title": "ISO 22301 Implementation Best Practices",
  "content": "Let's discuss effective approaches to implementing ISO 22301...",
  "tags": ["iso22301", "implementation", "best-practices"]
}
```

### Create Post
```bash
POST /api/v1/posts
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "topic_id": "topic_456",
  "content": "Great question! In my experience, starting with a thorough BIA is crucial...",
  "parent_id": null
}
```

### Get Forum Statistics
```bash
GET /api/v1/stats
Authorization: Bearer <jwt-token>

Response:
{
  "total_users": 1247,
  "total_topics": 3421,
  "total_posts": 12876,
  "active_users_24h": 89,
  "top_categories": [
    {"name": "BCP Planning", "topic_count": 456},
    {"name": "Risk Assessment", "topic_count": 324}
  ]
}
```

### WebSocket Events
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8006/ws?token=jwt_token');

// Listen for events
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch(data.type) {
    case 'new_post':
      // Handle new post notification
      break;
    case 'mention':
      // Handle mention notification
      break;
    case 'reaction':
      // Handle reaction notification
      break;
  }
};

// Send typing indicator
ws.send(JSON.stringify({
  type: 'typing',
  topic_id: 'topic_123'
}));
```

## 📊 Forum Categories

### BCM Knowledge Areas
```json
{
  "categories": {
    "business_continuity_planning": {
      "name": "Business Continuity Planning",
      "topics": ["BCP development", "Strategy", "Objectives"]
    },
    "risk_management": {
      "name": "Risk Management",
      "topics": ["Risk assessment", "Threat analysis", "Vulnerability"]
    },
    "business_impact_analysis": {
      "name": "Business Impact Analysis",
      "topics": ["Critical processes", "Dependencies", "RTOs"]
    },
    "incident_response": {
      "name": "Incident Response",
      "topics": ["Crisis management", "Response teams", "Communications"]
    },
    "exercises_testing": {
      "name": "Exercises & Testing",
      "topics": ["Tabletop exercises", "Simulations", "Testing methods"]
    },
    "compliance_audit": {
      "name": "Compliance & Audit",
      "topics": ["ISO 22301", "Regulatory", "Audit preparation"]
    }
  }
}
```

### User Roles and Permissions
- **Administrator** - Full forum management access
- **Moderator** - Content moderation and user management
- **Expert** - Verified BCM professional with special badges
- **Member** - Standard user with full participation rights
- **Observer** - Read-only access to public content

### Reputation System
```python
reputation_actions = {
    "post_created": 2,
    "post_liked": 1,
    "post_marked_helpful": 5,
    "post_marked_solution": 10,
    "topic_created": 3,
    "expert_verification": 50,
    "moderation_action": -5
}
```

## 🔐 Security & Privacy

### Data Protection
- **Multi-tenant isolation** by company and user permissions
- **Content moderation** with automated and manual review
- **Secure file uploads** with virus scanning and type validation
- **Audit logging** for all user actions and content changes

### Privacy Controls
- **GDPR compliance** with data export and deletion
- **User consent** management for data processing
- **Content visibility** controls (public, company, private)
- **Anonymous posting** options for sensitive discussions

## 🧪 Testing

### Unit Tests
```bash
# Test forum service
pytest tests/unit/test_forum_service.py

# Test user management
pytest tests/unit/test_user_management.py

# Test WebSocket functionality
pytest tests/unit/test_websocket.py
```

### Integration Tests
```bash
# Test API endpoints
pytest tests/integration/test_api_endpoints.py

# Test database operations
pytest tests/integration/test_database.py

# Test background workers
pytest tests/integration/test_workers.py
```

### Load Tests
```bash
# Test concurrent users
pytest tests/load/test_concurrent_users.py

# Test WebSocket connections
pytest tests/load/test_websocket_load.py
```

## 📈 Analytics & Monitoring

### Forum Metrics
- **User engagement** - Active users, posts per day, time spent
- **Content quality** - Reaction ratios, solution rates, expert participation
- **Knowledge sharing** - Topic creation, cross-company collaboration
- **Community health** - Moderation actions, user retention, satisfaction

### Monitoring Endpoints
```bash
# Health check
GET /health

# Metrics for Prometheus
GET /metrics

# Service status
GET /status
```

## 🔧 Configuration

### Environment Variables
```bash
# Service Configuration
PORT=8006                          # Service port
HOST=0.0.0.0                      # Service host
LOG_LEVEL=info                    # Logging level

# Security
FORUM_API_KEY=secure_api_key      # API authentication
JWT_SECRET=jwt_secret_key         # JWT token signing

# Database
DATABASE_URL=postgresql://...      # PostgreSQL connection
REDIS_URL=redis://...             # Redis connection

# BCM Integration
BCM_API_URL=http://bcm:8069       # BCM Platform URL
BCM_API_KEY=bcm_api_key          # BCM Platform API key

# Features
MAX_FILE_SIZE=10MB                # File upload limit
POSTS_PER_PAGE=20                 # Pagination limit
ENABLE_REACTIONS=true             # Reaction system
ENABLE_POLLS=true                 # Polling feature
```

### Docker Profiles
- **default** - Core forum service with database
- **storage** - Add MinIO for distributed file storage
- **search** - Add Elasticsearch for advanced search
- **worker** - Add background task processing
- **analytics** - Add analytics and reporting service
- **nginx** - Add reverse proxy and load balancing

## 🚀 Production Deployment

### High Availability Setup
- **Multiple forum instances** behind load balancer
- **Database clustering** with read replicas
- **Redis Cluster** for distributed caching
- **CDN integration** for file and static content delivery

### Performance Optimization
- **Connection pooling** for database and Redis
- **Content caching** with intelligent invalidation
- **WebSocket connection** management and scaling
- **Database indexing** for search and analytics queries

### Backup & Recovery
- **Database backups** with point-in-time recovery
- **File storage** backups and versioning
- **Configuration management** with version control
- **Disaster recovery** procedures and documentation

---

## 📚 Additional Resources

- [Forum API Documentation](api/README.md)
- [WebSocket Event Reference](docs/websocket.md)
- [Moderation Guidelines](docs/moderation.md)
- [BCM Knowledge Categories](docs/categories.md)
