"""Tests for Incident Manager"""
import pytest
import sys
sys.path.insert(0, '../src')

from incident_manager import IncidentManager

def test_create_incident():
    """Test incident creation"""
    mgr = IncidentManager()
    data = {
        'title': 'Test incident',
        'severity': 'high'
    }
    incident = mgr.create_incident(data)

    assert incident['title'] == 'Test incident'
    assert incident['severity'] == 'high'
    assert incident['status'] == 'open'

def test_list_incidents():
    """Test listing incidents"""
    mgr = IncidentManager()
    incidents = mgr.list_incidents()
    assert isinstance(incidents, list)

def test_has_active_incidents():
    """Test active incidents check"""
    mgr = IncidentManager()
    mgr.incidents = [{'status': 'open'}]
    assert mgr.has_active_incidents() == True
