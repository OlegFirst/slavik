// Monte Carlo Risk Simulation Service
// Интеграция с BCM Exercise Simulators для вероятностного моделирования рисков

import { Risk } from './risk-management-api'

export interface MonteCarloParameters {
  simulations: number // Количество симуляций (обычно 10000)
  confidenceLevel: number // Уровень доверия (например, 0.95 для 95%)
  timeHorizon: number // Временной горизонт в месяцах
  correlationMatrix?: number[][] // Матрица корреляций между рисками
}

export interface SimulationResult {
  riskId: string
  simulations: number
  statistics: {
    mean: number
    median: number
    standardDeviation: number
    min: number
    max: number
    percentiles: {
      p5: number
      p25: number
      p50: number
      p75: number
      p95: number
      p99: number
    }
  }
  distribution: Array<{
    value: number
    frequency: number
    probability: number
  }>
  valueAtRisk: number // VaR at confidence level
  conditionalValueAtRisk: number // CVaR/Expected Shortfall
  probabilityOfOccurrence: number
}

export interface AggregatedSimulationResult {
  totalSimulations: number
  timeHorizon: number
  aggregatedLoss: {
    mean: number
    median: number
    standardDeviation: number
    percentiles: {
      p5: number
      p25: number
      p50: number
      p75: number
      p95: number
      p99: number
    }
  }
  topRiskContributors: Array<{
    riskId: string
    riskTitle: string
    contribution: number // процент вклада в общий риск
  }>
  correlationImpact: number // влияние корреляций на общий риск
  confidence: {
    level: number
    lowerBound: number
    upperBound: number
  }
  recommendations: string[]
}

class MonteCarloSimulationService {

  // Запуск симуляции для одного риска
  async runSimulation(
    risk: Risk,
    parameters: MonteCarloParameters
  ): Promise<SimulationResult> {
    const results: number[] = []

    for (let i = 0; i < parameters.simulations; i++) {
      // Генерируем случайные значения для probability и impact
      // используя нормальное распределение вокруг текущих значений
      const probSample = this.sampleFromDistribution(
        risk.probability,
        risk.probability * 0.2 // 20% стандартное отклонение
      )

      const impactSample = this.sampleFromDistribution(
        risk.impact,
        risk.impact * 0.25 // 25% стандартное отклонение
      )

      // Рассчитываем риск для этой симуляции
      const riskScore = (probSample * impactSample) / 10
      results.push(riskScore)
    }

    // Сортируем для расчета перцентилей
    results.sort((a, b) => a - b)

    // Расчет статистик
    const mean = results.reduce((sum, val) => sum + val, 0) / results.length
    const median = results[Math.floor(results.length / 2)]
    const variance = results.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / results.length
    const stdDev = Math.sqrt(variance)

    // Расчет перцентилей
    const percentiles = {
      p5: results[Math.floor(results.length * 0.05)],
      p25: results[Math.floor(results.length * 0.25)],
      p50: median,
      p75: results[Math.floor(results.length * 0.75)],
      p95: results[Math.floor(results.length * 0.95)],
      p99: results[Math.floor(results.length * 0.99)]
    }

    // Расчет VaR и CVaR
    const varIndex = Math.floor(results.length * (1 - parameters.confidenceLevel))
    const valueAtRisk = results[results.length - varIndex - 1]
    const tailResults = results.slice(results.length - varIndex)
    const conditionalValueAtRisk = tailResults.reduce((sum, val) => sum + val, 0) / tailResults.length

    // Создание распределения для гистограммы
    const distribution = this.createDistribution(results)

    // Расчет вероятности наступления (score > threshold)
    const threshold = 5 // Средний уровень риска
    const probabilityOfOccurrence = results.filter(r => r >= threshold).length / results.length

    return {
      riskId: risk.id,
      simulations: parameters.simulations,
      statistics: {
        mean,
        median,
        standardDeviation: stdDev,
        min: results[0],
        max: results[results.length - 1],
        percentiles
      },
      distribution,
      valueAtRisk,
      conditionalValueAtRisk,
      probabilityOfOccurrence
    }
  }

