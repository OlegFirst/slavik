'use client'

import React from 'react'
import { useSpecialist, useProjects, useProposals } from '@/hooks/api'
import { useAuthStore } from '@/store/auth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import {
  Star,
  Briefcase,
  FileText,
  DollarSign,
  TrendingUp,
  Users,
  Clock,
  CheckCircle
} from 'lucide-react'

export function SpecialistDashboard() {
  const { user } = useAuthStore()
  const { data: specialistData } = useSpecialist(user?.id || '')
  const { data: projects } = useProjects({ specialistId: user?.id, status: 'active' })
  const { data: proposals } = useProposals({ specialistId: user?.id })

  const specialist = specialistData?.data
  const activeProjects = projects?.data?.items || []
  const pendingProposals = proposals?.data?.items?.filter((p: any) => p.state === 'submitted') || []

  if (!specialist) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Добро пожаловать, {specialist.name}!</h1>
            <p className="text-blue-100 mt-1">{specialist.title}</p>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-2">
              <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
              <span className="text-xl font-bold">{specialist.rating}</span>
            </div>
            <p className="text-blue-100 text-sm">{specialist.reviewCount} отзывов</p>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Активные проекты</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeProjects.length}</div>
            <p className="text-xs text-muted-foreground">
              +2 за последний месяц
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ожидающие предложения</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pendingProposals.length}</div>
            <p className="text-xs text-muted-foreground">
              Требуют внимания
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Доход за месяц</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₽125,000</div>
            <p className="text-xs text-muted-foreground">
              +15% от предыдущего
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Завершенность профиля</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{specialist.profileCompletion}%</div>
            <Progress value={specialist.profileCompletion} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Projects */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Briefcase className="h-5 w-5" />
              <span>Активные проекты</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {activeProjects.slice(0, 3).map((project: any) => (
                <div key={project.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex-1">
                    <h3 className="font-medium">{project.name}</h3>
                    <p className="text-sm text-gray-500">{project.clientName}</p>
                    <Progress value={project.progress} className="mt-2 w-32" />
                  </div>
                  <div className="text-right">
                    <Badge variant={
                      project.state === 'in_progress' ? 'default' :
                      project.state === 'on_hold' ? 'secondary' :
                      'outline'
                    }>
                      {project.state === 'in_progress' ? 'В работе' :
                       project.state === 'on_hold' ? 'Приостановлен' :
                       'Новый'}
                    </Badge>
                    <p className="text-sm text-gray-500 mt-1">
                      ₽{project.budget.toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
              {activeProjects.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Briefcase className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                  <p>У вас пока нет активных проектов</p>
                  <Button className="mt-3" variant="outline">
                    Найти проекты
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Быстрые действия</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start" variant="outline">
              <FileText className="mr-2 h-4 w-4" />
              Просмотреть новые запросы
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Users className="mr-2 h-4 w-4" />
              Обновить профиль
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Star className="mr-2 h-4 w-4" />
              Посмотреть отзывы
            </Button>
            <Button className="w-full justify-start" variant="outline">
              <Clock className="mr-2 h-4 w-4" />
              Добавить время работы
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Недавняя активность</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm">Завершена веха "Анализ рисков" в проекте "BCM для банка"</p>
                <p className="text-xs text-gray-500">2 часа назад</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <FileText className="h-5 w-5 text-blue-500 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm">Новое предложение отправлено на проект "Аудит BCM"</p>
                <p className="text-xs text-gray-500">5 часов назад</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Star className="h-5 w-5 text-yellow-500 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm">Получен новый отзыв 5 звезд от клиента "ООО Техком"</p>
                <p className="text-xs text-gray-500">1 день назад</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}