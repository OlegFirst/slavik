"""
PostgreSQL Storage Adapter

Standalone PostgreSQL storage implementation using SQLAlchemy async
"""

import logging
from typing import Dict, List, Optional, Any, Type
from datetime import datetime
from contextlib import asynccontextmanager

from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import selectinload

from .models import (
    Base,
    TenantModel,
    UserModel,
    OrganizationModel,
    DataSourceModel,
    SimulationResultModel,
    MetricSeriesModel,
    HealthScoreModel,
    PredictionModel,
    TheoryOfChangeModel,
    ImpactPassportModel
)
from . import models  # Import models module for type hints
from core.models.base import (
    OrganizationType,
    SimulationScenarioType,
    SimulationStatus,
    DataSourceType
)

logger = logging.getLogger(__name__)


# ============================================
# POSTGRESQL STORAGE
# ============================================

class PostgreSQLStorage:
    """
    PostgreSQL Storage Adapter

    Standalone async PostgreSQL storage using SQLAlchemy 2.0
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize PostgreSQL storage

        Args:
            config: Database configuration
        """
        self.config = config

        # Build connection URL
        self.database_url = self._build_database_url()

        # Engine and session
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker] = None

        # Statistics
        self.stats = {
            'queries_executed': 0,
            'records_created': 0,
            'records_updated': 0,
            'records_deleted': 0,
            'errors': 0
        }

        logger.info("PostgreSQL Storage initialized")

    def _build_database_url(self) -> str:
        """Build PostgreSQL connection URL"""
        host = self.config.get('host', 'localhost')
        port = self.config.get('port', 5432)
        database = self.config.get('database', 'digital_twin')
        username = self.config.get('username', 'postgres')
        password = self.config.get('password', 'postgres')

        # Use asyncpg driver
        url = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"

        logger.info(f"Database URL: postgresql+asyncpg://{username}:***@{host}:{port}/{database}")

        return url

    async def initialize(self) -> None:
        """Initialize database connection and create tables"""
        try:
            # Create async engine
            self.engine = create_async_engine(
                self.database_url,
                echo=self.config.get('echo', False),
                pool_size=self.config.get('pool_size', 20),
                max_overflow=self.config.get('max_overflow', 10),
                pool_pre_ping=True,  # Verify connections before using
            )

            # Create session factory
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            # Create all tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            logger.info("PostgreSQL storage initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL storage: {e}", exc_info=True)
            raise

    async def close(self) -> None:
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
            logger.info("PostgreSQL storage closed")

    @asynccontextmanager
    async def session(self):
        """Get database session context manager"""
        if not self.session_factory:
            raise RuntimeError("Storage not initialized. Call initialize() first.")

        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # ============================================
    # ORGANIZATION OPERATIONS
    # ============================================

    async def create_organization(self, org_data: Dict[str, Any]) -> OrganizationModel:
        """
        Create new organization

        Args:
            org_data: Organization data

        Returns:
            Created organization model
        """
        async with self.session() as session:
            try:
                org = OrganizationModel(**org_data)
                session.add(org)

                self.stats['records_created'] += 1
                self.stats['queries_executed'] += 1

                logger.info(f"Created organization: {org.id}")

                return org

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to create organization: {e}", exc_info=True)
                raise

    async def get_organization(
        self,
        org_id: Optional[str] = None,
        twin_id: Optional[str] = None
    ) -> Optional[OrganizationModel]:
        """
        Get organization by ID or twin_id

        Args:
            org_id: Organization ID
            twin_id: Twin ID

        Returns:
            Organization model or None
        """
        if not org_id and not twin_id:
            raise ValueError("Either org_id or twin_id must be provided")

        async with self.session() as session:
            try:
                if org_id:
                    stmt = select(OrganizationModel).where(OrganizationModel.id == org_id)
                else:
                    stmt = select(OrganizationModel).where(OrganizationModel.twin_id == twin_id)

                result = await session.execute(stmt)
                org = result.scalar_one_or_none()

                self.stats['queries_executed'] += 1

                return org

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to get organization: {e}", exc_info=True)
                raise

    async def update_organization(
        self,
        org_id: str,
        updates: Dict[str, Any]
    ) -> Optional[OrganizationModel]:
        """
        Update organization

        Args:
            org_id: Organization ID
            updates: Fields to update

        Returns:
            Updated organization model
        """
        async with self.session() as session:
            try:
                stmt = (
                    update(OrganizationModel)
                    .where(OrganizationModel.id == org_id)
                    .values(**updates, updated_at=datetime.utcnow())
                    .returning(OrganizationModel)
                )

                result = await session.execute(stmt)
                org = result.scalar_one_or_none()

                if org:
                    self.stats['records_updated'] += 1
                    logger.info(f"Updated organization: {org_id}")

                self.stats['queries_executed'] += 1

                return org

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to update organization: {e}", exc_info=True)
                raise

    async def delete_organization(self, org_id: str) -> bool:
        """
        Delete organization

        Args:
            org_id: Organization ID

        Returns:
            True if deleted
        """
        async with self.session() as session:
            try:
                stmt = delete(OrganizationModel).where(OrganizationModel.id == org_id)
                result = await session.execute(stmt)

                deleted = result.rowcount > 0

                if deleted:
                    self.stats['records_deleted'] += 1
                    logger.info(f"Deleted organization: {org_id}")

                self.stats['queries_executed'] += 1

                return deleted

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to delete organization: {e}", exc_info=True)
                raise

    async def list_organizations(
        self,
        tenant_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[OrganizationModel]:
        """
        List organizations with filters

        Args:
            tenant_id: Tenant ID for isolation (required for multi-tenancy)
            filters: Filter conditions
            limit: Max results
            offset: Skip results

        Returns:
            List of organization models
        """
        async with self.session() as session:
            try:
                stmt = select(OrganizationModel)

                # Apply tenant filter FIRST (security)
                conditions = []
                if tenant_id:
                    conditions.append(OrganizationModel.tenant_id == tenant_id)

                # Apply other filters
                if filters:
                    if 'org_type' in filters:
                        conditions.append(OrganizationModel.org_type == filters['org_type'])

                    if 'industry' in filters:
                        conditions.append(OrganizationModel.industry == filters['industry'])

                    if 'name_contains' in filters:
                        conditions.append(OrganizationModel.name.ilike(f"%{filters['name_contains']}%"))

                    if 'min_health_score' in filters:
                        conditions.append(OrganizationModel.health_score >= filters['min_health_score'])

                if conditions:
                    stmt = stmt.where(and_(*conditions))

                # Apply pagination
                stmt = stmt.limit(limit).offset(offset).order_by(OrganizationModel.created_at.desc())

                result = await session.execute(stmt)
                organizations = result.scalars().all()

                self.stats['queries_executed'] += 1

                return list(organizations)

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to list organizations: {e}", exc_info=True)
                raise

    # ============================================
    # SIMULATION OPERATIONS
    # ============================================

    async def create_simulation(self, sim_data: Dict[str, Any]) -> SimulationResultModel:
        """Create simulation result"""
        async with self.session() as session:
            try:
                simulation = SimulationResultModel(**sim_data)
                session.add(simulation)

                self.stats['records_created'] += 1
                self.stats['queries_executed'] += 1

                logger.info(f"Created simulation: {simulation.id}")

                return simulation

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to create simulation: {e}", exc_info=True)
                raise

    async def get_simulation(self, sim_id: str) -> Optional[SimulationResultModel]:
        """Get simulation by ID"""
        async with self.session() as session:
            try:
                stmt = select(SimulationResultModel).where(SimulationResultModel.id == sim_id)
                result = await session.execute(stmt)

                self.stats['queries_executed'] += 1

                return result.scalar_one_or_none()

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to get simulation: {e}", exc_info=True)
                raise

    async def update_simulation(
        self,
        sim_id: str,
        updates: Dict[str, Any]
    ) -> Optional[SimulationResultModel]:
        """Update simulation"""
        async with self.session() as session:
            try:
                stmt = (
                    update(SimulationResultModel)
                    .where(SimulationResultModel.id == sim_id)
                    .values(**updates, updated_at=datetime.utcnow())
                    .returning(SimulationResultModel)
                )

                result = await session.execute(stmt)
                simulation = result.scalar_one_or_none()

                if simulation:
                    self.stats['records_updated'] += 1
                    logger.info(f"Updated simulation: {sim_id}")

                self.stats['queries_executed'] += 1

                return simulation

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to update simulation: {e}", exc_info=True)
                raise

    async def list_simulations(
        self,
        tenant_id: Optional[str] = None,
        twin_id: Optional[str] = None,
        scenario: Optional[SimulationScenarioType] = None,
        status: Optional[SimulationStatus] = None,
        limit: int = 100
    ) -> List[SimulationResultModel]:
        """List simulations with filters (tenant-aware)"""
        async with self.session() as session:
            try:
                stmt = select(SimulationResultModel)

                conditions = []

                # Tenant filter (via twin_id relationship - need to join with organizations)
                # For now, we filter by twin_id which should belong to tenant
                if tenant_id:
                    # Join with organizations to filter by tenant
                    stmt = stmt.join(
                        OrganizationModel,
                        SimulationResultModel.twin_id == OrganizationModel.twin_id
                    ).where(OrganizationModel.tenant_id == tenant_id)

                if twin_id:
                    conditions.append(SimulationResultModel.twin_id == twin_id)
                if scenario:
                    conditions.append(SimulationResultModel.scenario == scenario)
                if status:
                    conditions.append(SimulationResultModel.status == status)

                if conditions:
                    stmt = stmt.where(and_(*conditions))

                stmt = stmt.limit(limit).order_by(SimulationResultModel.created_at.desc())

                result = await session.execute(stmt)

                self.stats['queries_executed'] += 1

                return list(result.scalars().all())

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to list simulations: {e}", exc_info=True)
                raise

    # ============================================
    # DATA SOURCE OPERATIONS
    # ============================================

    async def create_data_source(self, source_data: Dict[str, Any]) -> DataSourceModel:
        """Create data source"""
        async with self.session() as session:
            try:
                source = DataSourceModel(**source_data)
                session.add(source)

                self.stats['records_created'] += 1
                self.stats['queries_executed'] += 1

                logger.info(f"Created data source: {source.id}")

                return source

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to create data source: {e}", exc_info=True)
                raise

    async def list_data_sources(
        self,
        organization_id: str
    ) -> List[DataSourceModel]:
        """List data sources for organization"""
        async with self.session() as session:
            try:
                stmt = (
                    select(DataSourceModel)
                    .where(DataSourceModel.organization_id == organization_id)
                    .order_by(DataSourceModel.last_sync.desc())
                )

                result = await session.execute(stmt)

                self.stats['queries_executed'] += 1

                return list(result.scalars().all())

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to list data sources: {e}", exc_info=True)
                raise

    # ============================================
    # METRICS OPERATIONS
    # ============================================

    async def create_metric_series(self, metric_data: Dict[str, Any]) -> MetricSeriesModel:
        """Create metric series"""
        async with self.session() as session:
            try:
                metric = MetricSeriesModel(**metric_data)
                session.add(metric)

                self.stats['records_created'] += 1
                self.stats['queries_executed'] += 1

                return metric

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to create metric series: {e}", exc_info=True)
                raise

    async def get_metrics(
        self,
        twin_id: str,
        metric_name: Optional[str] = None
    ) -> List[MetricSeriesModel]:
        """Get metrics for twin"""
        async with self.session() as session:
            try:
                stmt = select(MetricSeriesModel).where(MetricSeriesModel.twin_id == twin_id)

                if metric_name:
                    stmt = stmt.where(MetricSeriesModel.metric_name == metric_name)

                stmt = stmt.order_by(MetricSeriesModel.created_at.desc())

                result = await session.execute(stmt)

                self.stats['queries_executed'] += 1

                return list(result.scalars().all())

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to get metrics: {e}", exc_info=True)
                raise

    async def create_health_score(self, health_data: Dict[str, Any]) -> HealthScoreModel:
        """Create health score snapshot"""
        async with self.session() as session:
            try:
                health = HealthScoreModel(**health_data)
                session.add(health)

                self.stats['records_created'] += 1
                self.stats['queries_executed'] += 1

                return health

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to create health score: {e}", exc_info=True)
                raise

    async def get_health_scores(
        self,
        twin_id: str,
        limit: int = 100
    ) -> List[HealthScoreModel]:
        """Get health score history"""
        async with self.session() as session:
            try:
                stmt = (
                    select(HealthScoreModel)
                    .where(HealthScoreModel.twin_id == twin_id)
                    .order_by(HealthScoreModel.calculated_at.desc())
                    .limit(limit)
                )

                result = await session.execute(stmt)

                self.stats['queries_executed'] += 1

                return list(result.scalars().all())

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to get health scores: {e}", exc_info=True)
                raise

    # ============================================
    # PREDICTION OPERATIONS
    # ============================================

    async def create_prediction(self, pred_data: Dict[str, Any]) -> PredictionModel:
        """Create prediction"""
        async with self.session() as session:
            try:
                prediction = PredictionModel(**pred_data)
                session.add(prediction)

                self.stats['records_created'] += 1
                self.stats['queries_executed'] += 1

                logger.info(f"Created prediction: {prediction.id}")

                return prediction

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to create prediction: {e}", exc_info=True)
                raise

    async def get_predictions(
        self,
        twin_id: str,
        prediction_type: Optional[str] = None
    ) -> List[PredictionModel]:
        """Get predictions for twin"""
        async with self.session() as session:
            try:
                stmt = select(PredictionModel).where(PredictionModel.twin_id == twin_id)

                if prediction_type:
                    stmt = stmt.where(PredictionModel.prediction_type == prediction_type)

                stmt = stmt.order_by(PredictionModel.created_at.desc())

                result = await session.execute(stmt)

                self.stats['queries_executed'] += 1

                return list(result.scalars().all())

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to get predictions: {e}", exc_info=True)
                raise

    # ============================================
    # THEORY OF CHANGE OPERATIONS
    # ============================================

    async def create_theory_of_change(self, toc_data: Dict[str, Any]) -> TheoryOfChangeModel:
        """Create Theory of Change"""
        async with self.session() as session:
            try:
                toc = TheoryOfChangeModel(**toc_data)
                session.add(toc)

                self.stats['records_created'] += 1
                self.stats['queries_executed'] += 1

                logger.info(f"Created Theory of Change: {toc.id}")

                return toc

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to create Theory of Change: {e}", exc_info=True)
                raise

    async def get_theory_of_change(self, twin_id: str) -> Optional[TheoryOfChangeModel]:
        """Get Theory of Change for twin"""
        async with self.session() as session:
            try:
                stmt = (
                    select(TheoryOfChangeModel)
                    .where(TheoryOfChangeModel.twin_id == twin_id)
                    .order_by(TheoryOfChangeModel.updated_at.desc())
                )

                result = await session.execute(stmt)

                self.stats['queries_executed'] += 1

                return result.scalars().first()

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to get Theory of Change: {e}", exc_info=True)
                raise

    # ============================================
    # IMPACT PASSPORT OPERATIONS
    # ============================================

    async def create_impact_passport(self, passport_data: Dict[str, Any]) -> ImpactPassportModel:
        """Create Impact Passport"""
        async with self.session() as session:
            try:
                passport = ImpactPassportModel(**passport_data)
                session.add(passport)

                self.stats['records_created'] += 1
                self.stats['queries_executed'] += 1

                logger.info(f"Created Impact Passport: {passport.id}")

                return passport

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to create Impact Passport: {e}", exc_info=True)
                raise

    async def get_impact_passport(
        self,
        passport_id: Optional[str] = None,
        passport_number: Optional[str] = None
    ) -> Optional[ImpactPassportModel]:
        """Get Impact Passport by ID or number"""
        async with self.session() as session:
            try:
                if passport_id:
                    stmt = select(ImpactPassportModel).where(ImpactPassportModel.id == passport_id)
                elif passport_number:
                    stmt = select(ImpactPassportModel).where(
                        ImpactPassportModel.passport_number == passport_number
                    )
                else:
                    raise ValueError("Either passport_id or passport_number must be provided")

                result = await session.execute(stmt)

                self.stats['queries_executed'] += 1

                return result.scalar_one_or_none()

            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Failed to get Impact Passport: {e}", exc_info=True)
                raise

    # ============================================
    # STATISTICS & UTILITIES
    # ============================================

    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        async with self.session() as session:
            try:
                # Count records
                org_count = await session.scalar(select(func.count(OrganizationModel.id)))
                sim_count = await session.scalar(select(func.count(SimulationResultModel.id)))

                return {
                    **self.stats,
                    'organizations': org_count,
                    'simulations': sim_count
                }

            except Exception as e:
                logger.error(f"Failed to get statistics: {e}")
                return self.stats

    async def health_check(self) -> bool:
        """Check database connection health"""
        try:
            async with self.session() as session:
                await session.execute(select(1))
                return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    # ============================================
    # TENANT METHODS
    # ============================================

    async def create_tenant(self, tenant_data: Dict[str, Any]) -> models.TenantModel:
        """Create new tenant"""
        async with self.Session() as session:
            tenant = models.TenantModel(**tenant_data)
            session.add(tenant)
            await session.commit()
            await session.refresh(tenant)
            logger.info(f"Created tenant: {tenant.id}")
            return tenant

    async def get_tenant(self, tenant_id: str) -> Optional[models.TenantModel]:
        """Get tenant by ID"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.TenantModel).where(models.TenantModel.id == tenant_id)
            )
            return result.scalar_one_or_none()

    async def get_tenant_by_slug(self, slug: str) -> Optional[models.TenantModel]:
        """Get tenant by slug"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.TenantModel).where(models.TenantModel.slug == slug)
            )
            return result.scalar_one_or_none()

    async def update_tenant(self, tenant_id: str, update_data: Dict[str, Any]) -> Optional[models.TenantModel]:
        """Update tenant"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.TenantModel).where(models.TenantModel.id == tenant_id)
            )
            tenant = result.scalar_one_or_none()
            if tenant:
                for key, value in update_data.items():
                    setattr(tenant, key, value)
                await session.commit()
                await session.refresh(tenant)
                logger.info(f"Updated tenant: {tenant_id}")
            return tenant

    # ============================================
    # USER METHODS
    # ============================================

    async def create_user(self, user_data: Dict[str, Any]) -> models.UserModel:
        """Create new user"""
        async with self.Session() as session:
            user = models.UserModel(**user_data)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info(f"Created user: {user.id} ({user.email})")
            return user

    async def get_user(self, user_id: str) -> Optional[models.UserModel]:
        """Get user by ID"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.UserModel).where(models.UserModel.id == user_id)
            )
            return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[models.UserModel]:
        """Get user by email"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.UserModel).where(models.UserModel.email == email)
            )
            return result.scalar_one_or_none()

    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[models.UserModel]:
        """Update user"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.UserModel).where(models.UserModel.id == user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                for key, value in update_data.items():
                    setattr(user, key, value)
                await session.commit()
                await session.refresh(user)
                logger.info(f"Updated user: {user_id}")
            return user

    async def list_users_by_tenant(self, tenant_id: str) -> list[models.UserModel]:
        """List all users in a tenant"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.UserModel)
                .where(models.UserModel.tenant_id == tenant_id)
                .order_by(models.UserModel.created_at.desc())
            )
            return list(result.scalars().all())

    # ============================================
    # SIMULATION HUB METHODS (Scenario Templates, Exercises, Predictions, BIA)
    # ============================================

    async def create_scenario_template(self, data: Dict[str, Any]) -> models.ScenarioTemplateModel:
        """Create scenario template"""
        async with self.Session() as session:
            scenario = models.ScenarioTemplateModel(**data)
            session.add(scenario)
            await session.commit()
            await session.refresh(scenario)
            logger.info(f"Created scenario template: {scenario.id}")
            return scenario

    async def get_scenario_template(self, scenario_id: str) -> Optional[models.ScenarioTemplateModel]:
        """Get scenario template by ID"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.ScenarioTemplateModel)
                .where(models.ScenarioTemplateModel.id == scenario_id)
            )
            return result.scalar_one_or_none()

    async def list_scenario_templates(
        self,
        tenant_id: str,
        category: Optional[str] = None,
        scenario_type: Optional[str] = None,
        is_public: Optional[bool] = None,
        limit: int = 100
    ) -> list[models.ScenarioTemplateModel]:
        """List scenario templates"""
        async with self.Session() as session:
            stmt = select(models.ScenarioTemplateModel)

            # Tenant's own scenarios OR public scenarios
            conditions = []
            if is_public:
                conditions.append(
                    or_(
                        models.ScenarioTemplateModel.tenant_id == tenant_id,
                        models.ScenarioTemplateModel.is_public == True
                    )
                )
            else:
                conditions.append(models.ScenarioTemplateModel.tenant_id == tenant_id)

            if category:
                conditions.append(models.ScenarioTemplateModel.category == category)

            if scenario_type:
                conditions.append(models.ScenarioTemplateModel.scenario_type == scenario_type)

            if conditions:
                stmt = stmt.where(and_(*conditions))

            stmt = stmt.where(models.ScenarioTemplateModel.is_active == True)
            stmt = stmt.order_by(models.ScenarioTemplateModel.created_at.desc())
            stmt = stmt.limit(limit)

            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def update_scenario_template(
        self,
        scenario_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[models.ScenarioTemplateModel]:
        """Update scenario template"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.ScenarioTemplateModel)
                .where(models.ScenarioTemplateModel.id == scenario_id)
            )
            scenario = result.scalar_one_or_none()
            if scenario:
                for key, value in update_data.items():
                    setattr(scenario, key, value)
                await session.commit()
                await session.refresh(scenario)
                logger.info(f"Updated scenario template: {scenario_id}")
            return scenario

    async def delete_scenario_template(self, scenario_id: str) -> bool:
        """Delete scenario template"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.ScenarioTemplateModel)
                .where(models.ScenarioTemplateModel.id == scenario_id)
            )
            scenario = result.scalar_one_or_none()
            if scenario:
                await session.delete(scenario)
                await session.commit()
                logger.info(f"Deleted scenario template: {scenario_id}")
                return True
            return False

    async def count_scenarios(self, tenant_id: str) -> int:
        """Count scenario templates for tenant"""
        async with self.Session() as session:
            from sqlalchemy import func
            result = await session.execute(
                select(func.count(models.ScenarioTemplateModel.id))
                .where(models.ScenarioTemplateModel.tenant_id == tenant_id)
                .where(models.ScenarioTemplateModel.is_active == True)
            )
            return result.scalar() or 0

    async def create_exercise(self, data: Dict[str, Any]) -> models.ExerciseModel:
        """Create exercise"""
        async with self.Session() as session:
            exercise = models.ExerciseModel(**data)
            session.add(exercise)
            await session.commit()
            await session.refresh(exercise)
            logger.info(f"Created exercise: {exercise.id}")
            return exercise

    async def get_exercise(self, exercise_id: str) -> Optional[models.ExerciseModel]:
        """Get exercise by ID"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.ExerciseModel).where(models.ExerciseModel.id == exercise_id)
            )
            return result.scalar_one_or_none()

    async def list_exercises(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        exercise_type: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = 100
    ) -> list[models.ExerciseModel]:
        """List exercises"""
        async with self.Session() as session:
            stmt = select(models.ExerciseModel)

            conditions = [models.ExerciseModel.tenant_id == tenant_id]

            if status:
                conditions.append(models.ExerciseModel.status == status)

            if exercise_type:
                conditions.append(models.ExerciseModel.exercise_type == exercise_type)

            if organization_id:
                conditions.append(models.ExerciseModel.organization_id == organization_id)

            stmt = stmt.where(and_(*conditions))
            stmt = stmt.order_by(models.ExerciseModel.created_at.desc())
            stmt = stmt.limit(limit)

            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def update_exercise(
        self,
        exercise_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[models.ExerciseModel]:
        """Update exercise"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.ExerciseModel).where(models.ExerciseModel.id == exercise_id)
            )
            exercise = result.scalar_one_or_none()
            if exercise:
                for key, value in update_data.items():
                    setattr(exercise, key, value)
                await session.commit()
                await session.refresh(exercise)
                logger.info(f"Updated exercise: {exercise_id}")
            return exercise

    async def delete_exercise(self, exercise_id: str) -> bool:
        """Delete exercise"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.ExerciseModel).where(models.ExerciseModel.id == exercise_id)
            )
            exercise = result.scalar_one_or_none()
            if exercise:
                await session.delete(exercise)
                await session.commit()
                logger.info(f"Deleted exercise: {exercise_id}")
                return True
            return False

    async def create_prediction(self, data: Dict[str, Any]) -> models.PredictionModel:
        """Create prediction"""
        async with self.Session() as session:
            prediction = models.PredictionModel(**data)
            session.add(prediction)
            await session.commit()
            await session.refresh(prediction)
            logger.info(f"Created prediction: {prediction.id}")
            return prediction

    async def get_prediction(self, prediction_id: str) -> Optional[models.PredictionModel]:
        """Get prediction by ID"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.PredictionModel).where(models.PredictionModel.id == prediction_id)
            )
            return result.scalar_one_or_none()

    async def list_predictions(
        self,
        tenant_id: str,
        prediction_type: Optional[str] = None,
        status: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = 100
    ) -> list[models.PredictionModel]:
        """List predictions"""
        async with self.Session() as session:
            stmt = select(models.PredictionModel)

            conditions = [models.PredictionModel.tenant_id == tenant_id]

            if prediction_type:
                conditions.append(models.PredictionModel.prediction_type == prediction_type)

            if status:
                conditions.append(models.PredictionModel.status == status)

            if organization_id:
                conditions.append(models.PredictionModel.organization_id == organization_id)

            stmt = stmt.where(and_(*conditions))
            stmt = stmt.order_by(models.PredictionModel.created_at.desc())
            stmt = stmt.limit(limit)

            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def update_prediction(
        self,
        prediction_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[models.PredictionModel]:
        """Update prediction"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.PredictionModel).where(models.PredictionModel.id == prediction_id)
            )
            prediction = result.scalar_one_or_none()
            if prediction:
                for key, value in update_data.items():
                    setattr(prediction, key, value)
                await session.commit()
                await session.refresh(prediction)
                logger.info(f"Updated prediction: {prediction_id}")
            return prediction

    async def delete_prediction(self, prediction_id: str) -> bool:
        """Delete prediction"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.PredictionModel).where(models.PredictionModel.id == prediction_id)
            )
            prediction = result.scalar_one_or_none()
            if prediction:
                await session.delete(prediction)
                await session.commit()
                logger.info(f"Deleted prediction: {prediction_id}")
                return True
            return False

    async def create_bia_analysis(self, data: Dict[str, Any]) -> models.BIAAnalysisModel:
        """Create BIA analysis"""
        async with self.Session() as session:
            bia = models.BIAAnalysisModel(**data)
            session.add(bia)
            await session.commit()
            await session.refresh(bia)
            logger.info(f"Created BIA analysis: {bia.id}")
            return bia

    async def get_bia_analysis(self, bia_id: str) -> Optional[models.BIAAnalysisModel]:
        """Get BIA analysis by ID"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.BIAAnalysisModel).where(models.BIAAnalysisModel.id == bia_id)
            )
            return result.scalar_one_or_none()

    async def list_bia_analyses(
        self,
        tenant_id: str,
        analysis_type: Optional[str] = None,
        status: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = 100
    ) -> list[models.BIAAnalysisModel]:
        """List BIA analyses"""
        async with self.Session() as session:
            stmt = select(models.BIAAnalysisModel)

            conditions = [models.BIAAnalysisModel.tenant_id == tenant_id]

            if analysis_type:
                conditions.append(models.BIAAnalysisModel.analysis_type == analysis_type)

            if status:
                conditions.append(models.BIAAnalysisModel.status == status)

            if organization_id:
                conditions.append(models.BIAAnalysisModel.organization_id == organization_id)

            stmt = stmt.where(and_(*conditions))
            stmt = stmt.order_by(models.BIAAnalysisModel.created_at.desc())
            stmt = stmt.limit(limit)

            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def update_bia_analysis(
        self,
        bia_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[models.BIAAnalysisModel]:
        """Update BIA analysis"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.BIAAnalysisModel).where(models.BIAAnalysisModel.id == bia_id)
            )
            bia = result.scalar_one_or_none()
            if bia:
                for key, value in update_data.items():
                    setattr(bia, key, value)
                await session.commit()
                await session.refresh(bia)
                logger.info(f"Updated BIA analysis: {bia_id}")
            return bia

    async def delete_bia_analysis(self, bia_id: str) -> bool:
        """Delete BIA analysis"""
        async with self.Session() as session:
            result = await session.execute(
                select(models.BIAAnalysisModel).where(models.BIAAnalysisModel.id == bia_id)
            )
            bia = result.scalar_one_or_none()
            if bia:
                await session.delete(bia)
                await session.commit()
                logger.info(f"Deleted BIA analysis: {bia_id}")
                return True
            return False

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
