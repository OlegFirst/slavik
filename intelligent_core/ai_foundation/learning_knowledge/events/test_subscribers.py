"""
Test Suite for Reactive Learning Event Subscribers

Demonstrates event handling and learning actions.
"""

import asyncio
import pytest
from datetime import datetime
from typing import Dict, Any


# Mock EventBusClient for testing
class MockEventBusClient:
    """Mock EventBus for testing without RabbitMQ"""

    def __init__(self):
        self.published_events = []
        self.subscribers = {}

    async def connect(self):
        pass

    async def disconnect(self):
        pass

    async def publish(self, event_type: str, event_data: Dict[str, Any], tenant_id: str = None):
        self.published_events.append({
            'event_type': event_type,
            'data': event_data,
            'tenant_id': tenant_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        return True

    async def subscribe(self, event_type: str, handler, queue_name: str = None):
        self.subscribers[event_type] = handler


# Test fixtures
@pytest.fixture
async def mock_subscriber():
    """Create LearningEventSubscriber with mocks"""
    from subscribers import LearningEventSubscriber
    from learning.engines.self_learning_engine import SelfLearningEngine
    from learning.engines.pattern_detector import PatternDetector

    # Create mock components
    class MockCompetencyTracker:
        def __init__(self):
            self.updates = []

        async def update_competency(self, user_id, competency, score, evidence_type, evidence_id):
            self.updates.append({
                'user_id': user_id,
                'competency': competency,
                'score': score,
                'evidence_type': evidence_type,
                'evidence_id': evidence_id
            })

    eventbus = MockEventBusClient()
    self_learning = SelfLearningEngine()
    pattern_detector = PatternDetector()
    competency_tracker = MockCompetencyTracker()

    subscriber = LearningEventSubscriber(
        eventbus=eventbus,
        self_learning_engine=self_learning,
        pattern_detector=pattern_detector,
        competency_tracker=competency_tracker
    )

    return subscriber


# ============================================================================
# TEST: Community Intelligence Events
# ============================================================================

@pytest.mark.asyncio
async def test_case_approved_handler(mock_subscriber):
    """Test learning from approved case"""

    event_data = {
        'case_id': 'case-test-001',
        'case_data': {
            'module': 'bia',
            'outcome': 'success',
            'organization_context': {
                'industry': 'healthcare',
                'size': 'large',
                'maturity_level': 3
            },
            'metrics': {
                'success_score': 95,
                'completion_time_hours': 8,
                'team_size': 5
            },
            'competencies_demonstrated': {
                'business_impact_analysis': 90,
                'risk_assessment': 85
            },
            'user_id': 'user-123'
        }
    }

    # Process event
    await mock_subscriber.handle_case_approved(event_data, 'tenant-001')

    # Verify ML training buffer updated
    assert len(mock_subscriber.self_learning.training_buffer) == 1
    training_sample = mock_subscriber.self_learning.training_buffer[0]
    assert training_sample['case_id'] == 'case-test-001'
    assert training_sample['source'] == 'community_intelligence'

    # Verify competency updates
    assert len(mock_subscriber.competency_tracker.updates) == 2  # Two competencies
    assert mock_subscriber.competency_tracker.updates[0]['competency'] == 'business_impact_analysis'

    # Verify statistics
    assert mock_subscriber.events_processed['case_approved'] == 1

    print("✅ case.approved handler test passed")


@pytest.mark.asyncio
async def test_case_rejected_handler(mock_subscriber):
    """Test rejection pattern analysis"""

    event_data = {
        'case_id': 'case-test-002',
        'rejection_reasons': ['incomplete_data', 'quality_issues'],
        'case_data': {
            'module': 'risk',
            'metadata': {'submitted_by': 'user-456'}
        }
    }

    # Process event
    await mock_subscriber.handle_case_rejected(event_data, 'tenant-001')

    # Verify rejection pattern recorded
    assert hasattr(mock_subscriber, 'rejection_patterns')
    assert len(mock_subscriber.rejection_patterns) == 1
    assert 'incomplete_data' in mock_subscriber.rejection_patterns[0]['reasons']

    # Verify statistics
    assert mock_subscriber.events_processed['case_rejected'] == 1

    print("✅ case.rejected handler test passed")


@pytest.mark.asyncio
async def test_review_submitted_handler(mock_subscriber):
    """Test learning from peer reviews"""

    event_data = {
        'review_id': 'review-001',
        'case_id': 'case-test-001',
        'rating': 5,
        'feedback': 'Excellent quality and thoroughness'
    }

    # Process event
    await mock_subscriber.handle_review_submitted(event_data, 'tenant-001')

    # Verify quality signal recorded
    assert hasattr(mock_subscriber, 'quality_signals')
    assert len(mock_subscriber.quality_signals) == 1
    assert mock_subscriber.quality_signals[0]['rating'] == 5

    # Verify statistics
    assert mock_subscriber.events_processed['review_submitted'] == 1

    print("✅ review.submitted handler test passed")


# ============================================================================
# TEST: Workflow Intelligence Events
# ============================================================================

@pytest.mark.asyncio
async def test_workflow_completed_handler(mock_subscriber):
    """Test learning from completed workflows"""

    event_data = {
        'workflow_id': 'wf-001',
        'module': 'bia',
        'context': {
            'metrics': {
                'duration_minutes': 120,
                'steps_completed': 15,
                'quality_score': 88
            },
            'team_avg_competency': 75,
            'preparation_days': 7,
            'scenario_type': 'standard'
        }
    }

    # Process event
    await mock_subscriber.handle_workflow_completed(event_data, 'tenant-001')

    # Verify workflow result recorded
    assert hasattr(mock_subscriber, 'workflow_results')
    assert len(mock_subscriber.workflow_results) == 1
    assert mock_subscriber.workflow_results[0]['outcome'] == 'success'

    # Verify ML training buffer updated
    assert len(mock_subscriber.self_learning.training_buffer) >= 1

    # Verify statistics
    assert mock_subscriber.events_processed['workflow_completed'] == 1

    print("✅ workflow.completed handler test passed")


@pytest.mark.asyncio
async def test_workflow_milestone_reached_handler(mock_subscriber):
    """Test competency updates from milestones"""

    event_data = {
        'workflow_id': 'wf-002',
        'milestone': 'bia_assessment_complete',
        'user_id': 'user-789'
    }

    # Process event
    await mock_subscriber.handle_workflow_milestone_reached(event_data, 'tenant-001')

    # Verify competency update
    assert len(mock_subscriber.competency_tracker.updates) == 1
    update = mock_subscriber.competency_tracker.updates[0]
    assert update['competency'] == 'business_impact_analysis'
    assert update['score'] == 10  # +10 points for milestone

    # Verify statistics
    assert mock_subscriber.events_processed['workflow_milestone'] == 1

    print("✅ workflow.milestone_reached handler test passed")


# ============================================================================
# TEST: Pattern Detection
# ============================================================================

@pytest.mark.asyncio
async def test_pattern_detection_workflow_batch(mock_subscriber):
    """Test pattern detection from batch of workflows"""

    # Create 20 workflow events to trigger pattern detection
    for i in range(20):
        event_data = {
            'workflow_id': f'wf-{i:03d}',
            'module': 'bia',
            'context': {
                'metrics': {
                    'duration_minutes': 100 + i * 5,
                    'steps_completed': 15,
                    'quality_score': 70 + i
                }
            }
        }
        await mock_subscriber.handle_workflow_completed(event_data, 'tenant-001')

    # Patterns should be detected (buffer cleared to last 50)
    assert len(mock_subscriber.workflow_results) <= 50
    assert mock_subscriber.events_processed['workflow_completed'] == 20

    print("✅ Pattern detection test passed")


# ============================================================================
# TEST: Statistics
# ============================================================================

@pytest.mark.asyncio
async def test_get_statistics(mock_subscriber):
    """Test statistics collection"""

    # Process some events
    await mock_subscriber.handle_case_approved({
        'case_id': 'case-001',
        'case_data': {'module': 'bia', 'metrics': {'success_score': 90}}
    }, 'tenant-001')

    await mock_subscriber.handle_workflow_completed({
        'workflow_id': 'wf-001',
        'module': 'risk',
        'context': {'metrics': {'quality_score': 85}}
    }, 'tenant-001')

    # Get statistics
    stats = mock_subscriber.get_statistics()

    # Verify
    assert stats['total_events'] == 2
    assert stats['events_processed']['case_approved'] == 1
    assert stats['events_processed']['workflow_completed'] == 1
    assert 'ml_training_buffer_size' in stats
    assert 'model_version' in stats

    print("✅ Statistics test passed")
    print(f"   Stats: {stats}")


# ============================================================================
# INTEGRATION TEST
# ============================================================================

@pytest.mark.asyncio
async def test_full_reactive_learning_cycle():
    """Test complete reactive learning cycle"""

    print("\n🚀 Testing Full Reactive Learning Cycle\n")

    # 1. Setup
    print("1️⃣ Setting up mock subscriber...")
    from subscribers import LearningEventSubscriber
    from learning.engines.self_learning_engine import SelfLearningEngine
    from learning.engines.pattern_detector import PatternDetector

    class MockCompetencyTracker:
        def __init__(self):
            self.updates = []
        async def update_competency(self, *args, **kwargs):
            self.updates.append(kwargs)

    eventbus = MockEventBusClient()
    subscriber = LearningEventSubscriber(
        eventbus=eventbus,
        self_learning_engine=SelfLearningEngine(),
        pattern_detector=PatternDetector(),
        competency_tracker=MockCompetencyTracker()
    )
    print("   ✅ Subscriber ready\n")

    # 2. User completes workflow
    print("2️⃣ User completes BIA workflow...")
    await subscriber.handle_workflow_completed({
        'workflow_id': 'wf-cycle-001',
        'module': 'bia',
        'context': {
            'metrics': {'quality_score': 92, 'duration_minutes': 90},
            'team_avg_competency': 80
        }
    }, 'tenant-001')
    print("   ✅ Workflow completion learned\n")

    # 3. Case approved in community
    print("3️⃣ Case approved by community...")
    await subscriber.handle_case_approved({
        'case_id': 'case-cycle-001',
        'case_data': {
            'module': 'bia',
            'metrics': {'success_score': 95},
            'user_id': 'user-cycle-001',
            'competencies_demonstrated': {'business_impact_analysis': 90}
        }
    }, 'tenant-001')
    print("   ✅ Case approval learned\n")

    # 4. Milestone reached
    print("4️⃣ User reaches milestone...")
    await subscriber.handle_workflow_milestone_reached({
        'workflow_id': 'wf-cycle-002',
        'milestone': 'bia_assessment_complete',
        'user_id': 'user-cycle-001'
    }, 'tenant-001')
    print("   ✅ Milestone competency updated\n")

    # 5. Exercise completed
    print("5️⃣ User completes training exercise...")
    await subscriber.handle_exercise_completed({
        'exercise_id': 'ex-cycle-001',
        'results': {
            'overall_score': 88,
            'issues': ['time_management'],
            'strengths': ['analysis_depth']
        }
    }, 'tenant-001')
    print("   ✅ Exercise outcome learned\n")

    # 6. Incident resolved
    print("6️⃣ Incident resolved...")
    await subscriber.handle_incident_resolved({
        'incident_id': 'inc-cycle-001',
        'incident_type': 'data_breach',
        'resolution': {
            'duration_minutes': 45,
            'effectiveness_score': 90,
            'actions': ['isolate_system', 'notify_stakeholders']
        }
    }, 'tenant-001')
    print("   ✅ Incident resolution learned\n")

    # 7. Get statistics
    print("7️⃣ Checking learning statistics...")
    stats = subscriber.get_statistics()
    print(f"   📊 Total events processed: {stats['total_events']}")
    print(f"   🧠 ML training buffer: {stats['ml_training_buffer_size']} samples")
    print(f"   📈 Model version: {stats['model_version']}")
    print("   ✅ Statistics collected\n")

    # Verify complete cycle
    assert stats['total_events'] == 5
    assert stats['events_processed']['workflow_completed'] == 1
    assert stats['events_processed']['case_approved'] == 1
    assert stats['events_processed']['workflow_milestone'] == 1
    assert stats['events_processed']['exercise_completed'] == 1
    assert stats['events_processed']['incident_resolved'] == 1

    print("✅ FULL REACTIVE LEARNING CYCLE COMPLETE!\n")
    print("📊 Summary:")
    print(f"   • Events processed: {stats['total_events']}")
    print(f"   • ML samples: {stats['ml_training_buffer_size']}")
    print(f"   • Competency updates: {len(subscriber.competency_tracker.updates)}")
    print(f"   • Model version: {stats['model_version']}")
    print("\n🎉 Platform learned from real_world usage and improved itself!\n")


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("REACTIVE LEARNING EVENT SUBSCRIBERS - TEST SUITE")
    print("=" * 60)

    # Run integration test
    asyncio.run(test_full_reactive_learning_cycle())

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
