"""
Process Visualization Module

Provides comprehensive visualization capabilities for the Process Framework:
- Mermaid diagram generation for process flows
- Real-time process status tracking
- Execution timeline analysis
- JSON export for frontend visualization libraries

This module enables visual representation of business processes and their execution state.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
from pathlib import Path

try:
    from .process_framework import (
        ProcessFramework,
        ProcessDefinition,
        ProcessInstance,
        ProcessStep,
        ProcessStatus,
        StepType,
        get_process_framework
    )
except ImportError:
    from process_framework import (
        ProcessFramework,
        ProcessDefinition,
        ProcessInstance,
        ProcessStep,
        ProcessStatus,
        StepType,
        get_process_framework
    )


@dataclass
class StepExecution:
    """Represents a single step execution in the timeline"""
    step_id: str
    step_name: str
    step_type: str
    executed_by: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    status: str
    data: Dict[str, Any]
    result: str


@dataclass
class ProcessStatusInfo:
    """Comprehensive status information for a process instance"""
    instance_id: str
    process_id: str
    process_name: str
    status: str
    current_step: Dict[str, Any]
    completed_steps: List[str]
    remaining_steps: List[str]
    progress_percentage: float
    estimated_completion: Optional[datetime]
    total_duration_seconds: Optional[float]


class ProcessVisualizer:
    """
    Process Visualization Engine

    Generates visual representations of business processes and their execution state.
    Supports multiple output formats including Mermaid diagrams, JSON for D3.js/vis.js,
    and detailed timeline analysis.

    Example:
        >>> from pathlib import Path
        >>> visualizer = ProcessVisualizer()
        >>>
        >>> # Generate Mermaid diagram
        >>> diagram = visualizer.generate_mermaid_diagram("bia_process_v1")
        >>> print(diagram)
        >>>
        >>> # Get current status
        >>> status = visualizer.generate_process_status("bia_process_v1-20250112150000")
        >>> print(f"Progress: {status['progress_percentage']}%")
        >>>
        >>> # Generate timeline
        >>> timeline = visualizer.generate_timeline("bia_process_v1-20250112150000")
        >>> for entry in timeline['entries']:
        >>>     print(f"{entry['step_name']}: {entry['duration_seconds']}s")
    """

    def __init__(self, framework: Optional[ProcessFramework] = None):
        """
        Initialize the ProcessVisualizer

        Args:
            framework: Optional ProcessFramework instance. If not provided, uses singleton.
        """
        self.framework = framework or get_process_framework()

    def generate_mermaid_diagram(self, process_id: str) -> str:
        """
        Generate Mermaid flowchart for a process definition

        Creates a visual flowchart representation using Mermaid syntax that shows:
        - All process steps with their types
        - Transitions between steps
        - Start and end nodes highlighted
        - Decision points and branches

        Args:
            process_id: The ID of the process definition to visualize

        Returns:
            Mermaid flowchart syntax as a string

        Raises:
            ValueError: If process_id is not found

        Example:
            >>> visualizer = ProcessVisualizer()
            >>> mermaid = visualizer.generate_mermaid_diagram("bia_process_v1")
            >>> # Can be rendered in Markdown or Mermaid Live Editor
            >>> print(mermaid)

            flowchart TD
                Start([Start])
                step1[Identify Critical Functions]
                step2[Analyze Dependencies]
                ...
        """
        process = self.framework.processes.get(process_id)
        if not process:
            raise ValueError(f"Process '{process_id}' not found")

        lines = ["flowchart TD"]

        # Start node
        lines.append(f"    Start([Start: {process.name}])")
        lines.append(f"    style Start fill:#90EE90,stroke:#333,stroke-width:2px")

        # Add all steps
        for step_id, step in process.steps.items():
            # Determine node shape based on step type
            node_shape = self._get_mermaid_node_shape(step.step_type)
            label = f"{step.name}\\n[{step.step_type.value}]"

            # Create node
            lines.append(f"    {step_id}{node_shape[0]}{label}{node_shape[1]}")

            # Apply styling based on step type
            style = self._get_mermaid_style(step.step_type)
            if style:
                lines.append(f"    style {step_id} {style}")

        # End nodes
        for end_step_id in process.end_step_ids:
            lines.append(f"    {end_step_id}_end([End: {end_step_id}])")
            lines.append(f"    style {end_step_id}_end fill:#FFB6C1,stroke:#333,stroke-width:2px")

        # Connect start to first step
        lines.append(f"    Start --> {process.start_step_id}")

        # Add transitions
        for step_id, step in process.steps.items():
            for next_step_id in step.next_steps:
                if next_step_id in process.end_step_ids:
                    lines.append(f"    {step_id} --> {next_step_id}_end")
                else:
                    lines.append(f"    {step_id} --> {next_step_id}")

            # Add conditional transitions if any
            if step.transition_conditions:
                for condition_target in step.transition_conditions.keys():
                    if condition_target not in step.next_steps:
                        if condition_target in process.end_step_ids:
                            lines.append(f"    {step_id} -.conditional.-> {condition_target}_end")
                        else:
                            lines.append(f"    {step_id} -.conditional.-> {condition_target}")

        return "\n".join(lines)

    def generate_process_status(self, instance_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive status information for a process instance

        Provides detailed information about the current state of a running process:
        - Current step position and details
        - List of completed steps with timestamps
        - Remaining steps in the process
        - Progress percentage calculation
        - Estimated time to completion based on historical data

        Args:
            instance_id: The ID of the process instance

        Returns:
            Dictionary containing:
                - instance_id: str
                - process_id: str
                - process_name: str
                - status: str (draft, active, in_progress, completed, suspended, cancelled)
                - current_step: dict with step details
                - completed_steps: list of completed step IDs with timestamps
                - remaining_steps: list of pending step IDs
                - progress_percentage: float (0-100)
                - estimated_completion: ISO datetime string or None
                - total_duration_seconds: float or None
                - started_at: ISO datetime string
                - updated_at: ISO datetime string

        Raises:
            ValueError: If instance_id is not found

        Example:
            >>> status = visualizer.generate_process_status("bia_process_v1-20250112150000")
            >>> print(f"Process: {status['process_name']}")
            >>> print(f"Progress: {status['progress_percentage']:.1f}%")
            >>> print(f"Current Step: {status['current_step']['name']}")
            >>> print(f"Completed: {len(status['completed_steps'])} steps")
            >>> print(f"Remaining: {len(status['remaining_steps'])} steps")
        """
        instance = self.framework.instances.get(instance_id)
        if not instance:
            raise ValueError(f"Process instance '{instance_id}' not found")

        process = self.framework.processes.get(instance.process_definition_id)
        if not process:
            raise ValueError(f"Process definition '{instance.process_definition_id}' not found")

        # Get current step details
        current_step = process.get_step(instance.current_step_id)
        current_step_info = {
            "id": current_step.id,
            "name": current_step.name,
            "type": current_step.step_type.value,
            "description": current_step.description,
            "estimated_duration_minutes": current_step.estimated_duration_minutes,
            "sla_hours": current_step.sla_hours
        } if current_step else None

        # Calculate completed and remaining steps
        completed_step_ids = [entry["step_id"] for entry in instance.step_history]
        all_step_ids = list(process.steps.keys())
        remaining_step_ids = [sid for sid in all_step_ids if sid not in completed_step_ids]

        # Calculate progress
        total_steps = len(all_step_ids)
        completed_count = len(completed_step_ids)
        progress = (completed_count / total_steps * 100) if total_steps > 0 else 0.0

        # Calculate total duration
        total_duration = None
        if instance.started_at:
            end_time = instance.completed_at or datetime.now()
            total_duration = (end_time - instance.started_at).total_seconds()

        # Estimate completion time
        estimated_completion = self._estimate_completion_time(
            instance, process, remaining_step_ids
        )

        # Build completed steps with details
        completed_steps_details = []
        for entry in instance.step_history:
            step = process.get_step(entry["step_id"])
            completed_steps_details.append({
                "step_id": entry["step_id"],
                "step_name": step.name if step else "Unknown",
                "timestamp": entry["timestamp"],
                "result": entry.get("result", "unknown")
            })

        return {
            "instance_id": instance.id,
            "process_id": process.id,
            "process_name": process.name,
            "status": instance.status.value,
            "current_step": current_step_info,
            "completed_steps": completed_steps_details,
            "remaining_steps": [
                {
                    "step_id": sid,
                    "step_name": process.get_step(sid).name if process.get_step(sid) else "Unknown",
                    "estimated_duration_minutes": process.get_step(sid).estimated_duration_minutes if process.get_step(sid) else None
                }
                for sid in remaining_step_ids
            ],
            "progress_percentage": round(progress, 2),
            "estimated_completion": estimated_completion.isoformat() if estimated_completion else None,
            "total_duration_seconds": total_duration,
            "started_at": instance.started_at.isoformat() if instance.started_at else None,
            "updated_at": datetime.now().isoformat()
        }

    def generate_timeline(self, instance_id: str) -> Dict[str, Any]:
        """
        Generate detailed execution timeline for a process instance

        Creates a chronological timeline of all step executions with:
        - Step execution order
        - Duration per step
        - Who executed each step
        - Timestamps for each execution
        - Data captured at each step

        Args:
            instance_id: The ID of the process instance

        Returns:
            Dictionary containing:
                - instance_id: str
                - process_name: str
                - timeline_entries: list of execution records
                - total_duration_seconds: float
                - average_step_duration_seconds: float
                - longest_step: dict with step info
                - shortest_step: dict with step info
                - started_at: ISO datetime string
                - last_updated: ISO datetime string

        Raises:
            ValueError: If instance_id is not found

        Example:
            >>> timeline = visualizer.generate_timeline("bia_process_v1-20250112150000")
            >>> print(f"Total Duration: {timeline['total_duration_seconds']}s")
            >>> print(f"Average Step Duration: {timeline['average_step_duration_seconds']}s")
            >>>
            >>> for entry in timeline['timeline_entries']:
            >>>     print(f"{entry['step_name']}: {entry['duration_seconds']}s by {entry['executed_by']}")
        """
        instance = self.framework.instances.get(instance_id)
        if not instance:
            raise ValueError(f"Process instance '{instance_id}' not found")

        process = self.framework.processes.get(instance.process_definition_id)
        if not process:
            raise ValueError(f"Process definition '{instance.process_definition_id}' not found")

        timeline_entries = []
        total_duration = 0.0

        # Process step history
        for i, entry in enumerate(instance.step_history):
            step = process.get_step(entry["step_id"])

            # Parse timestamp
            started_at = datetime.fromisoformat(entry["timestamp"])

            # Calculate duration (estimate based on next step or current time)
            if i + 1 < len(instance.step_history):
                completed_at = datetime.fromisoformat(instance.step_history[i + 1]["timestamp"])
            elif instance.completed_at:
                completed_at = instance.completed_at
            else:
                completed_at = datetime.now()

            duration = (completed_at - started_at).total_seconds()
            total_duration += duration

            timeline_entries.append({
                "sequence": i + 1,
                "step_id": entry["step_id"],
                "step_name": step.name if step else "Unknown",
                "step_type": step.step_type.value if step else "unknown",
                "executed_by": instance.started_by,  # In real system, track per-step
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "duration_seconds": round(duration, 2),
                "status": entry.get("result", "unknown"),
                "data_captured": entry.get("data", {}),
                "estimated_duration_minutes": step.estimated_duration_minutes if step else None,
                "on_schedule": self._is_on_schedule(duration, step) if step else None
            })

        # Calculate statistics
        avg_duration = total_duration / len(timeline_entries) if timeline_entries else 0.0

        longest_step = max(timeline_entries, key=lambda x: x["duration_seconds"]) if timeline_entries else None
        shortest_step = min(timeline_entries, key=lambda x: x["duration_seconds"]) if timeline_entries else None

        return {
            "instance_id": instance.id,
            "process_id": process.id,
            "process_name": process.name,
            "process_status": instance.status.value,
            "timeline_entries": timeline_entries,
            "total_duration_seconds": round(total_duration, 2),
            "average_step_duration_seconds": round(avg_duration, 2),
            "total_steps_executed": len(timeline_entries),
            "longest_step": {
                "step_name": longest_step["step_name"],
                "duration_seconds": longest_step["duration_seconds"]
            } if longest_step else None,
            "shortest_step": {
                "step_name": shortest_step["step_name"],
                "duration_seconds": shortest_step["duration_seconds"]
            } if shortest_step else None,
            "started_at": instance.started_at.isoformat() if instance.started_at else None,
            "last_updated": datetime.now().isoformat()
        }

    def export_to_json(self, process_id: str, include_instances: bool = False) -> str:
        """
        Export process definition to JSON for frontend visualization libraries

        Generates a JSON structure optimized for visualization libraries like:
        - D3.js (force-directed graphs, hierarchical layouts)
        - vis.js (network diagrams)
        - Cytoscape.js (graph visualization)
        - Dagre (directed graph layout)

        Args:
            process_id: The ID of the process definition to export
            include_instances: Whether to include active instances data

        Returns:
            JSON string with nodes and edges structure

        Raises:
            ValueError: If process_id is not found

        Example:
            >>> json_data = visualizer.export_to_json("bia_process_v1")
            >>> # Use in JavaScript:
            >>> # const data = JSON.parse(json_data);
            >>> # new vis.Network(container, data, options);

            >>> # Or with instances:
            >>> json_with_instances = visualizer.export_to_json("bia_process_v1", include_instances=True)
        """
        process = self.framework.processes.get(process_id)
        if not process:
            raise ValueError(f"Process '{process_id}' not found")

        # Build nodes array
        nodes = []

        # Start node
        nodes.append({
            "id": "start",
            "label": f"Start: {process.name}",
            "type": "start",
            "shape": "ellipse",
            "color": "#90EE90",
            "font": {"size": 16, "bold": True}
        })

        # Process steps
        for step_id, step in process.steps.items():
            node = {
                "id": step_id,
                "label": step.name,
                "type": step.step_type.value,
                "description": step.description,
                "shape": self._get_vis_shape(step.step_type),
                "color": self._get_vis_color(step.step_type),
                "metadata": {
                    "allowed_roles": step.allowed_roles,
                    "estimated_duration_minutes": step.estimated_duration_minutes,
                    "sla_hours": step.sla_hours,
                    "auto_approve": step.auto_approve,
                    "has_form": len(step.form_fields) > 0,
                    "form_fields_count": len(step.form_fields)
                }
            }
            nodes.append(node)

        # End nodes
        for end_step_id in process.end_step_ids:
            nodes.append({
                "id": f"{end_step_id}_end",
                "label": f"End: {end_step_id}",
                "type": "end",
                "shape": "ellipse",
                "color": "#FFB6C1",
                "font": {"size": 16, "bold": True}
            })

        # Build edges array
        edges = []

        # Start to first step
        edges.append({
            "from": "start",
            "to": process.start_step_id,
            "arrows": "to",
            "color": "#333333",
            "width": 2
        })

        # Step transitions
        for step_id, step in process.steps.items():
            for next_step_id in step.next_steps:
                target = f"{next_step_id}_end" if next_step_id in process.end_step_ids else next_step_id
                edges.append({
                    "from": step_id,
                    "to": target,
                    "arrows": "to",
                    "color": "#333333",
                    "width": 2,
                    "label": ""
                })

            # Conditional transitions
            if step.transition_conditions:
                for condition_target in step.transition_conditions.keys():
                    if condition_target not in step.next_steps:
                        target = f"{condition_target}_end" if condition_target in process.end_step_ids else condition_target
                        edges.append({
                            "from": step_id,
                            "to": target,
                            "arrows": "to",
                            "color": "#999999",
                            "width": 1,
                            "dashes": True,
                            "label": "conditional"
                        })

        # Build final structure
        result = {
            "process": {
                "id": process.id,
                "name": process.name,
                "version": process.version,
                "description": process.description,
                "category": process.category,
                "owner": process.owner,
                "tags": process.tags,
                "iso_clause": process.iso_clause,
                "compliance_requirements": process.compliance_requirements
            },
            "graph": {
                "nodes": nodes,
                "edges": edges
            },
            "metadata": {
                "total_steps": len(process.steps),
                "start_step": process.start_step_id,
                "end_steps": process.end_step_ids,
                "exported_at": datetime.now().isoformat()
            }
        }

        # Include instances if requested
        if include_instances:
            instances_data = []
            for instance_id, instance in self.framework.instances.items():
                if instance.process_definition_id == process_id:
                    instances_data.append({
                        "instance_id": instance.id,
                        "status": instance.status.value,
                        "current_step_id": instance.current_step_id,
                        "started_by": instance.started_by,
                        "started_at": instance.started_at.isoformat() if instance.started_at else None,
                        "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
                        "steps_completed": len(instance.step_history)
                    })
            result["instances"] = instances_data

        return json.dumps(result, indent=2, ensure_ascii=False)

    # Helper methods

    def _get_mermaid_node_shape(self, step_type: StepType) -> Tuple[str, str]:
        """Get Mermaid node shape based on step type"""
        shapes = {
            StepType.FORM_INPUT: ("[", "]"),
            StepType.APPROVAL: ("[", "]"),
            StepType.DECISION: ("{", "}"),
            StepType.ANALYSIS: ("[[", "]]"),
            StepType.DOCUMENT_GENERATION: ("[/", "/]"),
            StepType.NOTIFICATION: ("[(", ")]"),
            StepType.VALIDATION: ("{{", "}}"),
            StepType.EXECUTION: ("[", "]")
        }
        return shapes.get(step_type, ("[", "]"))

    def _get_mermaid_style(self, step_type: StepType) -> Optional[str]:
        """Get Mermaid style based on step type"""
        styles = {
            StepType.FORM_INPUT: "fill:#87CEEB,stroke:#333,stroke-width:2px",
            StepType.APPROVAL: "fill:#FFD700,stroke:#333,stroke-width:2px",
            StepType.DECISION: "fill:#FFA500,stroke:#333,stroke-width:2px",
            StepType.ANALYSIS: "fill:#DDA0DD,stroke:#333,stroke-width:2px",
            StepType.DOCUMENT_GENERATION: "fill:#98FB98,stroke:#333,stroke-width:2px",
            StepType.NOTIFICATION: "fill:#F0E68C,stroke:#333,stroke-width:2px",
            StepType.VALIDATION: "fill:#FFC0CB,stroke:#333,stroke-width:2px",
            StepType.EXECUTION: "fill:#B0C4DE,stroke:#333,stroke-width:2px"
        }
        return styles.get(step_type)

    def _get_vis_shape(self, step_type: StepType) -> str:
        """Get vis.js shape based on step type"""
        shapes = {
            StepType.FORM_INPUT: "box",
            StepType.APPROVAL: "box",
            StepType.DECISION: "diamond",
            StepType.ANALYSIS: "box",
            StepType.DOCUMENT_GENERATION: "box",
            StepType.NOTIFICATION: "ellipse",
            StepType.VALIDATION: "hexagon",
            StepType.EXECUTION: "box"
        }
        return shapes.get(step_type, "box")

    def _get_vis_color(self, step_type: StepType) -> str:
        """Get vis.js color based on step type"""
        colors = {
            StepType.FORM_INPUT: "#87CEEB",
            StepType.APPROVAL: "#FFD700",
            StepType.DECISION: "#FFA500",
            StepType.ANALYSIS: "#DDA0DD",
            StepType.DOCUMENT_GENERATION: "#98FB98",
            StepType.NOTIFICATION: "#F0E68C",
            StepType.VALIDATION: "#FFC0CB",
            StepType.EXECUTION: "#B0C4DE"
        }
        return colors.get(step_type, "#CCCCCC")

    def _estimate_completion_time(
        self,
        instance: ProcessInstance,
        process: ProcessDefinition,
        remaining_step_ids: List[str]
    ) -> Optional[datetime]:
        """Estimate when the process will be completed"""
        if not remaining_step_ids or instance.status == ProcessStatus.COMPLETED:
            return instance.completed_at

        total_estimated_minutes = 0
        for step_id in remaining_step_ids:
            step = process.get_step(step_id)
            if step and step.estimated_duration_minutes:
                total_estimated_minutes += step.estimated_duration_minutes
            else:
                # Default estimate if not specified
                total_estimated_minutes += 30

        if instance.started_at:
            return datetime.now() + timedelta(minutes=total_estimated_minutes)

        return None

    def _is_on_schedule(self, actual_duration_seconds: float, step: ProcessStep) -> Optional[bool]:
        """Check if step execution is on schedule"""
        if not step.estimated_duration_minutes:
            return None

        estimated_seconds = step.estimated_duration_minutes * 60
        return actual_duration_seconds <= estimated_seconds * 1.2  # 20% tolerance

    def generate_gantt_data(self, instance_id: str) -> Dict[str, Any]:
        """
        Generate Gantt chart data for process timeline

        Creates data structure suitable for Gantt chart visualization libraries
        like dhtmlxGantt, Frappe Gantt, or Google Charts Timeline.

        Args:
            instance_id: The ID of the process instance

        Returns:
            Dictionary containing tasks array with start/end dates

        Example:
            >>> gantt_data = visualizer.generate_gantt_data("bia_process_v1-20250112150000")
            >>> # Use with Frappe Gantt or similar library
        """
        timeline = self.generate_timeline(instance_id)

        tasks = []
        for entry in timeline["timeline_entries"]:
            tasks.append({
                "id": entry["step_id"],
                "name": entry["step_name"],
                "start": entry["started_at"],
                "end": entry["completed_at"],
                "progress": 100 if entry["status"] == "success" else 0,
                "dependencies": "",  # Could be enhanced to show dependencies
                "custom_class": entry["step_type"]
            })

        return {
            "tasks": tasks,
            "view_mode": "Day",
            "instance_id": instance_id,
            "process_name": timeline["process_name"]
        }

    def export_to_bpmn(self, process_id: str, output_path: Optional[Path] = None) -> str:
        """
        Export process to BPMN 2.0 XML format

        Generates Business Process Model and Notation (BPMN) XML representation
        that can be imported into tools like Camunda, Activiti, or bpmn.io.

        Args:
            process_id: The ID of the process definition
            output_path: Optional path to save the BPMN XML file

        Returns:
            BPMN XML string

        Note:
            This is a simplified BPMN export. Full BPMN 2.0 compliance would
            require additional elements and attributes.
        """
        process = self.framework.processes.get(process_id)
        if not process:
            raise ValueError(f"Process '{process_id}' not found")

        # Simple BPMN XML template
        bpmn_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<definitions xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             id="definitions_{process.id}"
             targetNamespace="http://ai-platform-iso.local/bpmn">

  <process id="{process.id}" name="{process.name}" isExecutable="true">

    <startEvent id="start" name="Start"/>

