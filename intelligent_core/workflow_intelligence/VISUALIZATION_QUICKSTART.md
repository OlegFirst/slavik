# Process Visualization - Quick Start Guide

Fast reference guide for using the ProcessVisualizer module.

## 5-Minute Quick Start

### 1. Import and Initialize

```python
from visualization import ProcessVisualizer
from process_framework import get_process_framework

framework = get_process_framework()
visualizer = ProcessVisualizer(framework)
```

### 2. Generate Mermaid Diagram

```python
# Get flowchart diagram
diagram = visualizer.generate_mermaid_diagram("bia_process_v1")
print(diagram)

# Save to file
with open("diagram.mmd", "w") as f:
    f.write(diagram)
```

### 3. Check Process Status

```python
# Get current status
status = visualizer.generate_process_status("instance_id")

print(f"Progress: {status['progress_percentage']}%")
print(f"Current: {status['current_step']['name']}")
print(f"ETA: {status['estimated_completion']}")
```

### 4. View Execution Timeline

```python
# Get timeline
timeline = visualizer.generate_timeline("instance_id")

for entry in timeline['timeline_entries']:
    print(f"{entry['step_name']}: {entry['duration_seconds']}s")
```

### 5. Export for Visualization

```python
# Export to JSON for D3.js, vis.js, etc.
json_data = visualizer.export_to_json("process_id", include_instances=True)

# Save for frontend
with open("process_graph.json", "w") as f:
    f.write(json_data)
```

## Common Patterns

### Dashboard Widget

```python
def get_process_dashboard():
    active_processes = []
    for instance_id, instance in framework.instances.items():
        if instance.status.value == "in_progress":
            status = visualizer.generate_process_status(instance_id)
            active_processes.append({
                "id": instance_id,
                "name": status["process_name"],
                "progress": status["progress_percentage"],
                "current": status["current_step"]["name"]
            })
    return active_processes
```

### Performance Check

```python
def check_bottlenecks(instance_id):
    timeline = visualizer.generate_timeline(instance_id)
    bottlenecks = []

    for entry in timeline['timeline_entries']:
        if not entry['on_schedule']:
            bottlenecks.append({
                "step": entry['step_name'],
                "duration": entry['duration_seconds'],
                "expected": entry['estimated_duration_minutes'] * 60
            })

    return bottlenecks
```

### Real-time Monitor

```python
def monitor_process(instance_id, callback):
    """Monitor process with callback on status change"""
    last_step = None

    while True:
        status = visualizer.generate_process_status(instance_id)
        current_step = status['current_step']['id']

        if current_step != last_step:
            callback(status)
            last_step = current_step

        if status['status'] == 'completed':
            break

        time.sleep(5)
```

## API Endpoints

### FastAPI Example

```python
from fastapi import FastAPI, HTTPException
from visualization import ProcessVisualizer

app = FastAPI()
visualizer = ProcessVisualizer()

@app.get("/api/processes/{process_id}/diagram")
async def get_diagram(process_id: str):
    try:
        diagram = visualizer.generate_mermaid_diagram(process_id)
        return {"diagram": diagram}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/instances/{instance_id}/status")
async def get_status(instance_id: str):
    try:
        status = visualizer.generate_process_status(instance_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/instances/{instance_id}/timeline")
async def get_timeline(instance_id: str):
    try:
        timeline = visualizer.generate_timeline(instance_id)
        return timeline
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/processes/{process_id}/export")
async def export_process(process_id: str, include_instances: bool = False):
    try:
        json_data = visualizer.export_to_json(process_id, include_instances)
        return json.loads(json_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

## Frontend Integration

### React Hook

```javascript
import { useState, useEffect } from 'react';

function useProcessStatus(instanceId) {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
      const response = await fetch(`/api/instances/${instanceId}/status`);
      const data = await response.json();
      setStatus(data);
      setLoading(false);
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Poll every 5s

    return () => clearInterval(interval);
  }, [instanceId]);

  return { status, loading };
}

// Usage
function ProcessMonitor({ instanceId }) {
  const { status, loading } = useProcessStatus(instanceId);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>{status.process_name}</h2>
      <ProgressBar value={status.progress_percentage} />
      <p>Current: {status.current_step.name}</p>
      <p>ETA: {status.estimated_completion}</p>
    </div>
  );
}
```

### Vue Composition API

```javascript
import { ref, onMounted, onUnmounted } from 'vue';

export function useProcessStatus(instanceId) {
  const status = ref(null);
  const loading = ref(true);
  let intervalId = null;

  const fetchStatus = async () => {
    const response = await fetch(`/api/instances/${instanceId}/status`);
    status.value = await response.json();
    loading.value = false;
  };

  onMounted(() => {
    fetchStatus();
    intervalId = setInterval(fetchStatus, 5000);
  });

  onUnmounted(() => {
    if (intervalId) clearInterval(intervalId);
  });

  return { status, loading };
}
```

## Visualization Examples

### vis.js Network

```javascript
import { Network } from 'vis-network';

