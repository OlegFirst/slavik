'use client'

import { useState, useEffect } from 'react'

export default function Home() {
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // TODO: Fetch real data from API
    // For now, mock data
    setTimeout(() => {
      setDashboardData({
        critical_processes: 12,
        high_risks: 8,
        active_incidents: 2,
        iso_compliance: '87%'
      })
      setLoading(false)
    }, 1000)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">
            🧠 BCM AI Platform
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Intelligent Business Continuity Management powered by AI
          </p>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <StatCard
            title="Critical Processes"
            value={dashboardData.critical_processes}
            icon="📊"
            color="blue"
          />
          <StatCard
            title="High Risks"
            value={dashboardData.high_risks}
            icon="⚠️"
            color="yellow"
          />
          <StatCard
            title="Active Incidents"
            value={dashboardData.active_incidents}
            icon="🚨"
            color="red"
          />
          <StatCard
            title="ISO 22301 Compliance"
            value={dashboardData.iso_compliance}
            icon="✅"
            color="green"
          />
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <ActionButton
              title="Create BIA"
              description="Conduct Business Impact Analysis"
              icon="📋"
            />
            <ActionButton
              title="Assess Risk"
              description="Perform risk assessment"
              icon="🎯"
            />
            <ActionButton
              title="Run Simulation"
              description="Digital Twin disruption test"
              icon="🔮"
            />
          </div>
        </div>

        {/* AI Chat Preview */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">🤖 AI Assistant</h2>
          <div className="bg-gray-50 rounded-lg p-4 mb-4">
            <p className="text-gray-700">
              Hi! I'm your BCM AI assistant. I can help you with:
            </p>
            <ul className="mt-2 space-y-1 text-sm text-gray-600">
              <li>• Creating and managing BIA processes</li>
              <li>• Assessing and quantifying risks (FAIR methodology)</li>
              <li>• Simulating disruption scenarios with Digital Twin</li>
              <li>• Recommending optimal recovery strategies</li>
              <li>• Ensuring ISO 22301 compliance</li>
            </ul>
          </div>
          <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition">
            Start Conversation
          </button>
        </div>
      </div>
    </main>
  )
}

// Components
function StatCard({ title, value, icon, color }: any) {
  const colorClasses = {
    blue: 'bg-blue-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    green: 'bg-green-500',
  }

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className={`flex-shrink-0 rounded-md p-3 ${colorClasses[color as keyof typeof colorClasses]}`}>
            <span className="text-2xl">{icon}</span>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">
                {title}
              </dt>
              <dd className="text-2xl font-semibold text-gray-900">
                {value}
              </dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  )
}

function ActionButton({ title, description, icon }: any) {
  return (
    <button className="text-left p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition">
      <div className="text-2xl mb-2">{icon}</div>
      <h3 className="font-semibold text-gray-900">{title}</h3>
      <p className="text-sm text-gray-600 mt-1">{description}</p>
    </button>
  )
}
