# -*- coding: utf-8 -*-
"""
Community Forum Service for BCM Platform
Knowledge sharing, discussion forums, and community features for BCM professionals
"""
import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
import hashlib
import structlog
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr
import uvicorn
import asyncpg
import aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import bleach
import markdown
from markdown.extensions import codehilite, tables, toc
import re
import json

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Enums for forum system
class ForumCategory(str, Enum):
    GENERAL = "general"
    BCM_POLICY = "bcm_policy"
    RISK_MANAGEMENT = "risk_management"
    BUSINESS_IMPACT = "business_impact"
    CONTINUITY_PLANNING = "continuity_planning"
    INCIDENT_RESPONSE = "incident_response"
    EXERCISES_TESTING = "exercises_testing"
    COMPLIANCE = "compliance"
    TECHNOLOGY = "technology"
    CASE_STUDIES = "case_studies"
    ANNOUNCEMENTS = "announcements"
    Q_AND_A = "q_and_a"

class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"
    MODERATED = "moderated"

class UserRole(str, Enum):
    MEMBER = "member"
    MODERATOR = "moderator"
    EXPERT = "expert"
    ADMIN = "admin"
    BCM_COORDINATOR = "bcm_coordinator"

class ReactionType(str, Enum):
    LIKE = "like"
    HELPFUL = "helpful"
    INSIGHTFUL = "insightful"
    AGREE = "agree"
    DISAGREE = "disagree"

# Pydantic models
class User(BaseModel):
    id: str
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    company_id: str
    role: UserRole = UserRole.MEMBER
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    reputation_score: int = 0
    join_date: datetime
    last_activity: Optional[datetime] = None
    is_verified: bool = False
    certifications: List[str] = []

class Category(BaseModel):
    id: str
    name: str
    description: str
    category_type: ForumCategory
    parent_id: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    post_count: int = 0
    is_private: bool = False
    allowed_roles: List[UserRole] = []
    moderators: List[str] = []

