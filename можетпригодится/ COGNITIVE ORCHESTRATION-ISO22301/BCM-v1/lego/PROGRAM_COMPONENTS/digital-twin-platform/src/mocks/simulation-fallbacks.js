/**
 * Simulation Fallback Mock Functions
 * 
 * ⚠️ ТОЛЬКО ДЛЯ FALLBACK РЕЖИМА!
 * Используется когда внешние simulation адаптеры недоступны
 */

import { createLogger } from '../../utils/logger.js';

const logger = createLogger('SimulationFallbacks');

/**
 * Генерирует fallback результат для симуляций
 * 
 * @param {string} experiment - Тип эксперимента
 * @param {Object} params - Параметры симуляции
 * @returns {Object} Mock результат в формате стандартного ответа
 */
export function generateFallbackResult(experiment, params) {
    logger.warn(`🔄 FALLBACK MODE: Generating mock result for ${experiment}`);
    
    const fallbackResults = {
        simpy_queue: {
            run_id: `fallback_simpy_${Date.now()}`,
            experiment: 'simpy_queue',
            best: {
                capacity: Math.ceil(Math.random() * 10 + 5),
                sla: 0.85 + Math.random() * 0.1,
                wait_p50_min: Math.random() * 15 + 5,
                cost: Math.ceil(Math.random() * 5000 + 10000)
            },
            frontier: [
                { capacity: 6, sla: 0.82, cost: 9600 },
                { capacity: 8, sla: 0.88, cost: 12800 },
                { capacity: 10, sla: 0.92, cost: 16000 }
            ],
            explain: "⚠️ FALLBACK: Реальные адаптеры недоступны - используются приблизительные данные"
        },
        
        mesa_abm: {
            run_id: `fallback_mesa_${Date.now()}`,
            experiment: 'mesa_abm',
            best: {
                kpi: 'coverage',
                value: 0.6 + Math.random() * 0.25
            },
            frontier: [
                { policy: 'baseline', coverage: 0.55 },
                { policy: 'enhanced', coverage: 0.65 + Math.random() * 0.15 }
            ],
            explain: "⚠️ FALLBACK: ABM адаптер недоступен - используется упрощенная модель"
        },
        
        routing_vrp: {
            run_id: `fallback_vrp_${Date.now()}`,
            experiment: 'routing_vrp',
            best: {
                total_cost: Math.ceil(Math.random() * 1000 + 2000),
                total_time: Math.ceil(Math.random() * 60 + 120),
                vehicles_used: Math.ceil(Math.random() * 3 + 2)
            },
            frontier: [],
            explain: "⚠️ FALLBACK: VRP адаптер недоступен - случайные результаты"
        }
    };
    
    return fallbackResults[experiment] || {
        run_id: `fallback_${experiment}_${Date.now()}`,
        experiment,
        best: { 
            status: 'fallback_mode', 
            value: Math.random(),
            warning: 'Внешний адаптер недоступен'
        },
        frontier: [],
        explain: `⚠️ FALLBACK: Адаптер для ${experiment} недоступен`
    };
}

/**
 * Проверяет доступность внешнего адаптера
 * 
 * @param {string} url - URL адаптера
 * @returns {Promise<boolean>} Доступен ли адаптер
 */
export async function checkAdapterAvailability(url) {
    try {
        const response = await fetch(url, { 
            method: 'GET',
            timeout: 3000
        });
        return response.ok;
    } catch (error) {
        logger.debug(`Адаптер ${url} недоступен:`, error.message);
        return false;
    }
}

/**
 * Возвращает признак того что система в fallback режиме
 */
export function isFallbackMode() {
    return process.env.SIMULATION_FALLBACK === 'true' || 
           process.env.NODE_ENV === 'development';
}