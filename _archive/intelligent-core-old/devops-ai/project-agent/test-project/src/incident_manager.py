"""Incident Management Module"""
import pickle
from datetime import datetime

class IncidentManager:
    """Manages incidents and crisis events"""

    def __init__(self):
        self.incidents = []
        self.load_incidents()

    def load_incidents(self):
        """Load incidents from storage"""
        try:
            # Security issue: using pickle
            with open('incidents.pkl', 'rb') as f:
                self.incidents = pickle.load(f)
        except FileNotFoundError:
            self.incidents = []

    def save_incidents(self):
        """Save incidents to storage"""
        with open('incidents.pkl', 'wb') as f:
            pickle.dump(self.incidents, f)

    def list_incidents(self):
        """List all incidents"""
        return self.incidents

    def create_incident(self, data):
        """Create new incident"""
        incident = {
            'id': len(self.incidents) + 1,
            'title': data.get('title'),
            'severity': data.get('severity'),
            'status': 'open',
            'created_at': datetime.now().isoformat()
        }
        self.incidents.append(incident)
        self.save_incidents()
        return incident

    def has_active_incidents(self):
        """Check if there are active incidents"""
        return any(i['status'] == 'open' for i in self.incidents)

    def get_critical_count(self):
        """Get count of critical incidents"""
        return sum(1 for i in self.incidents if i.get('severity') == 'critical')
