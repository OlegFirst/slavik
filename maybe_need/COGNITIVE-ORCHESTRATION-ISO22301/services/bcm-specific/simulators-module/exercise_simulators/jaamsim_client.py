# -*- coding: utf-8 -*-
"""
JaamSim Integration Client for BCM Platform
Provides simulation capabilities for business continuity exercises and training
"""
import os
import json
import subprocess
import logging
import asyncio
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import requests
import zipfile
import shutil
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

@dataclass
class ExerciseScenario:
    """BCM exercise scenario definition"""
    id: str
    name: str
    description: str
    scenario_type: str  # tabletop, functional, full_scale, simulation
    duration_minutes: int
    participants: List[str]
    objectives: List[str]
    injects: List[Dict[str, Any]]
    success_criteria: List[str]
    resources_required: List[str]
    company_id: str

@dataclass
class SimulationEntity:
    """JaamSim simulation entity"""
    name: str
    entity_type: str  # Server, Database, Network, Process, Person
    properties: Dict[str, Any]
    location: Optional[str] = None
    dependencies: List[str] = None
    capacity: Optional[float] = None
    failure_probability: Optional[float] = None

@dataclass
class SimulationEvent:
    """Simulation event/inject"""
    id: str
    name: str
    event_type: str  # failure, recovery, communication, decision
    trigger_time: float
    target_entity: str
    parameters: Dict[str, Any]
    expected_response: str

@dataclass
class ExerciseResult:
    """Exercise execution results"""
    exercise_id: str
    start_time: datetime
    end_time: datetime
    participants_count: int
    objectives_met: List[str]
    response_times: Dict[str, float]
    decisions_made: List[Dict[str, Any]]
    lessons_learned: List[str]
    improvement_actions: List[str]
    compliance_score: float

