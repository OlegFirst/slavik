'use client'

import { useState } from 'react'
import { dbIntegrationTest } from '@/lib/database/test-integration'

interface TestResults {
  passed: number
  failed: number
  results: Record<string, boolean>
  errors: Record<string, string>
  overall: 'success' | 'failure'
}

export default function DatabaseIntegrationTestPage() {
  const [testResults, setTestResults] = useState<TestResults | null>(null)
  const [healthResults, setHealthResults] = useState<any[]>([])
  const [performanceResults, setPerformanceResults] = useState<Record<string, number>>({})
  const [isRunning, setIsRunning] = useState(false)
  const [currentTest, setCurrentTest] = useState('')

  const runIntegrationTests = async () => {
    setIsRunning(true)
    setCurrentTest('Запуск интеграционных тестов...')

    try {
      // Run main integration tests
      setCurrentTest('Тестирование подключений к базам данных...')
      const results = await dbIntegrationTest.runAllTests()
      setTestResults(results)

      // Run health checks
      setCurrentTest('Проверка состояния всех баз данных...')
      const health = await dbIntegrationTest.checkAllDatabaseHealth()
      setHealthResults(health)

      // Run performance tests
      setCurrentTest('Запуск тестов производительности...')
      const performance = await dbIntegrationTest.performanceTest()
      setPerformanceResults(performance)

      setCurrentTest('Все тесты завершены!')
    } catch (error) {
      console.error('Test execution failed:', error)
      setCurrentTest('Ошибка при выполнении тестов')
    } finally {
      setIsRunning(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return '✅'
      case 'degraded': return '⚠️'
      case 'offline': return '❌'
      default: return '❓'
    }
  }

  const getOverallStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-600 bg-green-50 border-green-200'
      case 'failure': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Database Integration Test Dashboard
          </h1>
          <p className="text-gray-600">
            Проверка интеграции всех баз данных: PostgreSQL, Supabase, Redis, MongoDB, RabbitMQ
          </p>
        </div>

        {/* Test Controls */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold mb-2">Управление тестами</h2>
              {isRunning && (
                <p className="text-blue-600 text-sm">{currentTest}</p>
              )}
            </div>
            <button
              onClick={runIntegrationTests}
              disabled={isRunning}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isRunning ? 'Выполняются тесты...' : 'Запустить все тесты'}
            </button>
          </div>
        </div>

        {/* Test Results Summary */}
        {testResults && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className={`p-6 rounded-lg border-2 ${getOverallStatusColor(testResults.overall)}`}>
              <h3 className="text-lg font-semibold mb-2">Общий результат</h3>
              <p className="text-2xl font-bold">
                {testResults.overall === 'success' ? 'УСПЕШНО' : 'ЕСТЬ ОШИБКИ'}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-semibold mb-2 text-green-600">Пройдено</h3>
              <p className="text-3xl font-bold text-green-600">{testResults.passed}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-semibold mb-2 text-red-600">Ошибок</h3>
              <p className="text-3xl font-bold text-red-600">{testResults.failed}</p>
            </div>
          </div>
        )}

        {/* Detailed Test Results */}
        {testResults && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Детальные результаты тестов</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(testResults.results).map(([testName, passed]) => (
                <div key={testName} className="flex items-center justify-between p-3 border rounded">
                  <span className="font-medium">{testName.replace(/_/g, ' ')}</span>
                  <span className={`px-2 py-1 rounded text-sm ${
                    passed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {passed ? '✅ УСПЕШНО' : '❌ ОШИБКА'}
                  </span>
                </div>
              ))}
            </div>

            {Object.keys(testResults.errors).length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-3 text-red-600">Ошибки</h3>
                <div className="space-y-2">
                  {Object.entries(testResults.errors).map(([errorSource, errorMessage]) => (
                    <div key={errorSource} className="p-3 bg-red-50 border border-red-200 rounded">
                      <div className="font-semibold text-red-800">{errorSource}</div>
                      <div className="text-red-600 text-sm">{errorMessage}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Database Health Status */}
        {healthResults.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Состояние баз данных</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {healthResults.map((health, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-semibold">{health.database}</span>
                    <span className="text-2xl">{getStatusIcon(health.status)}</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    <p>Статус: <span className={`font-medium ${
                      health.status === 'online' ? 'text-green-600' :
                      health.status === 'degraded' ? 'text-yellow-600' : 'text-red-600'
                    }`}>{health.status}</span></p>
                    {health.responseTime && (
                      <p>Время ответа: {health.responseTime}ms</p>
                    )}
                    <p>Проверено: {new Date(health.lastChecked).toLocaleTimeString()}</p>
                  </div>
                  {health.error && (
                    <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-600">
                      {health.error}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Performance Results */}
        {Object.keys(performanceResults).length > 0 && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">Результаты тестов производительности</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(performanceResults).map(([testName, duration]) => (
                <div key={testName} className="flex items-center justify-between p-3 border rounded">
                  <span className="font-medium">{testName}</span>
                  <span className={`px-2 py-1 rounded text-sm ${
                    duration === -1 ? 'bg-red-100 text-red-800' :
                    duration < 1000 ? 'bg-green-100 text-green-800' :
                    duration < 3000 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {duration === -1 ? 'ОШИБКА' : `${duration}ms`}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}