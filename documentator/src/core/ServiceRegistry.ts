import { DigitalOfficeService, ServiceStatus, ServiceConfig } from '../types/ServiceInterface';
import * as fs from 'fs-extra';
import * as path from 'path';

export class ServiceRegistry {
  private services: Map<string, DigitalOfficeService> = new Map();
  private serviceStatuses: Map<string, ServiceStatus> = new Map();
  private configPath: string;

  constructor(configPath?: string) {
    this.configPath = configPath || path.join(process.cwd(), 'digital-office-config.json');
  }

  async registerService(service: DigitalOfficeService): Promise<void> {
    const serviceName = service.metadata.name;
    
    if (this.services.has(serviceName)) {
      throw new Error(`Сервіс ${serviceName} вже зареєстровано`);
    }

    this.services.set(serviceName, service);
    this.serviceStatuses.set(serviceName, {
      name: serviceName,
      enabled: await this.isServiceEnabled(serviceName),
      running: false,
      healthCheck: false
    });

    console.log(`Сервіс ${serviceName} зареєстровано`);
  }

  async unregisterService(serviceName: string): Promise<void> {
    const service = this.services.get(serviceName);
    if (service) {
      await this.stopService(serviceName);
      this.services.delete(serviceName);
      this.serviceStatuses.delete(serviceName);
      console.log(`Сервіс ${serviceName} відреєстровано`);
    }
  }

  async startService(serviceName: string): Promise<void> {
    const service = this.services.get(serviceName);
    const status = this.serviceStatuses.get(serviceName);

    if (!service || !status) {
      throw new Error(`Сервіс ${serviceName} не знайдено`);
    }

    if (!status.enabled) {
      throw new Error(`Сервіс ${serviceName} відключено в конфігурації`);
    }

    if (status.running) {
      console.log(`Сервіс ${serviceName} вже запущено`);
      return;
    }

    try {
      await service.initialize();
      status.running = true;
      status.lastStarted = new Date();
      status.lastError = undefined;
      console.log(`Сервіс ${serviceName} успішно запущено`);
    } catch (error) {
      status.lastError = error instanceof Error ? error.message : 'Невідома помилка';
      throw new Error(`Помилка запуску сервісу ${serviceName}: ${status.lastError}`);
    }
  }

  async stopService(serviceName: string): Promise<void> {
    const service = this.services.get(serviceName);
    const status = this.serviceStatuses.get(serviceName);

    if (!service || !status) {
      throw new Error(`Сервіс ${serviceName} не знайдено`);
    }

    if (!status.running) {
      console.log(`Сервіс ${serviceName} вже зупинено`);
      return;
    }

    try {
      await service.shutdown();
      status.running = false;
      console.log(`Сервіс ${serviceName} зупинено`);
    } catch (error) {
      status.lastError = error instanceof Error ? error.message : 'Невідома помилка';
      console.error(`Помилка зупинки сервісу ${serviceName}: ${status.lastError}`);
    }
  }

  async startAllEnabledServices(): Promise<void> {
    const enabledServices = Array.from(this.serviceStatuses.entries())
      .filter(([_, status]) => status.enabled)
      .map(([name, _]) => name);

    for (const serviceName of enabledServices) {
      try {
        await this.startService(serviceName);
      } catch (error) {
        console.error(`Не вдалося запустити сервіс ${serviceName}:`, error);
      }
    }
  }

  async stopAllServices(): Promise<void> {
    const runningServices = Array.from(this.serviceStatuses.entries())
      .filter(([_, status]) => status.running)
      .map(([name, _]) => name);

    for (const serviceName of runningServices) {
      await this.stopService(serviceName);
    }
  }

  async enableService(serviceName: string): Promise<void> {
    const status = this.serviceStatuses.get(serviceName);
    if (!status) {
      throw new Error(`Сервіс ${serviceName} не знайдено`);
    }

    status.enabled = true;
    await this.saveServiceConfig(serviceName, true);
    console.log(`Сервіс ${serviceName} увімкнено`);
  }

  async disableService(serviceName: string): Promise<void> {
    const status = this.serviceStatuses.get(serviceName);
    if (!status) {
      throw new Error(`Сервіс ${serviceName} не знайдено`);
    }

    if (status.running) {
      await this.stopService(serviceName);
    }

    status.enabled = false;
    await this.saveServiceConfig(serviceName, false);
    console.log(`Сервіс ${serviceName} вимкнено`);
  }

  getService(serviceName: string): DigitalOfficeService | undefined {
    return this.services.get(serviceName);
  }

  getAllServices(): DigitalOfficeService[] {
    return Array.from(this.services.values());
  }

  getEnabledServices(): DigitalOfficeService[] {
    return Array.from(this.services.entries())
      .filter(([name, _]) => this.serviceStatuses.get(name)?.enabled)
      .map(([_, service]) => service);
  }

  getRunningServices(): DigitalOfficeService[] {
    return Array.from(this.services.entries())
      .filter(([name, _]) => this.serviceStatuses.get(name)?.running)
      .map(([_, service]) => service);
  }

  getServiceStatus(serviceName: string): ServiceStatus | undefined {
    return this.serviceStatuses.get(serviceName);
  }

  getAllServiceStatuses(): ServiceStatus[] {
    return Array.from(this.serviceStatuses.values());
  }

  async performHealthChecks(): Promise<void> {
    for (const [serviceName, service] of this.services.entries()) {
      const status = this.serviceStatuses.get(serviceName);
      if (status && status.running) {
        try {
          status.healthCheck = await service.isHealthy();
        } catch (error) {
          status.healthCheck = false;
          status.lastError = error instanceof Error ? error.message : 'Health check failed';
        }
      }
    }
  }

  private async isServiceEnabled(serviceName: string): Promise<boolean> {
    try {
      const config = await this.loadConfig();
      const serviceConfig = config.services.find(s => s.name === serviceName);
      return serviceConfig?.enabled ?? true; // За замовчуванням увімкнено
    } catch (error) {
      return true; // За замовчуванням увімкнено, якщо конфіг не існує
    }
  }

  private async saveServiceConfig(serviceName: string, enabled: boolean): Promise<void> {
    try {
      const config = await this.loadConfig();
      const serviceIndex = config.services.findIndex(s => s.name === serviceName);
      
      if (serviceIndex >= 0) {
        config.services[serviceIndex].enabled = enabled;
      } else {
        config.services.push({ name: serviceName, enabled });
      }

      await fs.writeJson(this.configPath, config, { spaces: 2 });
    } catch (error) {
      console.error('Помилка збереження конфігурації:', error);
    }
  }

  private async loadConfig(): Promise<{ services: ServiceConfig[] }> {
    try {
      if (await fs.pathExists(this.configPath)) {
        return await fs.readJson(this.configPath);
      }
    } catch (error) {
      console.warn('Помилка завантаження конфігурації, використовуємо значення за замовчуванням');
    }

    return { services: [] };
  }
}