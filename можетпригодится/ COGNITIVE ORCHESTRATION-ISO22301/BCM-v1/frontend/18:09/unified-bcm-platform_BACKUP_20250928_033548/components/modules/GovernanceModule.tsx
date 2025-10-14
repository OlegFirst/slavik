'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { 
  Shield,
  FileText,
  Users,
  Target,
  AlertCircle,
  CheckCircle,
  Settings,
  Download,
  RefreshCw
} from 'lucide-react'

// Импорт Knowledge Base
import {
  ISO22301KnowledgeBase,
  useModuleRequirements,
  useComplianceAnalysis,
  MODULE_COMPLIANCE_MATRIX
} from '@/lib/knowledge-base-embedded'

export function GovernanceModule() {
  const [activeTab, setActiveTab] = useState<'overview' | 'policies' | 'procedures' | 'compliance'>('overview')

  // Получаем требования для модуля governance
  const { requirements } = useModuleRequirements('bcm_governance')
  const complianceAnalysis = useComplianceAnalysis('bcm_governance')

  // Mock данные для governance
  const { data: policies, isLoading: policiesLoading } = useQuery({
    queryKey: ['governance-policies'],
    queryFn: async () => [
      {
        id: '1',
        name: 'Business Continuity Policy',
        version: '2.1',
        status: 'active',
        lastReview: '2024-08-15',
        nextReview: '2025-08-15',
        owner: 'BC Manager',
        approvedBy: 'CEO',
        compliance: 'full'
      },
      {
        id: '2', 
        name: 'Risk Management Policy',
        version: '1.3',
        status: 'draft',
        lastReview: '2024-06-01',
        nextReview: '2025-06-01',
        owner: 'Risk Manager',
        approvedBy: 'Pending',
        compliance: 'partial'
      }
    ]
  })

  const { data: roles, isLoading: rolesLoading } = useQuery({
    queryKey: ['governance-roles'],
    queryFn: async () => [
      {
        id: '1',
        title: 'Business Continuity Manager',
        assignee: 'John Smith',
        department: 'Risk Management',
        responsibilities: ['BCMS oversight', 'Policy development', 'Training coordination'],
        status: 'active',
        lastUpdated: '2024-09-01'
      },
      {
        id: '2',
        title: 'Crisis Communication Lead',
        assignee: 'Sarah Johnson',
        department: 'Communications',
        responsibilities: ['Emergency communications', 'Stakeholder relations', 'Media management'],
        status: 'active',
        lastUpdated: '2024-08-20'
      }
    ]
  })

  const { data: metrics } = useQuery({
    queryKey: ['governance-metrics'],
    queryFn: async () => ({
      totalPolicies: 8,
      activePolicies: 6,
      overduePolicies: 2,
      assignedRoles: 12,
      complianceScore: complianceAnalysis.coverage
    })
  })

  if (policiesLoading || rolesLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-64"></div>
          <div className="grid grid-cols-4 gap-4">
            {[1,2,3,4].map(i => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Заголовок и соответствие ISO 22301 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Shield className="h-8 w-8 text-blue-600" />
            Governance & Leadership
          </h1>
          <p className="text-gray-600 mt-2">
            Управление политиками, процедурами и соответствием ISO 22301 (разделы 5.1, 5.2)
          </p>
          
          {/* Индикатор соответствия */}
          <div className="flex items-center gap-4 mt-3">
            <div className="flex items-center gap-2">
              <div className={cn(
                "w-3 h-3 rounded-full",
                complianceAnalysis.coverage >= 80 ? "bg-green-500" :
                complianceAnalysis.coverage >= 60 ? "bg-yellow-500" : "bg-red-500"
              )} />
              <span className="text-sm text-gray-600">
                ISO 22301 Соответствие: {Math.round(complianceAnalysis.coverage)}%
              </span>
            </div>
            <div className="text-sm text-gray-500">
              {requirements.filter(req => req.complianceLevel === 'full').length}/{requirements.length} требований выполнено
            </div>
          </div>
        </div>
        <div className="flex gap-3">
          <Button variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Обновить
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Отчет
          </Button>
          <Button>
            <FileText className="h-4 w-4 mr-2" />
            Новая политика
          </Button>
        </div>
      </div>

      {/* Метрики */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard 
          title="Всего политик"
          value={metrics?.totalPolicies || 0}
          icon={<FileText className="h-6 w-6" />}
          color="blue"
        />
        <MetricCard 
          title="Активные политики"
          value={metrics?.activePolicies || 0}
          icon={<CheckCircle className="h-6 w-6" />}
          color="green"
        />
        <MetricCard 
          title="Просроченные"
          value={metrics?.overduePolicies || 0}
          icon={<AlertCircle className="h-6 w-6" />}
          color="red"
        />
        <MetricCard 
          title="Назначенные роли"
          value={metrics?.assignedRoles || 0}
          icon={<Users className="h-6 w-6" />}
          color="purple"
        />
      </div>

      {/* Табы */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'overview', label: 'Обзор', icon: Target },
            { id: 'policies', label: 'Политики', icon: FileText },
            { id: 'procedures', label: 'Процедуры', icon: Settings },
            { id: 'compliance', label: 'Соответствие', icon: Shield }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={cn(
                "flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm",
                activeTab === tab.id
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              )}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Контент табов */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Последние политики */}
          <div className="bg-white rounded-lg border shadow-sm">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold">Последние политики</h3>
            </div>
            <div className="p-6 space-y-4">
              {policies?.slice(0, 3).map(policy => (
                <div key={policy.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">{policy.name}</div>
                    <div className="text-sm text-gray-500">Версия {policy.version} • {policy.owner}</div>
                  </div>
                  <div className={cn(
                    "px-2 py-1 text-xs font-medium rounded-full",
                    policy.status === 'active' ? "bg-green-100 text-green-800" :
                    policy.status === 'draft' ? "bg-yellow-100 text-yellow-800" :
                    "bg-gray-100 text-gray-800"
                  )}>
                    {policy.status}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Ключевые роли */}
          <div className="bg-white rounded-lg border shadow-sm">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold">Ключевые роли</h3>
            </div>
            <div className="p-6 space-y-4">
              {roles?.slice(0, 3).map(role => (
                <div key={role.id} className="flex items-start gap-3 p-3 border rounded-lg">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <Users className="h-5 w-5 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <div className="font-medium">{role.title}</div>
                    <div className="text-sm text-gray-600">{role.assignee} • {role.department}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {role.responsibilities.slice(0, 2).join(', ')}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'policies' && (
        <div className="bg-white rounded-lg border shadow-sm">
          <div className="p-6 border-b">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Политики управления</h3>
              <Button>
                <FileText className="h-4 w-4 mr-2" />
                Создать политику
              </Button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b">
                <tr>
                  <th className="text-left py-3 px-6 font-medium text-gray-500">Название</th>
                  <th className="text-left py-3 px-6 font-medium text-gray-500">Версия</th>
                  <th className="text-left py-3 px-6 font-medium text-gray-500">Статус</th>
                  <th className="text-left py-3 px-6 font-medium text-gray-500">Владелец</th>
                  <th className="text-left py-3 px-6 font-medium text-gray-500">Следующий пересмотр</th>
                  <th className="text-left py-3 px-6 font-medium text-gray-500">Соответствие</th>
                </tr>
              </thead>
              <tbody>
                {policies?.map(policy => (
                  <tr key={policy.id} className="border-b hover:bg-gray-50">
                    <td className="py-4 px-6">
                      <div className="font-medium text-gray-900">{policy.name}</div>
                    </td>
                    <td className="py-4 px-6 text-gray-500">{policy.version}</td>
                    <td className="py-4 px-6">
                      <span className={cn(
                        "inline-flex px-2 py-1 text-xs font-medium rounded-full",
                        policy.status === 'active' ? "bg-green-100 text-green-800" :
                        policy.status === 'draft' ? "bg-yellow-100 text-yellow-800" :
                        "bg-gray-100 text-gray-800"
                      )}>
                        {policy.status}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-gray-500">{policy.owner}</td>
                    <td className="py-4 px-6 text-gray-500">{policy.nextReview}</td>
                    <td className="py-4 px-6">
                      <span className={cn(
                        "inline-flex px-2 py-1 text-xs font-medium rounded-full",
                        policy.compliance === 'full' ? "bg-green-100 text-green-800" :
                        policy.compliance === 'partial' ? "bg-yellow-100 text-yellow-800" :
                        "bg-red-100 text-red-800"
                      )}>
                        {policy.compliance === 'full' ? 'Полное' :
                         policy.compliance === 'partial' ? 'Частичное' : 'Отсутствует'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'compliance' && (
        <div className="space-y-6">
          {/* Соответствие ISO 22301 */}
          <div className="bg-white rounded-lg border shadow-sm">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Соответствие ISO 22301 - Раздел 5 (Leadership)
              </h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {Math.round(complianceAnalysis.coverage)}%
                  </div>
                  <div className="text-sm text-gray-500">Общее соответствие</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {requirements.filter(req => req.complianceLevel === 'full').length}
                  </div>
                  <div className="text-sm text-gray-500">Выполнено требований</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">
                    {complianceAnalysis.missingRequirements.length}
                  </div>
                  <div className="text-sm text-gray-500">Невыполненных</div>
                </div>
              </div>

              {/* Список требований */}
              <div className="space-y-4">
                <h4 className="font-medium">Требования стандарта:</h4>
                {requirements.map(req => (
                  <div key={req.id} className={cn(
                    "p-4 border rounded-lg",
                    req.complianceLevel === 'full' ? "border-green-200 bg-green-50" :
                    req.complianceLevel === 'partial' ? "border-yellow-200 bg-yellow-50" :
                    "border-red-200 bg-red-50"
                  )}>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <div className="font-medium text-gray-900">
                            {req.clause} - {req.title}
                          </div>
                          <div className={cn(
                            "w-3 h-3 rounded-full",
                            req.complianceLevel === 'full' ? "bg-green-500" :
                            req.complianceLevel === 'partial' ? "bg-yellow-500" :
                            "bg-red-500"
                          )} />
                        </div>
                        <div className="text-sm text-gray-600 mt-2">{req.description}</div>
                        
                        {/* Необходимые доказательства */}
                        <div className="mt-3">
                          <div className="text-xs font-medium text-gray-700 mb-2">
                            Необходимые доказательства:
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {req.evidence.map((evidence, index) => (
                              <span key={index} className="inline-flex px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                                {evidence}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                      <div className={cn(
                        "ml-4 px-3 py-1 text-xs font-medium rounded-full",
                        req.riskLevel === 'critical' ? "bg-red-100 text-red-800" :
                        req.riskLevel === 'high' ? "bg-orange-100 text-orange-800" :
                        req.riskLevel === 'medium' ? "bg-yellow-100 text-yellow-800" :
                        "bg-gray-100 text-gray-800"
                      )}>
                        {req.riskLevel.charAt(0).toUpperCase() + req.riskLevel.slice(1)} Risk
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Компонент карточки метрики
interface MetricCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  color: 'blue' | 'green' | 'red' | 'purple'
}

function MetricCard({ title, value, icon, color }: MetricCardProps) {
  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-center justify-between">
        <div className={cn(
          "w-12 h-12 rounded-lg flex items-center justify-center",
          color === 'blue' && "bg-blue-50 text-blue-600",
          color === 'green' && "bg-green-50 text-green-600",
          color === 'red' && "bg-red-50 text-red-600",
          color === 'purple' && "bg-purple-50 text-purple-600"
        )}>
          {icon}
        </div>
      </div>
      <div className="mt-4">
        <div className="text-2xl font-bold text-gray-900">{value}</div>
        <div className="text-sm text-gray-500">{title}</div>
      </div>
    </div>
  )
}