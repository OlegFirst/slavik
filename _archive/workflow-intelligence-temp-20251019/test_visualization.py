"""
Test and demonstration script for ProcessVisualizer

This script demonstrates all features of the visualization module with a complete example.
"""

from pathlib import Path
from datetime import datetime, timedelta
import json

from process_framework import (
    ProcessFramework,
    ProcessDefinition,
    ProcessStep,
    FormField,
    FieldValidation,
    StepType,
    ValidationRule,
    get_process_framework
)
from visualization import ProcessVisualizer


def create_sample_process() -> ProcessDefinition:
    """Create a sample BIA process for testing"""

    # Create process definition
    process = ProcessDefinition(
        id="bia_process_v1",
        name="Business Impact Analysis",
        version="1.0",
        description="Comprehensive BIA process for critical business functions",
        category="bcm",
        owner="BCM Team",
        tags=["bia", "iso22301", "critical"],
        iso_clause="8.2.2",
        compliance_requirements=["ISO 22301:2019 - Clause 8.2"]
    )

    # Step 1: Identify Critical Functions
    step1 = ProcessStep(
        id="identify_functions",
        name="Identify Critical Functions",
        step_type=StepType.FORM_INPUT,
        description="Identify and document critical business functions",
        form_fields=[
            FormField(
                name="function_name",
                label="Function Name",
                field_type="text",
                required=True,
                validations=[
                    FieldValidation(
                        rule=ValidationRule.REQUIRED,
                        value=True,
                        error_message="Function name is required"
                    ),
                    FieldValidation(
                        rule=ValidationRule.MIN_LENGTH,
                        value=3,
                        error_message="Function name must be at least 3 characters"
                    )
                ]
            ),
            FormField(
                name="function_description",
                label="Function Description",
                field_type="textarea",
                required=True
            )
        ],
        next_steps=["assess_impact"],
        allowed_roles=["bia_analyst", "bcm_manager"],
        estimated_duration_minutes=30
    )

    # Step 2: Assess Impact
    step2 = ProcessStep(
        id="assess_impact",
        name="Assess Business Impact",
        step_type=StepType.ANALYSIS,
        description="Analyze the impact of function disruption",
        form_fields=[
            FormField(
                name="impact_level",
                label="Impact Level",
                field_type="select",
                required=True,
                options=[
                    {"value": "critical", "label": "Critical"},
                    {"value": "high", "label": "High"},
                    {"value": "medium", "label": "Medium"},
                    {"value": "low", "label": "Low"}
                ]
            ),
            FormField(
                name="rto_hours",
                label="Recovery Time Objective (hours)",
                field_type="number",
                required=True
            ),
            FormField(
                name="rpo_hours",
                label="Recovery Point Objective (hours)",
                field_type="number",
                required=True
            )
        ],
        next_steps=["identify_dependencies"],
        allowed_roles=["bia_analyst"],
        estimated_duration_minutes=45,
        ai_agent="analytics_specialist"
    )

    # Step 3: Identify Dependencies
    step3 = ProcessStep(
        id="identify_dependencies",
        name="Identify Dependencies",
        step_type=StepType.FORM_INPUT,
        description="Document dependencies and resources",
        form_fields=[
            FormField(
                name="dependencies",
                label="Key Dependencies",
                field_type="textarea",
                required=True
            ),
            FormField(
                name="resources",
                label="Required Resources",
                field_type="textarea",
                required=True
            )
        ],
        next_steps=["approval"],
        allowed_roles=["bia_analyst"],
        estimated_duration_minutes=25
    )

    # Step 4: Approval
    step4 = ProcessStep(
        id="approval",
        name="Manager Approval",
        step_type=StepType.APPROVAL,
        description="BCM Manager reviews and approves the BIA",
        form_fields=[
            FormField(
                name="approved",
                label="Approval Status",
                field_type="select",
                required=True,
                options=[
                    {"value": "approved", "label": "Approved"},
                    {"value": "rejected", "label": "Rejected"},
                    {"value": "needs_revision", "label": "Needs Revision"}
                ]
            ),
            FormField(
                name="comments",
                label="Comments",
                field_type="textarea"
            )
        ],
        next_steps=["generate_report"],
        allowed_roles=["bcm_manager"],
        estimated_duration_minutes=15
    )

    # Step 5: Generate Report
    step5 = ProcessStep(
        id="generate_report",
        name="Generate BIA Report",
        step_type=StepType.DOCUMENT_GENERATION,
        description="Generate comprehensive BIA report",
        next_steps=["complete"],
        allowed_roles=["bia_analyst"],
        document_template="bia_report_template.docx",
        estimated_duration_minutes=10,
        auto_approve=True
    )

    # Add all steps to process
    process.add_step(step1)
    process.add_step(step2)
    process.add_step(step3)
    process.add_step(step4)
    process.add_step(step5)

    # Set start and end
    process.start_step_id = "identify_functions"
    process.end_step_ids = ["complete"]

    return process


