"""
Tests for Contribution Service

Test cases:
1. Case submission workflow
2. Reviewer assignment
3. Peer review process
4. Approval/rejection logic
5. Reputation awarding
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import uuid
from ..services.contribution_service import ContributionService
from ..models.database import CaseContribution, PeerReview, UserReputation, ContributionStatus

@pytest.fixture
def mock_db():
    """Mock database session"""
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.get = AsyncMock()
    db.execute = AsyncMock()
    return db

@pytest.fixture
def mock_anonymizer():
    """Mock anonymizer"""
    anonymizer = AsyncMock()
    anonymizer.anonymize_case = AsyncMock(return_value=MagicMock(
        anonymized_data={"test": "data"},
        removed_fields=[],
        transformed_fields=[],
        risk_score=0.3
    ))
    return anonymizer

@pytest.fixture
def mock_case_library():
    """Mock case library"""
    library = AsyncMock()
    library.add_community_case = AsyncMock(return_value=uuid.uuid4())
    return library

@pytest.fixture
def service(mock_db, mock_anonymizer, mock_case_library):
    """Create service instance"""
    return ContributionService(mock_db, mock_anonymizer, mock_case_library)

@pytest.mark.asyncio
async def test_submit_case_creates_contribution(service, mock_db, mock_anonymizer):
    """Test case submission creates contribution record"""

    # Mock reviewer assignment
    service._assign_reviewers = AsyncMock(return_value=[
        MagicMock(user_id=uuid.uuid4()),
        MagicMock(user_id=uuid.uuid4()),
        MagicMock(user_id=uuid.uuid4())
    ])
    service._notify_reviewer = AsyncMock()

    case_data = {
        "organization_context": {"industry": "healthcare", "size": "medium"},
        "module": "bia"
    }

    contribution_id = await service.submit_case(
        contributor_id=str(uuid.uuid4()),
        case_data=case_data,
        module="bia"
    )

    # Verify anonymizer called
    mock_anonymizer.anonymize_case.assert_called_once()

    # Verify contribution created
    mock_db.add.assert_called()
    mock_db.commit.assert_called()

    assert contribution_id is not None

@pytest.mark.asyncio
async def test_assigns_three_reviewers(service):
    """Test that 3 reviewers are assigned"""

    # Mock qualified reviewers
    reviewers = [
        UserReputation(
            user_id=uuid.uuid4(),
            total_points=200,
            expertise={"bia": 70}
        ) for _ in range(5)
    ]

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = reviewers

    service.db.execute = AsyncMock(return_value=mock_result)
    service._get_pending_reviews_count = AsyncMock(return_value=2)

    assigned = await service._assign_reviewers(
        contribution_id=uuid.uuid4(),
        module="bia",
        exclude_user=str(uuid.uuid4())
    )

    assert len(assigned) == 3

@pytest.mark.asyncio
async def test_review_awards_reputation(service, mock_db):
    """Test that submitting review awards reputation"""

    review_data = {
        "approved": True,
        "quality_score": 8,
        "feedback": "Great case!",
        "anonymization_ok": True,
        "relevance_ok": True,
        "completeness_ok": True,
        "lessons_clear": True
    }

    service._award_reputation = AsyncMock()
    service._check_review_completion = AsyncMock()

    await service.submit_review(
        reviewer_id=str(uuid.uuid4()),
        contribution_id=str(uuid.uuid4()),
        review=review_data
    )

    # Verify reputation awarded
    service._award_reputation.assert_called_once()
    call_args = service._award_reputation.call_args
    assert call_args[1]['reason'] == 'peer_review_completed'
    assert call_args[1]['points'] == 5

@pytest.mark.asyncio
async def test_approval_with_majority(service, mock_db, mock_case_library):
    """Test case approved with 2+ approvals"""

    contribution = CaseContribution(
        id=uuid.uuid4(),
        contributor_id=uuid.uuid4(),
        case_data={"test": "data"},
        status=ContributionStatus.IN_REVIEW
    )

    reviews = [
        PeerReview(approved=True, quality_score=8),
        PeerReview(approved=True, quality_score=9),
        PeerReview(approved=False, quality_score=5)
    ]

    service._award_reputation = AsyncMock()
    service._notify_contributor_approved = AsyncMock()

    await service._approve_contribution(contribution, reviews)

    # Verify status updated
    assert contribution.status == ContributionStatus.APPROVED
    assert contribution.approved_at is not None
    assert contribution.added_to_library

    # Verify case added to library
    mock_case_library.add_community_case.assert_called_once()

    # Verify reputation awarded
    service._award_reputation.assert_called_once()

@pytest.mark.asyncio
async def test_level_calculation():
    """Test reputation level calculation"""

    service = ContributionService(None, None, None)

    assert service._calculate_level(50) == 'newcomer'
    assert service._calculate_level(150) == 'contributor'
    assert service._calculate_level(700) == 'expert'
    assert service._calculate_level(2500) == 'master'

@pytest.mark.asyncio
async def test_tag_extraction():
    """Test tag extraction from case data"""

    service = ContributionService(None, None, None)

    case_data = {
        "organization_context": {
            "industry": "healthcare",
            "size": "medium"
        },
        "success_patterns": [
            "Strong executive leadership drove adoption",
            "Automated workflow reduced manual effort"
        ]
    }

    tags = service._extract_tags(case_data, "bia")

    assert "bia" in tags
    assert "healthcare" in tags
    assert "medium" in tags
    assert len(tags) <= 10  # Max 10 tags
