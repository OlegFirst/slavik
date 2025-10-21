"""
JaamSim Simulation Engine

Integrates with JaamSim discrete-event simulation software.

Uses existing JaamSim configuration generator from Scenario Orchestrator service
for automated config file generation based on scenario parameters.

JaamSim Features:
- 3D visualization
- Discrete event simulation
- Process modeling
- Statistical analysis
- Complex scenario support

Integration:
- Uses configs from scenario_orchestrator_client
- Executes JaamSim Java process
- Monitors execution
- Collects results
"""

import logging
import subprocess
import asyncio
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json

from models.pydantic_models import (
    Scenario,
    SimulationResult,
    SimulationStatus,
    EngineConfig
)
from config.settings import Settings

logger = logging.getLogger(__name__)


class JaamSimEngine:
    """
    JaamSim simulation engine wrapper

    Provides:
    - Configuration file generation (via ScenarioOrchestratorClient)
    - JaamSim process execution
    - Real-time monitoring
    - Result collection and parsing
    """

    def __init__(self, settings: Settings):
        """
        Initialize JaamSim engine

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.jaamsim_path = settings.jaamsim_path
        self.jaamsim_jar = settings.jaamsim_jar
        self.jaamsim_executable = settings.jaamsim_executable
        self.working_dir = Path(settings.simulation_working_dir)
        self.enabled = settings.jaamsim_enabled

        self.process: Optional[subprocess.Popen] = None
        self.simulation_id: Optional[str] = None
        self.config_file: Optional[Path] = None
        self.output_file: Optional[Path] = None
        self.status = SimulationStatus.PENDING

    async def initialize(
        self,
        simulation_id: str,
        scenario: Scenario,
        config: EngineConfig,
        jaamsim_config_str: Optional[str] = None
    ) -> bool:
        """
        Initialize JaamSim engine

        Args:
            simulation_id: Simulation ID
            scenario: Scenario to simulate
            config: Engine configuration
            jaamsim_config_str: Pre-generated JaamSim config string (from ScenarioOrchestratorClient)

        Returns:
            True if initialized successfully
        """
        if not self.enabled:
            logger.error("JaamSim engine is disabled")
            return False

        try:
            self.simulation_id = simulation_id
            self.status = SimulationStatus.INITIALIZING

            # Create working directory for this simulation
            sim_working_dir = self.working_dir / simulation_id
            sim_working_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Initializing JaamSim engine for simulation {simulation_id}")

            # Check if JaamSim is installed
            if not self._check_jaamsim_installed():
                logger.error(f"JaamSim not found at {self.jaamsim_executable}")
                return False

            # Generate or use provided JaamSim configuration
            if jaamsim_config_str:
                logger.info("Using provided JaamSim configuration")
                config_content = jaamsim_config_str
            else:
                logger.info("Generating default JaamSim configuration")
                config_content = self._generate_default_config(scenario, config)

            # Save configuration file
            self.config_file = sim_working_dir / f"{simulation_id}.cfg"
            with open(self.config_file, 'w') as f:
                f.write(config_content)

            logger.info(f"JaamSim config saved: {self.config_file}")

            # Set output file path
            self.output_file = sim_working_dir / f"{simulation_id}_output.dat"

            logger.info(" JaamSim engine initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize JaamSim engine: {e}")
            self.status = SimulationStatus.FAILED
            return False

    async def run(self) -> SimulationResult:
        """
        Execute JaamSim simulation

        Returns:
            SimulationResult with execution data
        """
        if not self.config_file or not self.config_file.exists():
            raise ValueError("Engine not initialized or config file missing")

        try:
            self.status = SimulationStatus.RUNNING
            start_time = datetime.utcnow()

            logger.info(f"Starting JaamSim execution: {self.simulation_id}")

            # Build JaamSim command
            # JaamSim can run in batch mode: java -jar JaamSim.jar -b configfile.cfg
            command = [
                "java",
                "-jar",
                self.jaamsim_executable,
                "-b",  # Batch mode (no GUI)
                str(self.config_file)
            ]

            logger.info(f"Executing command: {' '.join(command)}")

            # Execute JaamSim
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.config_file.parent)
            )

            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    asyncio.create_task(
                        asyncio.to_thread(self.process.communicate)
                    ),
                    timeout=self.settings.max_simulation_duration_hours * 3600
                )

                return_code = self.process.returncode

                end_time = datetime.utcnow()
                duration_seconds = (end_time - start_time).total_seconds()

                logger.info(f"JaamSim execution completed: return_code={return_code}, "
                           f"duration={duration_seconds}s")

                # Parse results
                results = self._parse_results(stdout, stderr, return_code)

                # Build SimulationResult
                simulation_result = SimulationResult(
                    simulation_id=self.simulation_id,
                    status="completed" if return_code == 0 else "failed",
                    started_at=start_time,
                    completed_at=end_time,
                    duration_seconds=int(duration_seconds),
                    engine_used="jaamsim",
                    overall_success_rate=results.get("success_rate", 0.0),
                    quality_score=results.get("quality_score", 0.0),
                    complexity_level=results.get("complexity_level", 3),
                    metrics=results.get("metrics", {}),
                    detailed_metrics=results.get("detailed_metrics", {}),
                    events=results.get("events", []),
                    participant_performance=results.get("participant_performance", []),
                    success_criteria=results.get("success_criteria", []),
                    kpis_achieved=results.get("kpis_achieved", []),
                    lessons_learned=results.get("lessons_learned", []),
                    recommendations=results.get("recommendations", []),
                    improvement_areas=results.get("improvement_areas", [])
                )

                self.status = SimulationStatus.COMPLETED
                return simulation_result

            except asyncio.TimeoutError:
                logger.error(f"JaamSim execution timed out after {self.settings.max_simulation_duration_hours} hours")
                self.process.kill()
                self.status = SimulationStatus.FAILED

                return SimulationResult(
                    simulation_id=self.simulation_id,
                    status="failed",
                    started_at=start_time,
                    completed_at=datetime.utcnow(),
                    duration_seconds=int((datetime.utcnow() - start_time).total_seconds()),
                    engine_used="jaamsim",
                    overall_success_rate=0.0,
                    quality_score=0.0,
                    complexity_level=3,
                    metrics={"error": "timeout"},
                    detailed_metrics={},
                    events=[],
                    participant_performance=[],
                    success_criteria=[],
                    kpis_achieved=[],
                    lessons_learned=["Simulation timed out - consider reducing complexity"],
                    recommendations=["Optimize simulation parameters", "Check JaamSim configuration"],
                    improvement_areas=["Execution timeout"]
                )

        except Exception as e:
            logger.error(f"JaamSim execution failed: {e}", exc_info=True)
            self.status = SimulationStatus.FAILED

            return SimulationResult(
                simulation_id=self.simulation_id,
                status="failed",
                started_at=start_time,
                completed_at=datetime.utcnow(),
                duration_seconds=0,
                engine_used="jaamsim",
                overall_success_rate=0.0,
                quality_score=0.0,
                complexity_level=3,
                metrics={"error": str(e)},
                detailed_metrics={},
                events=[],
                participant_performance=[],
                success_criteria=[],
                kpis_achieved=[],
                lessons_learned=[f"Execution error: {str(e)}"],
                recommendations=["Check JaamSim installation", "Verify configuration"],
                improvement_areas=["Execution error"]
            )

    async def pause(self) -> bool:
        """
        Pause simulation (not supported by JaamSim in batch mode)

        Returns:
            False (not supported)
        """
        logger.warning("Pause not supported in JaamSim batch mode")
        return False

    async def resume(self) -> bool:
        """
        Resume simulation (not supported by JaamSim in batch mode)

        Returns:
            False (not supported)
        """
        logger.warning("Resume not supported in JaamSim batch mode")
        return False

    async def stop(self) -> bool:
        """
        Stop simulation

        Returns:
            True if stopped successfully
        """
        if self.process and self.process.poll() is None:
            logger.info(f"Stopping JaamSim simulation: {self.simulation_id}")
            self.process.terminate()
            try:
                await asyncio.wait_for(
                    asyncio.create_task(asyncio.to_thread(self.process.wait)),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                logger.warning("JaamSim didn't terminate gracefully, killing process")
                self.process.kill()

            self.status = SimulationStatus.CANCELLED
            return True

        return False

    async def get_status(self) -> Dict[str, Any]:
        """
        Get current simulation status

        Returns:
            Status dictionary
        """
        is_running = self.process and self.process.poll() is None

        return {
            "simulation_id": self.simulation_id,
            "engine": "jaamsim",
            "status": self.status.value if isinstance(self.status, SimulationStatus) else str(self.status),
            "is_running": is_running,
            "config_file": str(self.config_file) if self.config_file else None,
            "output_file": str(self.output_file) if self.output_file else None
        }

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _check_jaamsim_installed(self) -> bool:
        """Check if JaamSim is installed and accessible"""
        jaamsim_jar_path = Path(self.jaamsim_executable)
        return jaamsim_jar_path.exists()

    def _generate_default_config(
        self,
        scenario: Scenario,
        config: EngineConfig
    ) -> str:
        """
        Generate default JaamSim configuration

        This is a fallback if no config is provided from ScenarioOrchestratorClient.
        For production use, prefer using the ScenarioOrchestratorClient's generator.

        Args:
            scenario: Scenario to simulate
            config: Engine configuration

        Returns:
            JaamSim configuration string
        """
        duration_hours = config.parameters.get("duration_hours", 4)
        participants = config.parameters.get("participants", 10)

        config_str = f"""# JaamSim Configuration - Generated by Simulation Service
