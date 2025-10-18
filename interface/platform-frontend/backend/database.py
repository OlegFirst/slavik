"""
Database Client using Supabase
"""

from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from config import get_settings


class DatabaseClient:
    """Supabase database client"""

    def __init__(self):
        settings = get_settings()
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )

    # ============================================
    # USER OPERATIONS
    # ============================================

    async def create_user_profile(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user profile"""
        profile_data = {
            "id": user_id,
            **data
        }
        result = self.client.table("user_profiles").insert(profile_data).execute()
        return result.data[0] if result.data else None

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by ID"""
        result = self.client.table("user_profiles").select("*").eq("id", user_id).single().execute()
        return result.data if result.data else None

    async def update_user_profile(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        result = self.client.table("user_profiles").update(data).eq("id", user_id).execute()
        return result.data[0] if result.data else None

    # ============================================
    # ORGANIZATION OPERATIONS
    # ============================================

    async def create_organization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create organization"""
        result = self.client.table("organizations").insert(data).execute()
        return result.data[0] if result.data else None

    async def get_organization(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get organization by ID"""
        result = self.client.table("organizations").select("*").eq("id", org_id).single().execute()
        return result.data if result.data else None

    async def get_organization_by_owner(self, owner_id: str) -> Optional[Dict[str, Any]]:
        """Get organization by owner ID"""
        result = self.client.table("organizations").select("*").eq("owner_id", owner_id).execute()
        return result.data[0] if result.data else None

    async def update_organization(self, org_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update organization"""
        result = self.client.table("organizations").update(data).eq("id", org_id).execute()
        return result.data[0] if result.data else None

    async def delete_organization(self, org_id: str) -> bool:
        """Delete organization"""
        result = self.client.table("organizations").delete().eq("id", org_id).execute()
        return len(result.data) > 0

    # ============================================
    # DEPARTMENT OPERATIONS
    # ============================================

    async def create_department(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create department"""
        result = self.client.table("organization_departments").insert(data).execute()
        return result.data[0] if result.data else None

    async def list_departments(self, org_id: str) -> List[Dict[str, Any]]:
        """List departments for organization"""
        result = self.client.table("organization_departments").select("*").eq("organization_id", org_id).execute()
        return result.data if result.data else []

    async def get_department(self, dept_id: str) -> Optional[Dict[str, Any]]:
        """Get department by ID"""
        result = self.client.table("organization_departments").select("*").eq("id", dept_id).single().execute()
        return result.data if result.data else None

    # ============================================
    # PROCESS OPERATIONS
    # ============================================

    async def create_process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create process"""
        result = self.client.table("organization_processes").insert(data).execute()
        return result.data[0] if result.data else None

    async def list_processes(self, org_id: str) -> List[Dict[str, Any]]:
        """List processes for organization"""
        result = self.client.table("organization_processes").select("*").eq("organization_id", org_id).execute()
        return result.data if result.data else []

    async def get_process(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get process by ID"""
        result = self.client.table("organization_processes").select("*").eq("id", process_id).single().execute()
        return result.data if result.data else None

    # ============================================
    # BIA OPERATIONS
    # ============================================

    async def create_bia_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create BIA analysis"""
        result = self.client.table("bia_analyses").insert(data).execute()
        return result.data[0] if result.data else None

    async def list_bia_analyses(self, org_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List BIA analyses for organization"""
        query = self.client.table("bia_analyses").select("*").eq("organization_id", org_id)
        if status:
            query = query.eq("status", status)
        result = query.execute()
        return result.data if result.data else []

    async def get_bia_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get BIA analysis by ID"""
        result = self.client.table("bia_analyses").select("*").eq("id", analysis_id).single().execute()
        return result.data if result.data else None

    async def update_bia_analysis(self, analysis_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update BIA analysis"""
        result = self.client.table("bia_analyses").update(data).eq("id", analysis_id).execute()
        return result.data[0] if result.data else None

    async def delete_bia_analysis(self, analysis_id: str) -> bool:
        """Delete BIA analysis"""
        result = self.client.table("bia_analyses").delete().eq("id", analysis_id).execute()
        return len(result.data) > 0

    # ============================================
    # BIA PROCESS OPERATIONS
    # ============================================

    async def create_bia_process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create BIA process"""
        result = self.client.table("bia_processes").insert(data).execute()
        return result.data[0] if result.data else None

    async def list_bia_processes(
        self,
        analysis_id: str,
        criticality: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List BIA processes"""
        query = self.client.table("bia_processes").select("*").eq("analysis_id", analysis_id)
        if criticality:
            query = query.eq("criticality", criticality)
        result = query.execute()
        return result.data if result.data else []

    async def get_bia_process(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get BIA process by ID"""
        result = self.client.table("bia_processes").select("*").eq("id", process_id).single().execute()
        return result.data if result.data else None

    async def update_bia_process(self, process_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update BIA process"""
        result = self.client.table("bia_processes").update(data).eq("id", process_id).execute()
        return result.data[0] if result.data else None

    # ============================================
    # BIA DEPENDENCY OPERATIONS
    # ============================================

    async def create_bia_dependency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create BIA dependency"""
        result = self.client.table("bia_dependencies").insert(data).execute()
        return result.data[0] if result.data else None

    async def list_bia_dependencies(self, analysis_id: str) -> List[Dict[str, Any]]:
        """List BIA dependencies"""
        result = self.client.table("bia_dependencies").select("*").eq("analysis_id", analysis_id).execute()
        return result.data if result.data else []

    # ============================================
    # BIA QUESTIONNAIRE OPERATIONS
    # ============================================

    async def create_bia_question(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create BIA question"""
        result = self.client.table("bia_questions").insert(data).execute()
        return result.data[0] if result.data else None

    async def create_bia_questions_bulk(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple BIA questions"""
        result = self.client.table("bia_questions").insert(questions).execute()
        return result.data if result.data else []

    async def list_bia_questions(self, analysis_id: str) -> List[Dict[str, Any]]:
        """List BIA questions"""
        result = self.client.table("bia_questions").select("*").eq("analysis_id", analysis_id).order("sequence_number").execute()
        return result.data if result.data else []

    async def create_bia_answer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create BIA answer"""
        result = self.client.table("bia_answers").insert(data).execute()
        return result.data[0] if result.data else None

    async def create_bia_answers_bulk(self, answers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple BIA answers"""
        result = self.client.table("bia_answers").insert(answers).execute()
        return result.data if result.data else []

    # ============================================
    # BIA FINDING OPERATIONS
    # ============================================

    async def create_bia_finding(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create BIA finding"""
        result = self.client.table("bia_findings").insert(data).execute()
        return result.data[0] if result.data else None

    async def list_bia_findings(
        self,
        analysis_id: str,
        finding_type: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List BIA findings"""
        query = self.client.table("bia_findings").select("*").eq("analysis_id", analysis_id)
        if finding_type:
            query = query.eq("finding_type", finding_type)
        if severity:
            query = query.eq("severity", severity)
        result = query.execute()
        return result.data if result.data else []

    async def update_bia_finding(self, finding_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update BIA finding"""
        result = self.client.table("bia_findings").update(data).eq("id", finding_id).execute()
        return result.data[0] if result.data else None

    # ============================================
    # AI PROMPT OPERATIONS
    # ============================================

    async def get_ai_prompt(self, prompt_name: str) -> Optional[Dict[str, Any]]:
        """Get AI prompt by name"""
        result = self.client.table("ai_prompts").select("*").eq("name", prompt_name).eq("is_active", True).single().execute()
        return result.data if result.data else None

    async def log_ai_usage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Log AI usage"""
        result = self.client.table("ai_logs").insert(data).execute()
        return result.data[0] if result.data else None

    # ============================================
    # AUDIT LOG
    # ============================================

    async def create_audit_log(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create audit log entry"""
        result = self.client.table("audit_log").insert(data).execute()
        return result.data[0] if result.data else None