async function renderProcessGraph(processId, containerId) {
  // Fetch data
  const response = await fetch(`/api/processes/${processId}/export`);
  const data = await response.json();

  // Configure options
  const options = {
    layout: {
      hierarchical: {
        direction: 'UD',
        sortMethod: 'directed',
        nodeSpacing: 150,
        levelSeparation: 200
      }
    },
    nodes: {
      shape: 'box',
      font: { size: 14 }
    },
    edges: {
      arrows: 'to',
      smooth: { type: 'cubicBezier' }
    },
    physics: false
  };

  // Create network
  const container = document.getElementById(containerId);
  new Network(container, data.graph, options);
}
```

### D3.js Force Graph

```javascript
import * as d3 from 'd3';

async function renderForceGraph(processId, containerId) {
  const response = await fetch(`/api/processes/${processId}/export`);
  const data = await response.json();

  const width = 800;
  const height = 600;

  const svg = d3.select(`#${containerId}`)
    .append('svg')
    .attr('width', width)
    .attr('height', height);

  const simulation = d3.forceSimulation(data.graph.nodes)
    .force('link', d3.forceLink(data.graph.edges).id(d => d.id))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2));

  // Add edges
  const links = svg.append('g')
    .selectAll('line')
    .data(data.graph.edges)
    .enter().append('line')
    .attr('stroke', d => d.color)
    .attr('stroke-width', d => d.width);

  // Add nodes
  const nodes = svg.append('g')
    .selectAll('circle')
    .data(data.graph.nodes)
    .enter().append('circle')
    .attr('r', 20)
    .attr('fill', d => d.color);

  // Add labels
  const labels = svg.append('g')
    .selectAll('text')
    .data(data.graph.nodes)
    .enter().append('text')
    .text(d => d.label);

  simulation.on('tick', () => {
    links
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);

    nodes
      .attr('cx', d => d.x)
      .attr('cy', d => d.y);

    labels
      .attr('x', d => d.x)
      .attr('y', d => d.y);
  });
}
```

## Testing

```bash
# Run tests
cd /Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence
python3 test_visualization.py

# View generated files
ls -la test_processes/
```

## Cheat Sheet

| Task | Method | Output |
|------|--------|--------|
| Flowchart diagram | `generate_mermaid_diagram(process_id)` | Mermaid syntax |
| Process status | `generate_process_status(instance_id)` | Status dict |
| Execution timeline | `generate_timeline(instance_id)` | Timeline dict |
| Graph data | `export_to_json(process_id)` | JSON string |
| Gantt chart | `generate_gantt_data(instance_id)` | Gantt dict |
| BPMN export | `export_to_bpmn(process_id)` | BPMN XML |

## Error Handling

```python
from visualization import ProcessVisualizer

visualizer = ProcessVisualizer()

try:
    diagram = visualizer.generate_mermaid_diagram("process_id")
except ValueError as e:
    print(f"Error: {e}")
    # Handle missing process

try:
    status = visualizer.generate_process_status("instance_id")
except ValueError as e:
    print(f"Error: {e}")
    # Handle missing instance
```

## Best Practices

1. **Cache diagrams** for static processes
2. **Poll status** every 5-10 seconds for real-time updates
3. **Use include_instances=False** for better performance
4. **Validate IDs** before calling visualization methods
5. **Handle errors** gracefully in production
6. **Paginate** large result sets
7. **Use async** for non-blocking operations

## Performance Tips

```python
# Good: Cache diagram for static process
diagram_cache = {}

def get_diagram(process_id):
    if process_id not in diagram_cache:
        diagram_cache[process_id] = visualizer.generate_mermaid_diagram(process_id)
    return diagram_cache[process_id]

# Good: Batch status checks
def get_multiple_statuses(instance_ids):
    return {
        instance_id: visualizer.generate_process_status(instance_id)
        for instance_id in instance_ids
    }

# Good: Async generation
import asyncio

async def generate_all_visualizations(process_id):
    diagram = await asyncio.to_thread(
        visualizer.generate_mermaid_diagram, process_id
    )
    json_data = await asyncio.to_thread(
        visualizer.export_to_json, process_id
    )
    return {"diagram": diagram, "json": json_data}
```

## Next Steps

1. Read the [full documentation](./VISUALIZATION_README.md)
2. Review [process framework](./process_framework.py)
3. Check [example processes](./bcm_processes.py)
4. Explore [test file](./test_visualization.py)

---

**Quick Start Version:** 1.0.0
**Last Updated:** October 12, 2025