  // Запуск симуляции для портфеля рисков
  async runPortfolioSimulation(
    risks: Risk[],
    parameters: MonteCarloParameters
  ): Promise<AggregatedSimulationResult> {
    const portfolioResults: number[] = []
    const riskContributions = new Map<string, number[]>()

    // Инициализация для отслеживания вкладов
    risks.forEach(risk => {
      riskContributions.set(risk.id, [])
    })

    // Генерация корреляционной матрицы если не предоставлена
    const correlationMatrix = parameters.correlationMatrix ||
      this.generateDefaultCorrelationMatrix(risks.length)

    for (let sim = 0; sim < parameters.simulations; sim++) {
      let totalLoss = 0
      const samples: number[] = []

      // Генерируем коррелированные случайные числа
      const correlatedRandoms = this.generateCorrelatedRandomNumbers(
        risks.length,
        correlationMatrix
      )

      risks.forEach((risk, index) => {
        // Используем коррелированные случайные числа
        const probSample = this.sampleFromDistributionWithCorrelation(
          risk.probability,
          risk.probability * 0.2,
          correlatedRandoms[index]
        )

        const impactSample = this.sampleFromDistributionWithCorrelation(
          risk.impact,
          risk.impact * 0.25,
          correlatedRandoms[index]
        )

        const riskScore = (probSample * impactSample) / 10
        samples.push(riskScore)
        totalLoss += riskScore

        // Отслеживаем вклад каждого риска
        const contributions = riskContributions.get(risk.id) || []
        contributions.push(riskScore)
        riskContributions.set(risk.id, contributions)
      })

      portfolioResults.push(totalLoss)
    }

    // Сортировка для статистики
    portfolioResults.sort((a, b) => a - b)

    // Расчет агрегированных статистик
    const mean = portfolioResults.reduce((sum, val) => sum + val, 0) / portfolioResults.length
    const median = portfolioResults[Math.floor(portfolioResults.length / 2)]
    const variance = portfolioResults.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / portfolioResults.length
    const stdDev = Math.sqrt(variance)

    // Расчет вкладов рисков
    const topRiskContributors = risks.map(risk => {
      const contributions = riskContributions.get(risk.id) || []
      const avgContribution = contributions.reduce((sum, val) => sum + val, 0) / contributions.length
      return {
        riskId: risk.id,
        riskTitle: risk.title,
        contribution: (avgContribution / mean) * 100
      }
    }).sort((a, b) => b.contribution - a.contribution)

    // Расчет влияния корреляций
    const independentSum = risks.reduce((sum, risk) => sum + risk.riskScore, 0)
    const correlationImpact = ((mean - independentSum) / independentSum) * 100

    // Доверительный интервал
    const zScore = 1.96 // для 95% доверия
    const marginOfError = zScore * (stdDev / Math.sqrt(parameters.simulations))

    // Генерация рекомендаций на основе результатов
    const recommendations = this.generateRecommendations({
      mean,
      stdDev,
      topRiskContributors,
      correlationImpact
    })

    return {
      totalSimulations: parameters.simulations,
      timeHorizon: parameters.timeHorizon,
      aggregatedLoss: {
        mean,
        median,
        standardDeviation: stdDev,
        percentiles: {
          p5: portfolioResults[Math.floor(portfolioResults.length * 0.05)],
          p25: portfolioResults[Math.floor(portfolioResults.length * 0.25)],
          p50: median,
          p75: portfolioResults[Math.floor(portfolioResults.length * 0.75)],
          p95: portfolioResults[Math.floor(portfolioResults.length * 0.95)],
          p99: portfolioResults[Math.floor(portfolioResults.length * 0.99)]
        }
      },
      topRiskContributors: topRiskContributors.slice(0, 5),
      correlationImpact,
      confidence: {
        level: parameters.confidenceLevel,
        lowerBound: mean - marginOfError,
        upperBound: mean + marginOfError
      },
      recommendations
    }
  }

  // Вспомогательные методы

  private sampleFromDistribution(mean: number, stdDev: number): number {
    // Box-Muller transform для генерации нормального распределения
    const u1 = Math.random()
    const u2 = Math.random()
    const z0 = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2)

