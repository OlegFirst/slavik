"""
Documents Specialist AI

AI Digital Colleague for Document Management & Control.

Specializes in:
- Document lifecycle management
- Version control and approval workflows
- Document templates and standards
- Access control and permissions
- Document classification and metadata
- Archive and retention policies
- Living Documentation management (integration with living-docs service)
"""

import logging
from typing import Dict, Any
import httpx

from expertise_center.shared.base import BaseTacticalAssistant

logger = logging.getLogger(__name__)


class DocumentsSpecialistAI(BaseTacticalAssistant):
    """
    Documents Specialist AI - Your Document Management Expert

    Specializes in:
    - Document lifecycle management (draft → review → approve → publish → archive)
    - Version control and change management
    - Document templates and standardization
    - ISO 22301 documentation requirements
    - Access control and permissions
    - Document classification and metadata
    - Archive and retention policies
    - Document search and retrieval
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize DocumentsSpecialistAI."""
        super().__init__(
            assistant_id="documents_specialist",
            name="Documents Specialist AI",
            specialty="Document Management & Control",
            domain="bcm"
        )

        # AI Foundation integrations inherited from BaseTacticalAssistant:
        # self.rag, self.llm, self.context_builder are available

        self.config = config or {}
        self.documents_managed = 0
        self.templates_created = 0

        # Living Docs Service integration
        self.living_docs_url = self.config.get("living_docs_url", "http://localhost:8034")
        self.living_docs_enabled = self.config.get("living_docs_enabled", True)

        logger.info("Documents Specialist AI initialized and ready!")

    async def assist(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute document management task using ai-foundation"""
        # Implementation using self.llm, self.rag, self.context_builder
        pass

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build Documents Specialist AI's system prompt."""
        base_prompt = f"""You are **Documents Specialist AI**, an expert in document management and control systems.

**Your Expertise:**
- **Document Lifecycle**: Draft, review, approval, publication, archival
- **Version Control**: Change tracking, version history, rollback
- **ISO 22301 Documentation**: BCMS documentation requirements (clause 7.5)
- **Templates**: Standardized document templates for consistency
- **Metadata**: Classification, tags, ownership, retention periods
- **Access Control**: Role-based permissions, confidentiality levels
- **Workflow Automation**: Approval workflows, notifications, reminders
- **Document Types**: Policies, procedures, plans, forms, records, reports

**Your Personality:**
- Organized and detail-oriented
- Focused on compliance and auditability
- Pragmatic about documentation needs
- Advocate for usability and findability
- Skilled at template design

**Current Context:** {context.value}

**Guidelines for Responses:**
1. **Document Structure**: Clear hierarchy, consistent formatting
2. **Version Control**: Proper versioning and change logs
3. **Approval Workflows**: Appropriate review and approval chains
4. **Retention Policies**: Align with legal and regulatory requirements
5. **Accessibility**: Balance security with ease of access
6. **Templates**: Standardize while allowing flexibility

**Response Format:**
- Document recommendations with rationale
- Template structure and required fields
- Approval workflow suggestions
- Metadata and classification scheme
- Retention and archival guidance

**ISO 22301 Documentation Requirements:**
- **Mandatory Documented Information**:
  - Scope of BCMS (clause 4.3)
  - BCM Policy (clause 5.2)
  - Roles and responsibilities (clause 5.3)
  - Risk assessment and treatment (clause 8.2.1)
  - Business Impact Analysis (clause 8.2.2)
  - BC strategies and solutions (clause 8.3)
  - BC plans and procedures (clause 8.4)
  - Exercise and testing records (clause 8.5)
  - Performance monitoring (clause 9.1)
  - Internal audit results (clause 9.2)
  - Management review (clause 9.3)
  - Nonconformity and corrective action (clause 10.1)

**Document Lifecycle States:**
- **Draft**: Work in progress, not approved
- **Under Review**: Submitted for review and comments
- **Approved**: Approved but not yet published
- **Published**: Active and in use
- **Superseded**: Replaced by newer version
- **Archived**: Retained for records but no longer active
- **Obsolete**: Eligible for destruction per retention policy

**Best Practices:**
- Use clear, descriptive document titles
- Include version number, date, and author
- Maintain change log for traceability
- Apply consistent metadata and tags
- Define clear retention periods
- Regular review and update cycles
- Searchable and accessible repository
"""

        return base_prompt

    async def assist(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide document management assistance.

        Args:
            query: User's document-related question
            context: Context including document type, lifecycle state, etc.

        Returns:
            Assistance response with document recommendations
        """
        assistant_context = AssistantContext(
            module="documents",
            phase="document_management",
            current_step=context.get("step", "general"),
            value=context.get("description", query),
            metadata=context
        )

        response = await self._generate_response(
            query=query,
            context=assistant_context
        )

        self.documents_managed += 1

        return {
            "assistant": self.name,
            "specialty": self.specialty,
            "response": response,
            "context": assistant_context.to_dict(),
            "stats": {
                "documents_managed": self.documents_managed,
                "templates_created": self.templates_created
            }
        }

    async def search_living_docs(self, query: str, user_id: str = None) -> Dict[str, Any]:
        """
        Search living documentation.

        Integrates with living-docs service for self-evolving documentation.

        Args:
            query: Search query
            user_id: Optional user ID for personalized results

        Returns:
            Search results from living_docs
        """
        if not self.living_docs_enabled:
            return {
                "error": "Living Docs service not enabled",
                "results": []
            }

        try:
            async with httpx.AsyncClient() as client:
                params = {"query": query}
                if user_id:
                    params["user_id"] = user_id

                response = await client.get(
                    f"{self.living_docs_url}/api/v1/docs/search",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Living Docs search failed: {e}")
            return {
                "error": str(e),
                "results": []
            }

    async def get_living_doc(self, page_id: str, user_id: str = None, personalize: bool = True) -> Dict[str, Any]:
        """
        Get living documentation page (personalized if requested).

        Args:
            page_id: Documentation page ID
            user_id: User ID for personalization
            personalize: Enable personalization

        Returns:
            Documentation content
        """
        if not self.living_docs_enabled:
            return {
                "error": "Living Docs service not enabled"
            }

        try:
            async with httpx.AsyncClient() as client:
                params = {}
                if user_id:
                    params["user_id"] = user_id
                if personalize:
                    params["personalize"] = "true"

                response = await client.get(
                    f"{self.living_docs_url}/api/v1/docs/{page_id}",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Living Docs fetch failed: {e}")
            return {
                "error": str(e)
            }

    async def generate_example(self, topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI example from living_docs.

        Args:
            topic: Topic for example (e.g., "bia_process_identification")
            context: Context (industry, org_type, etc.)

        Returns:
            Generated example
        """
        if not self.living_docs_enabled:
            return {
                "error": "Living Docs service not enabled"
            }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.living_docs_url}/api/v1/docs/examples/generate",
                    json={
                        "topic": topic,
                        "context": context,
                        "format_type": "detailed"
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Living Docs example generation failed: {e}")
            return {
                "error": str(e)
            }
