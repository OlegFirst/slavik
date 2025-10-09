import inquirer from 'inquirer';
import chalk from 'chalk';
import {
  validateEmail,
  validateGoogleClientId,
  validateGoogleClientSecret,
  validateGoogleRefreshToken,
  validateOutlookTenantId,
  validateOutlookClientId,
  validateOutlookClientSecret,
  validateImapHost,
  validateImapPort,
  validatePassword,
  validateNotEmpty,
  createInquirerValidator
} from '../utils/validators';
import {
  printHeader,
  printInstructions,
  printConfigSummary,
  saveEmailCredentials,
  checkExistingConfig
} from '../utils/helpers';

export interface EmailConfig {
  provider: 'gmail' | 'outlook' | 'imap';
  email: string;
  clientId?: string;
  clientSecret?: string;
  refreshToken?: string;
  tenantId?: string;
  host?: string;
  port?: number;
  secure?: boolean;
  username?: string;
  password?: string;
}

export async function setupEmailCredentials(): Promise<EmailConfig | null> {
  printHeader('📧 Налаштування Email');

  // Перевіряємо чи вже є конфіг
  const hasExisting = await checkExistingConfig('email');
  if (hasExisting) {
    const { overwrite } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'overwrite',
        message: chalk.yellow('Email вже налаштовано. Перезаписати?'),
        default: false
      }
    ]);

    if (!overwrite) {
      console.log(chalk.gray('Налаштування email пропущено'));
      return null;
    }
  }

  // Вибір провайдера
  const { provider } = await inquirer.prompt([
    {
      type: 'list',
      name: 'provider',
      message: 'Виберіть провайдера email:',
      choices: [
        {
          name: chalk.cyan('Gmail') + chalk.gray(' (рекомендовано)'),
          value: 'gmail'
        },
        {
          name: chalk.cyan('Outlook / Office 365'),
          value: 'outlook'
        },
        {
          name: chalk.cyan('Інший (IMAP)'),
          value: 'imap'
        }
      ]
    }
  ]);

  let config: EmailConfig;

  switch (provider) {
    case 'gmail':
      config = await setupGmail();
      break;
    case 'outlook':
      config = await setupOutlook();
      break;
    case 'imap':
      config = await setupImap();
      break;
    default:
      throw new Error('Невідомий провайдер');
  }

  // Підсумок
  printConfigSummary(config, 'email');

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
    console.log(chalk.yellow('Налаштування email скасовано'));
    return null;
  }

  // Збереження
  await saveEmailCredentials(config);

  return config;
}

async function setupGmail(): Promise<EmailConfig> {
  console.log();
  console.log(chalk.cyan.bold('📬 Gmail OAuth2 налаштування'));
  console.log();

  printInstructions('Як отримати Google OAuth credentials:', [
    'Перейдіть на https://console.cloud.google.com/',
    'Створіть новий проект або виберіть існуючий',
    'Увімкніть Gmail API в розділі "Library"',
    'Створіть OAuth 2.0 Client ID (тип: Desktop app)',
    'Завантажте credentials.json',
    'Використайте OAuth Playground для отримання refresh token:',
    '  https://developers.google.com/oauthplayground/',
    '  - Оберіть "Gmail API v1" → scope: https://mail.google.com/',
    '  - Натисніть "Authorize APIs"',
    '  - Обміняйте authorization code на токени',
    '  - Скопіюйте Refresh Token'
  ]);

  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'email',
      message: 'Введіть ваш Gmail адрес:',
      validate: createInquirerValidator(validateEmail)
    },
    {
      type: 'input',
      name: 'clientId',
      message: 'Client ID (з Google Cloud Console):',
      validate: createInquirerValidator(validateGoogleClientId)
    },
    {
      type: 'password',
      name: 'clientSecret',
      message: 'Client Secret:',
      mask: '*',
      validate: createInquirerValidator(validateGoogleClientSecret)
    },
    {
      type: 'password',
      name: 'refreshToken',
      message: 'Refresh Token (з OAuth Playground):',
      mask: '*',
      validate: createInquirerValidator(validateGoogleRefreshToken)
    }
  ]);

  return {
    provider: 'gmail',
    ...answers
  };
}

async function setupOutlook(): Promise<EmailConfig> {
  console.log();
  console.log(chalk.cyan.bold('📬 Outlook / Office 365 налаштування'));
  console.log();

  printInstructions('Як отримати Outlook credentials:', [
    'Перейдіть на https://portal.azure.com/',
    'Зареєструйте додаток в Azure Active Directory',
    'Запишіть Application (client) ID та Directory (tenant) ID',
    'Створіть Client Secret в "Certificates & secrets"',
    'Додайте Mail.Read permissions в "API permissions"',
    'Детальна інструкція:',
    '  https://docs.microsoft.com/en-us/graph/auth-v2-service'
  ]);

  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'email',
      message: 'Введіть ваш Outlook/Office 365 адрес:',
      validate: createInquirerValidator(validateEmail)
    },
    {
      type: 'input',
      name: 'tenantId',
      message: 'Directory (tenant) ID (формат UUID):',
      validate: createInquirerValidator(validateOutlookTenantId)
    },
    {
      type: 'input',
      name: 'clientId',
      message: 'Application (client) ID (формат UUID):',
      validate: createInquirerValidator(validateOutlookClientId)
    },
    {
      type: 'password',
      name: 'clientSecret',
      message: 'Client Secret:',
      mask: '*',
      validate: createInquirerValidator(validateOutlookClientSecret)
    }
  ]);

  return {
    provider: 'outlook',
    ...answers
  };
}

async function setupImap(): Promise<EmailConfig> {
  console.log();
  console.log(chalk.cyan.bold('📬 IMAP налаштування'));
  console.log();

  printInstructions('Популярні IMAP налаштування:', [
    'Gmail: imap.gmail.com:993 (потрібен App Password)',
    'Outlook: outlook.office365.com:993',
    'Yahoo: imap.mail.yahoo.com:993',
    'Якщо використовуєте 2FA - створіть app-specific password',
    '',
    'Для Gmail App Password:',
    '  1. Увімкніть 2-Step Verification',
    '  2. Перейдіть на https://myaccount.google.com/apppasswords',
    '  3. Створіть App Password для "Mail"',
    '  4. Використайте згенерований 16-символьний пароль'
  ]);

  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'email',
      message: 'Введіть ваш email адрес:',
      validate: createInquirerValidator(validateEmail)
    },
    {
      type: 'input',
      name: 'host',
      message: 'IMAP сервер (наприклад: imap.gmail.com):',
      validate: createInquirerValidator(validateImapHost)
    },
    {
      type: 'input',
      name: 'port',
      message: 'IMAP порт:',
      default: '993',
      validate: createInquirerValidator(validateImapPort)
    },
    {
      type: 'confirm',
      name: 'secure',
      message: 'Використовувати SSL/TLS?',
      default: true
    },
    {
      type: 'input',
      name: 'username',
      message: 'Username (зазвичай ваш email):',
      default: (answers: any) => answers.email,
      validate: createInquirerValidator((v) => validateNotEmpty(v, 'Username'))
    },
    {
      type: 'password',
      name: 'password',
      message: 'Пароль (або App Password):',
      mask: '*',
      validate: createInquirerValidator(validatePassword)
    }
  ]);

  return {
    provider: 'imap',
    email: answers.email,
    host: answers.host,
    port: parseInt(answers.port, 10),
    secure: answers.secure,
    username: answers.username,
    password: answers.password
  };
}