    // Ограничиваем значения в пределах [1, 10]
    const sample = Math.max(1, Math.min(10, mean + z0 * stdDev))
    return sample
  }

  private sampleFromDistributionWithCorrelation(
    mean: number,
    stdDev: number,
    correlatedRandom: number
  ): number {
    // Используем предоставленное коррелированное случайное число
    const sample = Math.max(1, Math.min(10, mean + correlatedRandom * stdDev))
    return sample
  }

  private generateCorrelatedRandomNumbers(
    n: number,
    correlationMatrix: number[][]
  ): number[] {
    // Генерируем независимые нормальные случайные числа
    const independent: number[] = []
    for (let i = 0; i < n; i++) {
      const u1 = Math.random()
      const u2 = Math.random()
      independent.push(Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2))
    }

    // Применяем корреляционную матрицу (упрощенный метод)
    const correlated: number[] = []
    for (let i = 0; i < n; i++) {
      let value = 0
      for (let j = 0; j < n; j++) {
        value += correlationMatrix[i][j] * independent[j]
      }
      correlated.push(value)
    }

    return correlated
  }

  private generateDefaultCorrelationMatrix(n: number): number[][] {
    // Генерируем матрицу с небольшими корреляциями
    const matrix: number[][] = []
    for (let i = 0; i < n; i++) {
      matrix[i] = []
      for (let j = 0; j < n; j++) {
        if (i === j) {
          matrix[i][j] = 1 // Диагональ
        } else {
          matrix[i][j] = 0.1 + Math.random() * 0.3 // Слабые корреляции 0.1-0.4
        }
      }
    }
    return matrix
  }

  private createDistribution(values: number[]): Array<{
    value: number
    frequency: number
    probability: number
  }> {
    // Создаем гистограмму с 20 бинами
    const bins = 20
    const min = Math.min(...values)
    const max = Math.max(...values)
    const binWidth = (max - min) / bins

    const distribution: Array<{
      value: number
      frequency: number
      probability: number
    }> = []

    for (let i = 0; i < bins; i++) {
      const binStart = min + i * binWidth
      const binEnd = binStart + binWidth
      const binCenter = (binStart + binEnd) / 2

      const frequency = values.filter(v => v >= binStart && v < binEnd).length

      distribution.push({
        value: Number(binCenter.toFixed(2)),
        frequency,
        probability: frequency / values.length
      })
    }

    return distribution
  }

  private generateRecommendations(stats: {
    mean: number
    stdDev: number
    topRiskContributors: Array<{ riskTitle: string; contribution: number }>
    correlationImpact: number
  }): string[] {
    const recommendations: string[] = []

    // Рекомендации на основе среднего риска
    if (stats.mean > 7) {
      recommendations.push('Critical risk level detected. Immediate mitigation actions required.')
    } else if (stats.mean > 5) {
      recommendations.push('Elevated risk level. Review and strengthen existing controls.')
    }

    // Рекомендации на основе волатильности
    const coefficientOfVariation = stats.stdDev / stats.mean
    if (coefficientOfVariation > 0.5) {
      recommendations.push('High risk volatility detected. Consider implementing stabilizing controls.')
    }

    // Рекомендации по топ-рискам
    const topRisk = stats.topRiskContributors[0]
    if (topRisk && topRisk.contribution > 30) {
      recommendations.push(`Focus on "${topRisk.riskTitle}" which contributes ${topRisk.contribution.toFixed(1)}% to total risk.`)
    }

    // Рекомендации по корреляциям
    if (Math.abs(stats.correlationImpact) > 20) {
      recommendations.push(`Risk correlations ${stats.correlationImpact > 0 ? 'amplify' : 'reduce'} total exposure by ${Math.abs(stats.correlationImpact).toFixed(1)}%.`)
    }

    // Общие рекомендации
    recommendations.push('Consider running scenario-based exercises to validate simulation results.')
    recommendations.push('Update risk assessments quarterly to maintain accuracy.')

    return recommendations
  }
}

// Экспорт singleton экземпляра
export const monteCarloSimulation = new MonteCarloSimulationService()

// Экспорт для интеграции с существующими симуляторами
export async function integrateWithExerciseSimulators(
  risks: Risk[],
  simulatorEndpoint?: string
): Promise<any> {
  // Интеграция с exercise_simulators если доступны
  const endpoint = simulatorEndpoint || process.env.NEXT_PUBLIC_SIMULATOR_URL

  if (!endpoint) {
    console.log('Exercise simulators not configured, using local Monte Carlo')
    return null
  }

  try {
    const response = await fetch(`${endpoint}/api/risk-simulation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        risks,
        simulationType: 'monte_carlo',
        parameters: {
          iterations: 10000,
          engine: 'jaamsim' // Использование JaamSim для сложных симуляций
        }
      })
    })

    if (response.ok) {
      return await response.json()
    }
  } catch (error) {
    console.error('Failed to connect to exercise simulators:', error)
  }

  return null
}