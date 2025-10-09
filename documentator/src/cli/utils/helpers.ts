import * as fs from 'fs-extra';
import * as path from 'path';
import chalk from 'chalk';
import ora from 'ora';

/**
 * Отримує шлях до конфігураційної папки
 */
export function getConfigPath(): string {
  return path.join(process.cwd(), 'data', 'config');
}

/**
 * Отримує шлях до папки з інтеграціями
 */
export function getIntegrationsPath(): string {
  return path.join(process.cwd(), 'data', 'integrations');
}

/**
 * Зберігає email credentials
 */
export async function saveEmailCredentials(credentials: any): Promise<void> {
  const spinner = ora('Збереження налаштувань email...').start();

  try {
    const configPath = getConfigPath();
    await fs.ensureDir(configPath);

    const filePath = path.join(configPath, 'email-credentials.json');
    await fs.writeJson(filePath, credentials, { spaces: 2 });

    spinner.succeed(chalk.green('Email налаштування збережено!'));
    console.log(chalk.gray(`Файл: ${filePath}`));
  } catch (error) {
    spinner.fail(chalk.red('Помилка збереження email налаштувань'));
    throw error;
  }
}

/**
 * Завантажує існуючі email credentials (якщо є)
 */
export async function loadEmailCredentials(): Promise<any | null> {
  try {
    const filePath = path.join(getConfigPath(), 'email-credentials.json');
    if (await fs.pathExists(filePath)) {
      return await fs.readJson(filePath);
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Зберігає Asana налаштування в integrations config
 */
export async function saveAsanaConfig(asanaConfig: any): Promise<void> {
  const spinner = ora('Збереження налаштувань Asana...').start();

  try {
    const integrationsPath = getIntegrationsPath();
    await fs.ensureDir(integrationsPath);

    const filePath = path.join(integrationsPath, 'config.json');

    // Завантажуємо існуючий конфіг або створюємо новий
    let config: any = {};
    if (await fs.pathExists(filePath)) {
      config = await fs.readJson(filePath);
    }

    // Оновлюємо секцію taskManagement
    config.taskManagement = {
      provider: 'asana',
      ...asanaConfig
    };

    await fs.writeJson(filePath, config, { spaces: 2 });

    spinner.succeed(chalk.green('Asana налаштування збережено!'));
    console.log(chalk.gray(`Файл: ${filePath}`));
  } catch (error) {
    spinner.fail(chalk.red('Помилка збереження Asana налаштувань'));
    throw error;
  }
}

/**
 * Завантажує існуючі Asana налаштування (якщо є)
 */
export async function loadAsanaConfig(): Promise<any | null> {
  try {
    const filePath = path.join(getIntegrationsPath(), 'config.json');
    if (await fs.pathExists(filePath)) {
      const config = await fs.readJson(filePath);
      return config.taskManagement || null;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Виводить красивий заголовок
 */
export function printHeader(title: string): void {
  console.log();
  console.log(chalk.cyan.bold('═'.repeat(60)));
  console.log(chalk.cyan.bold(`  ${title}`));
  console.log(chalk.cyan.bold('═'.repeat(60)));
  console.log();
}

/**
 * Виводить інформаційне повідомлення в рамці
 */
export function printInfo(message: string): void {
  console.log();
  console.log(chalk.blue('┌' + '─'.repeat(58) + '┐'));
  message.split('\n').forEach(line => {
    console.log(chalk.blue('│ ') + line.padEnd(57) + chalk.blue('│'));
  });
  console.log(chalk.blue('└' + '─'.repeat(58) + '┘'));
  console.log();
}

/**
 * Виводить інструкції як отримати значення
 */
export function printInstructions(title: string, steps: string[]): void {
  console.log();
  console.log(chalk.yellow.bold(`📋 ${title}`));
  console.log();
  steps.forEach((step, index) => {
    console.log(chalk.gray(`   ${index + 1}. ${step}`));
  });
  console.log();
}

/**
 * Виводить success повідомлення
 */
export function printSuccess(message: string): void {
  console.log();
  console.log(chalk.green.bold('✅ ' + message));
  console.log();
}

/**
 * Виводить warning повідомлення
 */
export function printWarning(message: string): void {
  console.log();
  console.log(chalk.yellow.bold('⚠️  ' + message));
  console.log();
}

/**
 * Виводить error повідомлення
 */
export function printError(message: string): void {
  console.log();
  console.log(chalk.red.bold('❌ ' + message));
  console.log();
}

/**
 * Очищає консоль
 */
export function clearConsole(): void {
  console.clear();
}

/**
 * Пауза для читання
 */
export async function pause(ms: number = 1000): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Підсумок налаштувань
 */
export function printConfigSummary(config: any, type: 'email' | 'asana'): void {
  console.log();
  console.log(chalk.cyan.bold('📊 Підсумок налаштувань:'));
  console.log(chalk.gray('─'.repeat(60)));

  if (type === 'email') {
    console.log(chalk.white('  Провайдер:   ') + chalk.green(config.provider));
    console.log(chalk.white('  Email:       ') + chalk.green(config.email));

    if (config.provider === 'gmail') {
      console.log(chalk.white('  Client ID:   ') + chalk.gray(maskString(config.clientId)));
      console.log(chalk.white('  Secret:      ') + chalk.gray('***************************'));
      console.log(chalk.white('  Token:       ') + chalk.gray('***************************'));
    } else if (config.provider === 'outlook') {
      console.log(chalk.white('  Tenant ID:   ') + chalk.gray(config.tenantId));
      console.log(chalk.white('  Client ID:   ') + chalk.gray(config.clientId));
      console.log(chalk.white('  Secret:      ') + chalk.gray('***************************'));
    } else if (config.provider === 'imap') {
      console.log(chalk.white('  Host:        ') + chalk.green(config.host));
      console.log(chalk.white('  Port:        ') + chalk.green(config.port));
      console.log(chalk.white('  Username:    ') + chalk.green(config.username));
      console.log(chalk.white('  Password:    ') + chalk.gray('***************************'));
    }
  } else if (type === 'asana') {
    console.log(chalk.white('  Workspace:   ') + chalk.green(config.workspaceName || config.defaultWorkspace));
    console.log(chalk.white('  Project:     ') + chalk.green(config.defaultProject));
    console.log(chalk.white('  Assignee:    ') + chalk.green(config.defaultAssignee));
    console.log(chalk.white('  Token:       ') + chalk.gray('***************************'));
  }

  console.log(chalk.gray('─'.repeat(60)));
  console.log();
}

/**
 * Маскує чутливі дані
 */
function maskString(str: string, visibleChars: number = 4): string {
  if (!str || str.length <= visibleChars) {
    return '***';
  }

  const visible = str.substring(0, visibleChars);
  const masked = '*'.repeat(Math.min(20, str.length - visibleChars));
  return visible + masked;
}

/**
 * Відображає прогрес
 */
export class ProgressBar {
  private spinner: any;

  start(message: string): void {
    this.spinner = ora(message).start();
  }

  update(message: string): void {
    if (this.spinner) {
      this.spinner.text = message;
    }
  }

  succeed(message: string): void {
    if (this.spinner) {
      this.spinner.succeed(chalk.green(message));
    }
  }

  fail(message: string): void {
    if (this.spinner) {
      this.spinner.fail(chalk.red(message));
    }
  }

  stop(): void {
    if (this.spinner) {
      this.spinner.stop();
    }
  }
}

/**
 * Перевіряє чи файл вже існує та пропонує перезаписати
 */
export async function checkExistingConfig(type: 'email' | 'asana'): Promise<boolean> {
  if (type === 'email') {
    const existing = await loadEmailCredentials();
    return existing !== null;
  } else {
    const existing = await loadAsanaConfig();
    return existing !== null;
  }
}
