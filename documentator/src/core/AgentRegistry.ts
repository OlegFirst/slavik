import { BaseAgent } from './BaseAgent';
import { AgentScheduler } from './AgentScheduler';
import { AgentConfig, AgentStatus } from '../types/AgentInterface';
import * as fs from 'fs-extra';
import * as path from 'path';

export interface AgentRegistryConfig {
  agentsConfigPath: string;
  enableAutoLoad: boolean;
  logLevel: 'info' | 'warn' | 'error';
}

export class AgentRegistry {
  private agents: Map<string, BaseAgent> = new Map();
  private scheduler: AgentScheduler;
  private config: AgentRegistryConfig;
  private initialized: boolean = false;

  constructor(
    scheduler: AgentScheduler,
    config: AgentRegistryConfig = {
      agentsConfigPath: './data/agents-config.json',
      enableAutoLoad: true,
      logLevel: 'info'
    }
  ) {
    this.scheduler = scheduler;
    this.config = config;
  }

  async initialize(): Promise<void> {
    if (this.initialized) {
      console.log('AgentRegistry вже ініціалізовано');
      return;
    }

    await this.ensureConfigFile();

    if (this.config.enableAutoLoad) {
      await this.loadAgentsFromConfig();
    }

    this.initialized = true;
    console.log('AgentRegistry ініціалізовано');
  }

  async shutdown(): Promise<void> {
    if (!this.initialized) {
      return;
    }

    // Зупиняємо всі агенти
    for (const agent of this.agents.values()) {
      try {
        await this.scheduler.unregisterAgent(agent.metadata.name);
        await agent.shutdown();
      } catch (error) {
        console.error(`Помилка зупинки агента ${agent.metadata.name}:`, error);
      }
    }

    this.agents.clear();
    this.initialized = false;
    console.log('AgentRegistry зупинено');
  }

  async registerAgent(agent: BaseAgent): Promise<void> {
    const agentName = agent.metadata.name;

    if (this.agents.has(agentName)) {
      throw new Error(`Агент ${agentName} вже зареєстровано`);
    }

    // Ініціалізуємо агента
    await agent.initialize();

    // Реєструємо в реєстрі
    this.agents.set(agentName, agent);

    // Реєструємо в планувальнику
    await this.scheduler.registerAgent(agent);

    await this.saveAgentConfig(agentName, agent.getAgentStatus().config);

    this.log(`Агент ${agentName} зареєстровано`);
  }

  async unregisterAgent(agentName: string): Promise<void> {
    const agent = this.agents.get(agentName);
    if (!agent) {
      throw new Error(`Агент ${agentName} не знайдено`);
    }

    // Видаляємо з планувальника
    await this.scheduler.unregisterAgent(agentName);

    // Зупиняємо агента
    await agent.shutdown();

    // Видаляємо з реєстру
    this.agents.delete(agentName);

    await this.removeAgentConfig(agentName);

    this.log(`Агент ${agentName} видалено`);
  }

  async enableAgent(agentName: string): Promise<void> {
    const agent = this.agents.get(agentName);
    if (!agent) {
      throw new Error(`Агент ${agentName} не знайдено`);
    }

    agent.updateConfig({ enabled: true });
    await this.scheduler.resumeAgent(agentName);
    await this.saveAgentConfig(agentName, agent.getAgentStatus().config);

    this.log(`Агент ${agentName} увімкнено`);
  }

  async disableAgent(agentName: string): Promise<void> {
    const agent = this.agents.get(agentName);
    if (!agent) {
      throw new Error(`Агент ${agentName} не знайдено`);
    }

    agent.updateConfig({ enabled: false });
    await this.scheduler.pauseAgent(agentName);
    await this.saveAgentConfig(agentName, agent.getAgentStatus().config);

    this.log(`Агент ${agentName} вимкнено`);
  }

  async pauseAgent(agentName: string): Promise<void> {
    await this.scheduler.pauseAgent(agentName);
    this.log(`Агент ${agentName} призупинено`);
  }

  async resumeAgent(agentName: string): Promise<void> {
    await this.scheduler.resumeAgent(agentName);
    this.log(`Агент ${agentName} відновлено`);
  }

  async executeAgentNow(agentName: string): Promise<void> {
    await this.scheduler.executeAgentNow(agentName);
    this.log(`Агент ${agentName} виконано вручну`);
  }

