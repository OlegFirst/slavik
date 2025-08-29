#!/usr/bin/env node

import { McpServer } from './mcp/McpServer';
import { ApiServer } from './api/ApiServer';

async function main() {
  const args = process.argv.slice(2);
  const mode = args[0] || 'mcp';

  try {
    switch (mode) {
      case 'mcp':
        console.error('Запуск Documentator MCP сервера...');
        const mcpServer = new McpServer();
        await mcpServer.start();
        break;
        
      case 'api':
        console.log('Запуск Documentator API сервера...');
        const port = parseInt(process.env.PORT || '3000', 10);
        new ApiServer(port);
        break;
        
      case 'both':
        console.log('Запуск обох серверів...');
        
        const apiPort = parseInt(process.env.PORT || '3000', 10);
        new ApiServer(apiPort);
        
        console.error('Запуск MCP сервера...');
        const mcpBothServer = new McpServer();
        await mcpBothServer.start();
        break;
        
      default:
        console.error('Невідомий режим. Доступні: mcp, api, both');
        process.exit(1);
    }
  } catch (error) {
    console.error('Помилка запуску:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(error => {
    console.error('Критична помилка:', error);
    process.exit(1);
  });
}