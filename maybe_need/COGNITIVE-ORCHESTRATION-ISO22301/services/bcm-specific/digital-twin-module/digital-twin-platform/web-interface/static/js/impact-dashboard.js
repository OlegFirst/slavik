/**
 * Impact Dashboard UI
 * Интерфейс для Impact Passports и валидации симуляций
 */

class ImpactDashboard {
    constructor() {
        this.apiBase = window.location.origin + '/api/impact';
        this.currentOrganization = null;
        this.passport = null;
        this.validations = [];
    }

    /**
     * Инициализация дашборда
     */
    async initialize(organizationId) {
        this.currentOrganization = organizationId;
        
        // Загружаем данные
        await this.loadPassport();
        await this.loadValidations();
        await this.loadPendingValidations();
        
        // Рендерим UI
        this.render();
        
        // Устанавливаем обработчики
        this.setupEventHandlers();
    }

    /**
     * Загрузка Impact Passport
     */
    async loadPassport() {
        try {
            const response = await fetch(`${this.apiBase}/passports/${this.currentOrganization}`);
            if (response.ok) {
                this.passport = await response.json();
            }
        } catch (error) {
            console.error('Failed to load passport:', error);
        }
    }

    /**
     * Загрузка истории валидаций
     */
    async loadValidations() {
        try {
            const response = await fetch(`${this.apiBase}/validations/history/${this.currentOrganization}`);
            const data = await response.json();
            this.validations = data.validations || [];
        } catch (error) {
            console.error('Failed to load validations:', error);
        }
    }

    /**
     * Загрузка ожидающих валидаций
     */
    async loadPendingValidations() {
        try {
            const response = await fetch(`${this.apiBase}/validations/pending/${this.currentOrganization}`);
            const data = await response.json();
            this.pendingValidations = data.pending || [];
        } catch (error) {
            console.error('Failed to load pending validations:', error);
        }
    }

    /**
     * Рендеринг основного интерфейса
     */
    render() {
        const container = document.getElementById('impact-dashboard');
        if (!container) return;

        container.innerHTML = `
            <div class="impact-dashboard">
                <!-- Passport Card -->
                <div class="passport-card">
                    ${this.renderPassportCard()}
                </div>

                <!-- Metrics Overview -->
                <div class="metrics-grid">
                    ${this.renderMetrics()}
                </div>

                <!-- Achievements -->
                <div class="achievements-section">
                    ${this.renderAchievements()}
                </div>

                <!-- Validations Timeline -->
                <div class="validations-timeline">
                    ${this.renderValidationsTimeline()}
                </div>

                <!-- Action Buttons -->
                <div class="actions-section">
                    ${this.renderActions()}
                </div>
            </div>
        `;
    }

    /**
     * Рендер карточки паспорта
     */
    renderPassportCard() {
        if (!this.passport) {
            return `
                <div class="no-passport">
                    <h3>Impact Passport не создан</h3>
                    <p>Запустите первую симуляцию чтобы создать ваш Impact Passport</p>
                    <button class="btn-primary" onclick="impactDashboard.runFirstSimulation()">
                        Запустить симуляцию
                    </button>
                </div>
            `;
        }

        const reputation = this.passport.reputation || {};
        const levelClass = `reputation-${reputation.level || 'newcomer'}`;
        
        return `
            <div class="passport-header">
                <h2>Impact Passport</h2>
                <div class="passport-id">${this.passport.id}</div>
            </div>
            
            <div class="reputation-display ${levelClass}">
                <div class="reputation-score">
                    ${(reputation.score * 100).toFixed(0)}%
                </div>
                <div class="reputation-level">
                    ${this.translateLevel(reputation.level)}
                </div>
                <div class="reputation-trend">
                    ${this.renderTrend(reputation.trend)}
                </div>
            </div>

            <div class="passport-meta">
                <div class="created">Создан: ${this.formatDate(this.passport.createdAt)}</div>
                <div class="expires">Истекает: ${this.formatDate(this.passport.expiresAt)}</div>
            </div>
        `;
    }

    /**
     * Рендер метрик
     */
    renderMetrics() {
        const metrics = this.passport?.metrics || {};
        
        return `
            <div class="metric-card">
                <div class="metric-value">${metrics.totalSimulations || 0}</div>
                <div class="metric-label">Всего симуляций</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">${metrics.validatedSimulations || 0}</div>
                <div class="metric-label">Валидировано</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">${((metrics.averagePredictionAccuracy || 0) * 100).toFixed(0)}%</div>
                <div class="metric-label">Точность предсказаний</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">${metrics.impactScore || 0}</div>
                <div class="metric-label">Impact Score</div>
            </div>
        `;
    }

