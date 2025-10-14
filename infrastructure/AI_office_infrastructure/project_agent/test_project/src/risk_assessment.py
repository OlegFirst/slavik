"""Risk Assessment Module - FAIR methodology"""

class RiskAssessor:
    """Risk assessment using FAIR framework"""

    def __init__(self):
        # TODO: Load from config
        self.password = "admin123"  # Security issue
        self.risks = []

    def assess(self, data):
        """Perform risk assessment"""
        likelihood = data.get('likelihood', 0)
        impact = data.get('impact', 0)

        # FAIR calculation
        risk_score = self._calculate_fair_score(likelihood, impact)

        risk = {
            'likelihood': likelihood,
            'impact': impact,
            'score': risk_score,
            'level': self._get_risk_level(risk_score)
        }

        self.risks.append(risk)
        return risk

    def _calculate_fair_score(self, likelihood, impact):
        """Calculate FAIR risk score"""
        # TODO: Implement proper FAIR methodology
        return likelihood * impact

    def _get_risk_level(self, score):
        """Get risk level from score"""
        if score > 80:
            return 'critical'
        elif score > 60:
            return 'high'
        elif score > 40:
            return 'medium'
        else:
            return 'low'

    def has_high_risks(self):
        """Check if there are high risks"""
        return any(r['level'] in ['high', 'critical'] for r in self.risks)

    def get_risk_score(self):
        """Get average risk score"""
        if not self.risks:
            return 0
        return sum(r['score'] for r in self.risks) / len(self.risks)


# Duplicate code block (intentional for testing)
def _calculate_fair_score_v2(likelihood, impact):
    """Calculate FAIR risk score"""
    # TODO: Implement proper FAIR methodology
    return likelihood * impact

def _get_risk_level_v2(score):
    """Get risk level from score"""
    if score > 80:
        return 'critical'
    elif score > 60:
        return 'high'
    elif score > 40:
        return 'medium'
    else:
        return 'low'
