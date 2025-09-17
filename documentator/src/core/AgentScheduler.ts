import { BaseAgent } from './BaseAgent';
import { ScheduleConfig, ScheduleType } from '../types/AgentInterface';

export class AgentScheduler {
  private agents: Map<string, BaseAgent> = new Map();
  private intervals: Map<string, NodeJS.Timeout> = new Map();
  private timeouts: Map<string, NodeJS.Timeout> = new Map();
  private running: boolean = false;

  async start(): Promise<void> {
    if (this.running) {
      console.log('AgentScheduler вже запущено');
      return;
    }

    this.running = true;
    console.log('AgentScheduler запущено');

    // Запускаємо всі зареєстровані агенти
    for (const agent of this.agents.values()) {
      await this.scheduleAgent(agent);
    }
  }

  async stop(): Promise<void> {
    if (!this.running) {
      return;
    }

    this.running = false;

    // Зупиняємо всі інтервали та таймаути
    for (const interval of this.intervals.values()) {
      clearInterval(interval);
    }

    for (const timeout of this.timeouts.values()) {
      clearTimeout(timeout);
    }

    this.intervals.clear();
    this.timeouts.clear();

    // Зупиняємо автономне виконання всіх агентів
    for (const agent of this.agents.values()) {
      await agent.stopAutonomousExecution();
    }

    console.log('AgentScheduler зупинено');
  }

  async registerAgent(agent: BaseAgent): Promise<void> {
    const agentName = agent.metadata.name;

    if (this.agents.has(agentName)) {
      throw new Error(`Агент ${agentName} вже зареєстровано`);
    }

    this.agents.set(agentName, agent);
    console.log(`Агент ${agentName} зареєстровано в планувальнику`);

    // Якщо планувальник запущено, одразу плануємо агента
    if (this.running) {
      await this.scheduleAgent(agent);
    }
  }

  async unregisterAgent(agentName: string): Promise<void> {
    const agent = this.agents.get(agentName);
    if (!agent) {
      return;
    }

    await this.unscheduleAgent(agentName);
    await agent.stopAutonomousExecution();
    this.agents.delete(agentName);

    console.log(`Агент ${agentName} видалено з планувальника`);
  }

  private async scheduleAgent(agent: BaseAgent): Promise<void> {
    const agentName = agent.metadata.name;
    const schedule = agent.getScheduleConfig();

    if (!schedule.enabled) {
      console.log(`Планування агента ${agentName} відключено`);
      return;
    }

    await agent.startAutonomousExecution();

    switch (schedule.type) {
      case ScheduleType.INTERVAL:
        this.scheduleInterval(agent, schedule);
        break;
      case ScheduleType.CRON:
        this.scheduleCron(agent, schedule);
        break;
      case ScheduleType.ONCE:
        this.scheduleOnce(agent, schedule);
        break;
      case ScheduleType.EVENT_DRIVEN:
        this.scheduleEventDriven(agent, schedule);
        break;
    }
  }

  private scheduleInterval(agent: BaseAgent, schedule: ScheduleConfig): void {
    const agentName = agent.metadata.name;
    const intervalMs = schedule.intervalMs || 60000; // 1 хвилина за замовчуванням

    console.log(`Планування агента ${agentName} з інтервалом ${intervalMs}мс`);

    const interval = setInterval(async () => {
      try {
        await agent.executeOnce();
      } catch (error) {
        console.error(`Помилка планованого виконання агента ${agentName}:`, error);

        if (schedule.stopOnError) {
          console.log(`Зупинка агента ${agentName} через помилку`);
          await this.unscheduleAgent(agentName);
        }
      }
    }, intervalMs);

    this.intervals.set(agentName, interval);

    // Встановлюємо час наступного виконання
    const nextExecution = new Date(Date.now() + intervalMs);
    agent.updateNextExecution(nextExecution);
  }

  private scheduleCron(agent: BaseAgent, schedule: ScheduleConfig): void {
    const agentName = agent.metadata.name;
    console.log(`Cron планування для агента ${agentName} поки не реалізовано`);
    // TODO: Додати cron-parser для підтримки cron виразів
  }

  private scheduleOnce(agent: BaseAgent, schedule: ScheduleConfig): void {
    const agentName = agent.metadata.name;
    const delay = schedule.delayMs || 0;

    console.log(`Планування одноразового виконання агента ${agentName} через ${delay}мс`);

    const timeout = setTimeout(async () => {
      try {
        await agent.executeOnce();
        await this.unscheduleAgent(agentName);
      } catch (error) {
        console.error(`Помилка одноразового виконання агента ${agentName}:`, error);
      }
    }, delay);

    this.timeouts.set(agentName, timeout);

    // Встановлюємо час виконання
    const nextExecution = new Date(Date.now() + delay);
    agent.updateNextExecution(nextExecution);
  }

  private scheduleEventDriven(agent: BaseAgent, schedule: ScheduleConfig): void {
    const agentName = agent.metadata.name;
    console.log(`Event-driven планування для агента ${agentName} поки не реалізовано`);
    // TODO: Додати систему подій для event-driven агентів
  }

  private async unscheduleAgent(agentName: string): Promise<void> {
    // Очищаємо інтервал
    const interval = this.intervals.get(agentName);
    if (interval) {
      clearInterval(interval);
      this.intervals.delete(agentName);
    }

    // Очищаємо таймаут
    const timeout = this.timeouts.get(agentName);
    if (timeout) {
      clearTimeout(timeout);
      this.timeouts.delete(agentName);
    }

    console.log(`Планування агента ${agentName} скасовано`);
  }

  getScheduledAgents(): string[] {
    return Array.from(this.agents.keys());
  }

  getAgentStatus(agentName: string) {
    const agent = this.agents.get(agentName);
    return agent ? agent.getAgentStatus() : null;
  }

  async executeAgentNow(agentName: string): Promise<void> {
    const agent = this.agents.get(agentName);
    if (!agent) {
      throw new Error(`Агент ${agentName} не знайдено`);
    }

    await agent.executeOnce();
  }

  async pauseAgent(agentName: string): Promise<void> {
    await this.unscheduleAgent(agentName);
    const agent = this.agents.get(agentName);
    if (agent) {
      await agent.stopAutonomousExecution();
    }
  }

  async resumeAgent(agentName: string): Promise<void> {
    const agent = this.agents.get(agentName);
    if (!agent) {
      throw new Error(`Агент ${agentName} не знайдено`);
    }

    await this.scheduleAgent(agent);
  }

  isRunning(): boolean {
    return this.running;
  }
}