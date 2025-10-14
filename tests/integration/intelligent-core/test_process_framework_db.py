"""
Integration Tests for Process Framework Database Operations

Tests the integration of Process Framework with PostgreSQL database:
- Process definition persistence
- Process instance CRUD operations
- Step execution audit trail
- Document template management
- Generated documents tracking
- Database views and analytics

Author: AI Platform Team
Date: 2025-10-11
"""

import pytest
import asyncio
import psycopg2
from datetime import datetime
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

# Import Process Framework components
import sys
sys.path.append("/Users/MD/AI-Platform-ISO/intelligent-core/workflow_intelligence")


# =====================================================
# Test Fixtures
# =====================================================

@pytest.fixture
def db_connection():
    """PostgreSQL database connection for testing"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="workflow_intelligence",
            user="postgres",
            password="postgres"
        )
        yield conn
        conn.rollback()  # Rollback test changes
        conn.close()
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


@pytest.fixture
def db_cursor(db_connection):
    """Database cursor"""
    cursor = db_connection.cursor()
    yield cursor
    cursor.close()


# =====================================================
# Test Process Definitions Table
# =====================================================

class TestProcessDefinitionsTable:
    """Test process_definitions table operations"""

    def test_insert_process_definition(self, db_cursor, db_connection):
        """Test inserting a process definition"""
        db_cursor.execute("""
            INSERT INTO process_definitions (
                process_id, name, version, description, category, iso_clause,
                start_step_id, end_step_ids, owner
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
        """, (
            "test_process_v1",
            "Test Process",
            "1.0",
            "Test process description",
            "testing",
            "8.2.2",
            "step_1",
            '["END"]',
            "Test Team"
        ))

        process_id = db_cursor.fetchone()[0]
        assert process_id is not None

    def test_query_process_definition_by_process_id(self, db_cursor, db_connection):
        """Test querying process definition by process_id"""
        # Insert test process
        db_cursor.execute("""
            INSERT INTO process_definitions (
                process_id, name, version, start_step_id, end_step_ids
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            "query_test_v1",
            "Query Test",
            "1.0",
            "start",
            '["END"]'
        ))
        db_connection.commit()

        # Query
        db_cursor.execute("""
            SELECT process_id, name, version
            FROM process_definitions
            WHERE process_id = %s
        """, ("query_test_v1",))

        result = db_cursor.fetchone()
        assert result is not None
        assert result[0] == "query_test_v1"
        assert result[1] == "Query Test"

    def test_process_definition_unique_constraint(self, db_cursor, db_connection):
        """Test unique constraint on (process_id, version)"""
        db_cursor.execute("""
            INSERT INTO process_definitions (
                process_id, name, version, start_step_id, end_step_ids
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            "unique_test_v1",
            "Unique Test",
            "1.0",
            "start",
            '["END"]'
        ))
        db_connection.commit()

        # Try to insert duplicate
        with pytest.raises(psycopg2.IntegrityError):
            db_cursor.execute("""
                INSERT INTO process_definitions (
                    process_id, name, version, start_step_id, end_step_ids
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                "unique_test_v1",
                "Unique Test Duplicate",
                "1.0",
                "start",
                '["END"]'
            ))
            db_connection.commit()

    def test_process_definition_with_compliance(self, db_cursor, db_connection):
        """Test process definition with ISO compliance requirements"""
        db_cursor.execute("""
            INSERT INTO process_definitions (
                process_id, name, version, iso_clause, compliance_requirements,
                start_step_id, end_step_ids
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            "compliance_test_v1",
            "Compliance Test",
            "1.0",
            "8.2.2",
            '["ISO 22301:2019", "ISO 22313:2020"]',
            "start",
            '["END"]'
        ))
        db_connection.commit()

        db_cursor.execute("""
            SELECT iso_clause, compliance_requirements
            FROM process_definitions
            WHERE process_id = %s
        """, ("compliance_test_v1",))

        result = db_cursor.fetchone()
        assert result[0] == "8.2.2"
        assert "ISO 22301:2019" in str(result[1])


# =====================================================
# Test Process Steps Table
# =====================================================

class TestProcessStepsTable:
    """Test process_steps table operations"""

    def test_insert_process_step(self, db_cursor, db_connection):
        """Test inserting a process step"""
        # First create process definition
        db_cursor.execute("""
            INSERT INTO process_definitions (
                process_id, name, version, start_step_id, end_step_ids
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (
            "step_test_v1",
            "Step Test",
            "1.0",
            "step_1",
            '["END"]'
        ))
        process_def_id = db_cursor.fetchone()[0]

        # Insert step
        db_cursor.execute("""
            INSERT INTO process_steps (
                process_definition_id, step_id, name, description, step_type,
                next_steps, allowed_roles
            ) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            process_def_id,
            "step_1",
            "First Step",
            "First step description",
            "FORM_INPUT",
            '["step_2"]',
            '["user", "admin"]'
        ))

        step_id = db_cursor.fetchone()[0]
        assert step_id is not None

    def test_query_steps_for_process(self, db_cursor, db_connection):
        """Test querying all steps for a process"""
        # Create process
        db_cursor.execute("""
            INSERT INTO process_definitions (
                process_id, name, version, start_step_id, end_step_ids
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (
            "multi_step_v1",
            "Multi Step",
            "1.0",
            "step_1",
            '["END"]'
        ))
        process_def_id = db_cursor.fetchone()[0]

        # Insert multiple steps
        for i in range(1, 4):
            db_cursor.execute("""
                INSERT INTO process_steps (
                    process_definition_id, step_id, name, step_type,
                    next_steps, allowed_roles
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                process_def_id,
                f"step_{i}",
                f"Step {i}",
                "FORM_INPUT",
                '[]',
                '["user"]'
            ))
        db_connection.commit()

        # Query steps
        db_cursor.execute("""
            SELECT COUNT(*)
            FROM process_steps
            WHERE process_definition_id = %s
        """, (process_def_id,))

        count = db_cursor.fetchone()[0]
        assert count == 3

    def test_process_step_with_ai_agent(self, db_cursor, db_connection):
        """Test process step with AI agent configuration"""
        # Create process
        db_cursor.execute("""
            INSERT INTO process_definitions (
                process_id, name, version, start_step_id, end_step_ids
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (
            "ai_step_v1",
            "AI Step Test",
            "1.0",
            "analysis",
            '["END"]'
        ))
        process_def_id = db_cursor.fetchone()[0]

        # Insert AI-powered step
        db_cursor.execute("""
            INSERT INTO process_steps (
                process_definition_id, step_id, name, step_type,
                ai_agent, next_steps, allowed_roles
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            process_def_id,
            "analysis",
            "AI Analysis",
            "ANALYSIS",
            "analytics_specialist",
            '["END"]',
            '["system"]'
        ))
        db_connection.commit()

        # Query
        db_cursor.execute("""
            SELECT ai_agent
            FROM process_steps
            WHERE step_id = %s
        """, ("analysis",))

        result = db_cursor.fetchone()
        assert result[0] == "analytics_specialist"

    def test_cascade_delete_steps(self, db_cursor, db_connection):
        """Test cascade delete of steps when process is deleted"""
        # Create process with steps
        db_cursor.execute("""
            INSERT INTO process_definitions (
                process_id, name, version, start_step_id, end_step_ids
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (
            "cascade_test_v1",
            "Cascade Test",
            "1.0",
            "step_1",
            '["END"]'
        ))
        process_def_id = db_cursor.fetchone()[0]

        db_cursor.execute("""
            INSERT INTO process_steps (
                process_definition_id, step_id, name, step_type,
                next_steps, allowed_roles
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            process_def_id,
            "step_1",
            "Step 1",
            "FORM_INPUT",
            '[]',
            '["user"]'
        ))
        db_connection.commit()

        # Delete process
        db_cursor.execute("""
            DELETE FROM process_definitions WHERE id = %s
        """, (process_def_id,))
        db_connection.commit()

        # Check steps are deleted
        db_cursor.execute("""
            SELECT COUNT(*)
            FROM process_steps
            WHERE process_definition_id = %s
        """, (process_def_id,))

        count = db_cursor.fetchone()[0]
        assert count == 0


# =====================================================
# Test Process Instances Table
# =====================================================

class TestProcessInstancesTable:
    """Test process_instances table operations"""

    def test_insert_process_instance(self, db_cursor, db_connection):
        """Test inserting a process instance"""
        # Create process
        db_cursor.execute("""
            INSERT INTO process_definitions (
                process_id, name, version, start_step_id, end_step_ids
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (
            "instance_test_v1",
            "Instance Test",
            "1.0",
            "step_1",
            '["END"]'
        ))
        process_def_id = db_cursor.fetchone()[0]

        # Insert instance
        db_cursor.execute("""
            INSERT INTO process_instances (
                instance_id, process_definition_id, status, current_step_id,
                started_by, data
            ) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            "instance_test_v1-20251011120000",
            process_def_id,
            "active",
            "step_1",
            "test_user@example.com",
            '{"organization": "Test Org"}'
        ))

        instance_id = db_cursor.fetchone()[0]
        assert instance_id is not None

    def test_query_active_instances(self, db_cursor, db_connection):
        """Test querying active process instances"""
        # Create process
        db_cursor.execute("""
            INSERT INTO process_definitions (
                process_id, name, version, start_step_id, end_step_ids
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (
            "active_test_v1",
            "Active Test",
            "1.0",
            "step_1",
            '["END"]'
        ))
        process_def_id = db_cursor.fetchone()[0]

        # Insert active instance
        db_cursor.execute("""
            INSERT INTO process_instances (
                instance_id, process_definition_id, status, current_step_id,
                started_by
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            "active_instance_1",
            process_def_id,
            "active",
            "step_1",
            "user@example.com"
        ))

        # Insert completed instance
        db_cursor.execute("""
            INSERT INTO process_instances (
                instance_id, process_definition_id, status, current_step_id,
                started_by, completed_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            "completed_instance_1",
            process_def_id,
            "completed",
            "END",
            "user@example.com",
            datetime.now()
        ))
        db_connection.commit()

        # Query active only
        db_cursor.execute("""
            SELECT COUNT(*)
            FROM process_instances
            WHERE status = 'active'
        """)

        count = db_cursor.fetchone()[0]
        assert count >= 1

    def test_update_instance_status(self, db_cursor, db_connection):
        """Test updating instance status"""
        # Create process and instance
        db_cursor.execute("""
            INSERT INTO process_definitions (
                process_id, name, version, start_step_id, end_step_ids
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (
            "update_test_v1",
            "Update Test",
            "1.0",
            "step_1",
            '["END"]'
        ))
        process_def_id = db_cursor.fetchone()[0]

        db_cursor.execute("""
            INSERT INTO process_instances (
                instance_id, process_definition_id, status, current_step_id,
                started_by
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (
            "update_instance_1",
            process_def_id,
            "active",
            "step_1",
            "user@example.com"
        ))
        instance_id = db_cursor.fetchone()[0]
        db_connection.commit()

        # Update status
        db_cursor.execute("""
            UPDATE process_instances
            SET status = 'completed', current_step_id = 'END', completed_at = NOW()
            WHERE id = %s
        """, (instance_id,))
        db_connection.commit()

        # Verify
        db_cursor.execute("""
            SELECT status, completed_at
            FROM process_instances
            WHERE id = %s
        """, (instance_id,))

        result = db_cursor.fetchone()
        assert result[0] == "completed"
        assert result[1] is not None


# =====================================================
# Test Step Executions Table
# =====================================================

class TestStepExecutionsTable:
    """Test step_executions table (audit trail)"""

    def test_insert_step_execution(self, db_cursor, db_connection):
        """Test inserting a step execution"""
        # Create process and instance
        db_cursor.execute("""
            INSERT INTO process_definitions (
                process_id, name, version, start_step_id, end_step_ids
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (
            "exec_test_v1",
            "Execution Test",
            "1.0",
            "step_1",
            '["END"]'
        ))
        process_def_id = db_cursor.fetchone()[0]

        db_cursor.execute("""
            INSERT INTO process_instances (
                instance_id, process_definition_id, status, current_step_id,
                started_by
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (
            "exec_instance_1",
            process_def_id,
            "active",
            "step_1",
            "user@example.com"
        ))
        instance_id = db_cursor.fetchone()[0]

        # Insert step execution
        db_cursor.execute("""
            INSERT INTO step_executions (
                process_instance_id, step_id, executed_by, input_data,
                output_data, result, duration_ms
            ) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            instance_id,
            "step_1",
            "user@example.com",
            '{"scope": "Test scope"}',
            '{"validated": true}',
            "success",
            150
        ))

        execution_id = db_cursor.fetchone()[0]
        assert execution_id is not None

    def test_query_execution_history(self, db_cursor, db_connection):
        """Test querying execution history for an instance"""
        # Create process and instance
        db_cursor.execute("""
            INSERT INTO process_definitions (
                process_id, name, version, start_step_id, end_step_ids
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (
            "history_test_v1",
            "History Test",
            "1.0",
            "step_1",
            '["END"]'
        ))
        process_def_id = db_cursor.fetchone()[0]

        db_cursor.execute("""
            INSERT INTO process_instances (
                instance_id, process_definition_id, status, current_step_id,
                started_by
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (
            "history_instance_1",
            process_def_id,
            "active",
            "step_1",
            "user@example.com"
        ))
        instance_id = db_cursor.fetchone()[0]

        # Insert multiple executions
        for i in range(3):
            db_cursor.execute("""
                INSERT INTO step_executions (
                    process_instance_id, step_id, executed_by, result
                ) VALUES (%s, %s, %s, %s)
            """, (
                instance_id,
                f"step_{i+1}",
                "user@example.com",
                "success"
            ))
        db_connection.commit()

        # Query history
        db_cursor.execute("""
            SELECT COUNT(*)
            FROM step_executions
            WHERE process_instance_id = %s
            ORDER BY executed_at ASC
        """, (instance_id,))

        count = db_cursor.fetchone()[0]
        assert count == 3

    def test_ai_execution_tracking(self, db_cursor, db_connection):
        """Test tracking AI agent executions"""
        # Create process and instance
        db_cursor.execute("""
            INSERT INTO process_definitions (
                process_id, name, version, start_step_id, end_step_ids
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (
            "ai_exec_test_v1",
            "AI Execution Test",
            "1.0",
            "analysis",
            '["END"]'
        ))
        process_def_id = db_cursor.fetchone()[0]

        db_cursor.execute("""
            INSERT INTO process_instances (
                instance_id, process_definition_id, status, current_step_id,
                started_by
            ) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (
            "ai_exec_instance_1",
            process_def_id,
            "active",
            "analysis",
            "system"
        ))
        instance_id = db_cursor.fetchone()[0]

        # Insert AI execution
        db_cursor.execute("""
            INSERT INTO step_executions (
                process_instance_id, step_id, executed_by, result,
                ai_agent_used, ai_confidence
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            instance_id,
            "analysis",
            "AI_System",
            "success",
            "analytics_specialist",
            0.95
        ))
        db_connection.commit()

        # Query
        db_cursor.execute("""
            SELECT ai_agent_used, ai_confidence
            FROM step_executions
            WHERE process_instance_id = %s AND ai_agent_used IS NOT NULL
        """, (instance_id,))

        result = db_cursor.fetchone()
        assert result[0] == "analytics_specialist"
        assert result[1] == 0.95


# =====================================================
# Test Document Templates Table
# =====================================================

class TestDocumentTemplatesTable:
    """Test document_templates table operations"""

    def test_insert_document_template(self, db_cursor, db_connection):
        """Test inserting a document template"""
        db_cursor.execute("""
            INSERT INTO document_templates (
                template_id, name, version, document_type, iso_clause,
                sections, required_variables, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (
            "bia_report_v1",
            "BIA Report Template",
            "1.0",
            "bia_report",
            "8.2.2",
            '[]',
            '["organization_name", "analysis_date"]',
            "active"
        ))

        template_id = db_cursor.fetchone()[0]
        assert template_id is not None

    def test_query_active_templates(self, db_cursor, db_connection):
        """Test querying active document templates"""
        # Insert templates
        db_cursor.execute("""
            INSERT INTO document_templates (
                template_id, name, version, document_type, status
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            "active_template_1",
            "Active Template",
            "1.0",
            "report",
            "active"
        ))

        db_cursor.execute("""
            INSERT INTO document_templates (
                template_id, name, version, document_type, status
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            "archived_template_1",
            "Archived Template",
            "1.0",
            "report",
            "archived"
        ))
        db_connection.commit()

        # Query active only
        db_cursor.execute("""
            SELECT COUNT(*)
            FROM document_templates
            WHERE status = 'active'
        """)

        count = db_cursor.fetchone()[0]
        assert count >= 1


# =====================================================
# Test Analytics Views
# =====================================================

class TestAnalyticsViews:
    """Test database analytics views"""

    def test_process_completion_stats_view(self, db_cursor, db_connection):
        """Test process_completion_stats view"""
        db_cursor.execute("""
            SELECT * FROM process_completion_stats LIMIT 1
        """)

        # View should exist and be queryable
        columns = [desc[0] for desc in db_cursor.description]
        assert "process_id" in columns
        assert "total_instances" in columns
        assert "completion_rate_percent" in columns

    def test_step_execution_stats_view(self, db_cursor, db_connection):
        """Test step_execution_stats view"""
        db_cursor.execute("""
            SELECT * FROM step_execution_stats LIMIT 1
        """)

        columns = [desc[0] for desc in db_cursor.description]
        assert "step_id" in columns
        assert "total_executions" in columns
        assert "success_rate_percent" in columns

    def test_document_generation_stats_view(self, db_cursor, db_connection):
        """Test document_generation_stats view"""
        db_cursor.execute("""
            SELECT * FROM document_generation_stats LIMIT 1
        """)

        columns = [desc[0] for desc in db_cursor.description]
        assert "template_id" in columns
        assert "total_generated" in columns


# =====================================================
# Test Seed Data
# =====================================================

class TestSeedData:
    """Test that seed data was loaded correctly"""

    def test_bcm_processes_seeded(self, db_cursor):
        """Test that BCM processes are seeded"""
        db_cursor.execute("""
            SELECT COUNT(*)
            FROM process_definitions
            WHERE process_id IN ('bcm_bia_v1', 'bcm_risk_assessment_v1', 'bcm_bc_plan_v1')
        """)

        count = db_cursor.fetchone()[0]
        assert count == 3

    def test_document_templates_seeded(self, db_cursor):
        """Test that document templates are seeded"""
        db_cursor.execute("""
            SELECT COUNT(*)
            FROM document_templates
            WHERE template_id IN ('bia_report_v1', 'risk_register_v1', 'bc_plan_v1')
        """)

        count = db_cursor.fetchone()[0]
        assert count == 3

    def test_bia_process_has_iso_clause(self, db_cursor):
        """Test that BIA process has ISO clause"""
        db_cursor.execute("""
            SELECT iso_clause
            FROM process_definitions
            WHERE process_id = 'bcm_bia_v1'
        """)

        result = db_cursor.fetchone()
        assert result is not None
        assert result[0] == "8.2.2"


# =====================================================
# Run Tests
# =====================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
