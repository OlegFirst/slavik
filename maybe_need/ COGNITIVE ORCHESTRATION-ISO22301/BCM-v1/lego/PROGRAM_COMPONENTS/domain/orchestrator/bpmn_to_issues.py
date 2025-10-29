#!/usr/bin/env python3
"""
Generate GitHub issues from BPMN for BCM Platform
Extracts tasks, subprocesses, and events to create actionable backlog items
"""

import argparse
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import requests
from datetime import datetime
import re


class BPMNTaskExtractor:
    """Extract tasks and generate issues from BPMN files"""
    
    def __init__(self, bpmn_path: str):
        self.bpmn_path = bpmn_path
        self.ns = {
            'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
            'camunda': 'http://camunda.org/schema/1.0/bpmn'
        }
        self.tree = ET.parse(bpmn_path)
        self.root = self.tree.getroot()
        self.tasks = []
        self.subprocesses = []
        self.events = []
        self.gateways = []
    
    def extract_all(self) -> Dict[str, List[Dict]]:
        """Extract all BPMN elements"""
        self._extract_tasks()
        self._extract_subprocesses()
        self._extract_events()
        self._extract_gateways()
        self._extract_lanes()
        
        return {
            'tasks': self.tasks,
            'subprocesses': self.subprocesses,
            'events': self.events,
            'gateways': self.gateways,
            'total': len(self.tasks) + len(self.subprocesses) + len(self.events) + len(self.gateways)
        }
    
    def _extract_tasks(self):
        """Extract all tasks from BPMN"""
        for task in self.root.findall('.//bpmn:task', self.ns):
            self.tasks.append(self._process_task(task, 'task'))
        
        for user_task in self.root.findall('.//bpmn:userTask', self.ns):
            self.tasks.append(self._process_task(user_task, 'user_task'))
        
        for service_task in self.root.findall('.//bpmn:serviceTask', self.ns):
            self.tasks.append(self._process_task(service_task, 'service_task'))
        
        for business_task in self.root.findall('.//bpmn:businessRuleTask', self.ns):
            self.tasks.append(self._process_task(business_task, 'business_rule'))
    
    def _extract_subprocesses(self):
        """Extract all subprocesses"""
        for subprocess in self.root.findall('.//bpmn:subProcess', self.ns):
            sp_data = {
                'id': subprocess.attrib.get('id'),
                'name': subprocess.attrib.get('name', 'Unnamed Subprocess'),
                'type': 'subprocess',
                'triggered_by_event': subprocess.attrib.get('triggeredByEvent', 'false') == 'true',
                'tasks': []
            }
            
            # Extract tasks within subprocess
            for task in subprocess.findall('.//bpmn:task', self.ns):
                sp_data['tasks'].append(task.attrib.get('name', 'Unnamed'))
            
            self.subprocesses.append(sp_data)
    
    def _extract_events(self):
        """Extract all events"""
        event_types = [
            'startEvent', 'endEvent', 'intermediateCatchEvent', 
            'intermediateThrowEvent', 'boundaryEvent'
        ]
        
        for event_type in event_types:
            for event in self.root.findall(f'.//bpmn:{event_type}', self.ns):
                self.events.append({
                    'id': event.attrib.get('id'),
                    'name': event.attrib.get('name', f'Unnamed {event_type}'),
                    'type': event_type,
                    'message': self._get_event_definition(event)
                })
    
    def _extract_gateways(self):
        """Extract all gateways"""
        gateway_types = ['exclusiveGateway', 'parallelGateway', 'inclusiveGateway', 'eventBasedGateway']
        
        for gw_type in gateway_types:
            for gateway in self.root.findall(f'.//bpmn:{gw_type}', self.ns):
                self.gateways.append({
                    'id': gateway.attrib.get('id'),
                    'name': gateway.attrib.get('name', f'Unnamed {gw_type}'),
                    'type': gw_type
                })
    
    def _extract_lanes(self):
        """Extract swim lanes and their tasks"""
        lanes = {}
        for lane in self.root.findall('.//bpmn:lane', self.ns):
            lane_name = lane.attrib.get('name', 'Unnamed Lane')
            lanes[lane_name] = []
            
            for ref in lane.findall('.//bpmn:flowNodeRef', self.ns):
                lanes[lane_name].append(ref.text)
        
        # Map tasks to lanes
        for task in self.tasks:
            for lane_name, refs in lanes.items():
                if task['id'] in refs:
                    task['lane'] = lane_name
                    break
    
    def _process_task(self, element, task_type: str) -> Dict:
        """Process a task element"""
        task_data = {
            'id': element.attrib.get('id'),
            'name': element.attrib.get('name', 'Unnamed Task'),
            'type': task_type,
            'module': self._extract_module(element),
            'actor': self._extract_actor(element),
            'integration': self._extract_integration(element)
        }
        
        # Extract form fields if present
        form_fields = element.findall('.//camunda:formField', self.ns)
        if form_fields:
            task_data['form_fields'] = [f.attrib.get('label', '') for f in form_fields]
        
        return task_data
    
    def _extract_module(self, element) -> str:
        """Extract module from task properties"""
        for prop in element.findall('.//bpmn:property[@name="module"]', self.ns):
            return prop.text or prop.attrib.get('value', '')
        
        for param in element.findall('.//camunda:inputParameter[@name="module"]', self.ns):
            return param.text or ''
        
        return self._guess_module_from_name(element.attrib.get('name', ''))
    
    def _extract_actor(self, element) -> str:
        """Extract actor from task properties"""
        for prop in element.findall('.//bpmn:property[@name="actor"]', self.ns):
            return prop.text or prop.attrib.get('value', '')
        return ''
    
    def _extract_integration(self, element) -> str:
        """Extract integration info"""
        for param in element.findall('.//camunda:inputParameter[@name="integration"]', self.ns):
            return param.text or ''
        return ''
    
    def _get_event_definition(self, event) -> str:
        """Get event definition type"""
        definitions = [
            'messageEventDefinition', 'timerEventDefinition', 
            'conditionalEventDefinition', 'signalEventDefinition'
        ]
        
        for def_type in definitions:
            if event.find(f'.//bpmn:{def_type}', self.ns) is not None:
                return def_type.replace('EventDefinition', '')
        return ''
    
    def _guess_module_from_name(self, name: str) -> str:
        """Guess BCM module from task name"""
        name_lower = name.lower()
        
        module_keywords = {
            'bcm_bia': ['bia', 'impact', 'analysis', 'mtpd', 'rto', 'rpo'],
            'bcm_incident': ['incident', 'response', 'crisis'],
            'bcm_plans': ['plan', 'bcp', 'drp', 'continuity'],
            'bcm_audit': ['audit', 'compliance', 'iso', 'capa'],
            'bcm_training': ['training', 'exercise', 'drill', 'simulation'],
            'bcm_context': ['context', 'process', 'asset', 'import'],
            'bcm_kpi': ['kpi', 'metric', 'dashboard', 'performance'],
            'bcm_governance': ['governance', 'review', 'management', 'decision']
        }
        
        for module, keywords in module_keywords.items():
            if any(kw in name_lower for kw in keywords):
                return module
        
        return 'bcm_core'


