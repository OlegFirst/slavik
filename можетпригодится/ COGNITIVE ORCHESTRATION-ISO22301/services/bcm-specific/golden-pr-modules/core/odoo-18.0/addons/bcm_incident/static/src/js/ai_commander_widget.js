/* BCM Incident Management - AI Commander Widget */

odoo.define('bcm_incident_unified.ai_commander_widget', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var field_registry = require('web.field_registry');
var core = require('web.core');
var QWeb = core.qweb;

var AICommanderWidget = AbstractField.extend({
    template: 'bcm_incident_unified.AICommanderWidget',
    
    events: {
        'click .refresh_ai_analysis': '_onRefreshAIAnalysis',
        'click .apply_ai_recommendation': '_onApplyRecommendation',
        'click .view_similar_incidents': '_onViewSimilarIncidents',
    },

    init: function () {
        this._super.apply(this, arguments);
        this.ai_data = {};
        this._startRealtimeUpdates();
    },

    _render: function () {
        this._super.apply(this, arguments);
        this._renderAIRiskMeter();
        this._renderRecommendations();
        this._updateSimilarIncidents();
    },

    _renderAIRiskMeter: function () {
        var $meter = this.$('.ai_risk_meter');
        var riskScore = this.value || 0;
        
        // Create circular progress meter
        var canvas = $meter.find('canvas')[0];
        if (canvas) {
            var ctx = canvas.getContext('2d');
            var centerX = canvas.width / 2;
            var centerY = canvas.height / 2;
            var radius = 45;
            
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Background circle
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
            ctx.strokeStyle = '#e0e0e0';
            ctx.lineWidth = 8;
            ctx.stroke();
            
            // Risk score arc
            var endAngle = (riskScore / 100) * 2 * Math.PI - Math.PI / 2;
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, -Math.PI / 2, endAngle);
            
            // Color based on risk level
            if (riskScore < 30) ctx.strokeStyle = '#4CAF50';
            else if (riskScore < 60) ctx.strokeStyle = '#FF9800';
            else if (riskScore < 80) ctx.strokeStyle = '#FF5722';
            else ctx.strokeStyle = '#F44336';
            
            ctx.lineWidth = 8;
            ctx.lineCap = 'round';
            ctx.stroke();
            
            // Risk score text
            ctx.fillStyle = '#333';
            ctx.font = 'bold 18px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(Math.round(riskScore) + '%', centerX, centerY + 5);
        }
    },

    _renderRecommendations: function () {
        var $container = this.$('.ai_recommendations_container');
        var recommendations = this.recordData.ai_recommendations || '';
        
        if (recommendations) {
            var lines = recommendations.split('\n');
            $container.empty();
            
            lines.forEach(function(line, index) {
                if (line.trim()) {
                    var priority = line.includes('IMMEDIATE') || line.includes('CRITICAL') ? 'high' : 'normal';
                    var $card = $('<div class="ai_recommendation_card ' + (priority === 'high' ? 'high_priority' : '') + '">');
                    $card.html('<i class="fa fa-lightbulb-o"></i> ' + line);
                    $container.append($card);
                }
            });
        }
    },

    _updateSimilarIncidents: function () {
        var self = this;
        var $container = this.$('.similar_incidents_container');
        
        if (this.recordData.ai_similar_incidents && this.recordData.ai_similar_incidents.length > 0) {
            this._rpc({
                model: 'bcm.incident',
                method: 'read',
                args: [this.recordData.ai_similar_incidents, ['incident_number', 'title', 'severity']],
            }).then(function (incidents) {
                $container.empty();
                incidents.forEach(function(incident) {
                    var $item = $('<div class="similar_incident_item">');
                    $item.html('<strong>' + incident.incident_number + '</strong>: ' + incident.title);
                    $item.data('incident-id', incident.id);
                    $container.append($item);
                });
            });
        }
    },

    _onRefreshAIAnalysis: function (e) {
        e.preventDefault();
        var self = this;
        
        this._showLoadingSpinner();
        
        this._rpc({
            model: 'bcm.incident',
            method: '_trigger_ai_analysis',
            args: [this.res_id],
        }).then(function () {
            self._hideLoadingSpinner();
            self.trigger_up('reload');
        }).catch(function (error) {
            self._hideLoadingSpinner();
            self._showErrorMessage('Failed to refresh AI analysis: ' + error.message);
        });
    },

    _onApplyRecommendation: function (e) {
        e.preventDefault();
        var $button = $(e.currentTarget);
        var recommendation = $button.data('recommendation');
        
        // Apply specific AI recommendation
        this._rpc({
            model: 'bcm.incident',
            method: 'apply_ai_recommendation',
            args: [this.res_id, recommendation],
        }).then(function () {
            $button.addClass('btn-success').text('Applied').prop('disabled', true);
        });
    },

    _onViewSimilarIncidents: function (e) {
        e.preventDefault();
        var $item = $(e.currentTarget);
        var incidentId = $item.data('incident-id');
        
        this.do_action({
            type: 'ir.actions.act_window',
            res_model: 'bcm.incident',
            res_id: incidentId,
            views: [[false, 'form']],
            target: 'new',
        });
    },

    _startRealtimeUpdates: function () {
        var self = this;
        
        // Update AI analysis every 30 seconds for active incidents
        if (this.recordData.status && ['detected', 'assessing', 'responding'].includes(this.recordData.status)) {
            this.updateInterval = setInterval(function () {
                self._checkForAIUpdates();
            }, 30000);
        }
    },

    _checkForAIUpdates: function () {
        var self = this;
        
        this._rpc({
            model: 'bcm.incident',
            method: 'read',
            args: [this.res_id, ['ai_risk_score', 'ai_recommendations', 'ai_escalation_prediction']],
        }).then(function (data) {
            if (data.length > 0) {
                var incident = data[0];
                if (incident.ai_risk_score !== self.recordData.ai_risk_score) {
                    self.recordData.ai_risk_score = incident.ai_risk_score;
                    self._renderAIRiskMeter();
                }
                
                if (incident.ai_escalation_prediction && !self.recordData.ai_escalation_prediction) {
                    self._showEscalationAlert();
                }
            }
        });
    },

    _showEscalationAlert: function () {
        var $alert = $('<div class="alert alert-warning ai_escalation_alert">');
        $alert.html('<i class="fa fa-exclamation-triangle"></i> <strong>AI Alert:</strong> This incident is predicted to escalate. Consider immediate action.');
        this.$('.ai_commander_panel').prepend($alert);
        
        // Auto-hide after 10 seconds
        setTimeout(function () {
            $alert.fadeOut();
        }, 10000);
    },

    _showLoadingSpinner: function () {
        this.$('.ai_loading_spinner').show();
    },

    _hideLoadingSpinner: function () {
        this.$('.ai_loading_spinner').hide();
    },

    _showErrorMessage: function (message) {
        var $error = $('<div class="alert alert-danger">');
        $error.text(message);
        this.$('.ai_commander_panel').append($error);
        
        setTimeout(function () {
            $error.fadeOut();
        }, 5000);
    },

    destroy: function () {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        this._super.apply(this, arguments);
    },
});

