"""
Mock data for LMS Adapter testing
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

def get_mock_lms_configs() -> List[Dict[str, Any]]:
    """Generate mock LMS configurations"""
    return [
        {
            "id": "lms_001",
            "name": "Corporate Moodle",
            "lms_type": "moodle",
            "base_url": "https://learning.company.com",
            "api_key": "mock_moodle_token_12345",
            "tenant_id": "tenant_001", 
            "is_active": True,
            "settings": {
                "site_id": "corporate_main",
                "default_role": "student",
                "auto_enroll": True
            }
        },
        {
            "id": "lms_002", 
            "name": "Open edX Platform",
            "lms_type": "openedx",
            "base_url": "https://courses.company.com", 
            "api_key": "mock_edx_client_id",
            "api_secret": "mock_edx_client_secret",
            "tenant_id": "tenant_001",
            "is_active": True,
            "settings": {
                "client_id": "bcm_platform_client",
                "organization": "CompanyX"
            }
        },
        {
            "id": "lms_003",
            "name": "Canvas Training Portal",
            "lms_type": "canvas", 
            "base_url": "https://companyx.instructure.com",
            "api_key": "mock_canvas_token_67890",
            "tenant_id": "tenant_001",
            "is_active": True,
            "settings": {
                "account_id": "12345",
                "default_term": "Default Term"
            }
        }
    ]

def get_mock_courses() -> List[Dict[str, Any]]:
    """Generate mock courses for all LMS types"""
    base_time = datetime.utcnow()
    return [
        {
            "id": "course_001",
            "title": "Business Continuity Management Fundamentals",
            "description": "Introduction to BCM principles, framework, and best practices",
            "category": "BCM Foundation",
            "instructor": "Dr. Sarah Johnson",
            "duration_hours": 8,
            "enrollment_count": 145,
            "completion_rate": 87.5,
            "lms_course_id": "bcm_fundamentals_101",
            "lms_type": "moodle", 
            "is_active": True
        },
        {
            "id": "course_002",
            "title": "Risk Assessment and BIA", 
            "description": "Advanced course on risk assessment and business impact analysis",
            "category": "Risk Management",
            "instructor": "Prof. Michael Chen",
            "duration_hours": 12,
            "enrollment_count": 89,
            "completion_rate": 76.4,
            "lms_course_id": "risk_bia_201", 
            "lms_type": "openedx",
            "is_active": True
        },
        {
            "id": "course_003",
            "title": "Crisis Communication",
            "description": "Effective communication strategies during business disruptions",
            "category": "Communication",
            "instructor": "Ms. Lisa Rodriguez", 
            "duration_hours": 6,
            "enrollment_count": 203,
            "completion_rate": 91.2,
            "lms_course_id": "crisis_comm_101",
            "lms_type": "canvas",
            "is_active": True
        },
        {
            "id": "course_004", 
            "title": "Incident Response Procedures",
            "description": "Step-by-step incident response and recovery procedures",
            "category": "Incident Management",
            "instructor": "Mr. David Thompson",
            "duration_hours": 10,
            "enrollment_count": 67,
            "completion_rate": 82.1,
            "lms_course_id": "incident_response_301",
            "lms_type": "moodle",
            "is_active": True
        },
        {
            "id": "course_005",
            "title": "ISO 22301 Implementation",
            "description": "Comprehensive guide to implementing ISO 22301 standard",
            "category": "Compliance",
            "instructor": "Dr. Amanda White",
            "duration_hours": 16, 
            "enrollment_count": 34,
            "completion_rate": 70.6,
            "lms_course_id": "iso22301_impl_401",
            "lms_type": "openedx",
            "is_active": True
        }
    ]

def get_mock_enrollments() -> List[Dict[str, Any]]:
    """Generate mock user enrollments"""
    base_time = datetime.utcnow()
    return [
        {
            "id": "enroll_001",
            "course_id": "course_001",
            "user_id": "user_001", 
            "user_email": "john.doe@company.com",
            "enrolled_at": base_time - timedelta(days=30),
            "completed_at": base_time - timedelta(days=2),
            "progress_percent": 100.0,
            "status": "COMPLETED",
            "grade": 95.5,
            "certificate_url": "https://learning.company.com/certificates/cert_001.pdf"
        },
        {
            "id": "enroll_002",
            "course_id": "course_002",
            "user_id": "user_001",
            "user_email": "john.doe@company.com", 
            "enrolled_at": base_time - timedelta(days=15),
            "progress_percent": 65.0,
            "status": "IN_PROGRESS",
            "grade": None
        },
        {
            "id": "enroll_003", 
            "course_id": "course_003",
            "user_id": "user_002",
            "user_email": "jane.smith@company.com",
            "enrolled_at": base_time - timedelta(days=45),
            "completed_at": base_time - timedelta(days=20), 
            "progress_percent": 100.0,
            "status": "COMPLETED",
            "grade": 88.0,
            "certificate_url": "https://companyx.instructure.com/certificates/cert_002.pdf"
        },
        {
            "id": "enroll_004",
            "course_id": "course_001",
            "user_id": "user_003", 
            "user_email": "mike.wilson@company.com",
            "enrolled_at": base_time - timedelta(days=5),
            "progress_percent": 25.0,
            "status": "IN_PROGRESS"
        },
        {
            "id": "enroll_005",
            "course_id": "course_004",
            "user_id": "user_002",
            "user_email": "jane.smith@company.com",
            "enrolled_at": base_time - timedelta(days=60),
            "progress_percent": 0.0,
            "status": "ENROLLED"
        }
    ]

def get_mock_training_paths() -> List[Dict[str, Any]]:
    """Generate mock training paths/curricula"""
    return [
        {
            "id": "path_001",
            "name": "BCM Practitioner Certification",
            "description": "Complete certification path for BCM professionals",
            "required_courses": [
                "course_001",  # BCM Fundamentals
                "course_002",  # Risk Assessment and BIA
                "course_004",  # Incident Response
                "course_005"   # ISO 22301 Implementation
            ],
            "optional_courses": [
                "course_003"   # Crisis Communication
            ],
            "estimated_duration_weeks": 12,
            "certification_requirements": {
                "min_grade": 80.0,
                "practical_assessment": True,
                "continuing_education": "16 hours annually"
            }
        },
        {
            "id": "path_002", 
            "name": "Crisis Communication Specialist",
            "description": "Specialized path for communication roles during crises",
            "required_courses": [
                "course_001",  # BCM Fundamentals
                "course_003"   # Crisis Communication
            ],
            "optional_courses": [
                "course_004"   # Incident Response
            ],
            "estimated_duration_weeks": 6,
            "certification_requirements": {
                "min_grade": 85.0,
                "presentation_assessment": True
            }
        },
        {
            "id": "path_003",
            "name": "Executive BCM Overview", 
            "description": "Executive-level overview of business continuity management",
            "required_courses": [
                "course_001"   # BCM Fundamentals
            ],
            "optional_courses": [
                "course_003"   # Crisis Communication
            ],
            "estimated_duration_weeks": 2,
            "certification_requirements": {
                "min_grade": 75.0,
                "executive_briefing": True
            }
        }
    ]

def get_mock_competency_matrix() -> Dict[str, Any]:
    """Generate mock competency matrix for BCM roles"""
    return {
        "roles": {
            "bcm_manager": {
                "title": "BCM Manager",
                "required_competencies": [
                    "BCM Framework Understanding",
                    "Risk Assessment", 
                    "Plan Development",
                    "Team Leadership",
                    "Stakeholder Communication"
                ],
                "required_courses": ["course_001", "course_002", "course_004", "course_005"],
                "certification_level": "Expert"
            },
            "incident_coordinator": {
                "title": "Incident Coordinator", 
                "required_competencies": [
                    "Incident Response Procedures",
                    "Crisis Communication",
                    "Team Coordination",
                    "Decision Making Under Pressure"
                ],
                "required_courses": ["course_001", "course_003", "course_004"],
                "certification_level": "Practitioner"
            },
            "department_rep": {
                "title": "Department Representative",
                "required_competencies": [
                    "BCM Awareness",
                    "Emergency Procedures", 
                    "Communication Protocols"
                ],
                "required_courses": ["course_001", "course_003"],
                "certification_level": "Foundation"
            },
            "executive": {
                "title": "Executive/Senior Management",
                "required_competencies": [
                    "Strategic BCM Understanding",
                    "Governance and Oversight",
                    "Resource Allocation",
                    "Stakeholder Communication"
                ], 
                "required_courses": ["course_001"],
                "certification_level": "Executive"
            }
        },
        "competency_levels": {
            "Foundation": {"min_score": 70, "color": "green"},
            "Practitioner": {"min_score": 80, "color": "blue"},  
            "Expert": {"min_score": 90, "color": "gold"},
            "Executive": {"min_score": 75, "color": "purple"}
        }
    }

def get_mock_learning_analytics() -> Dict[str, Any]:
    """Generate mock learning analytics data"""
    return {
        "summary": {
            "total_users": 245,
            "active_enrollments": 89,
            "completed_courses": 156,
            "average_completion_rate": 84.2,
            "average_score": 87.5
        },
        "course_performance": [
            {
                "course_id": "course_001",
                "title": "BCM Fundamentals", 
                "enrollments": 145,
                "completions": 127,
                "completion_rate": 87.5,
                "average_score": 89.2,
                "time_to_complete_avg_days": 21
            },
            {
                "course_id": "course_002", 
                "title": "Risk Assessment and BIA",
                "enrollments": 89,
                "completions": 68,
                "completion_rate": 76.4,
                "average_score": 85.1,
                "time_to_complete_avg_days": 35
            }
        ],
        "trending": {
            "most_popular": "course_003",
            "highest_completion": "course_001", 
            "most_challenging": "course_005",
            "newest_enrollments": 23
        },
        "compliance_status": {
            "compliant_users": 189,
            "non_compliant_users": 56,
            "compliance_rate": 77.1,
            "overdue_certifications": 12
        }
    }