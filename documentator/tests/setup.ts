import * as fs from 'fs-extra';
import * as path from 'path';

// Налаштування тестового середовища
process.env.NODE_ENV = 'test';
process.env.JWT_SECRET = 'test-jwt-secret';
process.env.DATA_DIR = './test-data';

// Очищення тестових даних перед запуском тестів
beforeAll(async () => {
  const testDataDir = path.join(__dirname, '..', 'test-data');
  await fs.remove(testDataDir);
});

// Очищення після тестів
afterAll(async () => {
  const testDataDir = path.join(__dirname, '..', 'test-data');
  await fs.remove(testDataDir);
});