# Simulation ID: {self.simulation_id}
# Generated: {datetime.utcnow().isoformat()}

RecordEdits

# Define distributions
Define DiscreteDistribution {{ ImpactDistribution }}
Define ExponentialDistribution {{ RecoveryDistribution }}

ImpactDistribution ValueList {{ 1 2 3 4 5 }}
ImpactDistribution ProbabilityList {{ 0.1 0.2 0.4 0.2 0.1 }}

RecoveryDistribution Mean {{ {duration_hours} h }}

# Define simulation entities
Define EntityGenerator {{ IncidentSource }}
Define Queue {{ ResponseQueue }}
Define Server {{ ResponseTeam }}
Define EntitySink {{ ResolvedIncidents }}

# Configure response team capacity
ResponseTeam Capacity {{ {min(participants, 10)} }}

# Simulation duration
Define SimulationRun {{ BCMExercise }}
BCMExercise RunDuration {{ {duration_hours} h }}

# Connect entities
IncidentSource NextComponent {{ ResponseQueue }}
ResponseQueue NextComponent {{ ResponseTeam }}
ResponseTeam NextComponent {{ ResolvedIncidents }}

# Output configuration
"""

        return config_str

    def _parse_results(
        self,
        stdout: bytes,
        stderr: bytes,
        return_code: int
    ) -> Dict[str, Any]:
        """
        Parse JaamSim execution results

        Args:
            stdout: Standard output
            stderr: Standard error
            return_code: Process return code

        Returns:
            Parsed results dictionary
        """
        results = {
            "success_rate": 1.0 if return_code == 0 else 0.0,
            "quality_score": 8.0 if return_code == 0 else 3.0,
            "complexity_level": 4,  # JaamSim is for complex scenarios
            "metrics": {
                "return_code": return_code,
                "stdout_length": len(stdout),
                "stderr_length": len(stderr)
            },
            "detailed_metrics": {
                "stdout": stdout.decode('utf-8', errors='ignore')[:1000],  # First 1000 chars
                "stderr": stderr.decode('utf-8', errors='ignore')[:1000]
            },
            "events": [],
            "participant_performance": [],
            "success_criteria": ["JaamSim execution completed" if return_code == 0 else "Execution failed"],
            "kpis_achieved": ["Simulation executed"] if return_code == 0 else [],
            "lessons_learned": [
                "JaamSim simulation completed" if return_code == 0 else "Check JaamSim logs for errors"
            ],
            "recommendations": [
                "Review JaamSim output files for detailed results",
                "Analyze simulation statistics"
            ],
            "improvement_areas": [] if return_code == 0 else ["Execution errors encountered"]
        }

        # Try to parse output file if it exists
        if self.output_file and self.output_file.exists():
            try:
                with open(self.output_file, 'r') as f:
                    output_data = f.read()
                    results["detailed_metrics"]["output_file"] = output_data[:2000]
                    logger.info("JaamSim output file parsed successfully")
            except Exception as e:
                logger.warning(f"Failed to parse JaamSim output file: {e}")

        return results

    async def cleanup(self):
        """Clean up resources after simulation"""
        if self.process:
            await self.stop()

        logger.info(f"JaamSim engine cleanup completed for {self.simulation_id}")
