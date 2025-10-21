/**
 * NASH 4.0 Digital Twin System - Полный тест функциональности
 * Проверяет все 29 экспериментов и интеграции
 */

import fetch from 'node-fetch';
import { createLogger } from './utils/logger.js';

const logger = createLogger('SystemTest');

class SystemFunctionalityTest {
    constructor() {
        this.baseUrl = process.env.TEST_BASE_URL || 'http://localhost:3000';
        this.results = {
            total: 0,
            passed: 0,
            failed: 0,
            tests: []
        };
    }

    async runFullTest() {
        console.log(' Запуск полного теста функциональности NASH 4.0 Digital Twin...\n');

        await this.testSystemHealth();
        await this.testAvailableExperiments();
        await this.testExternalAdapters();
        await this.testDigitalTwinScenarios();
        await this.testInternalEngines();
        await this.testSEHEndpoints();
        await this.testImpactValidation();
        
        this.printResults();
    }

    async testSystemHealth() {
        console.log(' Проверка здоровья системы...');
        
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            const health = await response.json();
            
            this.addResult('system_health', response.ok, 
                response.ok ? 'Система здорова' : 'Проблемы со здоровьем системы', health);
                
            // Проверяем статус адаптеров
            if (health.adapters) {
                Object.entries(health.adapters).forEach(([adapter, status]) => {
                    this.addResult(`adapter_${adapter}`, status === 'healthy', 
                        `Адаптер ${adapter}: ${status}`);
                });
            }
            
        } catch (error) {
            this.addResult('system_health', false, `Ошибка здоровья: ${error.message}`);
        }
    }

    async testAvailableExperiments() {
        console.log(' Проверка доступных экспериментов...');
        
        try {
            const response = await fetch(`${this.baseUrl}/api/impact/simulations/experiments`);
            const result = await response.json();
            
            if (result.success && result.experiments) {
                const count = result.experiments.length;
                this.addResult('experiments_count', count === 29, 
                    `Доступно ${count}/29 экспериментов`, result.experiments);
                    
                // Проверяем наличие всех категорий
                const external = result.experiments.filter(e => e.type === 'external');
                const internal = result.experiments.filter(e => e.type === 'internal');
                
                this.addResult('external_adapters', external.length === 3,
                    `Внешние адаптеры: ${external.length}/3`);
                this.addResult('internal_engines', internal.length === 26,
                    `Внутренние движки: ${internal.length}/26`);
            } else {
                this.addResult('experiments_list', false, 'Не удалось получить список экспериментов');
            }
            
        } catch (error) {
            this.addResult('experiments_list', false, `Ошибка списка: ${error.message}`);
        }
    }

    async testExternalAdapters() {
        console.log(' Тестирование внешних SEH адаптеров...');
        
        const adapters = [
            {
                name: 'SimPy',
                experiment: 'simpy_queue',
                params: {
                    arrival_rate: 12,
                    service_time: { dist: 'lognormal', mu: '10m', sigma: 0.5 },
                    capacity_agents: [6, 8, 10]
                }
            },
            {
                name: 'Mesa',
                experiment: 'mesa_abm',
                params: {
                    steps: 200,
                    population_size: 2000,
                    policies: { sms: 1.5, vouchers: 1.1 }
                }
            },
            {
                name: 'EpiNow2',
                experiment: 'epi_nowcasting_rt',
                params: {
                    cases_ts: 'demo',
                    generation_time: 'dist_ref'
                }
            }
        ];

        for (const adapter of adapters) {
            await this.testSimulation(adapter.experiment, adapter.params, adapter.name);
        }
    }

    async testDigitalTwinScenarios() {
        console.log(' Тестирование Digital Twin сценариев...');
        
        const scenarios = [
            'automation', 'crisis', 'expansion', 'integration',
            'digital_transformation', 'ai_implementation', 'cybersecurity',
            'compliance', 'staff_training', 'process_optimization',
            'stakeholder_engagement', 'community_outreach', 'resource_allocation',
            'capacity_building', 'monitoring_evaluation', 'knowledge_management',
            'innovation_research', 'partnership_development', 'sustainability_planning',
            'grant_management', 'funding_diversification', 'impact_assessment'
        ];

        for (const scenario of scenarios) {
            await this.testSimulation(scenario, {
                budget: 50000,
                staff: 25,
                organizationData: { type: 'npo' }
            }, `DT-${scenario}`);
        }
    }

    async testInternalEngines() {
        console.log('️ Тестирование внутренних движков...');
        
        const engines = [
            {
                name: 'Theory of Change',
                experiment: 'theory_of_change',
                params: {
                    budget_cap: 50000,
                    objective: 'maximize_outcome_per_cost'
                }
            },
            {
                name: 'Capacity Sweep',
                experiment: 'capacity_sweep',
                params: {
                    min_capacity: 5,
                    max_capacity: 15
                }
            },
            {
                name: 'BCM Outage',
                experiment: 'bcm_outage',
                params: {
                    outage_duration: 24,
                    affected_systems: ['crm']
                }
            },
            {
                name: 'Budget Optimization',
                experiment: 'budget_optimization',
                params: {
                    total_budget: 100000,
                    priorities: ['staff', 'technology']
                }
            }
        ];

        for (const engine of engines) {
            await this.testSimulation(engine.experiment, engine.params, engine.name);
        }
    }

    async testSimulation(experiment, params, name) {
        try {
            const payload = {
                experiment,
                params,
                options: { monte_carlo_runs: 10 } // Быстрый тест
            };

            const response = await fetch(`${this.baseUrl}/api/impact/simulations/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            
            this.addResult(`sim_${experiment}`, response.ok && result.success,
                `${name}: ${response.ok && result.success ? 'Успешно' : result.error || 'Ошибка'}`,
                result);
                
        } catch (error) {
            this.addResult(`sim_${experiment}`, false, `${name}: ${error.message}`);
        }
    }

    async testSEHEndpoints() {
        console.log(' Тестирование SEH endpoints...');
        
        try {
            // Тест создания программы
            const programData = {
                name: 'Test Program',
                domain: 'health',
                status: 'active',
                organization_id: 'test-org'
            };

            const createResponse = await fetch(`${this.baseUrl}/api/seh/programs`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(programData)
            });

            this.addResult('seh_create_program', createResponse.ok,
                `SEH создание программы: ${createResponse.ok ? 'Успешно' : 'Ошибка'}`);

            // Тест получения программ
            const getResponse = await fetch(`${this.baseUrl}/api/seh/programs`);
            this.addResult('seh_get_programs', getResponse.ok,
                `SEH получение программ: ${getResponse.ok ? 'Успешно' : 'Ошибка'}`);
                
        } catch (error) {
            this.addResult('seh_endpoints', false, `SEH endpoints: ${error.message}`);
        }
    }

    async testImpactValidation() {
        console.log(' Тестирование Impact Validation...');
        
        try {
            // Тест workflow симуляции и регистрации
            const workflowData = {
                experiment: 'automation',
                params: { budget: 25000 },
                organizationData: { id: 'test-org', name: 'Test Org' }
            };

            const response = await fetch(`${this.baseUrl}/api/impact/workflow/simulate-and-register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(workflowData)
            });

            const result = await response.json();
            
            this.addResult('impact_workflow', response.ok && result.success,
                `Impact Workflow: ${response.ok && result.success ? 'Успешно' : 'Ошибка'}`,
                result);
                
        } catch (error) {
            this.addResult('impact_workflow', false, `Impact Workflow: ${error.message}`);
        }
    }

    addResult(testName, passed, message, data = null) {
        this.results.total++;
        if (passed) {
            this.results.passed++;
            console.log(` ${testName}: ${message}`);
        } else {
            this.results.failed++;
            console.log(` ${testName}: ${message}`);
        }
        
        this.results.tests.push({
            name: testName,
            passed,
            message,
            data
        });
    }

    printResults() {
        console.log('\n РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:');
        console.log('=' * 50);
        console.log(`Всего тестов: ${this.results.total}`);
        console.log(` Прошли: ${this.results.passed}`);
        console.log(` Не прошли: ${this.results.failed}`);
        console.log(` Успешность: ${((this.results.passed / this.results.total) * 100).toFixed(1)}%`);
        
        if (this.results.failed > 0) {
            console.log('\n НЕУСПЕШНЫЕ ТЕСТЫ:');
            this.results.tests
                .filter(t => !t.passed)
                .forEach(test => console.log(`  - ${test.name}: ${test.message}`));
        }
        
        console.log('\n Тест завершен!');
    }
}

// Запуск тестов
if (import.meta.url === `file://${process.argv[1]}`) {
    const tester = new SystemFunctionalityTest();
    tester.runFullTest().catch(console.error);
}

export { SystemFunctionalityTest };