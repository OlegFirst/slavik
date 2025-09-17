import * as fs from 'fs-extra';
import * as path from 'path';
import { BaseAgent } from './BaseAgent';
import { AgentRegistry } from './AgentRegistry';
import { EventBus } from './EventBus';
import { ScheduleType } from '../types/AgentInterface';

export interface AgentManifest {
  name: string;
  version: string;
  description: string;
  category: string;
  entryPoint: string;
  className: string;
  dependencies?: string[];
  config?: Record<string, any>;
  autoStart?: boolean;
  enabled?: boolean;
}

export interface LoadedAgent {
  manifest: AgentManifest;
  agentClass: typeof BaseAgent;
  instance?: BaseAgent;
  loadedAt: Date;
  error?: string;
}

export class AgentLoader {
  private agentsPath: string;
  private loadedAgents: Map<string, LoadedAgent> = new Map();
  private registry: AgentRegistry;
  private eventBus: EventBus;
  private watchMode: boolean = false;
  private watcher: fs.FSWatcher | null = null;

  constructor(agentsPath: string, registry: AgentRegistry) {
    this.agentsPath = agentsPath;
    this.registry = registry;
    this.eventBus = EventBus.getInstance();
  }

  async initialize(): Promise<void> {
    await fs.ensureDir(this.agentsPath);
    await this.createDefaultStructure();
    console.log(`[AgentLoader] Ініціалізовано з шляхом: ${this.agentsPath}`);
  }

  async loadAllAgents(): Promise<Map<string, LoadedAgent>> {
    console.log('[AgentLoader] Завантаження всіх агентів...');

    const categories = await this.getAgentCategories();

    for (const category of categories) {
      const categoryPath = path.join(this.agentsPath, category);
      const agents = await this.loadAgentsFromCategory(categoryPath, category);

      for (const [name, agent] of agents) {
        this.loadedAgents.set(name, agent);
      }
    }

    await this.instantiateEnabledAgents();

    this.eventBus.publishSync('agentloader.loaded', 'AgentLoader', {
      totalAgents: this.loadedAgents.size,
      agents: Array.from(this.loadedAgents.keys())
    });

    console.log(`[AgentLoader] Завантажено ${this.loadedAgents.size} агентів`);
    return this.loadedAgents;
  }

  async loadAgent(manifestPath: string): Promise<LoadedAgent | null> {
    try {
      if (!await fs.pathExists(manifestPath)) {
        console.error(`[AgentLoader] Маніфест не знайдено: ${manifestPath}`);
        return null;
      }

      const manifest: AgentManifest = await fs.readJson(manifestPath);
      const agentDir = path.dirname(manifestPath);
      const entryPointPath = path.join(agentDir, manifest.entryPoint);

      if (!await fs.pathExists(entryPointPath)) {
        throw new Error(`Entry point не знайдено: ${entryPointPath}`);
      }

      delete require.cache[require.resolve(entryPointPath)];
      const agentModule = require(entryPointPath);
      const AgentClass = agentModule[manifest.className] || agentModule.default;

      if (!AgentClass) {
        throw new Error(`Клас ${manifest.className} не знайдено в ${manifest.entryPoint}`);
      }

      const loadedAgent: LoadedAgent = {
        manifest,
        agentClass: AgentClass as any,
        loadedAt: new Date()
      };

      console.log(`[AgentLoader] Завантажено агент: ${manifest.name}`);
      return loadedAgent;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Невідома помилка';
      console.error(`[AgentLoader] Помилка завантаження агента:`, error);

      return {
        manifest: { name: 'unknown' } as AgentManifest,
        agentClass: class extends BaseAgent {
          public metadata = { name: 'unknown', version: '1.0.0', description: 'Unknown agent', category: 'unknown' };
          getScheduleConfig() { return { type: ScheduleType.ONCE, enabled: false }; }
          async executeAutonomously() {}
          getTools() { return []; }
          async handleToolCall() { throw new Error('Not implemented'); }
          protected async onInitialize() {}
          protected async onShutdown() {}
        } as any,
        loadedAt: new Date(),
        error: errorMessage
      };
    }
  }

