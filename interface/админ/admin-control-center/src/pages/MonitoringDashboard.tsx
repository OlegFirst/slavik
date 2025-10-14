/**
 * Monitoring Dashboard - Real-time BCM Platform Monitoring
 *
 * Integrates with Monitoring Backend API (port 8050)
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Chip
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';

interface DashboardMetrics {
  total_services: number;
  healthy_services: number;
  warning_services: number;
  error_services: number;
  cpu_usage: number;
  memory_usage: number;
  active_pdca_cycles: number;
  active_alerts: number;
  last_updated: string;
}

const MonitoringDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8050/api/v1/dashboard/overview');
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
        setError(null);
      } else {
        setError(`Error: ${response.status}`);
      }
    } catch (err) {
      setError('Failed to connect to monitoring API');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000); // Update every 10s
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Card>
          <CardContent>
            <Typography color="error">{error}</Typography>
            <Typography variant="body2" mt={2}>
              Make sure Monitoring Backend is running on port 8050
            </Typography>
          </CardContent>
        </Card>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        <DashboardIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        BCM Platform Monitoring
      </Typography>

      <Grid container spacing={3} mt={2}>
        {/* Services Status */}
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Services Status
              </Typography>
              <Typography variant="h3">
                {metrics?.healthy_services}/{metrics?.total_services}
              </Typography>
              <Box mt={1}>
                <Chip
                  icon={<CheckIcon />}
                  label={`${metrics?.healthy_services} Healthy`}
                  color="success"
                  size="small"
                  sx={{ mr: 1 }}
                />
                {(metrics?.error_services ?? 0) > 0 && (
                  <Chip
                    icon={<WarningIcon />}
                    label={`${metrics?.error_services} Error`}
                    color="error"
                    size="small"
                  />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* CPU Usage */}
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                CPU Usage
              </Typography>
              <Typography variant="h3">
                {metrics?.cpu_usage}%
              </Typography>
              <Box mt={1}>
                <MemoryIcon color="primary" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Memory Usage */}
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Memory Usage
              </Typography>
              <Typography variant="h3">
                {metrics?.memory_usage}%
              </Typography>
              <Box mt={1}>
                <StorageIcon color="primary" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* PDCA Cycles */}
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active PDCA Cycles
              </Typography>
              <Typography variant="h3">
                {metrics?.active_pdca_cycles}
              </Typography>
              <Typography variant="body2" color="textSecondary" mt={1}>
                Continuous Improvement
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Active Alerts */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Alerts
              </Typography>
              {(metrics?.active_alerts ?? 0) === 0 ? (
                <Typography color="success.main">
                  <CheckIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                  No active alerts
                </Typography>
              ) : (
                <Typography color="warning.main">
                  <WarningIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                  {metrics?.active_alerts} alerts require attention
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Typography variant="caption" display="block" mt={2} color="textSecondary">
        Last updated: {metrics?.last_updated ? new Date(metrics.last_updated).toLocaleString() : 'Never'}
      </Typography>
    </Box>
  );
};

export default MonitoringDashboard;