"""

        # Add tasks for each step
        for step_id, step in process.steps.items():
            task_type = "userTask" if step.step_type in [StepType.FORM_INPUT, StepType.APPROVAL] else "serviceTask"
            bpmn_xml += f'    <{task_type} id="{step_id}" name="{step.name}"/>\n'

        # Add end events
        for end_step_id in process.end_step_ids:
            bpmn_xml += f'    <endEvent id="{end_step_id}_end" name="End"/>\n'

        # Add sequence flows
        bpmn_xml += f'\n    <sequenceFlow id="flow_start" sourceRef="start" targetRef="{process.start_step_id}"/>\n'

        flow_counter = 1
        for step_id, step in process.steps.items():
            for next_step_id in step.next_steps:
                target = f"{next_step_id}_end" if next_step_id in process.end_step_ids else next_step_id
                bpmn_xml += f'    <sequenceFlow id="flow_{flow_counter}" sourceRef="{step_id}" targetRef="{target}"/>\n'
                flow_counter += 1

        bpmn_xml += """
  </process>
</definitions>
"""

        # Save to file if path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(bpmn_xml)

        return bpmn_xml


# Example usage and testing
if __name__ == "__main__":
    from pathlib import Path

    # This example demonstrates how to use the ProcessVisualizer
    print("Process Visualization Module - Example Usage")
    print("=" * 60)

    # Initialize visualizer
    visualizer = ProcessVisualizer()

    # Example 1: Generate Mermaid diagram
    print("\n1. Generating Mermaid Diagram")
    print("-" * 60)
    try:
        # Note: This will only work if you have processes registered
        # For demo purposes, we'll catch the exception
        diagram = visualizer.generate_mermaid_diagram("example_process")
        print(diagram)
    except ValueError as e:
        print(f"Note: {e}")
        print("Create and register a process first using ProcessFramework")

    # Example 2: Process status
    print("\n2. Process Status Example")
    print("-" * 60)
    print("""
    status = visualizer.generate_process_status("process_instance_id")
    print(f"Progress: {status['progress_percentage']}%")
    print(f"Current Step: {status['current_step']['name']}")
    print(f"Completed: {len(status['completed_steps'])} steps")
    """)

    # Example 3: Timeline
    print("\n3. Timeline Example")
    print("-" * 60)
    print("""
    timeline = visualizer.generate_timeline("process_instance_id")
    for entry in timeline['timeline_entries']:
        print(f"{entry['step_name']}: {entry['duration_seconds']}s")
    """)

    # Example 4: JSON Export
    print("\n4. JSON Export Example")
    print("-" * 60)
    print("""
    json_data = visualizer.export_to_json("process_id")
    # Use in JavaScript visualization library:
    # const data = JSON.parse(json_data);
    # new vis.Network(container, data.graph, options);
    """)

    print("\n" + "=" * 60)
    print("Module loaded successfully!")
    print("Use 'from visualization import ProcessVisualizer' to import")
