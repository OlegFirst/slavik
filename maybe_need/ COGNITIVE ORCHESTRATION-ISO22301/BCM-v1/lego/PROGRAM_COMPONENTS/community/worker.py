#!/usr/bin/env python3
"""
BCM Community Forum Background Worker
Handles background tasks for the forum service
"""

import asyncio
import os
import logging
from typing import Dict, Any
import json
from datetime import datetime, timedelta

import redis
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import aiohttp
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class ForumWorker:
    """Background worker for forum tasks"""
    
    def __init__(self):
        self.redis_client = redis.from_url(os.getenv('REDIS_URL'))
        self.database_url = os.getenv('DATABASE_URL')
        self.bcm_api_url = os.getenv('BCM_API_URL')
        self.bcm_api_key = os.getenv('BCM_API_KEY')
        self.concurrency = int(os.getenv('WORKER_CONCURRENCY', 2))
        
        # Create async database engine
        self.db_engine = create_async_engine(self.database_url)
        self.AsyncSessionLocal = sessionmaker(
            self.db_engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Task handlers
        self.task_handlers = {
            'send_notification': self.send_notification,
            'update_reputation': self.update_reputation,
            'generate_digest': self.generate_digest,
            'sync_user_data': self.sync_user_data,
            'cleanup_old_data': self.cleanup_old_data,
            'update_search_index': self.update_search_index,
            'process_mentions': self.process_mentions,
            'send_digest_email': self.send_digest_email
        }

    async def start(self):
        """Start the worker"""
        logger.info("Starting BCM Forum Worker", concurrency=self.concurrency)
        
        # Create worker tasks
        tasks = []
        for i in range(self.concurrency):
            task = asyncio.create_task(self.worker_loop(f"worker-{i}"))
            tasks.append(task)
        
        # Schedule periodic tasks
        periodic_task = asyncio.create_task(self.periodic_tasks())
        tasks.append(periodic_task)
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Shutting down worker...")
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

    async def worker_loop(self, worker_id: str):
        """Main worker loop"""
        logger.info("Worker started", worker_id=worker_id)
        
        while True:
            try:
                # Get task from Redis queue
                task_data = self.redis_client.brpop(['forum:tasks'], timeout=5)
                
                if task_data:
                    queue_name, task_json = task_data
                    task = json.loads(task_json)
                    
                    task_type = task.get('type')
                    task_id = task.get('id')
                    
                    logger.info("Processing task", 
                              worker_id=worker_id, 
                              task_type=task_type, 
                              task_id=task_id)
                    
                    # Execute task
                    if task_type in self.task_handlers:
                        try:
                            await self.task_handlers[task_type](task.get('data', {}))
                            logger.info("Task completed", 
                                      worker_id=worker_id, 
                                      task_type=task_type, 
                                      task_id=task_id)
                        except Exception as e:
                            logger.error("Task failed", 
                                       worker_id=worker_id, 
                                       task_type=task_type, 
                                       task_id=task_id, 
                                       error=str(e))
                            
                            # Retry logic could be added here
                            await self.handle_failed_task(task, str(e))
                    else:
                        logger.warning("Unknown task type", 
                                     worker_id=worker_id, 
                                     task_type=task_type)
                
            except Exception as e:
                logger.error("Worker loop error", worker_id=worker_id, error=str(e))
                await asyncio.sleep(1)

    async def periodic_tasks(self):
        """Run periodic maintenance tasks"""
        logger.info("Starting periodic tasks")
        
        while True:
            try:
                current_hour = datetime.now().hour
                
                # Run daily digest at 8 AM
                if current_hour == 8:
                    await self.schedule_digest_generation()
                
                # Run cleanup at 2 AM
                if current_hour == 2:
                    await self.schedule_cleanup_tasks()
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error("Periodic tasks error", error=str(e))
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def send_notification(self, data: Dict[str, Any]):
        """Send notification to user"""
        user_id = data.get('user_id')
        notification_type = data.get('type')
        message = data.get('message')
        metadata = data.get('metadata', {})
        
        async with self.AsyncSessionLocal() as session:
            # Insert notification into database
            query = text("""
                INSERT INTO notifications (user_id, type, message, metadata, created_at)
                VALUES (:user_id, :type, :message, :metadata, NOW())
            """)
            await session.execute(query, {
                'user_id': user_id,
                'type': notification_type,
                'message': message,
                'metadata': json.dumps(metadata)
            })
            await session.commit()
        
        # Send real-time notification via WebSocket (if user is online)
        await self.send_realtime_notification(user_id, {
            'type': notification_type,
            'message': message,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        })

    async def send_realtime_notification(self, user_id: str, notification: Dict[str, Any]):
        """Send real-time notification via WebSocket"""
        try:
            # Store in Redis for WebSocket handler to pick up
            channel = f"user:{user_id}:notifications"
            await self.redis_client.publish(channel, json.dumps(notification))
        except Exception as e:
            logger.warning("Failed to send real-time notification", 
                         user_id=user_id, error=str(e))

    async def update_reputation(self, data: Dict[str, Any]):
        """Update user reputation based on activity"""
        user_id = data.get('user_id')
        action = data.get('action')
        points = data.get('points', 0)
        
        async with self.AsyncSessionLocal() as session:
            # Update user reputation
            query = text("""
                UPDATE forum_users 
                SET reputation = reputation + :points,
                    updated_at = NOW()
                WHERE id = :user_id
            """)
            await session.execute(query, {
                'user_id': user_id,
                'points': points
            })
            
            # Log reputation change
            log_query = text("""
                INSERT INTO user_reputation_log (user_id, action, points, created_at)
                VALUES (:user_id, :action, :points, NOW())
            """)
            await session.execute(log_query, {
                'user_id': user_id,
                'action': action,
                'points': points
            })
            
            await session.commit()
        
        logger.info("Reputation updated", 
                   user_id=user_id, 
                   action=action, 
                   points=points)

    async def generate_digest(self, data: Dict[str, Any]):
        """Generate daily digest for users"""
        digest_date = data.get('date', datetime.now().date().isoformat())
        
        async with self.AsyncSessionLocal() as session:
            # Get active topics from the last 24 hours
            query = text("""
                SELECT t.id, t.title, t.created_by, u.username,
                       COUNT(p.id) as post_count,
                       MAX(p.created_at) as last_activity
                FROM topics t
                JOIN forum_users u ON t.created_by = u.id
                LEFT JOIN posts p ON t.id = p.topic_id
                WHERE t.created_at >= NOW() - INTERVAL '24 hours'
                   OR p.created_at >= NOW() - INTERVAL '24 hours'
                GROUP BY t.id, t.title, t.created_by, u.username
                ORDER BY last_activity DESC, post_count DESC
                LIMIT 10
            """)
            result = await session.execute(query)
            active_topics = result.fetchall()
            
            # Get new users
            user_query = text("""
                SELECT username, created_at
                FROM forum_users
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                ORDER BY created_at DESC
                LIMIT 5
            """)
            result = await session.execute(user_query)
            new_users = result.fetchall()
        
        # Create digest content
        digest_content = {
            'date': digest_date,
            'active_topics': [dict(row) for row in active_topics],
            'new_users': [dict(row) for row in new_users],
            'generated_at': datetime.now().isoformat()
        }
        
        # Store digest
        await self.store_digest(digest_content)
        
        # Schedule email sending for subscribed users
        await self.schedule_digest_emails(digest_content)

    async def store_digest(self, digest_content: Dict[str, Any]):
        """Store digest in database"""
        async with self.AsyncSessionLocal() as session:
            query = text("""
                INSERT INTO daily_digests (date, content, created_at)
                VALUES (:date, :content, NOW())
                ON CONFLICT (date) DO UPDATE SET
                    content = :content,
                    updated_at = NOW()
            """)
            await session.execute(query, {
                'date': digest_content['date'],
                'content': json.dumps(digest_content)
            })
            await session.commit()

    async def schedule_digest_emails(self, digest_content: Dict[str, Any]):
        """Schedule digest emails for subscribed users"""
        async with self.AsyncSessionLocal() as session:
            query = text("""
                SELECT id, email, username
                FROM forum_users
                WHERE email_notifications = true
                  AND email IS NOT NULL
                  AND is_active = true
            """)
            result = await session.execute(query)
            users = result.fetchall()
        
        # Schedule email task for each user
        for user in users:
            email_task = {
                'type': 'send_digest_email',
                'id': f"digest_email_{user.id}_{digest_content['date']}",
                'data': {
                    'user_id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'digest_content': digest_content
                }
            }
            self.redis_client.lpush('forum:tasks', json.dumps(email_task))

    async def send_digest_email(self, data: Dict[str, Any]):
        """Send digest email to user"""
        # Email sending would be implemented here
        # For now, just log the action
        logger.info("Digest email scheduled", 
                   user_id=data.get('user_id'),
                   email=data.get('email'))

    async def sync_user_data(self, data: Dict[str, Any]):
        """Sync user data with BCM platform"""
        if not self.bcm_api_url or not self.bcm_api_key:
            return
        
        user_id = data.get('user_id')
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {self.bcm_api_key}'}
                async with session.get(
                    f"{self.bcm_api_url}/api/users/{user_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        await self.update_user_profile(user_id, user_data)
        
        except Exception as e:
            logger.error("User sync failed", user_id=user_id, error=str(e))

    async def update_user_profile(self, user_id: str, user_data: Dict[str, Any]):
        """Update user profile with BCM data"""
        async with self.AsyncSessionLocal() as session:
            query = text("""
                UPDATE forum_users SET
                    full_name = :full_name,
                    company_id = :company_id,
                    department = :department,
                    updated_at = NOW()
                WHERE id = :user_id
            """)
            await session.execute(query, {
                'user_id': user_id,
                'full_name': user_data.get('name'),
                'company_id': user_data.get('company_id'),
                'department': user_data.get('department')
            })
            await session.commit()

    async def cleanup_old_data(self, data: Dict[str, Any]):
        """Clean up old data"""
        days_to_keep = data.get('days', 90)
        
        async with self.AsyncSessionLocal() as session:
            # Clean old notifications
            query = text("""
                DELETE FROM notifications
                WHERE created_at < NOW() - INTERVAL :days DAY
                  AND read_at IS NOT NULL
            """)
            result = await session.execute(query, {'days': days_to_keep})
            
            # Clean old digests
            digest_query = text("""
                DELETE FROM daily_digests
                WHERE created_at < NOW() - INTERVAL :days DAY
            """)
            await session.execute(digest_query, {'days': days_to_keep})
            
            await session.commit()
            
            logger.info("Cleanup completed", 
                       deleted_notifications=result.rowcount,
                       days_kept=days_to_keep)

    async def update_search_index(self, data: Dict[str, Any]):
        """Update search index for content"""
        # Elasticsearch integration would be implemented here
        content_type = data.get('content_type')
        content_id = data.get('content_id')
        
        logger.info("Search index update", 
                   content_type=content_type,
                   content_id=content_id)

    async def process_mentions(self, data: Dict[str, Any]):
        """Process @mentions in posts"""
        post_id = data.get('post_id')
        mentioned_users = data.get('mentioned_users', [])
        author_id = data.get('author_id')
        
        for user_id in mentioned_users:
            # Send mention notification
            await self.send_notification({
                'user_id': user_id,
                'type': 'mention',
                'message': f'You were mentioned in a post',
                'metadata': {
                    'post_id': post_id,
                    'author_id': author_id
                }
            })

    async def schedule_digest_generation(self):
        """Schedule daily digest generation"""
        task = {
            'type': 'generate_digest',
            'id': f"daily_digest_{datetime.now().date().isoformat()}",
            'data': {
                'date': datetime.now().date().isoformat()
            }
        }
        self.redis_client.lpush('forum:tasks', json.dumps(task))
        logger.info("Daily digest scheduled")

    async def schedule_cleanup_tasks(self):
        """Schedule cleanup tasks"""
        task = {
            'type': 'cleanup_old_data',
            'id': f"cleanup_{datetime.now().date().isoformat()}",
            'data': {
                'days': 90
            }
        }
        self.redis_client.lpush('forum:tasks', json.dumps(task))
        logger.info("Cleanup task scheduled")

    async def handle_failed_task(self, task: Dict[str, Any], error: str):
        """Handle failed task"""
        # Store failed task for debugging
        failed_task = {
            'original_task': task,
            'error': error,
            'failed_at': datetime.now().isoformat()
        }
        
        self.redis_client.lpush('forum:failed_tasks', json.dumps(failed_task))
        logger.error("Task stored in failed queue", task_id=task.get('id'))


async def main():
    """Main worker entry point"""
    worker = ForumWorker()
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