class Topic(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category_id: str
    author_id: str
    status: PostStatus = PostStatus.PUBLISHED
    is_pinned: bool = False
    is_locked: bool = False
    tags: List[str] = []
    post_count: int = 0
    view_count: int = 0
    reaction_count: Dict[str, int] = {}
    created_at: datetime
    updated_at: datetime
    last_post_at: Optional[datetime] = None
    last_post_author: Optional[str] = None

class Post(BaseModel):
    id: str
    topic_id: str
    author_id: str
    content: str
    content_html: str
    status: PostStatus = PostStatus.PUBLISHED
    is_solution: bool = False
    parent_post_id: Optional[str] = None
    attachments: List[Dict[str, Any]] = []
    reactions: Dict[str, int] = {}
    edited_at: Optional[datetime] = None
    edited_by: Optional[str] = None
    created_at: datetime

class TopicRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category_id: str
    content: str = Field(..., min_length=10, max_length=50000)
    tags: List[str] = Field(default=[], max_items=10)
    is_question: bool = False

class PostRequest(BaseModel):
    topic_id: str
    content: str = Field(..., min_length=5, max_length=50000)
    parent_post_id: Optional[str] = None
    attachments: List[Dict[str, Any]] = []

class ReactionRequest(BaseModel):
    target_id: str  # topic or post ID
    target_type: str  # 'topic' or 'post'
    reaction_type: ReactionType

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3)
    category_id: Optional[str] = None
    tags: List[str] = []
    author_id: Optional[str] = None
    date_range: Optional[Dict[str, str]] = None
    sort_by: str = "relevance"  # relevance, date, popularity
    limit: int = Field(20, le=100)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, topic_id: Optional[str] = None):
        await websocket.accept()
        
        # Store user connection
        self.user_connections[user_id] = websocket
        
        # Store topic-specific connection
        if topic_id:
            if topic_id not in self.active_connections:
                self.active_connections[topic_id] = []
            self.active_connections[topic_id].append(websocket)
        
        logger.info(f"User {user_id} connected to topic {topic_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: str, topic_id: Optional[str] = None):
        # Remove user connection
        if user_id in self.user_connections:
            del self.user_connections[user_id]
        
        # Remove from topic connections
        if topic_id and topic_id in self.active_connections:
            if websocket in self.active_connections[topic_id]:
                self.active_connections[topic_id].remove(websocket)
            if not self.active_connections[topic_id]:
                del self.active_connections[topic_id]
        
        logger.info(f"User {user_id} disconnected from topic {topic_id}")
    
    async def send_to_topic(self, topic_id: str, message: dict):
        if topic_id in self.active_connections:
            message_json = json.dumps(message)
            disconnected = []
            
            for websocket in self.active_connections[topic_id]:
                try:
                    await websocket.send_text(message_json)
                except:
                    disconnected.append(websocket)
            
            # Remove disconnected websockets
            for ws in disconnected:
                self.active_connections[topic_id].remove(ws)
    
    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.user_connections:
            try:
                message_json = json.dumps(message)
                await self.user_connections[user_id].send_text(message_json)
            except:
                del self.user_connections[user_id]

class ForumService:
    """BCM Community Forum Service"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.markdown_processor = self._setup_markdown()
        
        # BCM-specific content patterns
        self.bcm_tags = [
            "iso22301", "business-continuity", "risk-management", "bia",
            "disaster-recovery", "incident-response", "crisis-management",
            "continuity-planning", "resilience", "emergency-preparedness"
        ]
        
        # Content moderation settings
        self.allowed_html_tags = [
            'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'blockquote',
            'code', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'img'
        ]
        self.allowed_html_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'code': ['class'],
            'pre': ['class']
        }
    
    def _setup_markdown(self):
        """Setup markdown processor with extensions"""
        return markdown.Markdown(extensions=[
            'codehilite',
            'tables',
            'toc',
            'fenced_code',
            'nl2br',
            'sane_lists'
        ])
    
    def process_content(self, raw_content: str) -> str:
        """Process and sanitize forum content"""
        # Convert markdown to HTML
        html_content = self.markdown_processor.convert(raw_content)
        
        # Sanitize HTML
        clean_html = bleach.clean(
            html_content,
            tags=self.allowed_html_tags,
            attributes=self.allowed_html_attributes,
            strip=True
        )
        
        return clean_html
    
    def extract_mentions(self, content: str) -> List[str]:
        """Extract @mentions from content"""
        mention_pattern = r'@([a-zA-Z0-9_]+)'
        mentions = re.findall(mention_pattern, content)
        return mentions
    
    def extract_hashtags(self, content: str) -> List[str]:
        """Extract #hashtags from content"""
        hashtag_pattern = r'#([a-zA-Z0-9_]+)'
        hashtags = re.findall(hashtag_pattern, content)
        return hashtags
    
    def calculate_reputation_change(self, action: str, target_type: str) -> int:
        """Calculate reputation score change based on action"""
        reputation_changes = {
            'post_created': 2,
            'post_liked': 1,
            'post_helpful': 5,
            'solution_accepted': 15,
            'topic_created': 5,
            'expert_answer': 10,
            'moderation_action': -5
        }
        return reputation_changes.get(action, 0)
    
    async def notify_users(self, user_ids: List[str], notification: Dict[str, Any]):
        """Send notifications to users"""
        for user_id in user_ids:
            await self.connection_manager.send_to_user(user_id, {
                "type": "notification",
                "data": notification
            })
    
    async def update_user_activity(self, user_id: str):
        """Update user's last activity timestamp"""
        # This would update the database
        pass
    
    def generate_topic_slug(self, title: str) -> str:
        """Generate URL-friendly slug from topic title"""
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')

# Global variables
redis_client: Optional[aioredis.Redis] = None
db_engine = None
forum_service = ForumService()

# Security
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key for requests"""
    expected_key = os.getenv('FORUM_API_KEY')
    if not expected_key or credentials.credentials != expected_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return credentials.credentials

# FastAPI app
app = FastAPI(
    title="BCM Community Forum Service",
    description="Knowledge sharing and discussion platform for BCM professionals",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global redis_client, db_engine
    
    logger.info("Initializing BCM Community Forum Service")
    
    # Initialize Redis
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    try:
        redis_client = aioredis.from_url(redis_url)
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
    
    # Initialize Database
    db_url = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/forum')
    try:
        db_engine = create_async_engine(db_url)
        logger.info("Database connection established")
    except Exception as e:
        logger.warning(f"Database connection failed: {e}")
    
    logger.info("BCM Community Forum Service initialized")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "redis": redis_client is not None,
            "database": db_engine is not None
        },
        "active_connections": len(forum_service.connection_manager.user_connections)
    }

@app.get("/api/v1/categories")
async def get_categories(
    company_id: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Get forum categories"""
    try:
        # Mock data - in production this would query the database
        categories = [
            {
                "id": "general",
                "name": "General Discussion",
                "description": "General BCM topics and discussions",
                "category_type": "general",
                "post_count": 145,
                "icon": "forum",
                "color": "#2196F3"
            },
            {
                "id": "bcm_policy",
                "name": "BCM Policy & Governance",
                "description": "Discussions about BCM policies, frameworks, and governance",
                "category_type": "bcm_policy",
                "post_count": 89,
                "icon": "policy",
                "color": "#4CAF50"
            },
            {
                "id": "risk_mgmt",
                "name": "Risk Management",
                "description": "Risk assessment, threat analysis, and mitigation strategies",
                "category_type": "risk_management",
                "post_count": 156,
                "icon": "warning",
                "color": "#FF9800"
            },
            {
                "id": "case_studies",
                "name": "Case Studies",
                "description": "Real-world BCM implementations and lessons learned",
                "category_type": "case_studies",
                "post_count": 78,
                "icon": "case_study",
                "color": "#9C27B0"
            }
        ]
        
        return {
            "categories": categories,
            "total": len(categories)
        }
        
    except Exception as e:
        logger.error(f"Failed to get categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/topics")
async def create_topic(
    request: TopicRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Create new forum topic"""
    try:
        # Generate topic ID and slug
        topic_id = str(uuid.uuid4())
        slug = forum_service.generate_topic_slug(request.title)
        
        # Process content
        content_html = forum_service.process_content(request.content)
        
        # Extract mentions and hashtags
        mentions = forum_service.extract_mentions(request.content)
        hashtags = forum_service.extract_hashtags(request.content)
        
        # Create topic (mock response)
        topic = {
            "id": topic_id,
            "title": request.title,
            "slug": slug,
            "description": request.description,
            "category_id": request.category_id,
            "author_id": "current_user_id",  # Should come from auth
            "content": request.content,
            "content_html": content_html,
            "tags": request.tags + hashtags,
            "mentions": mentions,
            "is_question": request.is_question,
            "post_count": 1,
            "view_count": 0,
            "created_at": datetime.now().isoformat(),
            "status": "published"
        }
        
        # Process in background
        background_tasks.add_task(
            _process_new_topic_task,
            topic,
            mentions
        )
        
        return {
            "status": "created",
            "topic": topic
        }
        
    except Exception as e:
        logger.error(f"Failed to create topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/topics")
async def get_topics(
    category_id: Optional[str] = None,
    tag: Optional[str] = None,
    author_id: Optional[str] = None,
    status: PostStatus = PostStatus.PUBLISHED,
    sort_by: str = "latest",
    page: int = 1,
    limit: int = 20,
    api_key: str = Depends(verify_api_key)
):
    """Get forum topics with filtering"""
    try:
        # Mock data - in production this would query the database
        topics = [
            {
                "id": "topic-1",
                "title": "Best practices for ISO 22301 implementation",
                "slug": "best-practices-iso-22301-implementation",
                "category_id": "bcm_policy",
                "author": {
                    "id": "user-1",
                    "username": "bcm_expert",
                    "reputation": 1250
                },
                "post_count": 15,
                "view_count": 234,
                "last_activity": "2024-01-15T14:30:00Z",
                "tags": ["iso22301", "implementation", "best-practices"],
                "is_pinned": True,
                "reactions": {"helpful": 12, "like": 8}
            },
            {
                "id": "topic-2", 
                "title": "Business Impact Analysis automation tools",
                "slug": "bia-automation-tools",
                "category_id": "risk_mgmt",
                "author": {
                    "id": "user-2",
                    "username": "risk_analyst",
                    "reputation": 890
                },
                "post_count": 8,
                "view_count": 156,
                "last_activity": "2024-01-15T12:15:00Z",
                "tags": ["bia", "automation", "tools"],
                "is_question": True,
                "reactions": {"like": 6, "insightful": 3}
            }
        ]
        
        # Apply filtering (mock implementation)
        if category_id:
            topics = [t for t in topics if t["category_id"] == category_id]
        if tag:
            topics = [t for t in topics if tag in t["tags"]]
        
        return {
            "topics": topics,
            "total": len(topics),
            "page": page,
            "limit": limit,
            "has_next": False
        }
        
    except Exception as e:
        logger.error(f"Failed to get topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/topics/{topic_id}")
async def get_topic(
    topic_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get topic details with posts"""
    try:
        # Mock topic data
        topic = {
            "id": topic_id,
            "title": "Best practices for ISO 22301 implementation",
            "slug": "best-practices-iso-22301-implementation", 
            "description": "Discussion about effective ISO 22301 implementation strategies",
            "category_id": "bcm_policy",
            "author": {
                "id": "user-1",
                "username": "bcm_expert",
                "first_name": "John",
                "last_name": "Expert",
                "reputation": 1250,
                "role": "expert"
            },
            "content_html": "<p>What are the most effective strategies for implementing ISO 22301 in medium-sized organizations?</p>",
            "tags": ["iso22301", "implementation", "best-practices"],
            "post_count": 15,
            "view_count": 235,
            "created_at": "2024-01-10T09:00:00Z",
            "last_activity": "2024-01-15T14:30:00Z",
            "is_pinned": True,
            "is_locked": False,
            "reactions": {"helpful": 12, "like": 8, "insightful": 5}
        }
        
        # Mock posts data
        posts = [
            {
                "id": "post-1",
                "author": {
                    "id": "user-2",
                    "username": "compliance_pro",
                    "reputation": 750,
                    "role": "moderator"
                },
                "content_html": "<p>Great question! Here are my top 5 recommendations...</p>",
                "is_solution": True,
                "reactions": {"helpful": 8, "like": 5},
                "created_at": "2024-01-10T10:30:00Z"
            }
        ]
        
        # Increment view count (would be done in background)
        topic["view_count"] += 1
        
        return {
            "topic": topic,
            "posts": posts,
            "total_posts": len(posts)
        }
        
    except Exception as e:
        logger.error(f"Failed to get topic {topic_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/posts")
async def create_post(
    request: PostRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Create new post in topic"""
    try:
        post_id = str(uuid.uuid4())
        content_html = forum_service.process_content(request.content)
        mentions = forum_service.extract_mentions(request.content)
        
        post = {
            "id": post_id,
            "topic_id": request.topic_id,
            "author_id": "current_user_id",  # Should come from auth
            "content": request.content,
            "content_html": content_html,
            "parent_post_id": request.parent_post_id,
            "attachments": request.attachments,
            "mentions": mentions,
            "reactions": {},
            "created_at": datetime.now().isoformat()
        }
        
        # Process in background
        background_tasks.add_task(
            _process_new_post_task,
            post,
            mentions
        )
        
        # Notify topic subscribers via WebSocket
        await forum_service.connection_manager.send_to_topic(
            request.topic_id,
            {
                "type": "new_post",
                "data": post
            }
        )
        
        return {
            "status": "created",
            "post": post
        }
        
    except Exception as e:
        logger.error(f"Failed to create post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/reactions")
async def add_reaction(
    request: ReactionRequest,
    api_key: str = Depends(verify_api_key)
):
    """Add reaction to topic or post"""
    try:
        # Mock implementation
        result = {
            "target_id": request.target_id,
            "target_type": request.target_type,
            "reaction_type": request.reaction_type,
            "user_id": "current_user_id",
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast reaction via WebSocket if it's a post reaction
        if request.target_type == "post":
            # Get topic_id for the post (mock)
            topic_id = "topic-1"
            await forum_service.connection_manager.send_to_topic(
                topic_id,
                {
                    "type": "reaction_added",
                    "data": result
                }
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to add reaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/search")
async def search_forum(
    request: SearchRequest,
    api_key: str = Depends(verify_api_key)
):
    """Search forum content"""
    try:
        # Mock search results
        results = [
            {
                "type": "topic",
                "id": "topic-1",
                "title": "Best practices for ISO 22301 implementation",
                "snippet": "What are the most effective strategies for implementing ISO 22301...",
                "category": "BCM Policy & Governance",
                "author": "bcm_expert",
                "created_at": "2024-01-10T09:00:00Z",
                "relevance_score": 0.95
            },
            {
                "type": "post",
                "id": "post-5",
                "topic_title": "BCP template sharing",
                "snippet": "Here's a comprehensive BCP template that covers ISO 22301 requirements...",
                "author": "template_guru",
                "created_at": "2024-01-12T15:20:00Z",
                "relevance_score": 0.87
            }
        ]
        
        return {
            "query": request.query,
            "results": results,
            "total": len(results),
            "search_time": 0.045
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{topic_id}")
async def websocket_endpoint(websocket: WebSocket, topic_id: str):
    """WebSocket endpoint for real-time topic updates"""
    user_id = "current_user_id"  # Should come from auth
    
    await forum_service.connection_manager.connect(websocket, user_id, topic_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "typing":
                # Broadcast typing indicator
                await forum_service.connection_manager.send_to_topic(
                    topic_id,
                    {
                        "type": "user_typing",
                        "user_id": user_id,
                        "username": message.get("username")
                    }
                )
            elif message.get("type") == "ping":
                # Respond to ping
                await websocket.send_text(json.dumps({"type": "pong"}))
                
    except WebSocketDisconnect:
        forum_service.connection_manager.disconnect(websocket, user_id, topic_id)

@app.get("/api/v1/users/{user_id}/profile")
async def get_user_profile(
    user_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get user profile information"""
    try:
        # Mock user profile
        profile = {
            "id": user_id,
            "username": "bcm_expert",
            "first_name": "John",
            "last_name": "Expert", 
            "bio": "BCM consultant with 10+ years experience in ISO 22301 implementation",
            "company": "BCM Consulting Ltd",
            "role": "expert",
            "reputation_score": 1250,
            "join_date": "2023-03-15T00:00:00Z",
            "last_activity": "2024-01-15T14:30:00Z",
            "certifications": ["CBCP", "MBCI", "ISO 22301 Lead Auditor"],
            "stats": {
                "topics_created": 25,
                "posts_created": 156,
                "solutions_provided": 18,
                "helpful_reactions": 89
            },
            "badges": [
                {"name": "BCM Expert", "icon": "expert", "color": "#gold"},
                {"name": "Helpful Contributor", "icon": "helpful", "color": "#blue"}
            ]
        }
        
        return profile
        
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background tasks
async def _process_new_topic_task(topic: Dict[str, Any], mentions: List[str]):
    """Background task to process new topic"""
    try:
        # Update reputation
        # Send notifications to mentioned users
        # Update search index
        # Update category post count
        logger.info(f"Processed new topic: {topic['id']}")
    except Exception as e:
        logger.error(f"Failed to process new topic: {e}")

async def _process_new_post_task(post: Dict[str, Any], mentions: List[str]):
    """Background task to process new post"""
    try:
        # Update reputation
        # Send notifications to mentioned users and topic followers
        # Update search index
        # Update topic post count
        logger.info(f"Processed new post: {post['id']}")
    except Exception as e:
        logger.error(f"Failed to process new post: {e}")

if __name__ == "__main__":
    port = int(os.getenv('PORT', '8003'))
    host = os.getenv('HOST', '0.0.0.0')
    log_level = os.getenv('LOG_LEVEL', 'info').lower()
    
    uvicorn.run(
        "forum_service:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=False
    )
