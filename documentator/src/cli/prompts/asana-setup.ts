import inquirer from 'inquirer';
import chalk from 'chalk';
import {
  validateAsanaToken,
  validateAsanaWorkspaceGid,
  validateAsanaProjectGid,
  validateEmail,
  validateNotEmpty,
  createInquirerValidator
} from '../utils/validators';
import {
  printHeader,
  printInstructions,
  printConfigSummary,
  saveAsanaConfig,
  checkExistingConfig
} from '../utils/helpers';

export interface AsanaConfig {
  token: string;
  defaultWorkspace: string;
  workspaceName: string;
  defaultProject: string;
  defaultAssignee: string;
}

export async function setupAsanaIntegration(): Promise<AsanaConfig | null> {
  printHeader('📋 Налаштування Asana');

  // Перевіряємо чи вже є конфіг
  const hasExisting = await checkExistingConfig('asana');
  if (hasExisting) {
    const { overwrite } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'overwrite',
        message: chalk.yellow('Asana вже налаштовано. Перезаписати?'),
        default: false
      }
    ]);

    if (!overwrite) {
      console.log(chalk.gray('Налаштування Asana пропущено'));
      return null;
    }
  }

  console.log();
  console.log(chalk.cyan.bold('🔧 Інтеграція з Asana'));
  console.log();

  printInstructions('Як отримати Asana Personal Access Token:', [
    'Перейдіть на https://app.asana.com/',
    'Натисніть на ваше фото профілю (правий верхній кут)',
    'Оберіть "My Settings"',
    'Перейдіть на вкладку "Apps"',
    'Прокрутіть вниз до "Personal access tokens"',
    'Натисніть "+ Create new token"',
    'Введіть опис (наприклад: "Digital Office Email Agent")',
    'Натисніть "Create token"',
    'Скопіюйте токен (його можна побачити тільки один раз!)'
  ]);

  const { token } = await inquirer.prompt([
    {
      type: 'password',
      name: 'token',
      message: 'Asana Personal Access Token:',
      mask: '*',
      validate: createInquirerValidator(validateAsanaToken)
    }
  ]);

  console.log();
  console.log(chalk.green('✅ Токен валідний!'));
  console.log();

  printInstructions('Як знайти Workspace GID:', [
    'Відкрийте Asana у браузері',
    'Перейдіть до потрібного Workspace',
    'Подивіться на URL: https://app.asana.com/0/WORKSPACE_GID/...',
    'WORKSPACE_GID - це довге число після першого "0/"',
    '',
    'Або:',
    '1. Відкрийте Dev Tools (F12)',
    '2. В консолі виконайте:',
    '   fetch("https://app.asana.com/api/1.0/workspaces", {',
    '     headers: {"Authorization": "Bearer YOUR_TOKEN"}',
    '   }).then(r => r.json()).then(console.log)',
    '3. Знайдіть потрібний workspace та скопіюйте його "gid"'
  ]);

  const { defaultWorkspace, workspaceName } = await inquirer.prompt([
    {
      type: 'input',
      name: 'defaultWorkspace',
      message: 'Workspace GID (довге число):',
      validate: createInquirerValidator(validateAsanaWorkspaceGid)
    },
    {
      type: 'input',
      name: 'workspaceName',
      message: 'Назва Workspace (для зручності):',
      validate: createInquirerValidator((v) => validateNotEmpty(v, 'Назва Workspace'))
    }
  ]);

  console.log();

  printInstructions('Як знайти Project GID:', [
    'Відкрийте потрібний проект в Asana',
    'Подивіться на URL: https://app.asana.com/0/PROJECT_GID/...',
    'PROJECT_GID - це друге довге число в URL',
    '',
    'Або створіть новий проект:',
    '1. Натисніть "+" у лівому меню',
    '2. Оберіть "Project"',
    '3. Створіть проект з назвою "Email Tasks"',
    '4. Після створення скопіюйте GID з URL'
  ]);

  const { defaultProject, defaultAssignee } = await inquirer.prompt([
    {
      type: 'input',
      name: 'defaultProject',
      message: 'Project GID (для створення завдань):',
      validate: createInquirerValidator(validateAsanaProjectGid)
    },
    {
      type: 'input',
      name: 'defaultAssignee',
      message: 'Email виконавця за замовчуванням:',
      validate: createInquirerValidator(validateEmail)
    }
  ]);

  const config: AsanaConfig = {
    token,
    defaultWorkspace,
    workspaceName,
    defaultProject,
    defaultAssignee
  };

  // Підсумок
  printConfigSummary(config, 'asana');

  // Підтвердження
  const { confirm } = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'confirm',
      message: 'Зберегти ці налаштування?',
      default: true
    }
  ]);

  if (!confirm) {
    console.log(chalk.yellow('Налаштування Asana скасовано'));
    return null;
  }

  // Збереження
  await saveAsanaConfig(config);

  return config;
}
