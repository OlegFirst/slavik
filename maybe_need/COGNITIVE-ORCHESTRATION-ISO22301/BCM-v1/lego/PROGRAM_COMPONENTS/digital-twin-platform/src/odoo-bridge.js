/**
 * Odoo Bridge - API мост между Node.js и Odoo
 * Обеспечивает интеграцию Digital Twin веб-интерфейса с BCM модулями Odoo
 */

import axios from 'axios';
import logger from './logger.js';

class OdooBridge {
    constructor() {
        this.baseURL = process.env.ODOO_URL || 'http://localhost:8069';
        this.database = process.env.ODOO_DATABASE || 'bcm_platform';
        this.username = process.env.ODOO_USERNAME || 'admin';
        this.password = process.env.ODOO_PASSWORD || 'admin';
        this.sessionId = null;
        this.userId = null;

        logger.info('OdooBridge initialized', {
            baseURL: this.baseURL,
            database: this.database,
            username: this.username
        });
    }

    /**
     * Аутентификация в Odoo
     */
    async authenticate() {
        try {
            const response = await axios.post(`${this.baseURL}/web/session/authenticate`, {
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    db: this.database,
                    login: this.username,
                    password: this.password
                },
                id: Math.random()
            }, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.data.result && response.data.result.uid) {
                this.userId = response.data.result.uid;
                this.sessionId = response.headers['set-cookie']?.find(cookie =>
                    cookie.startsWith('session_id=')
                );

                logger.info('Successfully authenticated with Odoo', {
                    userId: this.userId
                });
                return true;
            } else {
                logger.error('Odoo authentication failed', response.data);
                return false;
            }
        } catch (error) {
            logger.error('Error authenticating with Odoo', error);
            return false;
        }
    }

    /**
     * Выполнение RPC вызова к Odoo
     */
    async rpcCall(model, method, args = [], kwargs = {}) {
        if (!this.userId) {
            const authenticated = await this.authenticate();
            if (!authenticated) {
                throw new Error('Failed to authenticate with Odoo');
            }
        }

        try {
            const response = await axios.post(`${this.baseURL}/web/dataset/call_kw`, {
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    model: model,
                    method: method,
                    args: args,
                    kwargs: kwargs
                },
                id: Math.random()
            }, {
                headers: {
                    'Content-Type': 'application/json',
                    'Cookie': this.sessionId
                }
            });

            if (response.data.error) {
                logger.error('Odoo RPC error', response.data.error);
                throw new Error(response.data.error.message);
            }

            return response.data.result;
        } catch (error) {
            logger.error('RPC call failed', { model, method, error: error.message });
            throw error;
        }
    }

    // ===== DIGITAL TWIN OPERATIONS =====

    /**
     * Получение всех Digital Twin из Odoo
     */
    async getDigitalTwins() {
        try {
            const twins = await this.rpcCall('bcm.digital.twin', 'search_read', []);
            logger.info(`Retrieved ${twins.length} digital twins from Odoo`);
            return twins;
        } catch (error) {
            logger.error('Failed to get digital twins', error);
            return [];
        }
    }

    /**
     * Создание нового Digital Twin в Odoo
     */
    async createDigitalTwin(twinData) {
        try {
            const twinId = await this.rpcCall('bcm.digital.twin', 'create', [twinData]);
            logger.info('Created digital twin in Odoo', { twinId, twinData });
            return twinId;
        } catch (error) {
            logger.error('Failed to create digital twin', error);
            throw error;
        }
    }

    /**
     * Обновление Digital Twin в Odoo
     */
    async updateDigitalTwin(twinId, updateData) {
        try {
            await this.rpcCall('bcm.digital.twin', 'write', [[twinId], updateData]);
            logger.info('Updated digital twin in Odoo', { twinId, updateData });
            return true;
        } catch (error) {
            logger.error('Failed to update digital twin', error);
            throw error;
        }
    }

    /**
     * Удаление Digital Twin из Odoo
     */
    async deleteDigitalTwin(twinId) {
        try {
            await this.rpcCall('bcm.digital.twin', 'unlink', [[twinId]]);
            logger.info('Deleted digital twin from Odoo', { twinId });
            return true;
        } catch (error) {
            logger.error('Failed to delete digital twin', error);
            throw error;
        }
    }

    // ===== DIGITAL COPY OPERATIONS =====

    /**
     * Создание снапшота Digital Twin
     */
    async createSnapshot(twinId, name, description = null) {
        try {
            const copyId = await this.rpcCall('bcm.digital.copy', 'create_snapshot',
                [twinId, name, description, 'manual']
            );
            logger.info('Created digital copy in Odoo', { copyId, twinId, name });
            return copyId;
        } catch (error) {
            logger.error('Failed to create snapshot', error);
            throw error;
        }
    }

    /**
     * Получение снапшотов для Digital Twin
     */
    async getSnapshots(twinId) {
        try {
            const snapshots = await this.rpcCall('bcm.digital.copy', 'search_read',
                [[['digital_twin_id', '=', twinId]]]
            );
            logger.info(`Retrieved ${snapshots.length} snapshots for twin ${twinId}`);
            return snapshots;
        } catch (error) {
            logger.error('Failed to get snapshots', error);
            return [];
        }
    }

    /**
     * Восстановление Digital Twin из снапшота
     */
    async restoreFromSnapshot(copyId) {
        try {
            await this.rpcCall('bcm.digital.copy', 'action_restore_snapshot', [[copyId]]);
            logger.info('Restored digital twin from snapshot', { copyId });
            return true;
        } catch (error) {
            logger.error('Failed to restore from snapshot', error);
            throw error;
        }
    }

    // ===== AI CONSULTANT OPERATIONS =====

    /**
     * Отправка сообщения AI консультанту
     */
    async sendMessageToAI(message, context = {}) {
        try {
            // Создаем сессию консультации если нужно
            let sessionId = context.sessionId;
            if (!sessionId) {
                sessionId = await this.rpcCall('bcm.ai.consultation.session', 'create', [{
                    name: `Консультация ${new Date().toISOString()}`,
                    status: 'active'
                }]);
            }

            // Отправляем сообщение
            const response = await this.rpcCall('bcm.ai.consultation.session', 'process_message',
                [sessionId, message, context]
            );

            logger.info('AI consultant response received', { sessionId, message: message.substring(0, 100) });
            return {
                sessionId,
                response: response.message,
                recommendations: response.recommendations || []
            };
        } catch (error) {
            logger.error('Failed to get AI consultant response', error);
            throw error;
        }
    }

    // ===== BCM CLIENT OPERATIONS =====

    /**
     * Получение BCM клиентов
     */
    async getBCMClients() {
        try {
            const clients = await this.rpcCall('bcm.client', 'search_read', []);
            logger.info(`Retrieved ${clients.length} BCM clients`);
            return clients;
        } catch (error) {
            logger.error('Failed to get BCM clients', error);
            return [];
        }
    }

    /**
     * Получение организаций для клиента
     */
    async getOrganizations(clientId = null) {
        try {
            const domain = clientId ? [['bcm_client_id', '=', clientId]] : [];
            const organizations = await this.rpcCall('bcm.digital.twin', 'search_read', [domain]);
            logger.info(`Retrieved ${organizations.length} organizations`);
            return organizations;
        } catch (error) {
            logger.error('Failed to get organizations', error);
            return [];
        }
    }

    // ===== AI ORCHESTRATOR OPERATIONS =====

    /**
     * Получение статуса AI органов
     */
    async getAIOrganStatus() {
        try {
            const organs = await this.rpcCall('bcm.ai.organ', 'search_read', []);
            logger.info(`Retrieved ${organs.length} AI organs status`);
            return organs;
        } catch (error) {
            logger.error('Failed to get AI organs status', error);
            return [];
        }
    }

    /**
     * Запуск симуляции через AI оркестратор
     */
    async runSimulation(twinId, scenarioData) {
        try {
            const result = await this.rpcCall('bcm.ai.twin.orchestrator', 'run_simulation',
                [twinId, scenarioData]
            );
            logger.info('Simulation completed', { twinId, result });
            return result;
        } catch (error) {
            logger.error('Failed to run simulation', error);
            throw error;
        }
    }

    // ===== UTILITY METHODS =====

    /**
     * Проверка подключения к Odoo
     */
    async healthCheck() {
        try {
            const result = await this.rpcCall('ir.module.module', 'search_count', []);
            logger.info('Odoo health check successful', { moduleCount: result });
            return { status: 'healthy', moduleCount: result };
        } catch (error) {
            logger.error('Odoo health check failed', error);
            return { status: 'unhealthy', error: error.message };
        }
    }

    /**
     * Получение информации о системе
     */
    async getSystemInfo() {
        try {
            const info = await this.rpcCall('ir.config_parameter', 'get_param', ['database.uuid']);
            return {
                database: this.database,
                userId: this.userId,
                systemUuid: info
            };
        } catch (error) {
            logger.error('Failed to get system info', error);
            return null;
        }
    }
}

export default new OdooBridge();