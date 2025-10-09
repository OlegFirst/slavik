"""
Consultation Session Pattern - Extracted from Odoo bcm_ai_consultant

Multi-turn conversation management for AI consultations with:
- Session lifecycle management (draft → active → completed)
- Message history tracking
- Context preservation across conversations
- User feedback and ratings
- Session analytics
- Export capabilities

Original Source: bcm_ai_consultant/models/consultation_session.py
Extracted: 2025-10-05
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


# ========== Enums ==========

class SessionState(Enum):
    """Consultation session states"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class MessageType(Enum):
    """Types of messages in conversation"""
    USER = "user"
    AI = "ai"
    SYSTEM = "system"


class ContextType(Enum):
    """Consultation context types"""
    GENERAL = "general"
    RISK_ASSESSMENT = "risk_assessment"
    BCP_DEVELOPMENT = "bcp_development"
    INCIDENT_RESPONSE = "incident_response"
    COMPLIANCE = "compliance"
    TRAINING = "training"


class ExportFormat(Enum):
    """Export format options"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    JSON = "json"


# ========== Data Models ==========

@dataclass
class ConsultationMessage:
    """
    Single message in consultation

    Represents one turn in the conversation
    """
    id: str
    session_id: str
    message_type: MessageType
    content: str
    sender: str

    # AI-specific fields
    confidence: Optional[float] = None  # 0.0 - 1.0
    metadata: Optional[Dict[str, Any]] = None

    # User feedback
    is_helpful: Optional[bool] = None
    user_rating: Optional[int] = None  # 1-3

    # System
    sequence: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ConsultationSession:
    """
    Consultation session with AI

    Manages multi-turn conversation with context preservation
    """
    id: str
    name: str
    consultant_id: str  # Which AI colleague is consulting
    client_id: str  # Organization/user being consulted

    # Session state
    state: SessionState = SessionState.DRAFT
    topic: Optional[str] = None
    context_type: ContextType = ContextType.GENERAL

    # Messages
    messages: List[ConsultationMessage] = field(default_factory=list)

    # Feedback
    rating: Optional[int] = None  # 1-5
    feedback: Optional[str] = None

    # Analytics
    message_count: int = 0
    duration_minutes: float = 0.0

    # Timestamps
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


# ========== Session Manager ==========

class ConsultationSessionManager:
    """
    Manages consultation sessions

    Handles session lifecycle, message history, and context
    """

    def __init__(self):
        self.sessions: Dict[str, ConsultationSession] = {}

    def create_session(
        self,
        session_id: str,
        consultant_id: str,
        client_id: str,
        topic: Optional[str] = None,
        context_type: ContextType = ContextType.GENERAL
    ) -> ConsultationSession:
        """Create new consultation session"""
        session = ConsultationSession(
            id=session_id,
            name=f"Консультация {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            consultant_id=consultant_id,
            client_id=client_id,
            topic=topic,
            context_type=context_type
        )

        self.sessions[session_id] = session
        logger.info(f"Created consultation session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[ConsultationSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)

    def start_session(self, session_id: str):
        """Start a session (draft → active)"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.state = SessionState.ACTIVE
        session.start_date = datetime.now()
        session.updated_at = datetime.now()

        logger.info(f"Started session: {session_id}")

    def complete_session(self, session_id: str):
        """Complete a session (active → completed)"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.state = SessionState.COMPLETED
        session.end_date = datetime.now()

        # Calculate duration
        if session.start_date:
            delta = session.end_date - session.start_date
            session.duration_minutes = delta.total_seconds() / 60

        session.updated_at = datetime.now()
        logger.info(f"Completed session: {session_id}, duration: {session.duration_minutes:.1f} min")

    def add_message(
        self,
        session_id: str,
        message_type: MessageType,
        content: str,
        sender: str,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConsultationMessage:
        """Add message to session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        message = ConsultationMessage(
            id=f"{session_id}_msg_{len(session.messages) + 1}",
            session_id=session_id,
            message_type=message_type,
            content=content,
            sender=sender,
            confidence=confidence,
            metadata=metadata,
            sequence=len(session.messages)
        )

        session.messages.append(message)
        session.message_count = len(session.messages)
        session.updated_at = datetime.now()

        return message

    def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[ConsultationMessage]:
        """Get conversation history for context"""
        session = self.get_session(session_id)
        if not session:
            return []

        messages = session.messages.copy()
        if limit:
            messages = messages[-limit:]

        return messages

    def add_feedback(
        self,
        session_id: str,
        rating: int,
        feedback: Optional[str] = None
    ):
        """Add user feedback to session"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.rating = rating
        session.feedback = feedback
        session.updated_at = datetime.now()

        logger.info(f"Added feedback to session {session_id}: {rating}/5")

    def rate_message(
        self,
        session_id: str,
        message_id: str,
        is_helpful: bool,
        rating: Optional[int] = None
    ):
        """Rate a specific AI message"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        message = next((m for m in session.messages if m.id == message_id), None)
        if not message:
            raise ValueError(f"Message {message_id} not found")

        message.is_helpful = is_helpful
        if rating:
            message.user_rating = rating

        session.updated_at = datetime.now()


