import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Database,
  LineChart,
  Shield,
  TrendingUp,
  Users,
  Zap,
  RefreshCw,
  Server
} from 'lucide-react';

import bcmRealDataService, {
  ComplianceStatus,
  RiskAssessment,
  BIAResult,
  IncidentRecord,
  KPIMetric,
  DigitalTwinMetrics,
  bcmCachedService
} from '../services/bcm-realdata';

interface DashboardStats {
  totalCompliance: number;
  activeRisks: number;
  openIncidents: number;
  criticalProcesses: number;
  kpiTargets: number;
  platformHealth: string;
}

const RealDataDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Unified database states
  const [systemMetrics, setSystemMetrics] = useState<UnifiedSystemMetrics | null>(null);
  const [bcmRealData, setBcmRealData] = useState<BCMRealData | null>(null);
  const [databasesHealth, setDatabasesHealth] = useState<DatabaseHealth[]>([]);

  // Core data states
  const [dashboardStats, setDashboardStats] = useState<DashboardStats>({
    totalCompliance: 0,
    activeRisks: 0,
    openIncidents: 0,
    criticalProcesses: 0,
    kpiTargets: 0,
    platformHealth: 'unknown'
  });

  const [complianceData, setComplianceData] = useState<ComplianceStatus[]>([]);
  const [riskData, setRiskData] = useState<RiskAssessment[]>([]);
  const [incidentData, setIncidentData] = useState<IncidentRecord[]>([]);
  const [kpiData, setKpiData] = useState<any>({});
  const [digitalTwinMetrics, setDigitalTwinMetrics] = useState<DigitalTwinMetrics | null>(null);
  const [platformHealth, setPlatformHealth] = useState<any>({});
  const [aiOrganStatus, setAiOrganStatus] = useState<any>({});
  const [cacheStats, setCacheStats] = useState<any>({});

  // Load all dashboard data from unified database
  const loadDashboardData = async (useCache: boolean = true) => {
    try {
      setRefreshing(true);
      setError(null);

      // Load unified system metrics and BCM real data
      const [systemHealth, realData] = await Promise.all([
        unifiedDatabaseService.checkAllDatabasesHealth(),
        unifiedDatabaseService.getBCMRealData()
      ]);

      // Update unified states
      setSystemMetrics(systemHealth);
      setBcmRealData(realData);
      setDatabasesHealth(systemHealth.databases);

      // Update legacy dashboard stats for compatibility
      setDashboardStats({
        totalCompliance: realData.compliance.total_items,
        activeRisks: realData.risks.high_risk + realData.risks.medium_risk,
        openIncidents: realData.incidents.active,
        criticalProcesses: realData.incidents.critical,
        kpiTargets: Math.floor(realData.users.total * 0.8), // Estimate
        platformHealth: systemHealth.overall_status
      });

      // Load legacy data in parallel for backward compatibility
      const [
        compliance,
        highRisks,
        activeIncidents,
        kpiDashboard,
        digitalTwin,
        health,
        aiOrgans,
        cache
      ] = await Promise.all([
        useCache ? bcmCachedService.getComplianceOverviewCached() : bcmRealDataService.getComplianceOverview(),
        bcmRealDataService.getHighPriorityRisks(),
        bcmRealDataService.getActiveIncidents(),
        useCache ? bcmCachedService.getKPIDashboardCached() : bcmRealDataService.getKPIDashboard(),
        bcmRealDataService.getDigitalTwinMetrics(),
        bcmRealDataService.getPlatformHealth(),
        bcmRealDataService.getAIOrganStatus(),
        bcmRealDataService.getCacheStats()
      ]);

      // Update states
      setComplianceData(compliance);
      setRiskData(highRisks);
      setIncidentData(activeIncidents);
      setKpiData(kpiDashboard);
      setDigitalTwinMetrics(digitalTwin);
      setPlatformHealth(health);
      setAiOrganStatus(aiOrgans);
      setCacheStats(cache);

      // Calculate dashboard stats
      setDashboardStats({
        totalCompliance: compliance.length,
        activeRisks: highRisks.length,
        openIncidents: activeIncidents.length,
        criticalProcesses: 0, // Will be updated separately
        kpiTargets: kpiDashboard.on_target || 0,
        platformHealth: health.overall_status || 'unknown'
      });

    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Ошибка загрузки данных BCM платформы');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Initial load
  useEffect(() => {
    loadDashboardData();

    // Set up auto-refresh every 5 minutes
    const interval = setInterval(() => {
      loadDashboardData(true); // Use cache for auto-refresh
    }, 300000);

    return () => clearInterval(interval);
  }, []);

  // Manual refresh
  const handleRefresh = () => {
    loadDashboardData(false); // Force fresh data
  };

  // Clear cache
  const handleClearCache = async () => {
    try {
      // Clear unified database service cache
      unifiedDatabaseService.clearCache();

      // Clear legacy service cache for backward compatibility
      await bcmRealDataService.clearCache('all');

      // Reload data
      loadDashboardData(false);
    } catch (err) {
      console.error('Error clearing cache:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p>Загрузка данных BCM платформы...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with refresh controls */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">BCM Platform Dashboard</h1>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleClearCache}
            disabled={refreshing}
          >
            Очистить кэш
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Обновить
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Unified Database Health Status */}
      {systemMetrics && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="w-5 h-5" />
              Unified Database Health
              <Badge
                variant={systemMetrics.overall_status === 'healthy' ? 'default' :
                        systemMetrics.overall_status === 'degraded' ? 'secondary' : 'destructive'}
              >
                {systemMetrics.overall_status.toUpperCase()}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-4">
              {systemMetrics.databases.map((db, index) => (
                <div key={index} className="text-center">
                  <div className={`p-3 rounded-lg border ${
                    db.status === 'online' ? 'border-green-200 bg-green-50' :
                    db.status === 'degraded' ? 'border-yellow-200 bg-yellow-50' :
                    'border-red-200 bg-red-50'
                  }`}>
                    <div className={`text-lg font-bold ${
                      db.status === 'online' ? 'text-green-600' :
                      db.status === 'degraded' ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {db.status === 'online' ? '✅' : db.status === 'degraded' ? '⚠️' : '❌'}
                    </div>
                    <div className="text-sm font-medium">{db.name}</div>
                    <div className="text-xs text-gray-600">{db.responseTime}ms</div>
                    {db.error && (
                      <div className="text-xs text-red-500 mt-1" title={db.error}>
                        Error
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* BCM Data Summary */}
            {bcmRealData && (
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4 pt-4 border-t">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{systemMetrics.data_summary.users}</div>
                  <div className="text-sm text-gray-600">Users</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{systemMetrics.data_summary.companies}</div>
                  <div className="text-sm text-gray-600">Companies</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{systemMetrics.data_summary.incidents}</div>
                  <div className="text-sm text-gray-600">Incidents</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{systemMetrics.data_summary.documents}</div>
                  <div className="text-sm text-gray-600">Documents</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">{systemMetrics.data_summary.ai_memories}</div>
                  <div className="text-sm text-gray-600">AI Memories</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-600">{systemMetrics.data_summary.audit_logs}</div>
                  <div className="text-sm text-gray-600">Audit Logs</div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Platform Health Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="w-5 h-5" />
            Состояние платформы
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className={`text-2xl font-bold ${
                platformHealth.overall_status === 'healthy' ? 'text-green-600' :
                platformHealth.overall_status === 'warning' ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {platformHealth.overall_status === 'healthy' ? '✅' :
                 platformHealth.overall_status === 'warning' ? '⚠️' : '❌'}
              </div>
              <p className="text-sm text-gray-600">Общий статус</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{platformHealth.active_users || 0}</div>
              <p className="text-sm text-gray-600">Активных пользователей</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{cacheStats.hit_rate || 0}%</div>
              <p className="text-sm text-gray-600">Cache Hit Rate</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{platformHealth.api_response_time || 0}ms</div>
              <p className="text-sm text-gray-600">Время ответа API</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Соответствие ISO 22301</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardStats.totalCompliance}</div>
            <p className="text-xs text-muted-foreground">
              организаций в оценке
            </p>
            {complianceData.length > 0 && (
              <div className="mt-2">
                <Progress
                  value={complianceData[0]?.compliance_percentage || 0}
                  className="h-2"
                />
                <p className="text-xs text-gray-600 mt-1">
                  {complianceData[0]?.compliance_percentage || 0}% соответствие
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Критические риски</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{dashboardStats.activeRisks}</div>
            <p className="text-xs text-muted-foreground">
              требуют внимания
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Активные инциденты</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{dashboardStats.openIncidents}</div>
            <p className="text-xs text-muted-foreground">
              в работе
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">KPI показатели</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{kpiData.on_target || 0}</div>
            <p className="text-xs text-muted-foreground">
              из {kpiData.total_metrics || 0} в норме
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Sections */}
      <Tabs defaultValue="compliance" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="compliance">Соответствие</TabsTrigger>
          <TabsTrigger value="risks">Риски</TabsTrigger>
          <TabsTrigger value="incidents">Инциденты</TabsTrigger>
          <TabsTrigger value="digital-twin">Digital Twin</TabsTrigger>
          <TabsTrigger value="ai-organs">AI Органы</TabsTrigger>
        </TabsList>

        <TabsContent value="compliance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Статус соответствия ISO 22301</CardTitle>
            </CardHeader>
            <CardContent>
              {complianceData.length > 0 ? (
                <div className="space-y-4">
                  {complianceData.map((org) => (
                    <div key={org.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-semibold">{org.organization_name}</h3>
                        <Badge variant={
                          org.iso22301_status === 'compliant' ? 'default' :
                          org.iso22301_status === 'partially_compliant' ? 'secondary' : 'destructive'
                        }>
                          {org.iso22301_status}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Соответствие:</span>
                          <div className="font-semibold">{org.compliance_percentage}%</div>
                        </div>
                        <div>
                          <span className="text-gray-600">Критические находки:</span>
                          <div className="font-semibold text-red-600">{org.critical_findings}</div>
                        </div>
                        <div>
                          <span className="text-gray-600">Открытые действия:</span>
                          <div className="font-semibold">{org.open_actions}</div>
                        </div>
                        <div>
                          <span className="text-gray-600">Следующий пересмотр:</span>
                          <div className="font-semibold">{new Date(org.next_review_date).toLocaleDateString()}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600">Нет данных о соответствии</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="risks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Критические риски</CardTitle>
            </CardHeader>
            <CardContent>
              {riskData.length > 0 ? (
                <div className="space-y-4">
                  {riskData.map((risk) => (
                    <div key={risk.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-semibold">{risk.risk_name}</h3>
                        <Badge variant={risk.risk_score > 15 ? 'destructive' : 'secondary'}>
                          Риск: {risk.risk_score}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Категория:</span>
                          <div className="font-semibold">{risk.category}</div>
                        </div>
                        <div>
                          <span className="text-gray-600">Владелец:</span>
                          <div className="font-semibold">{risk.owner}</div>
                        </div>
                        <div>
                          <span className="text-gray-600">Статус:</span>
                          <div className="font-semibold">{risk.mitigation_status}</div>
                        </div>
                        <div>
                          <span className="text-gray-600">Срок:</span>
                          <div className="font-semibold">{new Date(risk.due_date).toLocaleDateString()}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600">Нет критических рисков</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="incidents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Активные инциденты</CardTitle>
            </CardHeader>
            <CardContent>
              {incidentData.length > 0 ? (
                <div className="space-y-4">
                  {incidentData.map((incident) => (
                    <div key={incident.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-semibold">{incident.incident_type}</h3>
                        <Badge variant={
                          incident.severity === 'critical' ? 'destructive' :
                          incident.severity === 'high' ? 'secondary' : 'default'
                        }>
                          {incident.severity}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{incident.impact_description}</p>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Статус:</span>
                          <div className="font-semibold">{incident.status}</div>
                        </div>
                        <div>
                          <span className="text-gray-600">Дата:</span>
                          <div className="font-semibold">{new Date(incident.reported_date).toLocaleDateString()}</div>
                        </div>
                        <div>
                          <span className="text-gray-600">Время реагирования:</span>
                          <div className="font-semibold">{incident.response_time_minutes} мин</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600">Нет активных инцидентов</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="digital-twin" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Цифровой двойник организации</CardTitle>
            </CardHeader>
            <CardContent>
              {digitalTwinMetrics ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-blue-600">
                        {digitalTwinMetrics.resilience_score.toFixed(1)}
                      </div>
                      <p className="text-sm text-gray-600">Индекс устойчивости</p>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-green-600">
                        {digitalTwinMetrics.business_continuity_index.toFixed(1)}
                      </div>
                      <p className="text-sm text-gray-600">Индекс непрерывности</p>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-orange-600">
                        {digitalTwinMetrics.compliance_maturity.toFixed(1)}
                      </div>
                      <p className="text-sm text-gray-600">Зрелость соответствия</p>
                    </div>
                  </div>

                  {digitalTwinMetrics.simulation_results.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-3">Результаты моделирования</h4>
                      <div className="space-y-2">
                        {digitalTwinMetrics.simulation_results.map((sim, index) => (
                          <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                            <span className="font-medium">{sim.scenario_name}</span>
                            <div className="text-sm text-gray-600">
                              Воздействие: {sim.predicted_impact.toFixed(1)} |
                              Восстановление: {sim.recovery_time_estimate.toFixed(1)}ч |
                              Достоверность: {sim.confidence_level.toFixed(1)}%
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-600">Данные цифрового двойника недоступны</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ai-organs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>AI Органы платформы</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center">
                  <div className="text-2xl font-bold">{aiOrganStatus.total_organs || 0}</div>
                  <p className="text-sm text-gray-600">Всего органов</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{aiOrganStatus.active_organs || 0}</div>
                  <p className="text-sm text-gray-600">Активных</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{aiOrganStatus.processing_requests || 0}</div>
                  <p className="text-sm text-gray-600">Запросов в обработке</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{aiOrganStatus.avg_response_time || 0}ms</div>
                  <p className="text-sm text-gray-600">Среднее время ответа</p>
                </div>
              </div>

              {aiOrganStatus.organs && aiOrganStatus.organs.length > 0 && (
                <div className="space-y-3">
                  {aiOrganStatus.organs.map((organ: any, index: number) => (
                    <div key={index} className="flex justify-between items-center p-3 border rounded">
                      <div>
                        <span className="font-semibold">{organ.name}</span>
                        <div className="text-sm text-gray-600">
                          Последняя активность: {new Date(organ.last_activity).toLocaleString()}
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-sm">
                          Нагрузка: {organ.load_percentage}%
                        </div>
                        <Badge variant={
                          organ.status === 'active' ? 'default' :
                          organ.status === 'busy' ? 'secondary' : 'destructive'
                        }>
                          {organ.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default RealDataDashboard;