  async instantiateAgent(agentName: string): Promise<BaseAgent | null> {
    const loadedAgent = this.loadedAgents.get(agentName);

    if (!loadedAgent) {
      console.error(`[AgentLoader] Агент ${agentName} не завантажено`);
      return null;
    }

    if (loadedAgent.error) {
      console.error(`[AgentLoader] Агент ${agentName} має помилку: ${loadedAgent.error}`);
      return null;
    }

    try {
      const config = {
        enabled: loadedAgent.manifest.enabled !== false,
        ...loadedAgent.manifest.config
      };

      const instance = new (loadedAgent.agentClass as any)(config);
      loadedAgent.instance = instance;

      await this.registry.registerAgent(instance);

      this.eventBus.publishSync('agentloader.instantiated', 'AgentLoader', {
        agentName,
        manifest: loadedAgent.manifest
      });

      console.log(`[AgentLoader] Створено екземпляр агента: ${agentName}`);
      return instance;

    } catch (error) {
      console.error(`[AgentLoader] Помилка створення агента ${agentName}:`, error);
      loadedAgent.error = error instanceof Error ? error.message : 'Помилка створення';
      return null;
    }
  }

  async reloadAgent(agentName: string): Promise<boolean> {
    const loadedAgent = this.loadedAgents.get(agentName);

    if (!loadedAgent) {
      console.error(`[AgentLoader] Агент ${agentName} не знайдено`);
      return false;
    }

    try {
      if (loadedAgent.instance) {
        await this.registry.unregisterAgent(agentName);
        loadedAgent.instance = undefined;
      }

      const manifestPath = await this.findAgentManifest(agentName);
      if (!manifestPath) {
        throw new Error(`Маніфест для ${agentName} не знайдено`);
      }

      const reloadedAgent = await this.loadAgent(manifestPath);
      if (!reloadedAgent) {
        throw new Error(`Не вдалося перезавантажити ${agentName}`);
      }

      this.loadedAgents.set(agentName, reloadedAgent);

      if (reloadedAgent.manifest.autoStart || reloadedAgent.manifest.enabled) {
        await this.instantiateAgent(agentName);
      }

      this.eventBus.publishSync('agentloader.reloaded', 'AgentLoader', {
        agentName,
        success: true
      });

      console.log(`[AgentLoader] Перезавантажено агент: ${agentName}`);
      return true;

    } catch (error) {
      console.error(`[AgentLoader] Помилка перезавантаження ${agentName}:`, error);
      return false;
    }
  }

  async unloadAgent(agentName: string): Promise<boolean> {
    const loadedAgent = this.loadedAgents.get(agentName);

    if (!loadedAgent) {
      return false;
    }

    try {
      if (loadedAgent.instance) {
        await this.registry.unregisterAgent(agentName);
      }

      this.loadedAgents.delete(agentName);

      this.eventBus.publishSync('agentloader.unloaded', 'AgentLoader', {
        agentName
      });

      console.log(`[AgentLoader] Вивантажено агент: ${agentName}`);
      return true;

    } catch (error) {
      console.error(`[AgentLoader] Помилка вивантаження ${agentName}:`, error);
      return false;
    }
  }

  async startWatching(): Promise<void> {
    if (this.watchMode) {
      console.log('[AgentLoader] Вже в режимі спостереження');
      return;
    }

    this.watchMode = true;
    this.watcher = fs.watch(this.agentsPath, { recursive: true }, async (eventType, filename) => {
      if (filename && filename.endsWith('agent.json')) {
        console.log(`[AgentLoader] Виявлено зміни в ${filename}`);

        const manifestPath = path.join(this.agentsPath, filename);
        const agentName = await this.getAgentNameFromManifest(manifestPath);

        if (agentName) {
          if (await fs.pathExists(manifestPath)) {
            await this.reloadAgent(agentName);
          } else {
            await this.unloadAgent(agentName);
          }
        }
      }
    });

    console.log('[AgentLoader] Режим спостереження активовано');
  }