    /**
     * Рендер достижений
     */
    renderAchievements() {
        const achievements = this.passport?.achievements || [];
        
        if (achievements.length === 0) {
            return '<h3>Достижения</h3><p>Пока нет достижений</p>';
        }

        return `
            <h3>Достижения</h3>
            <div class="achievements-grid">
                ${achievements.map(a => `
                    <div class="achievement" title="${a.description}">
                        <div class="achievement-icon">${this.getAchievementIcon(a.icon)}</div>
                        <div class="achievement-name">${a.name}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    /**
     * Рендер таймлайна валидаций
     */
    renderValidationsTimeline() {
        return `
            <h3>История валидаций</h3>
            
            ${this.pendingValidations.length > 0 ? `
                <div class="pending-validations">
                    <h4>Ожидают валидации</h4>
                    ${this.pendingValidations.map(v => `
                        <div class="validation-pending">
                            <div class="validation-id">${v.simulationId}</div>
                            <div class="validation-scheduled">
                                Запланировано: ${this.formatDate(v.scheduledValidation)}
                            </div>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            <div class="validations-list">
                ${this.validations.length === 0 ? 
                    '<p>Нет завершенных валидаций</p>' :
                    this.validations.map(v => this.renderValidationItem(v)).join('')
                }
            </div>
        `;
    }

    /**
     * Рендер элемента валидации
     */
    renderValidationItem(validation) {
        const statusClass = `status-${validation.status}`;
        const accuracy = validation.accuracyMetrics?.overallAccuracy || 0;
        
        return `
            <div class="validation-item ${statusClass}">
                <div class="validation-header">
                    <span class="validation-date">${this.formatDate(validation.validatedAt)}</span>
                    <span class="validation-status">${this.translateStatus(validation.status)}</span>
                </div>
                <div class="validation-metrics">
                    <div class="accuracy">Точность: ${(accuracy * 100).toFixed(1)}%</div>
                    ${validation.impactCertificate ? 
                        `<div class="certificate">✓ Сертификат выдан</div>` : ''
                    }
                </div>
            </div>
        `;
    }

    /**
     * Рендер действий
     */
    renderActions() {
        return `
            <h3>Действия</h3>
            <div class="actions-grid">
                <button class="btn-action" onclick="impactDashboard.runSimulation()">
                    Запустить симуляцию
                </button>
                
                <button class="btn-action" onclick="impactDashboard.submitEvidence()">
                    Предоставить доказательства
                </button>
                
                <button class="btn-action" onclick="impactDashboard.exportPassport()">
                    Экспортировать паспорт
                </button>
                
                <button class="btn-action" onclick="impactDashboard.viewCertificates()">
                    Просмотр сертификатов
                </button>
            </div>
        `;
    }

    /**
     * Запуск симуляции
     */
    async runSimulation() {
        const modal = this.createSimulationModal();
        document.body.appendChild(modal);
    }

    /**
     * Создание модального окна симуляции
     */
    createSimulationModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h2>Запуск симуляции</h2>
                
                <div class="simulation-options">
                    <h4>Внешние SEH адаптеры</h4>
                    <label>
                        <input type="radio" name="experiment" value="simpy_queue">
                        SimPy - Очереди и capacity planning
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="mesa_abm">
                        Mesa - Agent-Based модели
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="epi_nowcasting_rt">
                        EpiNow2 - Эпидемиологическое моделирование
                    </label>
                    <label style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 5px; border-radius: 4px;">
                        <input type="radio" name="experiment" value="anylogic_hybrid">
                        AnyLogic - Гибридное моделирование с ML/AI
                    </label>
                    
                    <h4>Digital Twin сценарии</h4>
                    <label>
                        <input type="radio" name="experiment" value="automation" checked>
                        Автоматизация процессов
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="crisis">
                        Антикризисное управление
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="expansion">
                        Расширение деятельности
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="integration">
                        Интеграция систем
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="digital_transformation">
                        Цифровая трансформация
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="ai_implementation">
                        Внедрение ИИ
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="cybersecurity">
                        Кибербезопасность
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="compliance">
                        Соответствие требованиям
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="staff_training">
                        Обучение персонала
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="process_optimization">
                        Оптимизация процессов
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="stakeholder_engagement">
                        Взаимодействие с заинтересованными сторонами
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="community_outreach">
                        Работа с сообществом
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="resource_allocation">
                        Распределение ресурсов
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="capacity_building">
                        Наращивание потенциала
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="monitoring_evaluation">
                        Мониторинг и оценка
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="knowledge_management">
                        Управление знаниями
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="innovation_research">
                        Инновации и исследования
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="partnership_development">
                        Развитие партнерств
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="sustainability_planning">
                        Планирование устойчивости
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="grant_management">
                        Управление грантами
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="funding_diversification">
                        Диверсификация финансирования
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="impact_assessment">
                        Оценка воздействия
                    </label>
                    
                    <h4>Внутренние движки</h4>
                    <label>
                        <input type="radio" name="experiment" value="theory_of_change">
                        Theory of Change оптимизация
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="capacity_sweep">
                        Анализ пропускной способности
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="bcm_outage">
                        Симуляция сбоев BCM
                    </label>
                    <label>
                        <input type="radio" name="experiment" value="budget_optimization">
                        Оптимизация бюджета
                    </label>
                </div>
                
                <div class="simulation-params">
                    <label>
                        Бюджет:
                        <input type="number" id="budget" value="50000">
                    </label>
                    
                    <label>
                        Monte Carlo прогонов:
                        <input type="number" id="mc_runs" value="1000">
                    </label>
                </div>
                
                <div class="modal-actions">
                    <button onclick="impactDashboard.executeSimulation()">Запустить</button>
                    <button onclick="this.closest('.modal').remove()">Отмена</button>
                </div>
            </div>
        `;
        return modal;
    }

    /**
     * Выполнение симуляции
     */
    async executeSimulation() {
        const experiment = document.querySelector('input[name="experiment"]:checked').value;
        const budget = document.getElementById('budget').value;
        const mcRuns = document.getElementById('mc_runs').value;
        
        const payload = {
            experiment,
            params: this.getSimulationParams(experiment, budget),
            organizationData: {
                id: this.currentOrganization,
                name: 'Test Organization' // Получить из профиля
            },
            options: {
                monte_carlo_runs: parseInt(mcRuns)
            }
        };
        
        try {
            const response = await fetch(`${this.apiBase}/workflow/simulate-and-register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert('Симуляция запущена успешно!');
                document.querySelector('.modal').remove();
                await this.initialize(this.currentOrganization); // Обновляем данные
            } else {
                alert('Ошибка запуска симуляции');
            }
        } catch (error) {
            console.error('Simulation error:', error);
            alert('Ошибка: ' + error.message);
        }
    }

