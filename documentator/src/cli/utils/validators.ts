import chalk from 'chalk';

export interface ValidationResult {
  valid: boolean;
  message?: string;
}

/**
 * Валідатор для email адрес
 */
export function validateEmail(email: string): ValidationResult {
  if (!email || email.trim().length === 0) {
    return {
      valid: false,
      message: chalk.red('Email не може бути порожнім')
    };
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return {
      valid: false,
      message: chalk.red('Невірний формат email адреси')
    };
  }

  return { valid: true };
}

/**
 * Валідатор для Google Client ID
 * Формат: xxxxx-xxxxx.apps.googleusercontent.com
 */
export function validateGoogleClientId(clientId: string): ValidationResult {
  if (!clientId || clientId.trim().length === 0) {
    return {
      valid: false,
      message: chalk.red('Client ID не може бути порожнім')
    };
  }

  if (!clientId.includes('googleusercontent.com')) {
    return {
      valid: false,
      message: chalk.red('Client ID повинен містити "googleusercontent.com"')
    };
  }

  return { valid: true };
}

/**
 * Валідатор для Google Client Secret
 * Зазвичай це рядок довжиною 24-35 символів
 */
export function validateGoogleClientSecret(secret: string): ValidationResult {
  if (!secret || secret.trim().length === 0) {
    return {
      valid: false,
      message: chalk.red('Client Secret не може бути порожнім')
    };
  }

  if (secret.length < 20) {
    return {
      valid: false,
      message: chalk.red('Client Secret занадто короткий (має бути мінімум 20 символів)')
    };
  }

  return { valid: true };
}

/**
 * Валідатор для Google Refresh Token
 * Зазвичай починається з "1//"
 */
export function validateGoogleRefreshToken(token: string): ValidationResult {
  if (!token || token.trim().length === 0) {
    return {
      valid: false,
      message: chalk.red('Refresh Token не може бути порожнім')
    };
  }

  if (token.length < 50) {
    return {
      valid: false,
      message: chalk.red('Refresh Token занадто короткий. Переконайтеся що скопіювали весь токен')
    };
  }

  return { valid: true };
}

/**
 * Валідатор для Outlook Tenant ID
 * Формат: UUID (8-4-4-4-12)
 */
export function validateOutlookTenantId(tenantId: string): ValidationResult {
  if (!tenantId || tenantId.trim().length === 0) {
    return {
      valid: false,
      message: chalk.red('Tenant ID не може бути порожнім')
    };
  }

  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(tenantId)) {
    return {
      valid: false,
      message: chalk.red('Tenant ID має бути у форматі UUID (8-4-4-4-12)')
    };
  }

  return { valid: true };
}

/**
 * Валідатор для Outlook Application (Client) ID
 * Формат: UUID
 */
export function validateOutlookClientId(clientId: string): ValidationResult {
  if (!clientId || clientId.trim().length === 0) {
    return {
      valid: false,
      message: chalk.red('Application (Client) ID не може бути порожнім')
    };
  }

  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(clientId)) {
    return {
      valid: false,
      message: chalk.red('Application ID має бути у форматі UUID (8-4-4-4-12)')
    };
  }

  return { valid: true };
}

/**
 * Валідатор для Outlook Client Secret
 */
export function validateOutlookClientSecret(secret: string): ValidationResult {
  if (!secret || secret.trim().length === 0) {
    return {
      valid: false,
      message: chalk.red('Client Secret не може бути порожнім')
    };
  }

  if (secret.length < 10) {
    return {
      valid: false,
      message: chalk.red('Client Secret занадто короткий')
    };
  }

  return { valid: true };
}

/**
 * Валідатор для IMAP host
 */
export function validateImapHost(host: string): ValidationResult {
  if (!host || host.trim().length === 0) {
    return {
      valid: false,
      message: chalk.red('IMAP host не може бути порожнім')
    };
  }

  // Перевіряємо що це схоже на домен
  const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-_.]+[a-zA-Z0-9]$/;
  if (!domainRegex.test(host)) {
    return {
      valid: false,
      message: chalk.red('Невірний формат IMAP host (наприклад: imap.gmail.com)')
    };
  }

  return { valid: true };
}

/**
 * Валідатор для IMAP port
 */
