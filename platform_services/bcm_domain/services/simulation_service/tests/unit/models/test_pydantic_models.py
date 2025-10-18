"""
Unit tests for Pydantic models

Tests data validation, serialization, and business logic in Pydantic models.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from models.pydantic_models import (
    # Enums
    EngineType,
    SimulationStatus,
    ExerciseType,
    ScenarioCategory,
    DashboardType,
    ChartType,
    ReportFormat,
    ReportTemplate,

    # Models
    TaskSpecification,
    VisualizationConfig,
    IntegrationConfig,
    EngineConfig,
    ReportConfig,
    Scenario,
    SimulationEvent,
    ExerciseMetrics,
    SimulationResult,
    Simulation,
    SimulationRequest,
    SimulationState,
)


class TestTaskSpecification:
    """Tests for TaskSpecification model"""

    def test_create_valid_specification(self):
        """Test creating a valid specification"""
        spec = TaskSpecification(
            goal="Test BIA process resilience under cyber incident",
            constraints={"max_duration": 3600, "participants": 10},
            context={"organization_type": "hospital", "size": "large"},
            created_by="user_123",
            organization_id="org_456"
        )

        assert spec.goal == "Test BIA process resilience under cyber incident"
        assert spec.constraints["max_duration"] == 3600
        assert spec.context["organization_type"] == "hospital"
        assert spec.created_by == "user_123"
        assert spec.id.startswith("spec_")
        assert len(spec.id) == 17  # spec_ + 12 hex chars

    def test_goal_too_short(self):
        """Test validation fails for short goal"""
        with pytest.raises(ValidationError) as exc:
            TaskSpecification(
                goal="Test",  # Too short (< 10 chars)
                created_by="user_123",
                organization_id="org_456"
            )
        assert "Goal too short" in str(exc.value)

    def test_goal_empty(self):
        """Test validation fails for empty goal"""
        with pytest.raises(ValidationError) as exc:
            TaskSpecification(
                goal="   ",  # Empty after strip
                created_by="user_123",
                organization_id="org_456"
            )
        assert "Goal cannot be empty" in str(exc.value)

    def test_max_duration_too_short(self):
        """Test validation fails for too short duration"""
        with pytest.raises(ValidationError) as exc:
            TaskSpecification(
                goal="Test BIA process resilience",
                max_duration=30,  # Too short (< 60)
                created_by="user_123",
                organization_id="org_456"
            )

    def test_max_duration_too_long(self):
        """Test validation fails for too long duration"""
        with pytest.raises(ValidationError) as exc:
            TaskSpecification(
                goal="Test BIA process resilience",
                max_duration=30000,  # Too long (> 28800)
                created_by="user_123",
                organization_id="org_456"
            )

    def test_default_values(self):
        """Test default values are set correctly"""
        spec = TaskSpecification(
            goal="Test BIA process resilience",
            created_by="user_123",
            organization_id="org_456"
        )

        assert spec.constraints == {}
        assert spec.context == {}
        assert spec.processes == []
        assert spec.resources == {}
        assert spec.scenarios == []
        assert spec.alternatives == []
        assert spec.max_duration == 3600  # Default 1 hour
        assert spec.engine_preference is None
        assert isinstance(spec.created_at, datetime)

    def test_serialization(self):
        """Test model can be serialized to JSON"""
        spec = TaskSpecification(
            goal="Test BIA process resilience",
            created_by="user_123",
            organization_id="org_456"
        )

        json_data = spec.model_dump_json()
        assert "Test BIA process resilience" in json_data
        assert "user_123" in json_data

        # Should be able to parse back
        spec2 = TaskSpecification.model_validate_json(json_data)
        assert spec2.goal == spec.goal
        assert spec2.created_by == spec.created_by


class TestVisualizationConfig:
    """Tests for VisualizationConfig model"""

    def test_create_with_defaults(self):
        """Test creating with default values"""
        config = VisualizationConfig()

        assert config.dashboard_type == DashboardType.REAL_TIME
        assert "progress" in config.metrics
        assert "events" in config.metrics
        assert "resources" in config.metrics
        assert config.update_interval == 5
        assert config.enable_real_time_streaming is True
        assert config.enable_3d is False
        assert config.max_datapoints == 1000

    def test_custom_configuration(self):
        """Test custom configuration"""
        config = VisualizationConfig(
            dashboard_type=DashboardType.EXECUTIVE,
            metrics=["custom1", "custom2"],
            chart_types=[ChartType.LINE, ChartType.HEATMAP],
            update_interval=10,
            enable_3d=True
        )

        assert config.dashboard_type == DashboardType.EXECUTIVE
        assert config.metrics == ["custom1", "custom2"]
        assert ChartType.HEATMAP in config.chart_types
        assert config.update_interval == 10
        assert config.enable_3d is True

    def test_update_interval_too_low(self):
        """Test update interval validation - too low"""
        with pytest.raises(ValidationError):
            VisualizationConfig(update_interval=0)

    def test_update_interval_too_high(self):
        """Test update interval validation - too high"""
        with pytest.raises(ValidationError):
            VisualizationConfig(update_interval=100)

    def test_max_datapoints_bounds(self):
        """Test max datapoints validation"""
        with pytest.raises(ValidationError):
            VisualizationConfig(max_datapoints=50)  # Too low (< 100)

        with pytest.raises(ValidationError):
            VisualizationConfig(max_datapoints=20000)  # Too high (> 10000)


class TestIntegrationConfig:
    """Tests for IntegrationConfig model"""

    def test_default_configuration(self):
        """Test default values"""
        config = IntegrationConfig()

        # Core integrations enabled by default
        assert config.eventbus_enabled is True
        assert config.orchestrator_enabled is True
        assert config.workflow_enabled is True
        assert config.knowledge_enabled is True
        assert config.community_enabled is True
        assert config.foundation_enabled is True

        # Optional integrations disabled by default
        assert config.predictive_enabled is False
        assert config.digital_twin_enabled is False

        # Auto features enabled
        assert config.auto_pdca is True
        assert config.auto_knowledge_storage is True
        assert config.auto_community_contribution is True
        assert config.auto_contribution_min_quality_score == 8.0

    def test_disable_all_integrations(self):
        """Test disabling all integrations"""
        config = IntegrationConfig(
            eventbus_enabled=False,
            orchestrator_enabled=False,
            workflow_enabled=False,
            knowledge_enabled=False,
            community_enabled=False,
            foundation_enabled=False
        )

        assert config.eventbus_enabled is False
        assert config.orchestrator_enabled is False

    def test_quality_score_validation(self):
        """Test quality score bounds"""
        with pytest.raises(ValidationError):
            IntegrationConfig(auto_contribution_min_quality_score=-1.0)

        with pytest.raises(ValidationError):
            IntegrationConfig(auto_contribution_min_quality_score=15.0)

        # Valid score
        config = IntegrationConfig(auto_contribution_min_quality_score=7.5)
        assert config.auto_contribution_min_quality_score == 7.5


class TestEngineConfig:
    """Tests for EngineConfig model"""

    def test_create_jaamsim_config(self):
        """Test creating JaamSim configuration"""
        config = EngineConfig(
            engine_type=EngineType.JAAMSIM,
            executable_path="/opt/jaamsim/JaamSim2023-03.jar",
            max_memory_mb=2048,
            max_cpu_cores=2,
            jaamsim_settings={"graphics_mode": "headless"}
        )

        assert config.engine_type == EngineType.JAAMSIM
        assert config.executable_path == "/opt/jaamsim/JaamSim2023-03.jar"
        assert config.max_memory_mb == 2048
        assert config.jaamsim_settings["graphics_mode"] == "headless"

    def test_resource_limits_validation(self):
        """Test resource limits validation"""
        with pytest.raises(ValidationError):
            EngineConfig(
                engine_type=EngineType.SIMPY,
                max_memory_mb=100  # Too low (< 512)
            )

        with pytest.raises(ValidationError):
            EngineConfig(
                engine_type=EngineType.SIMPY,
                max_cpu_cores=0  # Too low (< 1)
            )

    def test_default_values(self):
        """Test default resource limits"""
        config = EngineConfig(engine_type=EngineType.SIMPY)

        assert config.max_memory_mb == 2048
        assert config.max_cpu_cores == 2
        assert config.timeout_seconds == 3600
        assert config.jaamsim_settings == {}
        assert config.simpy_settings == {}


class TestReportConfig:
    """Tests for ReportConfig model"""

    def test_default_configuration(self):
        """Test default report configuration"""
        config = ReportConfig()

        assert config.format == ReportFormat.PDF
        assert config.template == ReportTemplate.ISO_22301
        assert config.include_charts is True
        assert config.include_timeline is True
        assert config.include_recommendations is True
        assert config.include_raw_data is False
        assert config.language == "en"

    def test_custom_configuration(self):
        """Test custom report configuration"""
        config = ReportConfig(
            format=ReportFormat.DOCX,
            template=ReportTemplate.EXECUTIVE_SUMMARY,
            include_raw_data=True,
            language="ru"
        )

        assert config.format == ReportFormat.DOCX
        assert config.template == ReportTemplate.EXECUTIVE_SUMMARY
        assert config.include_raw_data is True
        assert config.language == "ru"


class TestScenario:
    """Tests for Scenario model"""

    def test_create_valid_scenario(self):
        """Test creating a valid scenario"""
        scenario = Scenario(
            name="Hospital Cyber Attack Response",
            description="Simulated ransomware attack on hospital IT systems",
            category=ScenarioCategory.CYBER_SECURITY,
            exercise_type=ExerciseType.FUNCTIONAL,
            duration_minutes=120,
            complexity_level=4,
            created_by="user_123",
            organization_id="org_456"
        )

        assert scenario.name == "Hospital Cyber Attack Response"
        assert scenario.category == ScenarioCategory.CYBER_SECURITY
        assert scenario.duration_minutes == 120
        assert scenario.complexity_level == 4
        assert scenario.id.startswith("scenario_")

    def test_duration_too_long(self):
        """Test duration validation - too long"""
        with pytest.raises(ValidationError) as exc:
            Scenario(
                name="Long Scenario",
                description="Very long scenario",
                category=ScenarioCategory.CUSTOM,
                exercise_type=ExerciseType.FULL_SCALE,
                duration_minutes=500,  # > 480 (8 hours)
                created_by="user_123",
                organization_id="org_456"
            )
        assert "8 hours" in str(exc.value)

    def test_complexity_level_validation(self):
        """Test complexity level bounds"""
        with pytest.raises(ValidationError):
            Scenario(
                name="Test",
                description="Test scenario",
                category=ScenarioCategory.CUSTOM,
                exercise_type=ExerciseType.TABLETOP,
                duration_minutes=60,
                complexity_level=0,  # < 1
                created_by="user_123",
                organization_id="org_456"
            )

        with pytest.raises(ValidationError):
            Scenario(
                name="Test",
                description="Test scenario",
                category=ScenarioCategory.CUSTOM,
                exercise_type=ExerciseType.TABLETOP,
                duration_minutes=60,
                complexity_level=6,  # > 5
                created_by="user_123",
                organization_id="org_456"
            )

    def test_default_values(self):
        """Test default values"""
        scenario = Scenario(
            name="Test Scenario",
            description="Test description here",
            category=ScenarioCategory.CUSTOM,
            exercise_type=ExerciseType.SIMULATION,
            duration_minutes=60,
            created_by="user_123",
            organization_id="org_456"
        )

        assert scenario.complexity_level == 1
        assert scenario.required_participants == 1
        assert scenario.incidents == []
        assert scenario.affected_processes == []
        assert scenario.tags == []
        assert scenario.source == "custom"
        assert scenario.usage_count == 0


class TestSimulationEvent:
    """Tests for SimulationEvent model"""

    def test_create_event(self):
        """Test creating a simulation event"""
        event = SimulationEvent(
            simulation_id="sim_abc123",
            event_type="incident",
            elapsed_seconds=900,
            description="Ransomware detected on file server",
            severity="critical"
        )

        assert event.simulation_id == "sim_abc123"
        assert event.event_type == "incident"
        assert event.elapsed_seconds == 900
        assert event.severity == "critical"
        assert event.id.startswith("event_")
        assert isinstance(event.timestamp, datetime)


class TestExerciseMetrics:
    """Tests for ExerciseMetrics model"""

    def test_create_metrics(self):
        """Test creating exercise metrics"""
        metrics = ExerciseMetrics(
            rto_achieved={"process_a": 300.0, "process_b": 450.0},
            recovery_success_rate=0.95,
            incidents_total=5,
            incidents_handled=4,
            average_response_time=180.0
        )

        assert metrics.rto_achieved["process_a"] == 300.0
        assert metrics.recovery_success_rate == 0.95
        assert metrics.incidents_total == 5
        assert metrics.incidents_handled == 4

    def test_success_rate_validation(self):
        """Test success rate bounds"""
        with pytest.raises(ValidationError):
            ExerciseMetrics(recovery_success_rate=1.5)  # > 1.0

        with pytest.raises(ValidationError):
            ExerciseMetrics(recovery_success_rate=-0.1)  # < 0.0


class TestSimulationResult:
    """Tests for SimulationResult model"""

    def test_create_result(self):
        """Test creating simulation result"""
        metrics = ExerciseMetrics(
            recovery_success_rate=0.90,
            incidents_total=3,
            incidents_handled=2
        )

        result = SimulationResult(
            simulation_id="sim_abc123",
            scenario_id="scenario_xyz789",
            specification_id="spec_def456",
            status=SimulationStatus.COMPLETED,
            duration_seconds=7200,
            metrics=metrics,
            key_findings=["Finding 1", "Finding 2"],
            recommendations=["Recommendation 1"],
            quality_score=8.5
        )

        assert result.simulation_id == "sim_abc123"
        assert result.status == SimulationStatus.COMPLETED
        assert result.duration_seconds == 7200
        assert result.quality_score == 8.5
        assert len(result.key_findings) == 2
        assert result.id.startswith("result_")

    def test_quality_score_validation(self):
        """Test quality score bounds"""
        metrics = ExerciseMetrics()

        with pytest.raises(ValidationError):
            SimulationResult(
                simulation_id="sim_123",
                scenario_id="scenario_123",
                specification_id="spec_123",
                status=SimulationStatus.COMPLETED,
                duration_seconds=100,
                metrics=metrics,
                quality_score=15.0  # > 10.0
            )


class TestSimulation:
    """Tests for Simulation model"""

    def test_create_simulation(self):
        """Test creating a simulation"""
        engine_config = EngineConfig(
            engine_type=EngineType.JAAMSIM,
            max_memory_mb=2048
        )

        simulation = Simulation(
            specification_id="spec_abc123",
            scenario_id="scenario_xyz789",
            engine=EngineType.JAAMSIM,
            engine_config=engine_config,
            created_by="user_123",
            organization_id="org_456"
        )

        assert simulation.specification_id == "spec_abc123"
        assert simulation.engine == EngineType.JAAMSIM
        assert simulation.status == SimulationStatus.PENDING
        assert simulation.progress_percentage == 0.0
        assert simulation.id.startswith("sim_")

    def test_progress_validation(self):
        """Test progress percentage validation"""
        engine_config = EngineConfig(engine_type=EngineType.SIMPY)

        with pytest.raises(ValidationError):
            Simulation(
                specification_id="spec_123",
                scenario_id="scenario_123",
                engine=EngineType.SIMPY,
                engine_config=engine_config,
                created_by="user_123",
                organization_id="org_456",
                progress_percentage=150.0  # > 100.0
            )

    def test_default_configs(self):
        """Test default configuration objects are created"""
        engine_config = EngineConfig(engine_type=EngineType.SIMPY)

        simulation = Simulation(
            specification_id="spec_123",
            scenario_id="scenario_123",
            engine=EngineType.SIMPY,
            engine_config=engine_config,
            created_by="user_123",
            organization_id="org_456"
        )

        assert isinstance(simulation.visualization_config, VisualizationConfig)
        assert isinstance(simulation.integration_config, IntegrationConfig)
        assert isinstance(simulation.report_config, ReportConfig)


class TestSimulationRequest:
    """Tests for SimulationRequest model"""

    def test_create_request(self):
        """Test creating a simulation request"""
        spec = TaskSpecification(
            goal="Test BIA process",
            created_by="user_123",
            organization_id="org_456"
        )

        request = SimulationRequest(
            specification=spec,
            engine=EngineType.JAAMSIM,
            auto_start=True,
            participants=["user_123", "user_456"]
        )

        assert request.specification.goal == "Test BIA process"
        assert request.engine == EngineType.JAAMSIM
        assert request.auto_start is True
        assert len(request.participants) == 2

    def test_minimal_request(self):
        """Test minimal request with only required fields"""
        spec = TaskSpecification(
            goal="Test BIA process",
            created_by="user_123",
            organization_id="org_456"
        )

        request = SimulationRequest(specification=spec)

        assert request.auto_start is False
        assert request.participants == []
        assert request.observers == []
        assert request.engine is None


class TestSimulationState:
    """Tests for SimulationState model"""

    def test_create_state(self):
        """Test creating simulation state"""
        state = SimulationState(
            simulation_id="sim_abc123",
            status=SimulationStatus.RUNNING,
            progress_percentage=45.5,
            current_phase="Incident injection phase",
            elapsed_seconds=1800,
            estimated_remaining=2000,
            events_processed=250
        )

        assert state.simulation_id == "sim_abc123"
        assert state.status == SimulationStatus.RUNNING
        assert state.progress_percentage == 45.5
        assert state.elapsed_seconds == 1800
        assert state.events_processed == 250

    def test_progress_bounds(self):
        """Test progress percentage validation"""
        with pytest.raises(ValidationError):
            SimulationState(
                simulation_id="sim_123",
                status=SimulationStatus.RUNNING,
                progress_percentage=-5.0  # < 0.0
            )


class TestModelSerialization:
    """Tests for model serialization and deserialization"""

    def test_task_specification_round_trip(self):
        """Test TaskSpecification serialization round trip"""
        spec = TaskSpecification(
            goal="Test serialization",
            created_by="user_123",
            organization_id="org_456"
        )

        # Serialize to JSON
        json_str = spec.model_dump_json()

        # Deserialize back
        spec2 = TaskSpecification.model_validate_json(json_str)

        assert spec2.goal == spec.goal
        assert spec2.created_by == spec.created_by
        assert spec2.id == spec.id

    def test_simulation_round_trip(self):
        """Test Simulation serialization round trip"""
        engine_config = EngineConfig(engine_type=EngineType.SIMPY)

        sim = Simulation(
            specification_id="spec_123",
            scenario_id="scenario_123",
            engine=EngineType.SIMPY,
            engine_config=engine_config,
            created_by="user_123",
            organization_id="org_456"
        )

        # Serialize to dict
        sim_dict = sim.model_dump()

        # Deserialize back
        sim2 = Simulation.model_validate(sim_dict)

        assert sim2.id == sim.id
        assert sim2.engine == sim.engine
        assert sim2.status == sim.status


class TestEnums:
    """Tests for enum values"""

    def test_engine_type_values(self):
        """Test EngineType enum"""
        assert EngineType.JAAMSIM.value == "jaamsim"
        assert EngineType.SIMPY.value == "simpy"
        assert EngineType.MONTE_CARLO.value == "monte_carlo"
        assert EngineType.WHAT_IF.value == "what_if"
        assert EngineType.WORKFLOW.value == "workflow"

    def test_simulation_status_values(self):
        """Test SimulationStatus enum"""
        assert SimulationStatus.PENDING.value == "pending"
        assert SimulationStatus.RUNNING.value == "running"
        assert SimulationStatus.COMPLETED.value == "completed"
        assert SimulationStatus.FAILED.value == "failed"

    def test_scenario_category_values(self):
        """Test ScenarioCategory enum"""
        assert ScenarioCategory.DISASTER_RECOVERY.value == "disaster_recovery"
        assert ScenarioCategory.CYBER_SECURITY.value == "cyber_security"
        assert ScenarioCategory.BIA_EXERCISE.value == "bia_exercise"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
