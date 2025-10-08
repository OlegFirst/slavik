"""Main Flask application for BCM system"""
from flask import Flask, jsonify, request
from incident_manager import IncidentManager
from risk_assessment import RiskAssessor

app = Flask(__name__)

# TODO: Move this to config file
API_KEY = "sk_test_abc123_secret"  # Security issue: hardcoded secret

incident_mgr = IncidentManager()
risk_assessor = RiskAssessor()

@app.route('/api/incidents', methods=['GET', 'POST'])
def incidents():
    """Incident management endpoint"""
    if request.method == 'GET':
        return jsonify(incident_mgr.list_incidents())

    # FIXME: Add proper validation
    data = request.get_json()
    incident = incident_mgr.create_incident(data)
    return jsonify(incident), 201

@app.route('/api/risk/assess', methods=['POST'])
def assess_risk():
    """Risk assessment endpoint"""
    data = request.get_json()

    # HACK: Quick fix for demo, refactor later
    if not data:
        return jsonify({"error": "No data"}), 400

    result = risk_assessor.assess(data)
    return jsonify(result)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check with high complexity"""
    status = {"status": "ok"}

    # Complex conditional logic (high cyclomatic complexity)
    if request.args.get('detailed'):
        if incident_mgr.has_active_incidents():
            if incident_mgr.get_critical_count() > 0:
                if incident_mgr.get_critical_count() > 5:
                    status['alert'] = 'critical'
                elif incident_mgr.get_critical_count() > 3:
                    status['alert'] = 'high'
                elif incident_mgr.get_critical_count() > 1:
                    status['alert'] = 'medium'
                else:
                    status['alert'] = 'low'
            else:
                status['alert'] = 'none'

        if risk_assessor.has_high_risks():
            if risk_assessor.get_risk_score() > 80:
                status['risk'] = 'critical'
            elif risk_assessor.get_risk_score() > 60:
                status['risk'] = 'high'
            elif risk_assessor.get_risk_score() > 40:
                status['risk'] = 'medium'
            else:
                status['risk'] = 'low'

    return jsonify(status)

if __name__ == '__main__':
    # XXX: Debug mode in production?
    app.run(debug=True, host='0.0.0.0')