// Register the widget
field_registry.add('ai_commander_widget', AICommanderWidget);

return AICommanderWidget;
});

/* GPS Tracking Widget */
odoo.define('bcm_incident_unified.gps_tracking_widget', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var field_registry = require('web.field_registry');

var GPSTrackingWidget = AbstractField.extend({
    template: 'bcm_incident_unified.GPSTrackingWidget',
    
    events: {
        'click .update_location': '_onUpdateLocation',
        'click .view_on_map': '_onViewOnMap',
    },

    init: function () {
        this._super.apply(this, arguments);
        this.coordinates = null;
        this._getCurrentLocation();
    },

    _getCurrentLocation: function () {
        var self = this;
        
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function (position) {
                    self.coordinates = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: new Date().toISOString()
                    };
                    self._updateLocationDisplay();
                },
                function (error) {
                    console.warn('GPS location access denied:', error);
                    self._showLocationError();
                }
            );
        }
    },

    _updateLocationDisplay: function () {
        if (this.coordinates) {
            this.$('.gps_coordinates').text(
                this.coordinates.lat.toFixed(6) + ', ' + this.coordinates.lng.toFixed(6)
            );
            this.$('.gps_accuracy').text('±' + Math.round(this.coordinates.accuracy) + 'm');
            this.$('.gps_timestamp').text(new Date(this.coordinates.timestamp).toLocaleString());
        }
    },

    _onUpdateLocation: function (e) {
        e.preventDefault();
        this._getCurrentLocation();
        
        if (this.coordinates) {
            this._rpc({
                model: 'bcm.incident.field.update',
                method: 'create',
                args: [{
                    incident_id: this.res_id,
                    reporter_id: this.getSession().uid,
                    update_text: 'Location updated via GPS',
                    gps_location: this.coordinates.lat + ',' + this.coordinates.lng,
                }],
            }).then(function () {
                self.trigger_up('show_effect', {
                    message: 'Location updated successfully',
                    type: 'rainbow_man',
                });
            });
        }
    },

    _onViewOnMap: function (e) {
        e.preventDefault();
        if (this.coordinates) {
            var mapUrl = 'https://maps.google.com/maps?q=' + 
                        this.coordinates.lat + ',' + this.coordinates.lng;
            window.open(mapUrl, '_blank');
        }
    },

    _showLocationError: function () {
        this.$('.gps_error').show().text('GPS location not available');
    },
});

field_registry.add('gps_tracking_widget', GPSTrackingWidget);

return GPSTrackingWidget;
});