class JaamSimClient:
    """JaamSim simulation engine client for BCM exercises"""
    
    def __init__(self, jaamsim_path: str = "/opt/jaamsim", 
                 working_dir: str = "/tmp/bcm_simulations"):
        self.jaamsim_path = Path(jaamsim_path)
        self.working_dir = Path(working_dir)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        
        # BCM-specific simulation templates
        self.bcm_templates = {
            "it_failure": "templates/it_system_failure.cfg",
            "pandemic": "templates/pandemic_response.cfg", 
            "natural_disaster": "templates/natural_disaster.cfg",
            "cyber_attack": "templates/cyber_incident.cfg",
            "supply_chain": "templates/supply_chain_disruption.cfg",
            "data_breach": "templates/data_breach_response.cfg"
        }
        
    def create_bcm_simulation(self, scenario: ExerciseScenario) -> str:
        """Create JaamSim simulation model for BCM exercise"""
        simulation_id = str(uuid.uuid4())
        sim_dir = self.working_dir / simulation_id
        sim_dir.mkdir(exist_ok=True)
        
        try:
            # Generate simulation configuration
            config_file = sim_dir / f"{scenario.name}.cfg"
            self._generate_simulation_config(scenario, config_file)
            
            # Create entity definitions
            entities_file = sim_dir / "entities.inc"
            self._create_simulation_entities(scenario, entities_file)
            
            # Define event schedule
            events_file = sim_dir / "events.inc" 
            self._create_event_schedule(scenario, events_file)
            
            # Generate monitoring scripts
            monitor_file = sim_dir / "monitor.py"
            self._create_monitoring_script(scenario, monitor_file)
            
            logger.info(f"Created BCM simulation: {simulation_id}")
            return simulation_id
            
        except Exception as e:
            logger.error(f"Failed to create simulation: {e}")
            shutil.rmtree(sim_dir, ignore_errors=True)
            raise
    
    def _generate_simulation_config(self, scenario: ExerciseScenario, config_file: Path):
        """Generate JaamSim configuration file"""
        config_content = f"""
# BCM Exercise Simulation: {scenario.name}
# Generated: {datetime.now().isoformat()}
# Scenario Type: {scenario.scenario_type}

RecordEdits

Define DiscreteDistribution {{ UniformDist }}
Define ExponentialDistribution {{ ExpDist }}
Define LogNormalDistribution {{ LogNormDist }}
Define NormalDistribution {{ NormDist }}
Define UniformDistribution {{ UnifDist }}

# Simulation parameters
Define SimulationRun {{ ExerciseRun }}
ExerciseRun Description {{ 'BCM Exercise: {scenario.name}' }}
ExerciseRun RunDuration {{ {scenario.duration_minutes} min }}
ExerciseRun PauseTime {{ 0 s }}

# Global settings
Define GlobalSubmodel {{ BCM_Model }}
BCM_Model Description {{ 'BCM Platform Exercise Model' }}

# Statistics collection
Define Statistics {{ ExerciseStats }}
ExerciseStats SampleValue {{ '[ExerciseRun].SimTime' }}
ExerciseStats UnitType {{ TimeUnit }}

# Include entity definitions
Include entities.inc

# Include event schedule  
Include events.inc

# Output configuration
Define FileToWrite {{ ResultsFile }}
ResultsFile DataSource {{ ExerciseStats }}
ResultsFile OutputFile {{ 'results.csv' }}

# View configuration
Define View {{ ExerciseView }}
ExerciseView Description {{ 'BCM Exercise Visualization' }}
ExerciseView ViewCenter {{ 0 0 0 m }}
ExerciseView ViewPosition {{ -10 -10 15 m }}
ExerciseView ShowLabels {{ TRUE }}
ExerciseView ShowSubModels {{ TRUE }}
"""
        
        config_file.write_text(config_content)
    
    def _create_simulation_entities(self, scenario: ExerciseScenario, entities_file: Path):
        """Create simulation entities based on scenario"""
        entities_content = f"# BCM Exercise Entities: {scenario.name}\n\n"
        
        # Standard BCM entities
        bcm_entities = [
            {
                "name": "BCM_Coordinator",
                "type": "EntityGenerator", 
                "properties": {
                    "Position": "0 5 0 m",
                    "NextComponent": "Response_Process",
                    "InterArrivalTime": "1 h"
                }
            },
            {
                "name": "IT_Infrastructure", 
                "type": "Server",
                "properties": {
                    "Position": "5 0 0 m",
                    "Capacity": "100",
                    "ServiceTime": "UniformDist 1 5 min"
                }
            },
            {
                "name": "Communication_System",
                "type": "Queue",
                "properties": {
                    "Position": "-5 0 0 m", 
                    "Capacity": "50"
                }
            },
            {
                "name": "Response_Process",
                "type": "Server", 
                "properties": {
                    "Position": "0 -5 0 m",
                    "ServiceTime": "LogNormDist 30 15 min"
                }
            },
            {
                "name": "Decision_Point",
                "type": "Branch",
                "properties": {
                    "Position": "0 0 0 m",
                    "NextComponentList": "Recovery_Process Escalation_Process",
                    "Choice": "1"
                }
            }
        ]
        
        # Add scenario-specific entities
        if scenario.scenario_type == "it_failure":
            bcm_entities.extend([
                {
                    "name": "Backup_System",
                    "type": "Server",
                    "properties": {
                        "Position": "10 0 0 m",
                        "Capacity": "50", 
                        "ServiceTime": "UniformDist 2 8 min"
                    }
                },
                {
                    "name": "Data_Recovery",
                    "type": "Seize",
                    "properties": {
                        "Position": "10 -5 0 m",
                        "ResourceName": "Recovery_Team"
                    }
                }
            ])
        elif scenario.scenario_type == "pandemic":
            bcm_entities.extend([
                {
                    "name": "Remote_Workers",
                    "type": "EntityGenerator",
                    "properties": {
                        "Position": "-10 5 0 m",
                        "InterArrivalTime": "30 min"
                    }
                },
                {
                    "name": "Health_Check",
                    "type": "Server", 
                    "properties": {
                        "Position": "-10 0 0 m",
                        "ServiceTime": "UniformDist 5 15 min"
                    }
                }
            ])
        
        # Generate entity definitions
        for entity in bcm_entities:
            entities_content += f"Define {entity['type']} {{ {entity['name']} }}\n"
            for prop, value in entity['properties'].items():
                entities_content += f"{entity['name']} {prop} {{ {value} }}\n"
            entities_content += "\n"
        
        # Add resources
        entities_content += "# BCM Resources\n"
        entities_content += "Define Resource { Recovery_Team }\n"
        entities_content += "Recovery_Team Capacity { 5 }\n\n"
        entities_content += "Define Resource { Communication_Team }\n" 
        entities_content += "Communication_Team Capacity { 3 }\n\n"
        
        entities_file.write_text(entities_content)
    
    def _create_event_schedule(self, scenario: ExerciseScenario, events_file: Path):
        """Create event schedule for exercise injects"""
        events_content = f"# BCM Exercise Events: {scenario.name}\n\n"
        
        # Define event controller
        events_content += "Define EventManager { ExerciseController }\n"
        events_content += "ExerciseController Description { 'Controls exercise event injection' }\n\n"
        
        # Standard BCM events based on scenario type
        standard_events = []
        
        if scenario.scenario_type == "it_failure":
            standard_events = [
                {"time": "5 min", "event": "SystemFailure", "target": "IT_Infrastructure"},
                {"time": "15 min", "event": "InitiateResponse", "target": "BCM_Coordinator"},
                {"time": "30 min", "event": "ActivateBackup", "target": "Backup_System"},
                {"time": "45 min", "event": "CommunicateStatus", "target": "Communication_System"}
            ]
        elif scenario.scenario_type == "pandemic":
            standard_events = [
                {"time": "10 min", "event": "HealthAlert", "target": "Health_Check"},
                {"time": "20 min", "event": "RemoteWorkActivation", "target": "Remote_Workers"},
                {"time": "40 min", "event": "SupplyChainImpact", "target": "Response_Process"}
            ]
        
        # Add custom injects from scenario
        for inject in scenario.injects:
            standard_events.append({
                "time": f"{inject.get('time_minutes', 0)} min",
                "event": inject.get('event_type', 'CustomInject'),
                "target": inject.get('target', 'Response_Process'),
                "description": inject.get('description', '')
            })
        
        # Generate event definitions
        for i, event in enumerate(standard_events):
            event_name = f"Event_{i+1}"
            events_content += f"Define TimedEvent {{ {event_name} }}\n"
            events_content += f"{event_name} FirstOccurrenceTime {{ {event['time']} }}\n"
            events_content += f"{event_name} TargetInput {{ {event['target']} }}\n"
            events_content += f"{event_name} ActionCommand {{ 'BCM_Event_{event['event']}' }}\n\n"
        
        events_file.write_text(events_content)
    
    def _create_monitoring_script(self, scenario: ExerciseScenario, monitor_file: Path):
        """Create Python monitoring script for simulation"""
        monitor_content = f"""#!/usr/bin/env python3
# BCM Exercise Monitoring Script
# Exercise: {scenario.name}
# Generated: {datetime.now().isoformat()}

import json
import time
import csv
import requests
from datetime import datetime
from pathlib import Path

class BCMExerciseMonitor:
    def __init__(self, exercise_id="{scenario.id}"):
        self.exercise_id = exercise_id
        self.start_time = datetime.now()
        self.metrics = []
        self.bcm_api_url = os.getenv('BCM_API_URL', 'http://localhost:8069')
        self.api_key = os.getenv('BCM_API_KEY', '')
        
    def log_event(self, event_type, entity, details):
        \"\"\"Log exercise event\"\"\"
        event = {{
            'timestamp': datetime.now().isoformat(),
            'exercise_id': self.exercise_id,
            'event_type': event_type,
            'entity': entity,
            'details': details
        }}
        self.metrics.append(event)
        print(f"[{{event['timestamp']}}] {{event_type}}: {{entity}} - {{details}}")
        
        # Send to BCM Platform
        try:
            requests.post(
                f"{{self.bcm_api_url}}/api/v1/exercise/event",
                json=event,
                headers={{'Authorization': f'Bearer {{self.api_key}}'}},
                timeout=5
            )
        except Exception as e:
            print(f"Failed to send event to BCM Platform: {{e}}")
    
    def monitor_simulation(self, duration_minutes={scenario.duration_minutes}):
        \"\"\"Monitor simulation execution\"\"\"
        end_time = time.time() + (duration_minutes * 60)
        
        self.log_event('EXERCISE_START', 'BCM_Coordinator', 
                      'Exercise simulation started')
        
        # Monitor key metrics
        while time.time() < end_time:
            try:
                # Read simulation statistics
                if Path('results.csv').exists():
                    with open('results.csv', 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            self.log_event('METRIC_UPDATE', 'Simulation',
                                         f"Time: {{row.get('Time', 'N/A')}}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Monitoring error: {{e}}")
                time.sleep(10)
        
        self.log_event('EXERCISE_END', 'BCM_Coordinator',
                      'Exercise simulation completed')
        
        # Generate final report
        self.generate_report()
    
    def generate_report(self):
        \"\"\"Generate exercise report\"\"\"
        report = {{
            'exercise_id': self.exercise_id,
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'events_count': len(self.metrics),
            'events': self.metrics,
            'objectives': {json.dumps(scenario.objectives)},
            'success_criteria': {json.dumps(scenario.success_criteria)}
        }}
        
        report_file = f'exercise_report_{{self.exercise_id}}.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Exercise report saved to: {{report_file}}")
        
        # Send report to BCM Platform
        try:
            requests.post(
                f"{{self.bcm_api_url}}/api/v1/exercise/report",
                json=report,
                headers={{'Authorization': f'Bearer {{self.api_key}}'}},
                timeout=30
            )
            print("Report sent to BCM Platform")
        except Exception as e:
            print(f"Failed to send report to BCM Platform: {{e}}")

if __name__ == '__main__':
    monitor = BCMExerciseMonitor()
    monitor.monitor_simulation()
"""
        
        monitor_file.write_text(monitor_content)
        monitor_file.chmod(0o755)
    
    async def run_simulation(self, simulation_id: str, 
                           headless: bool = True) -> Dict[str, Any]:
        """Execute JaamSim simulation"""
        sim_dir = self.working_dir / simulation_id
        if not sim_dir.exists():
            raise FileNotFoundError(f"Simulation {simulation_id} not found")
        
        config_files = list(sim_dir.glob("*.cfg"))
        if not config_files:
            raise FileNotFoundError("No simulation configuration found")
        
        config_file = config_files[0]
        
        # Prepare JaamSim command
        jaamsim_jar = self.jaamsim_path / "JaamSim2023-03.jar"
        if not jaamsim_jar.exists():
            raise FileNotFoundError(f"JaamSim not found at {jaamsim_jar}")
        
        cmd = [
            "java", "-jar", str(jaamsim_jar),
            str(config_file)
        ]
        
        if headless:
            cmd.extend(["-b", "-m"])  # Batch mode, minimized
        
        try:
            logger.info(f"Starting simulation: {simulation_id}")
            
            # Start monitoring script
            monitor_script = sim_dir / "monitor.py"
            monitor_process = None
            if monitor_script.exists():
                monitor_process = await asyncio.create_subprocess_exec(
                    "python3", str(monitor_script),
                    cwd=str(sim_dir),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            
            # Run simulation
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(sim_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Wait for monitor to complete
            if monitor_process:
                await monitor_process.wait()
            
            if process.returncode == 0:
                logger.info(f"Simulation {simulation_id} completed successfully")
                return await self._collect_results(sim_dir)
            else:
                error_msg = stderr.decode('utf-8')
                logger.error(f"Simulation failed: {error_msg}")
                raise RuntimeError(f"Simulation failed: {error_msg}")
        
        except Exception as e:
            logger.error(f"Failed to run simulation: {e}")
            raise
    
    async def _collect_results(self, sim_dir: Path) -> Dict[str, Any]:
        """Collect and analyze simulation results"""
        results = {
            "simulation_id": sim_dir.name,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "files_generated": [],
            "metrics": {},
            "events": []
        }
        
        # Collect generated files
        for file_path in sim_dir.iterdir():
            if file_path.is_file():
                results["files_generated"].append(file_path.name)
        
        # Parse results CSV if exists
        results_csv = sim_dir / "results.csv"
        if results_csv.exists():
            try:
                with open(results_csv, 'r') as f:
                    import csv
                    reader = csv.DictReader(f)
                    metrics_data = list(reader)
                    results["metrics"]["simulation_data"] = metrics_data
            except Exception as e:
                logger.warning(f"Failed to parse results CSV: {e}")
        
        # Parse exercise report if exists
        report_files = list(sim_dir.glob("exercise_report_*.json"))
        if report_files:
            try:
                with open(report_files[0], 'r') as f:
                    report_data = json.load(f)
                    results["events"] = report_data.get("events", [])
                    results["exercise_summary"] = {
                        "start_time": report_data.get("start_time"),
                        "end_time": report_data.get("end_time"), 
                        "events_count": report_data.get("events_count", 0),
                        "objectives": report_data.get("objectives", []),
                        "success_criteria": report_data.get("success_criteria", [])
                    }
            except Exception as e:
                logger.warning(f"Failed to parse exercise report: {e}")
        
        return results
    
    def cleanup_simulation(self, simulation_id: str):
        """Clean up simulation files"""
        sim_dir = self.working_dir / simulation_id
        if sim_dir.exists():
            shutil.rmtree(sim_dir)
            logger.info(f"Cleaned up simulation: {simulation_id}")


class BCMExerciseSimulator:
    """High-level BCM exercise simulation manager"""
    
    def __init__(self, jaamsim_client: JaamSimClient):
        self.jaamsim = jaamsim_client
        self.active_exercises = {}
        
    async def create_bcm_exercise(self, scenario: ExerciseScenario) -> str:
        """Create and prepare BCM exercise simulation"""
        try:
            simulation_id = self.jaamsim.create_bcm_simulation(scenario)
            
            self.active_exercises[scenario.id] = {
                "simulation_id": simulation_id,
                "scenario": scenario,
                "status": "prepared",
                "created_at": datetime.now()
            }
            
            logger.info(f"BCM exercise prepared: {scenario.id}")
            return scenario.id
            
        except Exception as e:
            logger.error(f"Failed to create BCM exercise: {e}")
            raise
    
    async def execute_exercise(self, exercise_id: str) -> ExerciseResult:
        """Execute BCM exercise simulation"""
        if exercise_id not in self.active_exercises:
            raise ValueError(f"Exercise {exercise_id} not found")
        
        exercise_info = self.active_exercises[exercise_id]
        scenario = exercise_info["scenario"]
        simulation_id = exercise_info["simulation_id"]
        
        try:
            # Update status
            exercise_info["status"] = "running"
            exercise_info["started_at"] = datetime.now()
            
            # Execute simulation
            sim_results = await self.jaamsim.run_simulation(simulation_id)
            
            # Process results into BCM exercise result
            result = ExerciseResult(
                exercise_id=exercise_id,
                start_time=exercise_info["started_at"],
                end_time=datetime.now(),
                participants_count=len(scenario.participants),
                objectives_met=scenario.objectives,  # TODO: Analyze actual completion
                response_times={},  # TODO: Extract from simulation
                decisions_made=[],  # TODO: Extract decision points
                lessons_learned=[],  # TODO: Generate from simulation
                improvement_actions=[],  # TODO: Generate recommendations
                compliance_score=0.85  # TODO: Calculate based on criteria
            )
            
            # Update exercise status
            exercise_info["status"] = "completed"
            exercise_info["completed_at"] = datetime.now()
            exercise_info["results"] = result
            
            logger.info(f"BCM exercise completed: {exercise_id}")
            return result
            
        except Exception as e:
            exercise_info["status"] = "failed"
            exercise_info["error"] = str(e)
            logger.error(f"BCM exercise failed: {exercise_id} - {e}")
            raise
    
    def get_exercise_status(self, exercise_id: str) -> Dict[str, Any]:
        """Get exercise status and progress"""
        if exercise_id not in self.active_exercises:
            raise ValueError(f"Exercise {exercise_id} not found")
        
        return self.active_exercises[exercise_id]
    
    def list_active_exercises(self) -> List[Dict[str, Any]]:
        """List all active exercises"""
        return list(self.active_exercises.values())
    
    def cleanup_exercise(self, exercise_id: str):
        """Clean up exercise resources"""
        if exercise_id in self.active_exercises:
            exercise_info = self.active_exercises[exercise_id]
            simulation_id = exercise_info.get("simulation_id")
            
            if simulation_id:
                self.jaamsim.cleanup_simulation(simulation_id)
            
            del self.active_exercises[exercise_id]
            logger.info(f"Cleaned up exercise: {exercise_id}")
