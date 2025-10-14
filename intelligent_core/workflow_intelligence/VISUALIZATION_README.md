# Process Visualization Module

Comprehensive visualization capabilities for the Process Framework, enabling visual representation of business processes and their execution state.

## Overview

The **ProcessVisualizer** class provides multiple visualization formats and data exports for business process workflows:

- **Mermaid Diagrams** - Flowchart visualization for documentation
- **Process Status** - Real-time progress tracking and monitoring
- **Execution Timeline** - Historical analysis of step executions
- **JSON Export** - Data for frontend visualization libraries (D3.js, vis.js, Cytoscape.js)
- **Gantt Charts** - Project timeline visualization
- **BPMN Export** - Standard BPMN 2.0 XML format

## File Location

```
/Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence/visualization.py
```

## Installation & Setup

The module is part of the workflow_intelligence package and requires:

```python
from workflow_intelligence.visualization import ProcessVisualizer
from workflow_intelligence.process_framework import get_process_framework

# Initialize
framework = get_process_framework()
visualizer = ProcessVisualizer(framework)
```

## Core Features

### 1. Mermaid Diagram Generation

Generate flowchart diagrams using Mermaid syntax for documentation and presentations.

```python
# Generate diagram for a process
mermaid_diagram = visualizer.generate_mermaid_diagram("bia_process_v1")
print(mermaid_diagram)

# Save to file
with open("process_diagram.mmd", "w") as f:
    f.write(mermaid_diagram)
```

**Output Features:**
- Color-coded nodes by step type
- Highlighted start and end nodes
- Clear transitions between steps
- Decision points with conditional paths
- Ready for Markdown rendering or Mermaid Live Editor

**Example Output:**
```mermaid
flowchart TD
    Start([Start: Business Impact Analysis])
    style Start fill:#90EE90,stroke:#333,stroke-width:2px
    identify_functions[Identify Critical Functions\n[form_input]]
    style identify_functions fill:#87CEEB,stroke:#333,stroke-width:2px
    assess_impact[[Assess Business Impact\n[analysis]]]
    style assess_impact fill:#DDA0DD,stroke:#333,stroke-width:2px
    ...
```

### 2. Process Status Tracking

Real-time status monitoring with progress calculation and completion estimates.

```python
# Get current process status
status = visualizer.generate_process_status("bia_process_v1-20251012160132")

print(f"Process: {status['process_name']}")
print(f"Progress: {status['progress_percentage']}%")
print(f"Current Step: {status['current_step']['name']}")
print(f"Completed: {len(status['completed_steps'])} steps")
print(f"Remaining: {len(status['remaining_steps'])} steps")
print(f"Estimated Completion: {status['estimated_completion']}")
```

**Returned Data Structure:**
```json
{
  "instance_id": "bia_process_v1-20251012160132",
  "process_id": "bia_process_v1",
  "process_name": "Business Impact Analysis",
  "status": "in_progress",
  "current_step": {
    "id": "assess_impact",
    "name": "Assess Business Impact",
    "type": "analysis",
    "description": "Analyze the impact of function disruption",
    "estimated_duration_minutes": 45,
    "sla_hours": null
  },
  "completed_steps": [
    {
      "step_id": "identify_functions",
      "step_name": "Identify Critical Functions",
      "timestamp": "2025-10-12T16:01:32.847723",
      "result": "success"
    }
  ],
  "remaining_steps": [
    {
      "step_id": "identify_dependencies",
      "step_name": "Identify Dependencies",
      "estimated_duration_minutes": 25
    },
    ...
  ],
  "progress_percentage": 20.0,
  "estimated_completion": "2025-10-12T17:36:32.847734",
  "total_duration_seconds": 125.5,
  "started_at": "2025-10-12T16:01:32.847715"
}
```

### 3. Execution Timeline Analysis

Detailed chronological analysis of step executions with performance metrics.

