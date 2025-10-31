// Gamification API Integration for Learning Community
import { odooClient } from '@/lib/api/odoo-client'
import { validateUserId, validatePoints, sanitizeHTML } from '@/lib/security/validation'

// Gamification API Types
export interface UserPoints {
  userId: string
  totalPoints: number
  weeklyPoints: number
  monthlyPoints: number
  rank: number
  level: string
  nextLevelPoints: number
}

export interface Achievement {
  id: string
  name: string
  description: string
  icon: string
  category: string
  points: number
  unlockedAt?: string
  progress?: number
  maxProgress?: number
}

export interface LeaderboardEntry {
  userId: string
  userName: string
  userAvatar?: string
  points: number
  rank: number
  achievements: number
  level: string
  department?: string
}

export interface LearningPath {
  id: string
  name: string
  description: string
  modules: LearningModule[]
  progress: number
  estimatedTime: number
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  prerequisites?: string[]
  rewards: {
    points: number
    achievements: string[]
  }
}

export interface LearningModule {
  id: string
  name: string
  type: 'course' | 'exercise' | 'assessment' | 'workshop'
  status: 'locked' | 'available' | 'in_progress' | 'completed'
  progress: number
  duration: number
  contentUrl?: string
}

export interface CommunityChallenge {
  id: string
  name: string
  description: string
  startDate: string
  endDate: string
  participants: number
  reward: {
    points: number
    badge?: string
  }
  leaderboard?: LeaderboardEntry[]
  userProgress?: number
}

// Gamification API Functions
export const gamificationAPI = {
  // Points System
  async getUserPoints(userId: string): Promise<UserPoints> {
    const validUserId = validateUserId(userId)
    return odooClient.get(`/bcm_gamification/points/${validUserId}`)
  },

  async awardPoints(userId: string, points: number, reason: string): Promise<void> {
    const validUserId = validateUserId(userId)
    const validPoints = validatePoints(points)
    await odooClient.post('/bcm_gamification/points/award', {
      user_id: validUserId,
      points: validPoints,
      reason: sanitizeHTML(reason)
    })
  },

  // Achievements
  async getUserAchievements(userId: string): Promise<Achievement[]> {
    const validUserId = validateUserId(userId)
    return odooClient.get(`/bcm_gamification/achievements/${validUserId}`)
  },

  async getAllAchievements(): Promise<Achievement[]> {
    return odooClient.get('/bcm_gamification/achievements')
  },

  async unlockAchievement(userId: string, achievementId: string): Promise<void> {
    const validUserId = validateUserId(userId)
    await odooClient.post('/bcm_gamification/achievements/unlock', {
      user_id: validUserId,
      achievement_id: achievementId
    })
  },

  // Leaderboard
  async getWeeklyLeaderboard(limit: number = 10): Promise<LeaderboardEntry[]> {
    return odooClient.get('/bcm_gamification/leaderboard', { period: 'weekly', limit })
  },

  async getMonthlyLeaderboard(limit: number = 10): Promise<LeaderboardEntry[]> {
    return odooClient.get('/bcm_gamification/leaderboard', { period: 'monthly', limit })
  },

  async getGlobalLeaderboard(limit: number = 100): Promise<LeaderboardEntry[]> {
    return odooClient.get('/bcm_gamification/leaderboard', { period: 'all-time', limit })
  },

  async getDepartmentLeaderboard(department: string, limit: number = 10): Promise<LeaderboardEntry[]> {
    return odooClient.get('/bcm_gamification/leaderboard', {
      period: 'weekly',
      limit,
      department: sanitizeHTML(department)
    })
  },

  // Learning Paths
  async getUserLearningPaths(userId: string): Promise<LearningPath[]> {
    const validUserId = validateUserId(userId)
    return odooClient.get('/bcm_gamification/learning_paths', { user_id: validUserId })
  },

  async getAllLearningPaths(): Promise<LearningPath[]> {
    return odooClient.get('/bcm_gamification/learning_paths')
  },

  async enrollInLearningPath(userId: string, pathId: string): Promise<void> {
    const validUserId = validateUserId(userId)
    await odooClient.post('/bcm_gamification/learning_paths/enroll', {
      user_id: validUserId,
      path_id: pathId
    })
  },

  async updateModuleProgress(
    userId: string,
    pathId: string,
    moduleId: string,
    progress: number
  ): Promise<void> {
    const validUserId = validateUserId(userId)
    const validProgress = Math.min(100, Math.max(0, progress))
    await odooClient.patch('/bcm_gamification/module_progress', {
      user_id: validUserId,
      path_id: pathId,
      module_id: moduleId,
      progress: validProgress
    })
  },

  // E-Learning Conversion
  async convertTemplateToLearning(templateId: string, config: any): Promise<string> {
    const response = await odooClient.post(`/bcm_gamification/convert_template/${templateId}`, config)
    return response.learningModuleId
  },

  async createExerciseFromScenario(scenarioId: string, config: any): Promise<string> {
    const response = await odooClient.post(`/bcm_gamification/create_exercise/${scenarioId}`, config)
    return response.exerciseId
  },

  // Community Challenges
  async getActiveChallenges(): Promise<CommunityChallenge[]> {
    return odooClient.get('/bcm_gamification/challenges/active')
  },

  async joinChallenge(userId: string, challengeId: string): Promise<void> {
    const validUserId = validateUserId(userId)
    await odooClient.post('/bcm_gamification/challenges/join', {
      user_id: validUserId,
      challenge_id: challengeId
    })
  },

  async submitChallengeProgress(
    userId: string,
    challengeId: string,
    progress: number
  ): Promise<void> {
    const validUserId = validateUserId(userId)
    const validProgress = Math.min(100, Math.max(0, progress))
    await odooClient.post('/bcm_gamification/challenges/progress', {
      user_id: validUserId,
      challenge_id: challengeId,
      progress: validProgress
    })
  },

  // Calendar Integration
  async scheduleTrainingReview(templateId: string, date: string, participants: string[]): Promise<void> {
    const validParticipants = participants.map(p => validateUserId(p))
    await odooClient.post('/bcm_gamification/schedule_review', {
      template_id: templateId,
      date,
      participants: validParticipants,
      type: 'training_review'
    })
  },

  async scheduleExercise(exerciseId: string, date: string, participants: string[]): Promise<void> {
    const validParticipants = participants.map(p => validateUserId(p))
    await odooClient.post('/bcm_gamification/schedule_exercise', {
      exercise_id: exerciseId,
      date,
      participants: validParticipants,
      type: 'bcm_exercise'
    })
  },

  // Analytics
  async getUserAnalytics(userId: string): Promise<any> {
    const validUserId = validateUserId(userId)
    return odooClient.get(`/bcm_gamification/analytics/user/${validUserId}`)
  },

  async getTeamAnalytics(teamId: string): Promise<any> {
    return odooClient.get(`/bcm_gamification/analytics/team/${teamId}`)
  }
}

// Production-ready error handling
export class GamificationAPIError extends Error {
  constructor(message: string, public statusCode?: number) {
    super(message)
    this.name = 'GamificationAPIError'
  }
}

// Export error handling for use in components