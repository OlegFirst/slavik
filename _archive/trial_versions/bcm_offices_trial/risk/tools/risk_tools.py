"""
Risk Tools - Database Operations for Risk Office

Handles all DB operations for risk management:
- CRUD for risks
- Likelihood scores
- Impact assessments
- FAIR metrics
- Treatment plans
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class RiskTools:
    """
    Risk Tools - DB operations for risk.* tables

    Tables:
    - risk.assessments
    - risk.identified_risks
    - risk.likelihood_scores
    - risk.impact_assessments
    - risk.fair_metrics
    - risk.treatments
    """

    def __init__(self, db_session):
        """
        Initialize Risk Tools

        Args:
            db_session: Supabase/PostgreSQL session
        """
        self.db = db_session

    # ========================================================================
    # PROCESS OPERATIONS
    # ========================================================================

    async def get_process(self, process_id: str) -> Optional[Dict[str, Any]]:
        """
        Get business process data

        Args:
            process_id: Process ID

        Returns:
            Process data or None
        """
        if not self.db:
            return None

        try:
            result = await self.db.table('bia.processes').select('*').eq('id', process_id).execute()

            if result.data:
                return result.data[0]

            return None

        except Exception as e:
            print(f"Error getting process: {e}")
            return None

    # ========================================================================
    # RISK OPERATIONS
    # ========================================================================

    async def save_risk(self, risk_data: Dict[str, Any]) -> Optional[str]:
        """
        Save identified risk

        Args:
            risk_data: Risk data
                - process_id
                - description
                - threat
                - vulnerability
                - category

        Returns:
            Risk ID if successful
        """
        if not self.db:
            return None

        try:
            risk_record = {
                'process_id': risk_data.get('process_id'),
                'description': risk_data.get('description'),
                'threat': risk_data.get('threat'),
                'vulnerability': risk_data.get('vulnerability'),
                'category': risk_data.get('category', 'operational'),
                'identified_at': datetime.utcnow().isoformat(),
                'status': 'identified'
            }

            result = await self.db.table('risk.identified_risks').insert(risk_record).execute()

            if result.data:
                return result.data[0]['id']

            return None

        except Exception as e:
            print(f"Error saving risk: {e}")
            return None

    async def get_risks(self, risk_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get risks by IDs

        Args:
            risk_ids: List of risk IDs

        Returns:
            List of risk records
        """
        if not self.db or not risk_ids:
            return []

        try:
            result = await self.db.table('risk.identified_risks').select('*').in_('id', risk_ids).execute()

            return result.data if result else []

        except Exception as e:
            print(f"Error getting risks: {e}")
            return []

    async def get_risks_with_likelihood(self, risk_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get risks with likelihood scores

        Args:
            risk_ids: List of risk IDs

        Returns:
            List of risks with likelihood data
        """
        if not self.db or not risk_ids:
            return []

        try:
            # Get risks
            risks_result = await self.db.table('risk.identified_risks').select('*').in_('id', risk_ids).execute()
            risks = risks_result.data if risks_result else []

            # Get likelihood scores
            likelihood_result = await self.db.table('risk.likelihood_scores').select('*').in_('risk_id', risk_ids).execute()
            likelihood_scores = {l['risk_id']: l for l in (likelihood_result.data if likelihood_result else [])}

            # Merge
            for risk in risks:
                risk['likelihood_score'] = likelihood_scores.get(risk['id'])

            return risks

        except Exception as e:
            print(f"Error getting risks with likelihood: {e}")
            return []

    async def get_risks_full_analysis(self, risk_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get risks with all analysis data (likelihood + impact + FAIR)

        Args:
            risk_ids: List of risk IDs

        Returns:
            List of risks with full analysis
        """
        if not self.db or not risk_ids:
            return []

        try:
            # Get risks
            risks_result = await self.db.table('risk.identified_risks').select('*').in_('id', risk_ids).execute()
            risks = risks_result.data if risks_result else []

            # Get likelihood
            likelihood_result = await self.db.table('risk.likelihood_scores').select('*').in_('risk_id', risk_ids).execute()
            likelihood_scores = {l['risk_id']: l for l in (likelihood_result.data if likelihood_result else [])}

            # Get impact
            impact_result = await self.db.table('risk.impact_assessments').select('*').in_('risk_id', risk_ids).execute()
            impact_assessments = {i['risk_id']: i for i in (impact_result.data if impact_result else [])}

            # Get FAIR metrics
            fair_result = await self.db.table('risk.fair_metrics').select('*').in_('risk_id', risk_ids).execute()
            fair_metrics = {f['risk_id']: f for f in (fair_result.data if fair_result else [])}

            # Merge all
            for risk in risks:
                risk['likelihood'] = likelihood_scores.get(risk['id'])
                risk['impact'] = impact_assessments.get(risk['id'])
                risk['fair'] = fair_metrics.get(risk['id'])

            return risks

        except Exception as e:
            print(f"Error getting full risk analysis: {e}")
            return []

    # ========================================================================
    # LIKELIHOOD OPERATIONS
    # ========================================================================

    async def save_likelihood_score(self, score_data: Dict[str, Any]) -> bool:
        """
        Save likelihood score

        Args:
            score_data: Likelihood data
                - risk_id
                - score (1-5)
                - frequency_estimate
                - reasoning
                - confidence

        Returns:
            True if successful
        """
        if not self.db:
            return False

        try:
            score_record = {
                'risk_id': score_data.get('risk_id'),
                'score': score_data.get('score', 3),
                'frequency_estimate': score_data.get('frequency_estimate'),
                'reasoning': score_data.get('reasoning'),
                'confidence': score_data.get('confidence', 0.7),
                'assessed_at': datetime.utcnow().isoformat()
            }

            # Upsert (insert or update)
            result = await self.db.table('risk.likelihood_scores').upsert(
                score_record,
                on_conflict='risk_id'
            ).execute()

            return bool(result.data)

        except Exception as e:
            print(f"Error saving likelihood score: {e}")
            return False

    # ========================================================================
    # IMPACT OPERATIONS
    # ========================================================================

    async def save_impact_scores(self, impact_data: Dict[str, Any]) -> bool:
        """
        Save impact scores

        Args:
            impact_data: Impact data
                - risk_id
                - financial (0-100)
                - operational (0-100)
                - reputational (0-100)
                - regulatory (0-100)
                - reasoning

        Returns:
            True if successful
        """
        if not self.db:
            return False

        try:
            impact_record = {
                'risk_id': impact_data.get('risk_id'),
                'financial': impact_data.get('financial', 0),
                'operational': impact_data.get('operational', 0),
                'reputational': impact_data.get('reputational', 0),
                'regulatory': impact_data.get('regulatory', 0),
                'reasoning': impact_data.get('reasoning'),
                'assessed_at': datetime.utcnow().isoformat()
            }

            # Upsert
            result = await self.db.table('risk.impact_assessments').upsert(
                impact_record,
                on_conflict='risk_id'
            ).execute()

            return bool(result.data)

        except Exception as e:
            print(f"Error saving impact scores: {e}")
            return False

    # ========================================================================
    # FAIR OPERATIONS
    # ========================================================================

    async def save_fair_metrics(self, fair_data: Dict[str, Any]) -> bool:
        """
        Save FAIR metrics

        Args:
            fair_data: FAIR data
                - risk_id
                - tef (Threat Event Frequency)
                - lm (Loss Magnitude)
                - ale (Annual Loss Expectancy = TEF × LM)
                - reasoning

        Returns:
            True if successful
        """
        if not self.db:
            return False

        try:
            fair_record = {
                'risk_id': fair_data.get('risk_id'),
                'tef': fair_data.get('tef', 0),
                'lm': fair_data.get('lm', 0),
                'ale': fair_data.get('ale', 0),
                'reasoning': fair_data.get('reasoning'),
                'calculated_at': datetime.utcnow().isoformat()
            }

            # Upsert
            result = await self.db.table('risk.fair_metrics').upsert(
                fair_record,
                on_conflict='risk_id'
            ).execute()

            return bool(result.data)

        except Exception as e:
            print(f"Error saving FAIR metrics: {e}")
            return False

    # ========================================================================
    # TREATMENT OPERATIONS
    # ========================================================================

    async def save_treatment_plan(self, treatment_data: Dict[str, Any]) -> bool:
        """
        Save treatment plan

        Args:
            treatment_data: Treatment data
                - risk_id
                - treatment_type (reduce, accept, transfer, avoid)
                - actions (list)
                - priority
                - estimated_cost
                - expected_reduction
                - reasoning

        Returns:
            True if successful
        """
        if not self.db:
            return False

        try:
            treatment_record = {
                'risk_id': treatment_data.get('risk_id'),
                'treatment_type': treatment_data.get('treatment_type', 'reduce'),
                'actions': treatment_data.get('actions', []),
                'priority': treatment_data.get('priority', 'medium'),
                'estimated_cost': treatment_data.get('estimated_cost'),
                'expected_reduction': treatment_data.get('expected_reduction'),
                'reasoning': treatment_data.get('reasoning'),
                'status': 'planned',
                'planned_at': datetime.utcnow().isoformat()
            }

            # Upsert
            result = await self.db.table('risk.treatments').upsert(
                treatment_record,
                on_conflict='risk_id'
            ).execute()

            return bool(result.data)

        except Exception as e:
            print(f"Error saving treatment plan: {e}")
            return False

    # ========================================================================
    # SUMMARY OPERATIONS
    # ========================================================================

    async def get_risk_summary(self, risk_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete risk summary (all data)

        Args:
            risk_id: Risk ID

        Returns:
            Complete risk data or None
        """
        if not self.db:
            return None

        try:
            # Get risk
            risk_result = await self.db.table('risk.identified_risks').select('*').eq('id', risk_id).execute()
            if not risk_result.data:
                return None

            risk = risk_result.data[0]

            # Get likelihood
            likelihood_result = await self.db.table('risk.likelihood_scores').select('*').eq('risk_id', risk_id).execute()
            risk['likelihood'] = likelihood_result.data[0] if likelihood_result.data else None

            # Get impact
            impact_result = await self.db.table('risk.impact_assessments').select('*').eq('risk_id', risk_id).execute()
            risk['impact'] = impact_result.data[0] if impact_result.data else None

            # Get FAIR
            fair_result = await self.db.table('risk.fair_metrics').select('*').eq('risk_id', risk_id).execute()
            risk['fair'] = fair_result.data[0] if fair_result.data else None

            # Get treatment
            treatment_result = await self.db.table('risk.treatments').select('*').eq('risk_id', risk_id).execute()
            risk['treatment'] = treatment_result.data[0] if treatment_result.data else None

            return risk

        except Exception as e:
            print(f"Error getting risk summary: {e}")
            return None

    async def get_assessment_summary(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get assessment summary with all risks

        Args:
            assessment_id: Assessment ID

        Returns:
            Assessment summary or None
        """
        if not self.db:
            return None

        try:
            # Get assessment
            assessment_result = await self.db.table('risk.assessments').select('*').eq('id', assessment_id).execute()
            if not assessment_result.data:
                return None

            assessment = assessment_result.data[0]

            # Get all risks for assessment
            risks_result = await self.db.table('risk.identified_risks').select('*').eq('assessment_id', assessment_id).execute()
            risks = risks_result.data if risks_result else []

            # Get full data for each risk
            risk_ids = [r['id'] for r in risks]
            full_risks = await self.get_risks_full_analysis(risk_ids)

            assessment['risks'] = full_risks
            assessment['risk_count'] = len(full_risks)

            # Calculate total ALE
            total_ale = sum(
                r.get('fair', {}).get('ale', 0)
                for r in full_risks
                if r.get('fair')
            )
            assessment['total_ale'] = total_ale

            return assessment

        except Exception as e:
            print(f"Error getting assessment summary: {e}")
            return None