  async stopWatching(): Promise<void> {
    if (!this.watchMode || !this.watcher) {
      return;
    }

    this.watcher.close();
    this.watcher = null;
    this.watchMode = false;

    console.log('[AgentLoader] Режим спостереження деактивовано');
  }

  getLoadedAgents(): LoadedAgent[] {
    return Array.from(this.loadedAgents.values());
  }

  getAgentInfo(agentName: string): LoadedAgent | undefined {
    return this.loadedAgents.get(agentName);
  }

  isAgentLoaded(agentName: string): boolean {
    return this.loadedAgents.has(agentName);
  }

  getAgentsByCategory(category: string): LoadedAgent[] {
    return Array.from(this.loadedAgents.values())
      .filter(agent => agent.manifest.category === category);
  }

  private async createDefaultStructure(): Promise<void> {
    const categories = ['monitoring', 'automation', 'integration', 'analytics', 'custom'];

    for (const category of categories) {
      const categoryPath = path.join(this.agentsPath, category);
      await fs.ensureDir(categoryPath);

      const readmePath = path.join(categoryPath, 'README.md');
      if (!await fs.pathExists(readmePath)) {
        const readmeContent = `# ${category.charAt(0).toUpperCase() + category.slice(1)} Agents\n\n` +
          `This directory contains ${category} agents.\n\n` +
          `## Agent Structure\n\n` +
          `Each agent should have:\n` +
          `- \`agent.json\` - Agent manifest file\n` +
          `- \`index.ts\` or \`index.js\` - Agent implementation\n` +
          `- \`README.md\` - Agent documentation (optional)\n`;

        await fs.writeFile(readmePath, readmeContent);
      }
    }
  }

  private async getAgentCategories(): Promise<string[]> {
    const entries = await fs.readdir(this.agentsPath, { withFileTypes: true });
    return entries
      .filter(entry => entry.isDirectory())
      .map(entry => entry.name);
  }

  private async loadAgentsFromCategory(
    categoryPath: string,
    category: string
  ): Promise<Map<string, LoadedAgent>> {
    const agents = new Map<string, LoadedAgent>();
    const entries = await fs.readdir(categoryPath, { withFileTypes: true });

    for (const entry of entries) {
      if (entry.isDirectory()) {
        const manifestPath = path.join(categoryPath, entry.name, 'agent.json');

        if (await fs.pathExists(manifestPath)) {
          const agent = await this.loadAgent(manifestPath);

          if (agent && !agent.error) {
            agents.set(agent.manifest.name, agent);
          }
        }
      }
    }

    return agents;
  }

  private async instantiateEnabledAgents(): Promise<void> {
    for (const [name, agent] of this.loadedAgents) {
      if ((agent.manifest.autoStart || agent.manifest.enabled) && !agent.error) {
        await this.instantiateAgent(name);
      }
    }
  }

  private async findAgentManifest(agentName: string): Promise<string | null> {
    const categories = await this.getAgentCategories();

    for (const category of categories) {
      const categoryPath = path.join(this.agentsPath, category);
      const entries = await fs.readdir(categoryPath, { withFileTypes: true });

      for (const entry of entries) {
        if (entry.isDirectory()) {
          const manifestPath = path.join(categoryPath, entry.name, 'agent.json');

          if (await fs.pathExists(manifestPath)) {
            const manifest: AgentManifest = await fs.readJson(manifestPath);

            if (manifest.name === agentName) {
              return manifestPath;
            }
          }
        }
      }
    }

    return null;
  }

  private async getAgentNameFromManifest(manifestPath: string): Promise<string | null> {
    try {
      if (await fs.pathExists(manifestPath)) {
        const manifest: AgentManifest = await fs.readJson(manifestPath);
        return manifest.name;
      }
    } catch (error) {
      console.error(`[AgentLoader] Помилка читання маніфесту ${manifestPath}:`, error);
    }

    return null;
  }
}