def test_visualization():
    """Test all visualization features"""

    print("=" * 80)
    print("PROCESS VISUALIZATION MODULE - COMPREHENSIVE TEST")
    print("=" * 80)

    # Initialize framework
    processes_dir = Path(__file__).parent / "test_processes"
    processes_dir.mkdir(exist_ok=True)

    framework = ProcessFramework(processes_dir)
    visualizer = ProcessVisualizer(framework)

    # Create and register sample process
    print("\n1. Creating sample BIA process...")
    process = create_sample_process()
    success = framework.register_process(process)
    print(f"   Process registered: {success}")

    # Test 1: Generate Mermaid Diagram
    print("\n" + "=" * 80)
    print("TEST 1: MERMAID DIAGRAM GENERATION")
    print("=" * 80)

    mermaid_diagram = visualizer.generate_mermaid_diagram("bia_process_v1")
    print(mermaid_diagram)

    # Save to file
    mermaid_file = processes_dir / "bia_process_diagram.mmd"
    with open(mermaid_file, 'w') as f:
        f.write(mermaid_diagram)
    print(f"\nDiagram saved to: {mermaid_file}")

    # Test 2: Start a process instance and track status
    print("\n" + "=" * 80)
    print("TEST 2: PROCESS STATUS TRACKING")
    print("=" * 80)

    # Start process
    instance = framework.start_process(
        process_id="bia_process_v1",
        started_by="john.doe@company.com",
        initial_data={"organization": "ACME Corp"}
    )
    print(f"\nProcess instance started: {instance.id}")

    # Execute Step 1
    print("\nExecuting Step 1: Identify Critical Functions")
    step1_data = {
        "function_name": "Customer Support System",
        "function_description": "24/7 customer support ticketing and resolution system"
    }
    success, error, next_step = framework.execute_step(
        instance.id,
        step1_data,
        "john.doe@company.com"
    )
    print(f"   Step 1 completed: {success}, Next step: {next_step}")

    # Get status after step 1
    status = visualizer.generate_process_status(instance.id)
    print(f"\nProcess Status:")
    print(f"   Progress: {status['progress_percentage']}%")
    print(f"   Current Step: {status['current_step']['name']}")
    print(f"   Completed Steps: {len(status['completed_steps'])}")
    print(f"   Remaining Steps: {len(status['remaining_steps'])}")
    print(f"   Estimated Completion: {status['estimated_completion']}")

    # Save status to JSON
    status_file = processes_dir / f"status_{instance.id}.json"
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    print(f"\nStatus saved to: {status_file}")

    # Execute Step 2
    print("\nExecuting Step 2: Assess Business Impact")
    step2_data = {
        "impact_level": "critical",
        "rto_hours": 4,
        "rpo_hours": 1
    }
    success, error, next_step = framework.execute_step(
        instance.id,
        step2_data,
        "jane.smith@company.com"
    )
    print(f"   Step 2 completed: {success}, Next step: {next_step}")

    # Execute Step 3
    print("\nExecuting Step 3: Identify Dependencies")
    step3_data = {
        "dependencies": "CRM system, Knowledge base, Communication tools",
        "resources": "Support staff, IT infrastructure, Network connectivity"
    }
    success, error, next_step = framework.execute_step(
        instance.id,
        step3_data,
        "john.doe@company.com"
    )
    print(f"   Step 3 completed: {success}, Next step: {next_step}")

    # Test 3: Generate Timeline
    print("\n" + "=" * 80)
    print("TEST 3: EXECUTION TIMELINE")
    print("=" * 80)

    timeline = visualizer.generate_timeline(instance.id)
    print(f"\nProcess: {timeline['process_name']}")
    print(f"Total Duration: {timeline['total_duration_seconds']} seconds")
    print(f"Average Step Duration: {timeline['average_step_duration_seconds']} seconds")
    print(f"Longest Step: {timeline['longest_step']['step_name']} ({timeline['longest_step']['duration_seconds']}s)")
    print(f"Shortest Step: {timeline['shortest_step']['step_name']} ({timeline['shortest_step']['duration_seconds']}s)")

    print("\nTimeline Entries:")
    print(f"{'Seq':<5} {'Step Name':<30} {'Duration':<12} {'Status':<10} {'On Schedule':<12}")
    print("-" * 80)
    for entry in timeline['timeline_entries']:
        print(f"{entry['sequence']:<5} {entry['step_name']:<30} {entry['duration_seconds']:<12} "
              f"{entry['status']:<10} {str(entry.get('on_schedule', 'N/A')):<12}")

    # Save timeline to JSON
    timeline_file = processes_dir / f"timeline_{instance.id}.json"
    with open(timeline_file, 'w') as f:
        json.dump(timeline, f, indent=2)
    print(f"\nTimeline saved to: {timeline_file}")

    # Test 4: Export to JSON for visualization
    print("\n" + "=" * 80)
    print("TEST 4: JSON EXPORT FOR VISUALIZATION LIBRARIES")
    print("=" * 80)

    json_export = visualizer.export_to_json("bia_process_v1", include_instances=True)
    json_data = json.loads(json_export)

    print(f"\nProcess: {json_data['process']['name']}")
    print(f"Total Nodes: {len(json_data['graph']['nodes'])}")
    print(f"Total Edges: {len(json_data['graph']['edges'])}")
    print(f"Active Instances: {len(json_data.get('instances', []))}")

    print("\nNode Types:")
    node_types = {}
    for node in json_data['graph']['nodes']:
        node_type = node['type']
        node_types[node_type] = node_types.get(node_type, 0) + 1
    for node_type, count in node_types.items():
        print(f"   {node_type}: {count}")

    # Save JSON export
    json_file = processes_dir / "bia_process_visualization.json"
    with open(json_file, 'w') as f:
        f.write(json_export)
    print(f"\nVisualization data saved to: {json_file}")
    print("\nThis JSON can be used with:")
    print("   - D3.js (force-directed graphs)")
    print("   - vis.js (network diagrams)")
    print("   - Cytoscape.js (graph visualization)")
    print("   - React Flow (flow diagrams)")

    # Test 5: Gantt Chart Data
    print("\n" + "=" * 80)
    print("TEST 5: GANTT CHART DATA")
    print("=" * 80)

    gantt_data = visualizer.generate_gantt_data(instance.id)
    print(f"\nProcess: {gantt_data['process_name']}")
    print(f"Total Tasks: {len(gantt_data['tasks'])}")

    print("\nGantt Tasks:")
    print(f"{'Task Name':<30} {'Start':<20} {'End':<20} {'Progress':<10}")
    print("-" * 80)
    for task in gantt_data['tasks']:
        print(f"{task['name']:<30} {task['start'][:19]:<20} "
              f"{task['end'][:19]:<20} {task['progress']}%")

    # Save Gantt data
    gantt_file = processes_dir / f"gantt_{instance.id}.json"
    with open(gantt_file, 'w') as f:
        json.dump(gantt_data, f, indent=2)
    print(f"\nGantt data saved to: {gantt_file}")

    # Test 6: BPMN Export
    print("\n" + "=" * 80)
    print("TEST 6: BPMN 2.0 EXPORT")
    print("=" * 80)

    bpmn_file = processes_dir / "bia_process.bpmn"
    bpmn_xml = visualizer.export_to_bpmn("bia_process_v1", bpmn_file)
    print(f"\nBPMN file saved to: {bpmn_file}")
    print("\nBPMN XML Preview (first 500 chars):")
    print(bpmn_xml[:500] + "...")
    print("\nThis BPMN file can be imported into:")
    print("   - Camunda Modeler")
    print("   - bpmn.io")
    print("   - Activiti")
    print("   - Flowable")

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"\nAll tests completed successfully!")
    print(f"\nGenerated files in: {processes_dir}")
    print(f"   1. {mermaid_file.name} - Mermaid diagram")
    print(f"   2. {status_file.name} - Process status")
    print(f"   3. {timeline_file.name} - Execution timeline")
    print(f"   4. {json_file.name} - Visualization data")
    print(f"   5. {gantt_file.name} - Gantt chart data")
    print(f"   6. {bpmn_file.name} - BPMN 2.0 XML")

    print("\n" + "=" * 80)
    print("VISUALIZATION MODULE TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_visualization()