class GitHubIssueGenerator:
    """Generate GitHub issues from BPMN tasks"""
    
    def __init__(self, repo: str, token: str = None):
        self.repo = repo
        self.token = token
        self.api_base = f"https://api.github.com/repos/{repo}"
        self.headers = {
            'Accept': 'application/vnd.github+json'
        }
        if token:
            self.headers['Authorization'] = f'token {token}'
    
    def generate_issues(self, bpmn_data: Dict, dry_run: bool = True) -> List[Dict]:
        """Generate issues from BPMN data"""
        issues = []
        
        # Generate task issues
        for task in bpmn_data.get('tasks', []):
            issue = self._create_task_issue(task)
            issues.append(issue)
        
        # Generate subprocess issues
        for subprocess in bpmn_data.get('subprocesses', []):
            issue = self._create_subprocess_issue(subprocess)
            issues.append(issue)
        
        # Generate event handler issues
        for event in bpmn_data.get('events', []):
            if event['name'] != event['type']:  # Skip unnamed events
                issue = self._create_event_issue(event)
                issues.append(issue)
        
        # Generate gateway logic issues
        for gateway in bpmn_data.get('gateways', []):
            if 'Gateway' not in gateway['name']:  # Skip default names
                issue = self._create_gateway_issue(gateway)
                issues.append(issue)
        
        if not dry_run and self.token:
            self._post_issues_to_github(issues)
        
        return issues
    
    def _create_task_issue(self, task: Dict) -> Dict:
        """Create issue for a task"""
        labels = ['bpmn', 'task']
        
        if task.get('module'):
            labels.append(f"module:{task['module']}")
        
        if task['type'] == 'user_task':
            labels.append('frontend')
        elif task['type'] == 'service_task':
            labels.append('backend')
        elif task['type'] == 'business_rule':
            labels.append('rules-engine')
        
        if task.get('integration'):
            labels.append('integration')
        
        title = f"[BPMN] {task['name']}"
        
        body = f"""## Task Implementation Required

**BPMN ID**: `{task['id']}`
**Type**: {task['type']}
**Module**: {task.get('module', 'TBD')}
**Actor**: {task.get('actor', 'TBD')}
**Lane**: {task.get('lane', 'TBD')}

### Description
Implement the task "{task['name']}" as defined in the BPMN process.

### Technical Requirements
- [ ] Create handler function in `{task.get('module', 'bcm_core')}`
- [ ] Add API endpoint if user-facing
- [ ] Implement business logic
- [ ] Add event emission
- [ ] Create tests

### Integration
{task.get('integration', 'No specific integration required')}

### Form Fields
{self._format_form_fields(task.get('form_fields', []))}

### Acceptance Criteria
- [ ] Task can be triggered by appropriate event
- [ ] Task produces expected output/side effects
- [ ] Task emits completion event
- [ ] Error handling implemented
- [ ] Logging added

### Related BPMN Elements
- Previous: TBD
- Next: TBD
"""
        
        return {
            'title': title,
            'body': body,
            'labels': labels
        }
    
    def _create_subprocess_issue(self, subprocess: Dict) -> Dict:
        """Create issue for a subprocess"""
        labels = ['bpmn', 'subprocess', 'epic']
        
        if subprocess.get('triggered_by_event'):
            labels.append('event-driven')
        
        title = f"[BPMN Epic] {subprocess['name']}"
        
        body = f"""## Subprocess Implementation

**BPMN ID**: `{subprocess['id']}`
**Event Triggered**: {subprocess.get('triggered_by_event', False)}

### Description
Implement the subprocess "{subprocess['name']}" containing multiple coordinated tasks.

### Subtasks
{self._format_subtasks(subprocess.get('tasks', []))}

### Technical Requirements
- [ ] Create subprocess coordinator
- [ ] Implement state management
- [ ] Handle subprocess events
- [ ] Implement error recovery
- [ ] Add subprocess monitoring

### Acceptance Criteria
- [ ] Subprocess can be initiated
- [ ] All subtasks execute in correct order
- [ ] Subprocess completes successfully
- [ ] Error handling covers all subtasks
- [ ] Subprocess state is trackable
"""
        
        return {
            'title': title,
            'body': body,
            'labels': labels
        }
    
    def _create_event_issue(self, event: Dict) -> Dict:
        """Create issue for an event handler"""
        labels = ['bpmn', 'event', 'orchestrator']
        
        if event.get('message'):
            labels.append(f"event-type:{event['message']}")
        
        title = f"[BPMN Event] Handle {event['name']}"
        
        body = f"""## Event Handler Implementation

**BPMN ID**: `{event['id']}`
**Event Type**: {event['type']}
**Message Type**: {event.get('message', 'N/A')}

### Description
Implement handler for the event "{event['name']}".

### Technical Requirements
- [ ] Create event listener
- [ ] Implement event processing logic
- [ ] Add event validation
- [ ] Implement retry logic if needed
- [ ] Add event logging

### Acceptance Criteria
- [ ] Event is properly captured
- [ ] Event triggers correct workflow
- [ ] Event data is validated
- [ ] Failed events are handled gracefully
"""
        
        return {
            'title': title,
            'body': body,
            'labels': labels
        }
    
    def _create_gateway_issue(self, gateway: Dict) -> Dict:
        """Create issue for a gateway"""
        labels = ['bpmn', 'gateway', 'business-logic']
        
        title = f"[BPMN Gateway] Implement {gateway['name']}"
        
        body = f"""## Gateway Logic Implementation

**BPMN ID**: `{gateway['id']}`
**Gateway Type**: {gateway['type']}

### Description
Implement the decision logic for "{gateway['name']}".

### Technical Requirements
- [ ] Define decision rules
- [ ] Implement condition evaluation
- [ ] Handle all possible paths
- [ ] Add decision logging
- [ ] Create tests for all branches

### Acceptance Criteria
- [ ] All conditions are evaluated correctly
- [ ] Correct path is chosen based on data
- [ ] Invalid conditions are handled
- [ ] Decision is logged for audit
"""
        
        return {
            'title': title,
            'body': body,
            'labels': labels
        }
    
    def _format_form_fields(self, fields: List[str]) -> str:
        """Format form fields for issue body"""
        if not fields:
            return "No form fields defined"
        
        return "\n".join([f"- [ ] {field}" for field in fields])
    
    def _format_subtasks(self, tasks: List[str]) -> str:
        """Format subtasks for issue body"""
        if not tasks:
            return "No subtasks defined"
        
        return "\n".join([f"- [ ] {task}" for task in tasks])
    
    def _post_issues_to_github(self, issues: List[Dict]):
        """Post issues to GitHub"""
        api_url = f"{self.api_base}/issues"
        
        for issue in issues:
            try:
                response = requests.post(
                    api_url,
                    headers=self.headers,
                    json=issue
                )
                
                if response.status_code == 201:
                    result = response.json()
                    print(f"Created: {result['html_url']}")
                else:
                    print(f"Failed: {issue['title']} - {response.status_code}")
                    print(response.text)
            
            except Exception as e:
                print(f"Error creating issue: {e}")


