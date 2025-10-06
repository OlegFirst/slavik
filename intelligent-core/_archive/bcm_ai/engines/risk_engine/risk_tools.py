"""
Risk Tools
Database operations for Risk management
"""
from typing import Dict, List, Optional, Any
from datetime import datetime


class RiskTools:
    """
    Tools for Risk Engine

    Provides DB operations for risk analysis
    """

    def __init__(self, db_session):
        """
        Initialize tools

        Args:
            db_session: Database session (Supabase/PostgreSQL)
        """
        self.db = db_session

    async def get_process_details(self, process_id: str) -> Dict[str, Any]:
        """
        Get process details from BIA

        Query: SELECT * FROM bia.processes WHERE id = process_id
        """
        try:
            result = await self.db.table('bia.processes').select('*').eq(
                'id', process_id
            ).execute()

            if result.data:
                return result.data[0]
            return {}

        except Exception as e:
            print(f"Error getting process details: {e}")
            return {}

    async def get_process_dependencies(self, process_id: str) -> List[Dict[str, Any]]:
        """
        Get process dependencies

        Query: SELECT * FROM bia.dependencies WHERE process_id = process_id
        """
        try:
            result = await self.db.table('bia.dependencies').select('*').eq(
                'process_id', process_id
            ).execute()

            return result.data if result else []

        except Exception as e:
            print(f"Error getting dependencies: {e}")
            return []

    async def get_existing_risks(self, process_id: str) -> List[Dict[str, Any]]:
        """
        Get existing risks for process

        Query: SELECT * FROM risk.risk_register WHERE process_id = process_id
        """
        try:
            result = await self.db.table('risk.risk_register').select('*').eq(
                'process_id', process_id
            ).execute()

            return result.data if result else []

        except Exception as e:
            print(f"Error getting existing risks: {e}")
            return []

    async def save_risk_analysis(self, analysis: Dict[str, Any]) -> str:
        """
        Save risk analysis

        INSERT INTO risk.analyses (process_id, severity, vulnerabilities, ...)
        """
        try:
            record = {
                'process_id': analysis.get('process_id'),
                'severity': analysis.get('severity'),
                'vulnerabilities': analysis.get('vulnerabilities', []),
                'threats': analysis.get('threats', []),
                'likelihood': analysis.get('likelihood'),
                'impact': analysis.get('impact'),
                'risk_score': analysis.get('risk_score'),
                'fair_analysis': analysis.get('fair_analysis', {}),
                'recommendations': analysis.get('recommendations', []),
                'analyzed_by': 'risk_engine',
                'analyzed_at': datetime.utcnow().isoformat(),
                'metadata': analysis.get('metadata', {})
            }

            result = await self.db.table('risk.analyses').insert(
                record
            ).execute()

            if result.data:
                return result.data[0]['id']

            return None

        except Exception as e:
            print(f"Error saving risk analysis: {e}")
            return None

    async def create_risk_treatment(self, treatment: Dict[str, Any]) -> str:
        """
        Create risk treatment plan

        INSERT INTO risk.treatments (risk_id, treatment_type, actions, ...)
        """
        try:
            record = {
                'risk_id': treatment.get('risk_id'),
                'process_id': treatment.get('process_id'),
                'treatment_type': treatment.get('treatment_type'),  # reduce, accept, transfer, avoid
                'treatment_actions': treatment.get('actions', []),
                'priority': treatment.get('priority'),
                'responsible': treatment.get('responsible'),
                'deadline': treatment.get('deadline'),
                'status': 'planned',
                'created_at': datetime.utcnow().isoformat(),
                'metadata': treatment.get('metadata', {})
            }

            result = await self.db.table('risk.treatments').insert(
                record
            ).execute()

            if result.data:
                return result.data[0]['id']

            return None

        except Exception as e:
            print(f"Error creating treatment: {e}")
            return None

    async def get_risk_assessments(
        self,
        process_id: Optional[str] = None,
        severity_min: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get risk assessments with filters

        Query: SELECT * FROM risk.assessments WHERE ...
        """
        try:
            query = self.db.table('risk.assessments').select('*')

            if process_id:
                query = query.eq('process_id', process_id)
            if severity_min:
                query = query.gte('severity', severity_min)

            result = await query.execute()
            return result.data if result else []

        except Exception as e:
            print(f"Error getting assessments: {e}")
            return []

    async def update_risk_status(
        self,
        risk_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update risk status

        UPDATE risk.risk_register SET status = ?, updated_at = NOW()
        """
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow().isoformat()
            }

            if notes:
                update_data['notes'] = notes

            result = await self.db.table('risk.risk_register').update(
                update_data
            ).eq('id', risk_id).execute()

            return bool(result.data)

        except Exception as e:
            print(f"Error updating risk status: {e}")
            return False