    /**
     * Получение параметров симуляции
     */
    getSimulationParams(experiment, budget) {
        switch (experiment) {
            case 'theory_of_change':
                return {
                    objective: 'maximize_outcome_per_cost',
                    budget_cap: parseInt(budget),
                    decision_variables: [
                        { id: 'sms', min: 0, max: 2, step: 0.1 },
                        { id: 'vouchers', min: 0, max: 2, step: 0.1 },
                        { id: 'counsel', min: 0, max: 2, step: 0.1 }
                    ]
                };
                
            case 'mesa_abm':
                return {
                    steps: 200,
                    population_size: 2000,
                    policies: { sms: 1.5, vouchers: 1.1, counsel: 1.0 }
                };
                
            case 'simpy_queue':
                return {
                    arrival_rate: 12,
                    service_time: { dist: 'lognormal', mu: '10m', sigma: 0.5 },
                    capacity_agents: [6, 8, 10],
                    targets: { sla_target: 0.95, wait_p50_min: '15m' }
                };
                
            default:
                return {};
        }
    }

    /**
     * Экспорт паспорта
     */
    async exportPassport() {
        try {
            const response = await fetch(`${this.apiBase}/passports/${this.currentOrganization}/export`);
            const vc = await response.json();
            
            // Скачиваем как JSON
            const blob = new Blob([JSON.stringify(vc, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `impact-passport-${this.currentOrganization}.json`;
            a.click();
        } catch (error) {
            console.error('Export error:', error);
            alert('Ошибка экспорта паспорта');
        }
    }

    /**
     * Утилиты
     */
    formatDate(dateString) {
        if (!dateString) return 'Н/Д';
        return new Date(dateString).toLocaleDateString('ru-RU');
    }

    translateLevel(level) {
        const translations = {
            'newcomer': 'Новичок',
            'beginner': 'Начинающий',
            'intermediate': 'Средний',
            'advanced': 'Продвинутый',
            'expert': 'Эксперт'
        };
        return translations[level] || level;
    }

    translateStatus(status) {
        const translations = {
            'validated': 'Валидировано',
            'rejected': 'Отклонено',
            'provisional': 'Условно',
            'pending_evidence': 'Ожидает данных'
        };
        return translations[status] || status;
    }

    renderTrend(trend) {
        if (trend === 'rising') return '↑';
        if (trend === 'falling') return '↓';
        return '→';
    }

    getAchievementIcon(icon) {
        const icons = {
            'star': '⭐',
            'target': '🎯',
            'shield': '🛡️',
            'trophy': '🏆'
        };
        return icons[icon] || '🏅';
    }

    setupEventHandlers() {
        // Автообновление каждые 30 секунд
        setInterval(() => {
            this.loadPassport();
            this.loadValidations();
        }, 30000);
    }
}

// Глобальный экземпляр
window.impactDashboard = new ImpactDashboard();