```python
# Generate timeline
timeline = visualizer.generate_timeline("bia_process_v1-20251012160132")

print(f"Total Duration: {timeline['total_duration_seconds']}s")
print(f"Average Step: {timeline['average_step_duration_seconds']}s")
print(f"Longest Step: {timeline['longest_step']['step_name']}")

# Iterate through timeline
for entry in timeline['timeline_entries']:
    print(f"{entry['step_name']}: {entry['duration_seconds']}s")
    print(f"  Executed by: {entry['executed_by']}")
    print(f"  On Schedule: {entry['on_schedule']}")
```

**Timeline Entry Structure:**
```json
{
  "sequence": 1,
  "step_id": "identify_functions",
  "step_name": "Identify Critical Functions",
  "step_type": "form_input",
  "executed_by": "john.doe@company.com",
  "started_at": "2025-10-12T16:01:32.847723",
  "completed_at": "2025-10-12T16:01:32.847858",
  "duration_seconds": 135.0,
  "status": "success",
  "data_captured": {
    "function_name": "Customer Support System",
    "function_description": "24/7 customer support ticketing system"
  },
  "estimated_duration_minutes": 30,
  "on_schedule": true
}
```

### 4. JSON Export for Visualization Libraries

Export process structure in a format optimized for frontend visualization libraries.

```python
# Export to JSON
json_data = visualizer.export_to_json("bia_process_v1", include_instances=True)

# Parse and use
import json
data = json.loads(json_data)

# Access graph structure
nodes = data['graph']['nodes']
edges = data['graph']['edges']

# Use with vis.js, D3.js, Cytoscape.js, etc.
```

**Compatible Libraries:**
- **vis.js** - Network diagrams
- **D3.js** - Force-directed graphs, hierarchical layouts
- **Cytoscape.js** - Graph visualization and analysis
- **React Flow** - Interactive node-based UIs
- **Dagre** - Directed graph layout

**Data Structure:**
```json
{
  "process": {
    "id": "bia_process_v1",
    "name": "Business Impact Analysis",
    "version": "1.0",
    "description": "...",
    "category": "bcm",
    "tags": ["bia", "iso22301"]
  },
  "graph": {
    "nodes": [
      {
        "id": "identify_functions",
        "label": "Identify Critical Functions",
        "type": "form_input",
        "shape": "box",
        "color": "#87CEEB",
        "metadata": {
          "allowed_roles": ["bia_analyst", "bcm_manager"],
          "estimated_duration_minutes": 30,
          "has_form": true,
          "form_fields_count": 2
        }
      }
    ],
    "edges": [
      {
        "from": "identify_functions",
        "to": "assess_impact",
        "arrows": "to",
        "color": "#333333",
        "width": 2
      }
    ]
  },
  "instances": [
    {
      "instance_id": "bia_process_v1-20251012160132",
      "status": "in_progress",
      "current_step_id": "approval",
      "steps_completed": 3
    }
  ]
}
```

### 5. Gantt Chart Data

Generate data suitable for Gantt chart visualization libraries.

```python
# Generate Gantt data
gantt_data = visualizer.generate_gantt_data("bia_process_v1-20251012160132")

# Use with Frappe Gantt, dhtmlxGantt, etc.
for task in gantt_data['tasks']:
    print(f"{task['name']}: {task['start']} to {task['end']}")
```

**Compatible Libraries:**
- Frappe Gantt
- dhtmlxGantt
- Google Charts Timeline
- Bryntum Gantt

### 6. BPMN 2.0 Export

Export process definitions to standard BPMN 2.0 XML format.

```python
# Export to BPMN
bpmn_xml = visualizer.export_to_bpmn(
    "bia_process_v1",
    output_path=Path("process.bpmn")
)

# Import into:
# - Camunda Modeler
# - bpmn.io
# - Activiti
# - Flowable
```

## Color Scheme

The visualizer uses a consistent color scheme across all visualization formats:

| Step Type | Color | Hex Code | Usage |
|-----------|-------|----------|-------|
| Start/End | Light Green/Pink | #90EE90 / #FFB6C1 | Start and end nodes |
| Form Input | Sky Blue | #87CEEB | User input steps |
| Approval | Gold | #FFD700 | Approval/decision steps |
| Decision | Orange | #FFA500 | Conditional branches |
| Analysis | Plum | #DDA0DD | Analysis/AI steps |
| Document Generation | Pale Green | #98FB98 | Document creation |
| Notification | Khaki | #F0E68C | Notification steps |
| Validation | Pink | #FFC0CB | Validation steps |
| Execution | Light Steel Blue | #B0C4DE | Execution steps |