  getAgent(agentName: string): BaseAgent | undefined {
    return this.agents.get(agentName);
  }

  getAllAgents(): BaseAgent[] {
    return Array.from(this.agents.values());
  }

  getAgentNames(): string[] {
    return Array.from(this.agents.keys());
  }

  getAgentStatus(agentName: string): AgentStatus | null {
    const agent = this.agents.get(agentName);
    return agent ? agent.getAgentStatus() : null;
  }

  getAllAgentStatuses(): AgentStatus[] {
    return this.getAllAgents().map(agent => agent.getAgentStatus());
  }

  async updateAgentConfig(agentName: string, config: Partial<AgentConfig>): Promise<void> {
    const agent = this.agents.get(agentName);
    if (!agent) {
      throw new Error(`Агент ${agentName} не знайдено`);
    }

    agent.updateConfig(config);
    await this.saveAgentConfig(agentName, agent.getAgentStatus().config);

    this.log(`Конфігурація агента ${agentName} оновлено`);
  }

  async clearAgentErrors(agentName: string): Promise<void> {
    const agent = this.agents.get(agentName);
    if (!agent) {
      throw new Error(`Агент ${agentName} не знайдено`);
    }

    agent.clearErrors();
    this.log(`Помилки агента ${agentName} очищено`);
  }

  private async ensureConfigFile(): Promise<void> {
    const configPath = this.config.agentsConfigPath;
    const configDir = path.dirname(configPath);

    await fs.ensureDir(configDir);

    if (!await fs.pathExists(configPath)) {
      const initialConfig = {
        agents: {},
        registry: {
          version: '1.0.0',
          lastUpdated: new Date().toISOString()
        }
      };

      await fs.writeJson(configPath, initialConfig, { spaces: 2 });
      this.log('Створено файл конфігурації агентів');
    }
  }

  private async loadAgentsFromConfig(): Promise<void> {
    try {
      const configPath = this.config.agentsConfigPath;
      const config = await fs.readJson(configPath);

      // TODO: Реалізувати автоматичне завантаження агентів з конфігурації
      // Це буде потребувати системи плагінів для динамічного завантаження агентів

      this.log('Конфігурація агентів завантажена');
    } catch (error) {
      console.error('Помилка завантаження конфігурації агентів:', error);
    }
  }

  private async saveAgentConfig(agentName: string, agentConfig: AgentConfig): Promise<void> {
    try {
      const configPath = this.config.agentsConfigPath;
      const config = await fs.readJson(configPath);

      config.agents[agentName] = {
        ...agentConfig,
        lastUpdated: new Date().toISOString()
      };

      config.registry.lastUpdated = new Date().toISOString();

      await fs.writeJson(configPath, config, { spaces: 2 });
    } catch (error) {
      console.error(`Помилка збереження конфігурації агента ${agentName}:`, error);
    }
  }

  private async removeAgentConfig(agentName: string): Promise<void> {
    try {
      const configPath = this.config.agentsConfigPath;
      const config = await fs.readJson(configPath);

      delete config.agents[agentName];
      config.registry.lastUpdated = new Date().toISOString();

      await fs.writeJson(configPath, config, { spaces: 2 });
    } catch (error) {
      console.error(`Помилка видалення конфігурації агента ${agentName}:`, error);
    }
  }

  getRegistryHealth(): {
    totalAgents: number;
    runningAgents: number;
    healthyAgents: number;
    schedulerRunning: boolean;
  } {
    const statuses = this.getAllAgentStatuses();

    return {
      totalAgents: statuses.length,
      runningAgents: statuses.filter(s => s.isRunning).length,
      healthyAgents: statuses.filter(s => s.healthCheck).length,
      schedulerRunning: this.scheduler.isRunning()
    };
  }

  private log(message: string, level: 'info' | 'warn' | 'error' = 'info'): void {
    if (this.config.logLevel === 'error' && level !== 'error') return;
    if (this.config.logLevel === 'warn' && level === 'info') return;

    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [AgentRegistry] ${message}`;

    switch (level) {
      case 'error':
        console.error(logMessage);
        break;
      case 'warn':
        console.warn(logMessage);
        break;
      default:
        console.log(logMessage);
    }
  }
}