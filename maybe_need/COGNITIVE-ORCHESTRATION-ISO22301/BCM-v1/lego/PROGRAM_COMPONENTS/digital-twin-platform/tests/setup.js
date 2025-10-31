/**
 * Jest Setup для NASH 4.0 Digital Twin
 */

// Мокаем внешние сервисы
jest.mock('node:fs/promises');
jest.mock('sqlite3');

// Глобальные переменные для тестов
global.TEST_ENV = true;
global.MOCK_MODE = true;

// Увеличиваем таймаут для долгих операций
jest.setTimeout(30000);

// Подавляем логи в тестах
console.log = jest.fn();
console.info = jest.fn();
console.warn = jest.fn();

// Очистка после каждого теста
afterEach(() => {
    jest.clearAllMocks();
});

console.log('🧪 Test environment initialized');
