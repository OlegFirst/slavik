import { DigitalOfficeService, ServiceMetadata, ServiceStatus } from '../types/ServiceInterface';
import { Tool } from '@modelcontextprotocol/sdk/types.js';

export abstract class BaseService implements DigitalOfficeService {
  public abstract metadata: ServiceMetadata;
  private initialized: boolean = false;
  private healthy: boolean = false;

  async initialize(): Promise<void> {
    if (this.initialized) {
      console.log(`Сервіс ${this.metadata.name} вже ініціалізовано`);
      return;
    }

    try {
      await this.onInitialize();
      this.initialized = true;
      this.healthy = true;
      console.log(`Сервіс ${this.metadata.name} v${this.metadata.version} ініціалізовано`);
    } catch (error) {
      this.healthy = false;
      throw error;
    }
  }

  async shutdown(): Promise<void> {
    if (!this.initialized) {
      return;
    }

    try {
      await this.onShutdown();
      this.initialized = false;
      this.healthy = false;
      console.log(`Сервіс ${this.metadata.name} зупинено`);
    } catch (error) {
      console.error(`Помилка зупинки сервісу ${this.metadata.name}:`, error);
      throw error;
    }
  }

  async isHealthy(): Promise<boolean> {
    if (!this.initialized) {
      return false;
    }

    try {
      const customHealthCheck = await this.performHealthCheck();
      this.healthy = customHealthCheck;
      return this.healthy;
    } catch (error) {
      this.healthy = false;
      return false;
    }
  }

  getStatus(): ServiceStatus {
    return {
      name: this.metadata.name,
      enabled: true, // Буде встановлено ServiceRegistry
      running: this.initialized,
      healthCheck: this.healthy,
      lastStarted: this.initialized ? new Date() : undefined
    };
  }

  protected abstract onInitialize(): Promise<void>;
  
  protected abstract onShutdown(): Promise<void>;
  
  protected async performHealthCheck(): Promise<boolean> {
    // За замовчуванням, якщо сервіс ініціалізовано - він здоровий
    return this.initialized;
  }

  // Методи для інструментів - можуть бути перевизначені в підкласах
  public getTools(): Tool[] {
    return [];
  }

  public async handleToolCall(toolName: string, args: any): Promise<any> {
    throw new Error(`Tool ${toolName} not implemented in ${this.metadata.name}`);
  }
}