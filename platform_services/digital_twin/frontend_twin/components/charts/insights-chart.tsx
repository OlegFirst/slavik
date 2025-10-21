'use client';

import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';

interface InsightsSummary {
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
}

interface InsightsChartProps {
  summary: InsightsSummary;
}

const COLORS = {
  critical: '#EF4444',
  high: '#F97316',
  medium: '#EAB308',
  low: '#22C55E',
};

export function InsightsChart({ summary }: InsightsChartProps) {
  // Data for pie chart
  const pieData = [
    { name: 'Critical', value: summary.critical_count, color: COLORS.critical },
    { name: 'High', value: summary.high_count, color: COLORS.high },
    { name: 'Medium', value: summary.medium_count, color: COLORS.medium },
    { name: 'Low', value: summary.low_count, color: COLORS.low },
  ].filter((item) => item.value > 0); // Only show non-zero values

  // Data for bar chart
  const barData = [
    { level: 'Critical', count: summary.critical_count, fill: COLORS.critical },
    { level: 'High', count: summary.high_count, fill: COLORS.high },
    { level: 'Medium', count: summary.medium_count, fill: COLORS.medium },
    { level: 'Low', count: summary.low_count, fill: COLORS.low },
  ];

  const total = summary.critical_count + summary.high_count + summary.medium_count + summary.low_count;

  // Risk score calculation (weighted)
  const riskScore =
    (summary.critical_count * 10 +
      summary.high_count * 6 +
      summary.medium_count * 3 +
      summary.low_count * 1) /
    (total * 10) *
    100;

  // Radar data for risk profile
  const radarData = [
    {
      category: 'Critical',
      score: (summary.critical_count / Math.max(total, 1)) * 100,
    },
    {
      category: 'High',
      score: (summary.high_count / Math.max(total, 1)) * 100,
    },
    {
      category: 'Medium',
      score: (summary.medium_count / Math.max(total, 1)) * 100,
    },
    {
      category: 'Low',
      score: (summary.low_count / Math.max(total, 1)) * 100,
    },
  ];

  return (
    <div className="grid grid-cols-3 gap-6">
      {/* Pie Chart - Distribution */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 text-center">Insights Distribution</h3>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
        <div className="text-center mt-4">
          <p className="text-sm text-gray-600">Total Insights</p>
          <p className="text-3xl font-bold text-gray-900">{total}</p>
        </div>
      </div>

      {/* Bar Chart - Count by Level */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 text-center">Insights by Priority</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={barData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="level" />
            <YAxis />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
              }}
            />
            <Bar dataKey="count" radius={[8, 8, 0, 0]}>
              {barData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Risk Profile Radar */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 text-center">Risk Profile</h3>
        <ResponsiveContainer width="100%" height={250}>
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
            <PolarGrid stroke="#E5E7EB" />
            <PolarAngleAxis dataKey="category" />
            <PolarRadiusAxis angle={90} domain={[0, 100]} />
            <Radar
              name="Risk"
              dataKey="score"
              stroke="#3B82F6"
              fill="#3B82F6"
              fillOpacity={0.6}
            />
            <Tooltip
              formatter={(value: number) => `${value.toFixed(1)}%`}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
        <div className="text-center mt-4">
          <p className="text-sm text-gray-600">Risk Score</p>
          <p className={`text-3xl font-bold ${
            riskScore > 70 ? 'text-red-600' :
            riskScore > 40 ? 'text-orange-600' :
            riskScore > 20 ? 'text-yellow-600' :
            'text-green-600'
          }`}>
            {riskScore.toFixed(1)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {riskScore > 70 ? ' High Risk' :
             riskScore > 40 ? ' Moderate Risk' :
             riskScore > 20 ? ' Low Risk' :
             ' Minimal Risk'}
          </p>
        </div>
      </div>
    </div>
  );
}
