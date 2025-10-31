'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  Trophy,
  Star,
  TrendingUp,
  Award,
  Target,
  Users,
  Calendar,
  ChevronUp,
  ChevronDown,
  Medal,
  Zap,
  BookOpen,
  CheckCircle2,
  Clock,
  BarChart3
} from 'lucide-react'
import { gamificationAPI, GamificationAPIError } from '@/lib/api/gamification'
import { useAuth, getCurrentUser } from '@/hooks/useAuth'

export function GamificationDashboard() {
  const { isAuthenticated, user } = useAuth()
  const [userPoints, setUserPoints] = useState<any>(null)
  const [achievements, setAchievements] = useState<any[]>([])
  const [weeklyLeaderboard, setWeeklyLeaderboard] = useState<any[]>([])
  const [selectedPeriod, setSelectedPeriod] = useState<'weekly' | 'monthly' | 'all-time'>('weekly')
  const [loading, setLoading] = useState(false)

  // Fetch gamification data
  useEffect(() => {
    const fetchData = async () => {
      if (!isAuthenticated || !user) {
        setLoading(false)
        return
      }

      setLoading(true)
      try {
        // Real API calls to backend
        const [points, userAchievements, leaderboard] = await Promise.all([
          gamificationAPI.getUserPoints(user.id),
          gamificationAPI.getUserAchievements(user.id),
          gamificationAPI.getWeeklyLeaderboard(10)
        ])

        setUserPoints(points)
        setAchievements(userAchievements)
        setWeeklyLeaderboard(leaderboard)
      } catch (error) {
        console.error('Failed to fetch gamification data:', error)
        // Show user-friendly error message
        if (error instanceof GamificationAPIError) {
          console.error('Gamification API Error:', error.message)
        }
      }
      setLoading(false)
    }

    fetchData()
  }, [isAuthenticated, user, selectedPeriod])

  const getLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'expert': return 'text-purple-600 bg-purple-100'
      case 'advanced': return 'text-blue-600 bg-blue-100'
      case 'intermediate': return 'text-green-600 bg-green-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getRankChange = (rank: number) => {
    const change = Math.floor(Math.random() * 5) - 2 // Mock rank change
    if (change > 0) return { icon: ChevronUp, color: 'text-green-500', text: `+${change}` }
    if (change < 0) return { icon: ChevronDown, color: 'text-red-500', text: `${change}` }
    return { icon: null, color: 'text-gray-400', text: '-' }
  }

  // Authentication guard
  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Authentication Required</h3>
          <p className="text-gray-600">Please log in to view your gamification dashboard.</p>
        </div>
      </div>
    )
  }

  // Loading state
  if (loading || !userPoints) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* User Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Trophy className="h-4 w-4 text-yellow-500" />
              Total Points
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{userPoints?.totalPoints?.toLocaleString() || '0'}</div>
            <p className="text-xs text-muted-foreground">
              Rank #{userPoints?.rank || '-'} globally
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Zap className="h-4 w-4 text-blue-500" />
              Current Level
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Badge className={getLevelColor(userPoints?.level || 'beginner')}>
                {userPoints?.level || 'Beginner'}
              </Badge>
            </div>
            <Progress
              value={userPoints?.totalPoints ? (userPoints.totalPoints % 1000) / 10 : 0}
              className="mt-2 h-1"
            />
            <p className="text-xs text-muted-foreground mt-1">
              {userPoints?.nextLevelPoints || 0} pts to next level
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-500" />
              This Week
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">+{userPoints.weeklyPoints}</div>
            <p className="text-xs text-muted-foreground">
              {Math.round((userPoints.weeklyPoints / userPoints.monthlyPoints) * 100)}% of monthly goal
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Award className="h-4 w-4 text-purple-500" />
              Achievements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {achievements.filter(a => a.unlockedAt).length}/{achievements.length}
            </div>
            <p className="text-xs text-muted-foreground">
              {Math.round((achievements.filter(a => a.unlockedAt).length / achievements.length) * 100)}% unlocked
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Leaderboard */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Medal className="h-5 w-5" />
                Leaderboard
              </CardTitle>
              <div className="flex gap-2">
                <Button
                  variant={selectedPeriod === 'weekly' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedPeriod('weekly')}
                >
                  Weekly
                </Button>
                <Button
                  variant={selectedPeriod === 'monthly' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedPeriod('monthly')}
                >
                  Monthly
                </Button>
                <Button
                  variant={selectedPeriod === 'all-time' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedPeriod('all-time')}
                >
                  All Time
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {weeklyLeaderboard.map((entry, index) => {
                const rankChange = getRankChange(entry.rank)
                return (
                  <div
                    key={entry.userId}
                    className={`flex items-center justify-between p-3 rounded-lg ${
                      index === 0 ? 'bg-yellow-50 border border-yellow-200' :
                      index === 1 ? 'bg-gray-50 border border-gray-200' :
                      index === 2 ? 'bg-orange-50 border border-orange-200' :
                      'hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-8 h-8">
                        {index === 0 ? <Trophy className="h-5 w-5 text-yellow-500" /> :
                         index === 1 ? <Medal className="h-5 w-5 text-gray-400" /> :
                         index === 2 ? <Medal className="h-5 w-5 text-orange-400" /> :
                         <span className="font-bold text-gray-500">#{entry.rank}</span>}
                      </div>
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={entry.userAvatar} />
                        <AvatarFallback>
                          {entry.userName.split(' ').map(n => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium text-sm">{entry.userName}</p>
                        <p className="text-xs text-muted-foreground">{entry.department}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="font-bold">{entry.points.toLocaleString()}</p>
                        <div className="flex items-center gap-1">
                          {rankChange.icon && (
                            <rankChange.icon className={`h-3 w-3 ${rankChange.color}`} />
                          )}
                          <span className={`text-xs ${rankChange.color}`}>
                            {rankChange.text}
                          </span>
                        </div>
                      </div>
                      <Badge className={getLevelColor(entry.level)} variant="outline">
                        {entry.level}
                      </Badge>
                    </div>
                  </div>
                )
              })}
            </div>
            <Button variant="outline" className="w-full mt-4">
              View Full Leaderboard
            </Button>
          </CardContent>
        </Card>

        {/* Recent Achievements */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="h-5 w-5" />
              Achievements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="recent" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="recent">Recent</TabsTrigger>
                <TabsTrigger value="progress">In Progress</TabsTrigger>
              </TabsList>

              <TabsContent value="recent" className="space-y-3 mt-4">
                {achievements
                  .filter(a => a.unlockedAt)
                  .slice(0, 3)
                  .map(achievement => (
                    <div key={achievement.id} className="flex items-start gap-3 p-3 rounded-lg bg-green-50">
                      <div className="text-2xl">{achievement.icon}</div>
                      <div className="flex-1">
                        <p className="font-medium text-sm">{achievement.name}</p>
                        <p className="text-xs text-muted-foreground">{achievement.description}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="secondary" className="text-xs">
                            +{achievement.points} pts
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {new Date(achievement.unlockedAt!).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                    </div>
                  ))}
              </TabsContent>

              <TabsContent value="progress" className="space-y-3 mt-4">
                {achievements
                  .filter(a => !a.unlockedAt && a.progress)
                  .map(achievement => (
                    <div key={achievement.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50">
                      <div className="text-2xl opacity-50">{achievement.icon}</div>
                      <div className="flex-1">
                        <p className="font-medium text-sm">{achievement.name}</p>
                        <p className="text-xs text-muted-foreground">{achievement.description}</p>
                        <div className="mt-2">
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span>Progress</span>
                            <span>{achievement.progress}/{achievement.maxProgress}</span>
                          </div>
                          <Progress
                            value={(achievement.progress! / achievement.maxProgress!) * 100}
                            className="h-1"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
              </TabsContent>
            </Tabs>

            <Button variant="outline" className="w-full mt-4">
              View All Achievements
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Active Challenges */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Active Challenges
            </CardTitle>
            <Button size="sm">Join Challenge</Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <Badge variant="secondary">Weekly</Badge>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </div>
              <h4 className="font-medium mb-1">Knowledge Sprint</h4>
              <p className="text-sm text-muted-foreground mb-3">
                Complete 5 learning modules this week
              </p>
              <Progress value={60} className="mb-2" />
              <div className="flex items-center justify-between text-xs">
                <span>3/5 completed</span>
                <span className="text-muted-foreground">2 days left</span>
              </div>
            </div>

            <div className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <Badge variant="secondary">Monthly</Badge>
                <Users className="h-4 w-4 text-muted-foreground" />
              </div>
              <h4 className="font-medium mb-1">Team Excellence</h4>
              <p className="text-sm text-muted-foreground mb-3">
                Achieve 10,000 team points together
              </p>
              <Progress value={75} className="mb-2" />
              <div className="flex items-center justify-between text-xs">
                <span>7,500/10,000 pts</span>
                <span className="text-muted-foreground">156 participants</span>
              </div>
            </div>

            <div className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <Badge variant="secondary">Special</Badge>
                <Award className="h-4 w-4 text-yellow-500" />
              </div>
              <h4 className="font-medium mb-1">BCM Master</h4>
              <p className="text-sm text-muted-foreground mb-3">
                Complete the BCM certification path
              </p>
              <Progress value={40} className="mb-2" />
              <div className="flex items-center justify-between text-xs">
                <span>4/10 modules</span>
                <span className="text-muted-foreground">500 pts reward</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}