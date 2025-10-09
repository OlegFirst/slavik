#!/usr/bin/env ts-node

import inquirer from 'inquirer';
import chalk from 'chalk';
import { setupEmailCredentials } from './prompts/email-setup';
import { setupAsanaIntegration } from './prompts/asana-setup';
import {
  clearConsole,
  printHeader,
  printSuccess,
  printError,
  printInfo
} from './utils/helpers';

async function main() {
  try {
    clearConsole();

    // Привітання
    printWelcome();

    // Вибір що налаштовувати
    const { setupOptions } = await inquirer.prompt([
      {
        type: 'checkbox',
        name: 'setupOptions',
        message: 'Що налаштовуємо?',
        choices: [
          {
            name: chalk.cyan('📧 Email (Gmail/Outlook/IMAP)') + chalk.gray(' - для Email Digest Agent'),
            value: 'email',
            checked: true
          },
          {
            name: chalk.cyan('📋 Asana') + chalk.gray(' - для створення завдань з email'),
            value: 'asana',
            checked: true
          }
        ],
        validate: (answer) => {
          if (answer.length === 0) {
            return 'Виберіть хоча б одну опцію';
          }
          return true;
        }
      }
    ]);

    console.log();

    // Налаштування Email
    if (setupOptions.includes('email')) {
      const emailConfig = await setupEmailCredentials();
      if (emailConfig) {
        printSuccess('Email налаштовано успішно!');
      }
    }

    // Налаштування Asana
    if (setupOptions.includes('asana')) {
      const asanaConfig = await setupAsanaIntegration();
      if (asanaConfig) {
        printSuccess('Asana налаштовано успішно!');
      }
    }

    // Завершення
    printCompletion();

  } catch (error) {
    console.log();
    if (error instanceof Error) {
      printError(`Помилка: ${error.message}`);
    } else {
      printError('Невідома помилка');
    }
    process.exit(1);
  }
}

function printWelcome() {
  console.log();
  console.log(chalk.cyan.bold('╔════════════════════════════════════════════════════════════╗'));
  console.log(chalk.cyan.bold('║                                                            ║'));
  console.log(chalk.cyan.bold('║          ') + chalk.white.bold('🚀 Digital Office Setup Wizard') + chalk.cyan.bold('              ║'));
  console.log(chalk.cyan.bold('║                                                            ║'));
  console.log(chalk.cyan.bold('║') + chalk.gray('        Інтерактивне налаштування Email та Asana         ') + chalk.cyan.bold('║'));
  console.log(chalk.cyan.bold('║                                                            ║'));
  console.log(chalk.cyan.bold('╚════════════════════════════════════════════════════════════╝'));
  console.log();

  printInfo(
    'Цей wizard допоможе налаштувати:\n' +
    '  • Email для моніторингу пошти (Gmail/Outlook/IMAP)\n' +
    '  • Asana для автоматичного створення завдань\n\n' +
    'Всі дані зберігаються локально у папці data/config/\n' +
    'і НІКОЛИ не передаються третім особам.'
  );
}

function printCompletion() {
  console.log();
  console.log(chalk.green.bold('═'.repeat(60)));
  console.log(chalk.green.bold('  ✅ Налаштування завершено!'));
  console.log(chalk.green.bold('═'.repeat(60)));
  console.log();
  console.log(chalk.white('Наступні кроки:'));
  console.log();
  console.log(chalk.gray('  1. Перевірте файли конфігурації:'));
  console.log(chalk.cyan('     • data/config/email-credentials.json'));
  console.log(chalk.cyan('     • data/integrations/config.json'));
  console.log();
  console.log(chalk.gray('  2. Налаштуйте Email Digest Agent:'));
  console.log(chalk.cyan('     • Відредагуйте src/agents/monitoring/email-digest/agent.json'));
  console.log(chalk.cyan('     • Змініть digest.sendTo на вашу пошту'));
  console.log();
  console.log(chalk.gray('  3. Зберіть проект:'));
  console.log(chalk.cyan('     npm run build'));
  console.log();
  console.log(chalk.gray('  4. Запустіть Digital Office Hub:'));
  console.log(chalk.cyan('     npm start hub'));
  console.log();
  console.log(chalk.gray('  5. Email Digest Agent запуститься о 16:00 по Київу'));
  console.log();
  console.log(chalk.yellow('  💡 Підказка: Для ручного тестування:'));
  console.log(chalk.cyan('     Використайте MCP tool "trigger_digest" в Claude Desktop'));
  console.log();
  console.log(chalk.green.bold('═'.repeat(60)));
  console.log();
  console.log(chalk.white('Дякуємо що використовуєте Digital Office! 🎉'));
  console.log();
}

// Точка входу
if (require.main === module) {
  main().catch((error) => {
    console.error(chalk.red('\n❌ Критична помилка:'), error);
    process.exit(1);
  });
}

export { main as runSetupWizard };