export function validateImapPort(portStr: string): ValidationResult {
  if (!portStr || portStr.trim().length === 0) {
    return {
      valid: false,
      message: chalk.red('IMAP port не може бути порожнім')
    };
  }

  const port = parseInt(portStr, 10);
  if (isNaN(port) || port < 1 || port > 65535) {
    return {
      valid: false,
      message: chalk.red('Port має бути числом від 1 до 65535')
    };
  }

  // Рекомендовані порти
  if (port !== 993 && port !== 143) {
    return {
      valid: true,
      message: chalk.yellow(`Зверніть увагу: стандартні IMAP порти - 993 (SSL) або 143 (без SSL)`)
    };
  }

  return { valid: true };
}

/**
 * Валідатор для паролів
 */
export function validatePassword(password: string): ValidationResult {
  if (!password || password.trim().length === 0) {
    return {
      valid: false,
      message: chalk.red('Пароль не може бути порожнім')
    };
  }

  if (password.length < 6) {
    return {
      valid: false,
      message: chalk.red('Пароль занадто короткий (мінімум 6 символів)')
    };
  }

  return { valid: true };
}

/**
 * Валідатор для Asana Personal Access Token
 * Формат: 1/xxxxxxx:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
 */
export function validateAsanaToken(token: string): ValidationResult {
  if (!token || token.trim().length === 0) {
    return {
      valid: false,
      message: chalk.red('Asana Personal Access Token не може бути порожнім')
    };
  }

  // Asana токени зазвичай починаються з "1/" або мають довжину близько 40+ символів
  if (!token.startsWith('1/') && token.length < 32) {
    return {
      valid: false,
      message: chalk.red('Схоже, що це не Asana Personal Access Token. Переконайтеся що скопіювали правильний токен')
    };
  }

  if (token.length < 30) {
    return {
      valid: false,
      message: chalk.red('Asana Token занадто короткий. Переконайтеся що скопіювали весь токен')
    };
  }

  return { valid: true };
}

/**
 * Валідатор для Asana Workspace GID
 * Формат: довге число (15-20 цифр)
 */
export function validateAsanaWorkspaceGid(gid: string): ValidationResult {
  if (!gid || gid.trim().length === 0) {
    return {
      valid: false,
      message: chalk.red('Workspace GID не може бути порожнім')
    };
  }

  // Асана використовує довгі числові GID
  const gidRegex = /^\d{10,20}$/;
  if (!gidRegex.test(gid)) {
    return {
      valid: false,
      message: chalk.red('Workspace GID має бути числом (10-20 цифр)')
    };
  }

  return { valid: true };
}

/**
 * Валідатор для Asana Project GID
 */
export function validateAsanaProjectGid(gid: string): ValidationResult {
  if (!gid || gid.trim().length === 0) {
    return {
      valid: false,
      message: chalk.red('Project GID не може бути порожнім')
    };
  }

  const gidRegex = /^\d{10,20}$/;
  if (!gidRegex.test(gid)) {
    return {
      valid: false,
      message: chalk.red('Project GID має бути числом (10-20 цифр)')
    };
  }

  return { valid: true };
}

/**
 * Валідатор для непорожніх рядків
 */
export function validateNotEmpty(value: string, fieldName: string = 'Поле'): ValidationResult {
  if (!value || value.trim().length === 0) {
    return {
      valid: false,
      message: chalk.red(`${fieldName} не може бути порожнім`)
    };
  }

  return { valid: true };
}

/**
 * Валідатор для URL
 */
export function validateUrl(url: string): ValidationResult {
  if (!url || url.trim().length === 0) {
    return {
      valid: false,
      message: chalk.red('URL не може бути порожнім')
    };
  }

  try {
    new URL(url);
    return { valid: true };
  } catch {
    return {
      valid: false,
      message: chalk.red('Невірний формат URL')
    };
  }
}

/**
 * Комбінований валідатор для inquirer
 * Повертає true якщо валідно, або повідомлення про помилку
 */
export function createInquirerValidator(validatorFn: (value: string) => ValidationResult) {
  return (input: string): boolean | string => {
    const result = validatorFn(input);
    return result.valid ? true : (result.message || 'Невірне значення');
  };
}