## API Reference

### ProcessVisualizer Class

#### `__init__(framework: Optional[ProcessFramework] = None)`
Initialize the visualizer with a ProcessFramework instance.

#### `generate_mermaid_diagram(process_id: str) -> str`
Generate Mermaid flowchart syntax for a process definition.

**Parameters:**
- `process_id`: Process definition ID

**Returns:**
- Mermaid flowchart string

**Raises:**
- `ValueError`: If process not found

#### `generate_process_status(instance_id: str) -> Dict[str, Any]`
Generate comprehensive status information for a process instance.

**Parameters:**
- `instance_id`: Process instance ID

**Returns:**
- Dictionary with status details (see structure above)

**Raises:**
- `ValueError`: If instance not found

#### `generate_timeline(instance_id: str) -> Dict[str, Any]`
Generate detailed execution timeline with performance metrics.

**Parameters:**
- `instance_id`: Process instance ID

**Returns:**
- Dictionary with timeline entries and statistics

**Raises:**
- `ValueError`: If instance not found

#### `export_to_json(process_id: str, include_instances: bool = False) -> str`
Export process definition to JSON for visualization libraries.

**Parameters:**
- `process_id`: Process definition ID
- `include_instances`: Include active instance data

**Returns:**
- JSON string with graph structure

**Raises:**
- `ValueError`: If process not found

#### `generate_gantt_data(instance_id: str) -> Dict[str, Any]`
Generate Gantt chart data for process timeline.

**Parameters:**
- `instance_id`: Process instance ID

**Returns:**
- Dictionary with tasks array

#### `export_to_bpmn(process_id: str, output_path: Optional[Path] = None) -> str`
Export process to BPMN 2.0 XML format.

**Parameters:**
- `process_id`: Process definition ID
- `output_path`: Optional file path to save XML

**Returns:**
- BPMN XML string

## Usage Examples

### Example 1: Dashboard Integration

```python
from visualization import ProcessVisualizer
from process_framework import get_process_framework

# Initialize
framework = get_process_framework()
visualizer = ProcessVisualizer(framework)

# Get all active process instances
active_instances = [
    instance_id for instance_id, instance in framework.instances.items()
    if instance.status.value == "in_progress"
]

# Generate dashboard data
dashboard_data = []
for instance_id in active_instances:
    status = visualizer.generate_process_status(instance_id)
    dashboard_data.append({
        "id": status["instance_id"],
        "name": status["process_name"],
        "progress": status["progress_percentage"],
        "current_step": status["current_step"]["name"],
        "eta": status["estimated_completion"]
    })

# Return to frontend
return {"processes": dashboard_data}
```

### Example 2: Process Documentation

```python
# Generate complete documentation package
process_id = "bia_process_v1"

# 1. Mermaid diagram for flowchart
diagram = visualizer.generate_mermaid_diagram(process_id)
with open(f"docs/{process_id}_flowchart.mmd", "w") as f:
    f.write(diagram)

# 2. JSON for interactive visualization
json_data = visualizer.export_to_json(process_id)
with open(f"docs/{process_id}_graph.json", "w") as f:
    f.write(json_data)

# 3. BPMN for process modeling tools
bpmn_xml = visualizer.export_to_bpmn(
    process_id,
    output_path=Path(f"docs/{process_id}.bpmn")
)

print("Documentation package created!")
```

### Example 3: Performance Analysis

```python
# Analyze process performance
instance_id = "bia_process_v1-20251012160132"
timeline = visualizer.generate_timeline(instance_id)

# Check for bottlenecks
print("Performance Analysis")
print("=" * 60)

for entry in timeline['timeline_entries']:
    duration = entry['duration_seconds']
    estimated = entry['estimated_duration_minutes'] * 60

    if estimated and duration > estimated * 1.2:  # 20% over estimate
        print(f"⚠️  BOTTLENECK: {entry['step_name']}")
        print(f"   Expected: {estimated}s, Actual: {duration}s")
        print(f"   Overrun: {((duration/estimated - 1) * 100):.1f}%")

# Overall statistics
print(f"\nTotal Duration: {timeline['total_duration_seconds']}s")
print(f"Average Step: {timeline['average_step_duration_seconds']}s")
print(f"Longest Step: {timeline['longest_step']['step_name']}")
```