def main():
    parser = argparse.ArgumentParser(description='Generate GitHub issues from BPMN')
    parser.add_argument('--bpmn', required=True, help='Path to BPMN file')
    parser.add_argument('--out', help='Output JSON file for issues')
    parser.add_argument('--repo', help='GitHub repository (org/repo)')
    parser.add_argument('--token', help='GitHub personal access token')
    parser.add_argument('--live', action='store_true', help='Actually create issues on GitHub')
    parser.add_argument('--stats', action='store_true', help='Show statistics only')
    
    args = parser.parse_args()
    
    # Extract BPMN elements
    extractor = BPMNTaskExtractor(args.bpmn)
    bpmn_data = extractor.extract_all()
    
    if args.stats:
        print("\nBPMN Statistics:")
        print(f"  Tasks: {len(bpmn_data['tasks'])}")
        print(f"  Subprocesses: {len(bpmn_data['subprocesses'])}")
        print(f"  Events: {len(bpmn_data['events'])}")
        print(f"  Gateways: {len(bpmn_data['gateways'])}")
        print(f"  Total Elements: {bpmn_data['total']}")
        
        # Module distribution
        modules = {}
        for task in bpmn_data['tasks']:
            module = task.get('module', 'unknown')
            modules[module] = modules.get(module, 0) + 1
        
        print("\nModule Distribution:")
        for module, count in sorted(modules.items()):
            print(f"  {module}: {count}")
        
        return
    
    # Generate issues
    generator = GitHubIssueGenerator(args.repo, args.token)
    issues = generator.generate_issues(bpmn_data, dry_run=not args.live)
    
    # Save to JSON if requested
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump({
                'bpmn_file': args.bpmn,
                'generated_at': datetime.now().isoformat(),
                'statistics': {
                    'tasks': len(bpmn_data['tasks']),
                    'subprocesses': len(bpmn_data['subprocesses']),
                    'events': len(bpmn_data['events']),
                    'gateways': len(bpmn_data['gateways'])
                },
                'issues': issues
            }, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(issues)} issues to {args.out}")
    
    if not args.live:
        print(f"\nGenerated {len(issues)} issues (dry run)")
        print("Use --live flag to actually create issues on GitHub")
    else:
        print(f"\nCreated {len(issues)} issues on GitHub")


if __name__ == "__main__":
    main()
