"""
Predictive Service - Database Repository

Handles all database operations for predictions:
- Save journey predictions
- Save certification predictions
- Track prediction accuracy
- Query historical predictions
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
import asyncpg
from supabase import create_client, Client
import os


class PredictiveRepository:
    """Repository for Predictive Service database operations"""

    def __init__(self, supabase_client: Client = None):
        if supabase_client:
            self.supabase = supabase_client
        else:
            # Initialize from environment
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            self.supabase = create_client(supabase_url, supabase_key)

    # =====================================================
    # JOURNEY PREDICTIONS
    # =====================================================

    async def save_journey_prediction(
        self,
        org_id: str,
        prediction_data: Dict[str, Any]
    ) -> str:
        """
        Save journey timeline prediction to database

        Args:
            org_id: Organization UUID
            prediction_data: Full prediction response from JourneyPredictor

        Returns:
            prediction_id (UUID)
        """
        try:
            data = {
                "org_id": org_id,
                "horizon_days": prediction_data.get('horizon_days', 90),
                "milestones": prediction_data.get('milestones', []),
                "timeline": prediction_data.get('timeline', []),
                "critical_path": prediction_data.get('critical_path', []),
                "estimated_completion_date": prediction_data.get('estimated_completion'),
                "confidence_overall": prediction_data.get('confidence_overall', 0.5),
                "organization_data": prediction_data.get('organization', {}),
                "similar_orgs_count": prediction_data.get('similar_orgs_count', 0)
            }

            result = self.supabase.table("journey_predictions").insert(data).execute()

            if result.data:
                prediction_id = result.data[0]["id"]
                return prediction_id
            else:
                raise Exception("Failed to save journey prediction")

        except Exception as e:
            raise Exception(f"Error saving journey prediction: {e}")

    async def get_latest_journey_prediction(self, org_id: str) -> Optional[Dict]:
        """Get most recent journey prediction for organization"""
        try:
            result = self.supabase.rpc(
                "get_latest_journey_prediction",
                {"p_org_id": org_id}
            ).execute()

            return result.data[0] if result.data else None

        except Exception as e:
            print(f"Error getting latest journey prediction: {e}")
            return None

    async def get_journey_predictions_history(
        self,
        org_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get historical journey predictions for organization"""
        try:
            result = self.supabase.table("journey_predictions") \
                .select("*") \
                .eq("org_id", org_id) \
                .order("prediction_date", desc=True) \
                .limit(limit) \
                .execute()

            return result.data

        except Exception as e:
            print(f"Error getting journey predictions history: {e}")
            return []

    # =====================================================
    # CERTIFICATION PREDICTIONS
    # =====================================================

    async def save_certification_prediction(
        self,
        org_id: str,
        prediction_data: Dict[str, Any]
    ) -> str:
        """Save certification timeline prediction"""
        try:
            data = {
                "org_id": org_id,
                "predicted_certification_date": prediction_data.get('predicted_certification_date'),
                "months_remaining": prediction_data.get('months_remaining'),
                "success_probability": prediction_data.get('success_probability'),
                "confidence": prediction_data.get('confidence'),
                "based_on_orgs_count": prediction_data.get('based_on_orgs_count', 0),
                "key_factors": prediction_data.get('key_factors', [])
            }

            result = self.supabase.table("certification_predictions").insert(data).execute()

            if result.data:
                return result.data[0]["id"]
            else:
                raise Exception("Failed to save certification prediction")

        except Exception as e:
            raise Exception(f"Error saving certification prediction: {e}")

    async def update_certification_actual(
        self,
        prediction_id: str,
        actual_date: datetime,
        actual_success: bool
    ):
        """Update certification prediction with actual outcome"""
        try:
            # Get prediction
            prediction = self.supabase.table("certification_predictions") \
                .select("*") \
                .eq("id", prediction_id) \
                .execute()

            if not prediction.data:
                return

            pred_date = datetime.fromisoformat(prediction.data[0]["predicted_certification_date"])
            error_days = (actual_date - pred_date).days

            # Update with actual
            self.supabase.table("certification_predictions") \
                .update({
                    "actual_certification_date": actual_date.isoformat(),
                    "actual_success": actual_success,
                    "accuracy_error_days": error_days
                }) \
                .eq("id", prediction_id) \
                .execute()

            # Also record in accuracy tracking
            await self.record_prediction_accuracy(
                prediction_id=prediction_id,
                prediction_type="certification",
                predicted_date=pred_date,
                actual_date=actual_date,
                confidence=prediction.data[0].get("confidence", 0.5),
                org_id=prediction.data[0]["org_id"]
            )

        except Exception as e:
            print(f"Error updating certification actual: {e}")

    # =====================================================
    # PREDICTION ACCURACY TRACKING
    # =====================================================

    async def record_prediction_accuracy(
        self,
        prediction_id: str,
        prediction_type: str,
        predicted_date: datetime,
        actual_date: datetime,
        confidence: float,
        org_id: str,
        milestone: str = None,
        module: str = None
    ):
        """Record prediction accuracy for ML improvement"""
        try:
            error_days = (actual_date - predicted_date).days
            error_percentage = (abs(error_days) / ((actual_date - datetime.now()).days + 1)) * 100

            # Calculate confidence vs accuracy
            # If error is small and confidence was high, good calibration
            # If error is large but confidence was low, also good
            # Bad: high confidence + large error OR low confidence + small error
            calibration = 1.0 - (abs(confidence - (1.0 - min(abs(error_days) / 30, 1.0))))

            data = {
                "prediction_id": prediction_id,
                "prediction_type": prediction_type,
                "milestone": milestone,
                "predicted_date": predicted_date.isoformat(),
                "actual_date": actual_date.isoformat(),
                "error_days": error_days,
                "error_percentage": error_percentage,
                "predicted_confidence": confidence,
                "confidence_vs_accuracy": calibration,
                "org_id": org_id,
                "module": module
            }

            self.supabase.table("prediction_accuracy").insert(data).execute()

        except Exception as e:
            print(f"Error recording prediction accuracy: {e}")

    async def get_prediction_accuracy_stats(
        self,
        prediction_type: str = None,
        module: str = None,
        days: int = 90
    ) -> Dict[str, Any]:
        """Get prediction accuracy statistics"""
        try:
            result = self.supabase.rpc(
                "get_prediction_accuracy_stats",
                {
                    "p_prediction_type": prediction_type,
                    "p_module": module,
                    "p_days": days
                }
            ).execute()

            return result.data[0] if result.data else {}

        except Exception as e:
            print(f"Error getting accuracy stats: {e}")
            return {}

    # =====================================================
    # EXPERT DEMAND FORECASTS
    # =====================================================

    async def save_demand_forecast(
        self,
        forecast_data: Dict[str, Any]
    ) -> str:
        """Save expert demand forecast"""
        try:
            data = {
                "horizon_days": forecast_data.get('horizon_days', 30),
                "specialty": forecast_data.get('specialty'),
                "region": forecast_data.get('region'),
                "expected_projects": forecast_data.get('total_predicted_projects', 0),
                "peak_week": forecast_data.get('peak_week'),
                "confidence": forecast_data.get('confidence', 0.5),
                "by_industry": forecast_data.get('by_industry', {}),
                "by_region": forecast_data.get('by_region', {}),
                "by_specialty": forecast_data.get('by_specialty', {})
            }

            result = self.supabase.table("expert_demand_forecasts").insert(data).execute()

            if result.data:
                return result.data[0]["id"]
            else:
                raise Exception("Failed to save demand forecast")

        except Exception as e:
            raise Exception(f"Error saving demand forecast: {e}")

    async def get_latest_demand_forecast(
        self,
        specialty: str = None,
        region: str = None
    ) -> Optional[Dict]:
        """Get most recent demand forecast"""
        try:
            query = self.supabase.table("expert_demand_forecasts").select("*")

            if specialty:
                query = query.eq("specialty", specialty)
            if region:
                query = query.eq("region", region)

            result = query.order("forecast_date", desc=True).limit(1).execute()

            return result.data[0] if result.data else None

        except Exception as e:
            print(f"Error getting demand forecast: {e}")
            return None

    # =====================================================
    # PROACTIVE RECOMMENDATIONS
    # =====================================================

    async def save_proactive_recommendation(
        self,
        org_id: str,
        user_id: str,
        recommendation_data: Dict[str, Any]
    ) -> str:
        """Save proactive recommendation"""
        try:
            data = {
                "org_id": org_id,
                "user_id": user_id,
                "type": recommendation_data.get('type'),
                "priority": recommendation_data.get('priority'),
                "milestone": recommendation_data.get('milestone'),
                "days_until": recommendation_data.get('days_until'),
                "confidence": recommendation_data.get('confidence'),
                "title": recommendation_data.get('title'),
                "message": recommendation_data.get('message'),
                "actions": recommendation_data.get('actions', []),
                "resources": recommendation_data.get('resources', [])
            }

            result = self.supabase.table("proactive_recommendations").insert(data).execute()

            if result.data:
                return result.data[0]["id"]
            else:
                raise Exception("Failed to save recommendation")

        except Exception as e:
            raise Exception(f"Error saving recommendation: {e}")

    async def mark_recommendation_sent(
        self,
        recommendation_id: str,
        sent_via: List[str],
        notification_ids: List[str] = None
    ):
        """Mark recommendation as sent"""
        try:
            self.supabase.table("proactive_recommendations") \
                .update({
                    "sent_at": datetime.now().isoformat(),
                    "sent_via": sent_via,
                    "notification_ids": notification_ids or []
                }) \
                .eq("id", recommendation_id) \
                .execute()

        except Exception as e:
            print(f"Error marking recommendation sent: {e}")

    async def get_active_recommendations(
        self,
        org_id: str,
        user_id: str = None
    ) -> List[Dict]:
        """Get active recommendations for organization/user"""
        try:
            result = self.supabase.rpc(
                "get_active_recommendations",
                {
                    "p_org_id": org_id,
                    "p_user_id": user_id
                }
            ).execute()

            return result.data

        except Exception as e:
            print(f"Error getting active recommendations: {e}")
            return []

    async def mark_recommendation_viewed(self, recommendation_id: str):
        """Mark recommendation as viewed"""
        try:
            self.supabase.table("proactive_recommendations") \
                .update({"viewed_at": datetime.now().isoformat()}) \
                .eq("id", recommendation_id) \
                .execute()

        except Exception as e:
            print(f"Error marking recommendation viewed: {e}")

    async def mark_recommendation_dismissed(self, recommendation_id: str):
        """Mark recommendation as dismissed"""
        try:
            self.supabase.table("proactive_recommendations") \
                .update({"dismissed_at": datetime.now().isoformat()}) \
                .eq("id", recommendation_id) \
                .execute()

        except Exception as e:
            print(f"Error marking recommendation dismissed: {e}")