### Example 4: Real-time Monitoring

```python
import time
from datetime import datetime

# Monitor process execution in real-time
instance_id = "bia_process_v1-20251012160132"

while True:
    status = visualizer.generate_process_status(instance_id)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Process Status")
    print(f"Progress: {status['progress_percentage']}%")
    print(f"Current: {status['current_step']['name']}")

    if status['status'] == 'completed':
        print("✓ Process completed!")
        break

    time.sleep(5)  # Check every 5 seconds
```

## Testing

Run the comprehensive test suite:

```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence
python3 test_visualization.py
```

The test creates:
- Sample BIA process definition
- Process instance with multiple steps executed
- All visualization formats
- Output files in `test_processes/` directory

## Integration with Frontend

### React Example

```javascript
import { useEffect, useState } from 'react';
import { Network } from 'vis-network';

function ProcessVisualization({ processId }) {
  const [graphData, setGraphData] = useState(null);

  useEffect(() => {
    // Fetch visualization data
    fetch(`/api/processes/${processId}/visualization`)
      .then(res => res.json())
      .then(data => {
        setGraphData(data.graph);

        // Create vis.js network
        const container = document.getElementById('network');
        const network = new Network(container, data.graph, {
          layout: { hierarchical: true },
          physics: false
        });
      });
  }, [processId]);

  return <div id="network" style={{ width: '100%', height: '600px' }} />;
}
```

### Vue Example

```javascript
<template>
  <div>
    <div ref="network" class="network-container"></div>
  </div>
</template>

<script>
import { Network } from 'vis-network';

export default {
  props: ['processId'],
  mounted() {
    this.loadVisualization();
  },
  methods: {
    async loadVisualization() {
      const response = await fetch(`/api/processes/${this.processId}/visualization`);
      const data = await response.json();

      new Network(this.$refs.network, data.graph, {
        layout: { hierarchical: true },
        physics: false
      });
    }
  }
}
</script>
```

## Performance Considerations

- **Caching**: Cache generated visualizations for frequently accessed processes
- **Lazy Loading**: Load instance data on demand using `include_instances=False`
- **Pagination**: For processes with many instances, paginate the results
- **Async Generation**: Use async/await for non-blocking visualization generation

## Troubleshooting

### Common Issues

**1. Process not found error**
```python
ValueError: Process 'process_id' not found
```
**Solution:** Ensure the process is registered with the framework first.

**2. Empty timeline**
```python
timeline['timeline_entries'] == []
```
**Solution:** Process instance has no executed steps yet. Execute at least one step.

**3. Import errors**
```python
ImportError: No module named 'process_framework'
```
**Solution:** Ensure you're in the correct directory or use proper package imports.

## Future Enhancements

Planned features for future versions:

- [ ] Real-time WebSocket updates for live process monitoring
- [ ] Process comparison visualization (side-by-side diagrams)
- [ ] Heatmap visualization for bottleneck identification
- [ ] 3D process visualization for complex workflows
- [ ] Animation of process execution flow
- [ ] Interactive process editor with visual design
- [ ] Export to PDF/PNG for reports
- [ ] Integration with BI tools (Tableau, Power BI)

## Related Documentation

- [Process Framework](./process_framework.py) - Core process execution engine
- [BCM Processes](./bcm_processes.py) - Pre-built BCM process definitions
- [Process Orchestration API](./process_orchestration_api.py) - REST API wrapper

## Support

For issues or questions:
- Check the test file: `test_visualization.py`
- Review the inline documentation in `visualization.py`
- Contact the development team

## License

Part of the AI-Platform-ISO project. See main project LICENSE for details.

---

**Last Updated:** October 12, 2025
**Module Version:** 1.0.0
**Author:** AI Platform Team
