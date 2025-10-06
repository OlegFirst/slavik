"""
Database Manager for Deployment Service
=======================================

PostgreSQL persistence for deployment history and state.
"""

import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid

from config import config
from models import DeploymentRecord, DeploymentStatus

logger = logging.getLogger(__name__)

Base = declarative_base()


class DeploymentModel(Base):
    """SQLAlchemy model for deployments"""
    __tablename__ = "deployments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)

    # Deployment details
    strategy = Column(String, nullable=False)
    requested_services = Column(JSON)
    deployed_services = Column(JSON, default=list)
    failed_services = Column(JSON, default=list)

    # Metadata
    initiated_by = Column(String)
    ai_strategy_used = Column(Boolean, default=False)
    rollback_executed = Column(Boolean, default=False)
    error_message = Column(Text)
    metadata = Column(JSON, default=dict)


class DeploymentDB:
    """Database manager for deployments"""

    def __init__(self):
        """Initialize database connection"""
        try:
            self.engine = create_engine(config.DATABASE_URL, echo=False)
            Base.metadata.create_all(self.engine)
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    def create_deployment(self, record: DeploymentRecord) -> str:
        """
        Create new deployment record.

        Args:
            record: DeploymentRecord

        Returns:
            Deployment ID
        """
        session = self.get_session()
        try:
            db_deployment = DeploymentModel(
                id=record.id,
                tenant_id=record.tenant_id,
                status=record.status.value if isinstance(record.status, DeploymentStatus) else record.status,
                started_at=record.started_at,
                completed_at=record.completed_at,
                duration_seconds=record.duration_seconds,
                strategy=record.strategy,
                requested_services=record.requested_services,
                deployed_services=record.deployed_services,
                failed_services=record.failed_services,
                initiated_by=record.initiated_by,
                ai_strategy_used=record.ai_strategy_used,
                rollback_executed=record.rollback_executed,
                error_message=record.error_message,
                metadata=record.metadata
            )

            session.add(db_deployment)
            session.commit()
            logger.info(f"Created deployment record: {record.id}")
            return record.id

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create deployment record: {e}")
            raise
        finally:
            session.close()

    def update_deployment(self, deployment_id: str, updates: dict):
        """
        Update deployment record.

        Args:
            deployment_id: Deployment ID
            updates: Dictionary of fields to update
        """
        session = self.get_session()
        try:
            deployment = session.query(DeploymentModel).filter(
                DeploymentModel.id == deployment_id
            ).first()

            if deployment:
                for key, value in updates.items():
                    if hasattr(deployment, key):
                        setattr(deployment, key, value)

                session.commit()
                logger.info(f"Updated deployment: {deployment_id}")
            else:
                logger.warning(f"Deployment not found: {deployment_id}")

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update deployment: {e}")
            raise
        finally:
            session.close()

    def get_deployment(self, deployment_id: str) -> Optional[DeploymentRecord]:
        """
        Get deployment by ID.

        Args:
            deployment_id: Deployment ID

        Returns:
            DeploymentRecord or None
        """
        session = self.get_session()
        try:
            deployment = session.query(DeploymentModel).filter(
                DeploymentModel.id == deployment_id
            ).first()

            if deployment:
                return DeploymentRecord(
                    id=deployment.id,
                    tenant_id=deployment.tenant_id,
                    status=deployment.status,
                    started_at=deployment.started_at,
                    completed_at=deployment.completed_at,
                    duration_seconds=deployment.duration_seconds,
                    strategy=deployment.strategy,
                    requested_services=deployment.requested_services,
                    deployed_services=deployment.deployed_services,
                    failed_services=deployment.failed_services,
                    initiated_by=deployment.initiated_by,
                    ai_strategy_used=deployment.ai_strategy_used,
                    rollback_executed=deployment.rollback_executed,
                    error_message=deployment.error_message,
                    metadata=deployment.metadata
                )
            return None

        finally:
            session.close()

    def get_recent_deployments(
        self,
        tenant_id: Optional[str] = None,
        limit: int = 10
    ) -> List[DeploymentRecord]:
        """
        Get recent deployments.

        Args:
            tenant_id: Filter by tenant (optional)
            limit: Maximum number of results

        Returns:
            List of DeploymentRecord
        """
        session = self.get_session()
        try:
            query = session.query(DeploymentModel)

            if tenant_id:
                query = query.filter(DeploymentModel.tenant_id == tenant_id)

            deployments = query.order_by(
                DeploymentModel.started_at.desc()
            ).limit(limit).all()

            return [
                DeploymentRecord(
                    id=d.id,
                    tenant_id=d.tenant_id,
                    status=d.status,
                    started_at=d.started_at,
                    completed_at=d.completed_at,
                    duration_seconds=d.duration_seconds,
                    strategy=d.strategy,
                    requested_services=d.requested_services,
                    deployed_services=d.deployed_services,
                    failed_services=d.failed_services,
                    initiated_by=d.initiated_by,
                    ai_strategy_used=d.ai_strategy_used,
                    rollback_executed=d.rollback_executed,
                    error_message=d.error_message,
                    metadata=d.metadata
                )
                for d in deployments
            ]

        finally:
            session.close()

    def get_deployment_stats(self, tenant_id: Optional[str] = None) -> dict:
        """
        Get deployment statistics.

        Args:
            tenant_id: Filter by tenant (optional)

        Returns:
            Statistics dictionary
        """
        session = self.get_session()
        try:
            query = session.query(DeploymentModel)

            if tenant_id:
                query = query.filter(DeploymentModel.tenant_id == tenant_id)

            total = query.count()
            successful = query.filter(
                DeploymentModel.status == DeploymentStatus.SUCCESS.value
            ).count()
            failed = query.filter(
                DeploymentModel.status == DeploymentStatus.FAILED.value
            ).count()
            partial = query.filter(
                DeploymentModel.status == DeploymentStatus.PARTIAL.value
            ).count()

            return {
                "total_deployments": total,
                "successful": successful,
                "failed": failed,
                "partial": partial,
                "success_rate": (successful / total * 100) if total > 0 else 0
            }

        finally:
            session.close()
