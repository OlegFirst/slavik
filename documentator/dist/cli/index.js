#!/usr/bin/env node
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const ServiceManager_1 = require("./ServiceManager");
async function main() {
    const args = process.argv.slice(2);
    const command = args[0];
    const subCommand = args[1];
    const cli = new ServiceManager_1.ServiceManagerCLI();
    await cli.initialize();
    try {
        switch (command) {
            case 'services':
                switch (subCommand) {
                    case 'list':
                        const filter = args[2] || 'all';
                        await cli.listServices(filter);
                        break;
                    case 'status':
                        if (!args[2]) {
                            console.error('❌ Вкажіть назву сервісу');
                            process.exit(1);
                        }
                        await cli.serviceStatus(args[2]);
                        break;
                    case 'enable':
                        if (!args[2]) {
                            console.error('❌ Вкажіть назву сервісу');
                            process.exit(1);
                        }
                        await cli.enableService(args[2]);
                        break;
                    case 'disable':
                        if (!args[2]) {
                            console.error('❌ Вкажіть назву сервісу');
                            process.exit(1);
                        }
                        await cli.disableService(args[2]);
                        break;
                    case 'start':
                        if (!args[2]) {
                            console.error('❌ Вкажіть назву сервісу');
                            process.exit(1);
                        }
                        await cli.startService(args[2]);
                        break;
                    case 'stop':
                        if (!args[2]) {
                            console.error('❌ Вкажіть назву сервісу');
                            process.exit(1);
                        }
                        await cli.stopService(args[2]);
                        break;
                    case 'health':
                        await cli.healthCheck();
                        break;
                    default:
                        showServicesHelp();
                }
                break;
            case 'config':
                switch (subCommand) {
                    case 'show':
                        await cli.showConfig();
                        break;
                    case 'init':
                        await cli.createDefaultConfig();
                        break;
                    default:
                        showConfigHelp();
                }
                break;
            case 'help':
            case '--help':
            case '-h':
                showHelp();
                break;
            default:
                console.error('❌ Невідома команда. Використайте "help" для допомоги.');
                process.exit(1);
        }
    }
    catch (error) {
        console.error('❌ Помилка:', error instanceof Error ? error.message : 'Невідома помилка');
        process.exit(1);
    }
}
function showHelp() {
    console.log(`
🏢 Digital Office CLI - Управління сервісами

Використання:
  digital-office <команда> [опції]

Команди:
  services          Управління сервісами
  config           Управління конфігурацією
  help             Показати цю довідку

Використайте "digital-office <команда> --help" для детальної інформації про команду.
`);
}
function showServicesHelp() {
    console.log(`
📋 Управління сервісами

Використання:
  digital-office services <підкоманда> [опції]

Підкоманди:
  list [фільтр]    Показати список сервісів (all|enabled|running|disabled)
  status <назва>   Показати статус сервісу
  enable <назва>   Увімкнути сервіс
  disable <назва>  Вимкнути сервіс
  start <назва>    Запустити сервіс
  stop <назва>     Зупинити сервіс
  health           Перевірка здоров'я всіх сервісів

Приклади:
  digital-office services list
  digital-office services list running
  digital-office services status documentator
  digital-office services enable documentator
  digital-office services start documentator
`);
}
function showConfigHelp() {
    console.log(`
⚙️ Управління конфігурацією

Використання:
  digital-office config <підкоманда>

Підкоманди:
  show             Показати поточну конфігурацію
  init             Створити файл конфігурації за замовчуванням

Приклади:
  digital-office config show
  digital-office config init
`);
}
if (require.main === module) {
    main().catch(error => {
        console.error('💥 Критична помилка:', error);
        process.exit(1);
    });
}
//# sourceMappingURL=index.js.map