# ========== Session Context Builder ==========

class SessionContextBuilder:
    """
    Builds context for AI from session history

    Provides conversation context to AI for coherent responses
    """

    def __init__(self, session_manager: ConsultationSessionManager):
        self.session_manager = session_manager

    def build_context(
        self,
        session_id: str,
        include_messages: int = 10
    ) -> Dict[str, Any]:
        """
        Build full context for AI consultation

        Args:
            session_id: Session to build context for
            include_messages: Number of recent messages to include

        Returns:
            Context dict with session info and conversation history
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Get recent conversation history
        recent_messages = self.session_manager.get_conversation_history(
            session_id,
            limit=include_messages
        )

        # Build context
        context = {
            'session_id': session.id,
            'client_id': session.client_id,
            'topic': session.topic,
            'context_type': session.context_type.value,
            'message_count': session.message_count,
            'duration_minutes': session.duration_minutes,
            'conversation_history': [
                {
                    'role': msg.message_type.value,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat(),
                    'confidence': msg.confidence
                }
                for msg in recent_messages
            ]
        }

        return context

    def format_for_llm(
        self,
        session_id: str,
        new_user_message: str,
        system_prompt: str
    ) -> List[Dict[str, str]]:
        """
        Format session context as LLM messages

        Args:
            session_id: Session ID
            new_user_message: New message from user
            system_prompt: System prompt for AI

        Returns:
            List of messages in LLM format
        """
        context = self.build_context(session_id)

        messages = [
            {'role': 'system', 'content': system_prompt}
        ]

        # Add conversation history
        for msg in context['conversation_history']:
            role = 'assistant' if msg['role'] == 'ai' else 'user'
            messages.append({
                'role': role,
                'content': msg['content']
            })

        # Add new user message
        messages.append({
            'role': 'user',
            'content': new_user_message
        })

        return messages


# ========== Session Analytics ==========

class SessionAnalytics:
    """
    Analytics for consultation sessions

    Tracks metrics and insights
    """

    @staticmethod
    def calculate_session_metrics(session: ConsultationSession) -> Dict[str, Any]:
        """Calculate session metrics"""
        ai_messages = [m for m in session.messages if m.message_type == MessageType.AI]
        user_messages = [m for m in session.messages if m.message_type == MessageType.USER]

        # Average AI confidence
        confidences = [m.confidence for m in ai_messages if m.confidence is not None]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Helpful messages
        rated_messages = [m for m in ai_messages if m.is_helpful is not None]
        helpful_count = sum(1 for m in rated_messages if m.is_helpful)

        return {
            'total_messages': session.message_count,
            'ai_messages': len(ai_messages),
            'user_messages': len(user_messages),
            'avg_ai_confidence': avg_confidence,
            'rated_messages': len(rated_messages),
            'helpful_messages': helpful_count,
            'helpfulness_rate': helpful_count / len(rated_messages) if rated_messages else 0.0,
            'duration_minutes': session.duration_minutes,
            'session_rating': session.rating
        }

    @staticmethod
    def get_context_type_stats(sessions: List[ConsultationSession]) -> Dict[str, int]:
        """Get statistics by context type"""
        stats = {}
        for session in sessions:
            context = session.context_type.value
            stats[context] = stats.get(context, 0) + 1
        return stats


# ========== Session Exporter ==========

class SessionExporter:
    """
    Export consultation sessions to various formats

    Supports PDF, DOCX, TXT, JSON exports
    """

    def export_to_text(self, session: ConsultationSession) -> str:
        """Export session as plain text"""
        lines = [
            f"Консультация: {session.name}",
            f"Тема: {session.topic or 'Не указана'}",
            f"Дата: {session.start_date.strftime('%d.%m.%Y %H:%M') if session.start_date else 'N/A'}",
            f"Длительность: {session.duration_minutes:.1f} мин",
            f"Сообщений: {session.message_count}",
            "",
            "=" * 80,
            ""
        ]

        for msg in session.messages:
            sender_prefix = "🤖 AI:" if msg.message_type == MessageType.AI else "👤 Пользователь:"
            timestamp = msg.created_at.strftime("%H:%M")

            lines.append(f"[{timestamp}] {sender_prefix}")
            lines.append(msg.content)

            if msg.confidence:
                lines.append(f"  (Уверенность: {msg.confidence:.0%})")

            lines.append("")

        if session.rating:
            lines.extend([
                "",
                "=" * 80,
                f"Оценка сессии: {session.rating}/5",
                f"Отзыв: {session.feedback or 'Нет отзыва'}"
            ])

        return "\n".join(lines)

    def export_to_json(self, session: ConsultationSession) -> str:
        """Export session as JSON"""
        data = {
            'session_id': session.id,
            'name': session.name,
            'topic': session.topic,
            'context_type': session.context_type.value,
            'state': session.state.value,
            'start_date': session.start_date.isoformat() if session.start_date else None,
            'end_date': session.end_date.isoformat() if session.end_date else None,
            'duration_minutes': session.duration_minutes,
            'rating': session.rating,
            'feedback': session.feedback,
            'messages': [
                {
                    'id': msg.id,
                    'type': msg.message_type.value,
                    'sender': msg.sender,
                    'content': msg.content,
                    'confidence': msg.confidence,
                    'is_helpful': msg.is_helpful,
                    'user_rating': msg.user_rating,
                    'timestamp': msg.created_at.isoformat()
                }
                for msg in session.messages
            ]
        }

        return json.dumps(data, ensure_ascii=False, indent=2)


# ========== Usage Example ==========

def example_consultation_session():
    """Example of using consultation session management"""

    # Create manager
    manager = ConsultationSessionManager()
    context_builder = SessionContextBuilder(manager)

    # Create session
    session = manager.create_session(
        session_id="session_001",
        consultant_id="colleague_bia_specialist",
        client_id="org_123",
        topic="Проведение BIA",
        context_type=ContextType.RISK_ASSESSMENT
    )

    # Start session
    manager.start_session(session.id)

    # Add user message
    manager.add_message(
        session.id,
        MessageType.USER,
        "Как правильно провести анализ влияния на бизнес?",
        "John Doe"
    )

    # Build context for AI
    context = context_builder.build_context(session.id)

    # Add AI response
    manager.add_message(
        session.id,
        MessageType.AI,
        "Для проведения BIA следуйте следующим шагам: 1) Определите критические функции...",
        "BIA Specialist",
        confidence=0.92,
        metadata={'knowledge_used': ['kb_bia_001']}
    )

    # Rate message
    manager.rate_message(
        session.id,
        f"{session.id}_msg_2",
        is_helpful=True,
        rating=3
    )

    # Complete session
    manager.complete_session(session.id)

    # Add feedback
    manager.add_feedback(session.id, rating=5, feedback="Очень полезная консультация!")

    # Analytics
    metrics = SessionAnalytics.calculate_session_metrics(session)
    print("Session metrics:", metrics)

    # Export
    exporter = SessionExporter()
    text_export = exporter.export_to_text(session)
    print("Exported session:")
    print(text_export)


if __name__ == "__main__":
    example_consultation_session()
