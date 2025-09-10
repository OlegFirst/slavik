#!/usr/bin/env node

import { DigitalOfficeHub } from './core/DigitalOfficeHub';
import { DocumentatorService } from './services/documentator/DocumentatorService';
import { PMService } from './services/pm/PMService';
import { ApiServer } from './api/ApiServer';

async function main() {
  const args = process.argv.slice(2);
  const mode = args[0] || 'hub';

  try {
    switch (mode) {
      case 'hub':
        console.error('Запуск Digital Office Hub...');
        await startHub();
        break;
        
      case 'api':
        console.log('Запуск Digital Office API сервера...');
        const port = parseInt(process.env.PORT || '3000', 10);
        new ApiServer(port);
        break;
        
      case 'both':
        console.log('Запуск Hub та API серверів...');
        
        // Запуск API сервера
        const apiPort = parseInt(process.env.PORT || '3000', 10);
        new ApiServer(apiPort);
        
        // Запуск Hub
        console.error('Запуск Digital Office Hub...');
        await startHub();
        break;
        
      default:
        console.error('Невідомий режим. Доступні: hub, api, both');
        process.exit(1);
    }
  } catch (error) {
    console.error('Помилка запуску:', error);
    process.exit(1);
  }
}

async function startHub() {
  const hub = new DigitalOfficeHub();
  
  // Реєструємо сервіси
  const documentatorService = new DocumentatorService();
  await hub.registerService(documentatorService);
  
  const pmService = new PMService();
  await hub.registerService(pmService);
  
  // TODO: Тут можна додати інші сервіси
  // const calendarService = new CalendarService();
  // await hub.registerService(calendarService);
  
  // Запускаємо hub
  await hub.start();
  
  // Обробка сигналів для graceful shutdown
  process.on('SIGINT', async () => {
    console.error('\nОтримано сигнал SIGINT, зупиняємо Hub...');
    await hub.shutdown();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.error('Отримано сигнал SIGTERM, зупиняємо Hub...');
    await hub.shutdown();
    process.exit(0);
  });
}

if (require.main === module) {
  main().catch(error => {
    console.error('Критична помилка:', error);
    process.exit(1);
  });
}