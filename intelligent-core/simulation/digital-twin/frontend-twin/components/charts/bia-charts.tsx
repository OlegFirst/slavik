'use client';

import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface BIAChartsProps {
  queueMetrics: {
    average_wait_time: number;
    average_queue_length: number;
    server_utilization: number;
    probability_wait: number;
  };
  recoveryStrategies: Array<{
    name: string;
    estimated_cost_annual: number;
    expected_rto_hours: number;
    risk_reduction_percentage: number;
  }>;
}

export function BIACharts({ queueMetrics, recoveryStrategies }: BIAChartsProps) {
  // Queue metrics data for bar chart
  const metricsData = [
    {
      name: 'Wait Time',
      value: queueMetrics.average_wait_time * 60, // Convert to minutes
      unit: 'min',
      color: '#3B82F6',
    },
    {
      name: 'Queue Length',
      value: queueMetrics.average_queue_length,
      unit: 'customers',
      color: '#8B5CF6',
    },
    {
      name: 'Utilization',
      value: queueMetrics.server_utilization * 100,
      unit: '%',
      color: queueMetrics.server_utilization > 0.8 ? '#F97316' : '#22C55E',
    },
    {
      name: 'Wait Probability',
      value: queueMetrics.probability_wait * 100,
      unit: '%',
      color: '#EAB308',
    },
  ];

  // Utilization gauge data
  const utilizationData = [
    { name: 'Used', value: queueMetrics.server_utilization * 100 },
    { name: 'Available', value: (1 - queueMetrics.server_utilization) * 100 },
  ];

  const utilizationColors = queueMetrics.server_utilization > 0.9
    ? ['#EF4444', '#F3F4F6']
    : queueMetrics.server_utilization > 0.8
    ? ['#F97316', '#F3F4F6']
    : ['#22C55E', '#F3F4F6'];

  // Recovery strategies comparison
  const strategiesData = recoveryStrategies.map((s) => ({
    name: s.name.length > 15 ? s.name.substring(0, 15) + '...' : s.name,
    cost: s.estimated_cost_annual / 1000, // Convert to thousands
    rto: s.expected_rto_hours * 60, // Convert to minutes
    risk_reduction: s.risk_reduction_percentage,
  }));

  return (
    <div className="space-y-8">
      {/* Queue Metrics Bar Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Queue Metrics Overview</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={metricsData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip
              formatter={(value: number, name: string, props: any) => {
                const unit = props.payload.unit;
                return [`${value.toFixed(2)} ${unit}`, name];
              }}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
              }}
            />
            <Bar dataKey="value" fill="#3B82F6" radius={[8, 8, 0, 0]}>
              {metricsData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Two column layout */}
      <div className="grid grid-cols-2 gap-6">
        {/* Server Utilization Gauge */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Server Utilization</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={utilizationData}
                cx="50%"
                cy="50%"
                startAngle={180}
                endAngle={0}
                innerRadius={60}
                outerRadius={100}
                paddingAngle={2}
                dataKey="value"
              >
                {utilizationData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={utilizationColors[index]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
            </PieChart>
          </ResponsiveContainer>
          <div className="text-center mt-4">
            <p className="text-3xl font-bold">
              {(queueMetrics.server_utilization * 100).toFixed(1)}%
            </p>
            <p className="text-sm text-gray-600 mt-1">
              {queueMetrics.server_utilization > 0.9
                ? '⚠️ Critical - Consider adding servers'
                : queueMetrics.server_utilization > 0.8
                ? '⚡ High - Monitor closely'
                : '✅ Healthy utilization'}
            </p>
          </div>
        </div>

        {/* Wait Time Distribution (simulated) */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Wait Time Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart
              data={[
                { time: '0-5', customers: 45 },
                { time: '5-10', customers: 72 },
                { time: '10-15', customers: 55 },
                { time: '15-20', customers: 28 },
                { time: '20-25', customers: 15 },
                { time: '25+', customers: 8 },
              ]}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="time" label={{ value: 'Wait Time (min)', position: 'insideBottom', offset: -5 }} />
              <YAxis label={{ value: 'Customers', angle: -90, position: 'insideLeft' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                }}
              />
              <Line
                type="monotone"
                dataKey="customers"
                stroke="#3B82F6"
                strokeWidth={3}
                dot={{ fill: '#3B82F6', r: 5 }}
                activeDot={{ r: 7 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recovery Strategies Comparison */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Recovery Strategies Cost-Benefit Analysis</h3>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={strategiesData} layout="horizontal">
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis type="number" />
            <YAxis dataKey="name" type="category" width={120} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
              }}
              formatter={(value: number, name: string) => {
                if (name === 'cost') return [`$${value.toFixed(0)}k`, 'Annual Cost'];
                if (name === 'rto') return [`${value.toFixed(0)} min`, 'RTO'];
                if (name === 'risk_reduction') return [`${value.toFixed(0)}%`, 'Risk Reduction'];
                return [value, name];
              }}
            />
            <Legend
              wrapperStyle={{ paddingTop: '20px' }}
              formatter={(value) => {
                if (value === 'cost') return 'Annual Cost ($k)';
                if (value === 'rto') return 'RTO (minutes)';
                if (value === 'risk_reduction') return 'Risk Reduction (%)';
                return value;
              }}
            />
            <Bar dataKey="cost" fill="#EF4444" radius={[0, 4, 4, 0]} />
            <Bar dataKey="risk_reduction" fill="#22C55E" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
        <p className="text-xs text-gray-500 mt-4 text-center">
          💡 Lower cost + higher risk reduction = better strategy
        </p>
      </div>
    </div>
  );
}
