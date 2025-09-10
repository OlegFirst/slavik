#!/usr/bin/env node
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const McpServer_1 = require("./mcp/McpServer");
const ApiServer_1 = require("./api/ApiServer");
async function main() {
    const args = process.argv.slice(2);
    const mode = args[0] || 'mcp';
    try {
        switch (mode) {
            case 'mcp':
                console.error('Запуск Documentator MCP сервера...');
                const mcpServer = new McpServer_1.McpServer();
                await mcpServer.start();
                break;
            case 'api':
                console.log('Запуск Documentator API сервера...');
                const port = parseInt(process.env.PORT || '3000', 10);
                new ApiServer_1.ApiServer(port);
                break;
            case 'both':
                console.log('Запуск обох серверів...');
                const apiPort = parseInt(process.env.PORT || '3000', 10);
                new ApiServer_1.ApiServer(apiPort);
                console.error('Запуск MCP сервера...');
                const mcpBothServer = new McpServer_1.McpServer();
                await mcpBothServer.start();
                break;
            default:
                console.error('Невідомий режим. Доступні: mcp, api, both');
                process.exit(1);
        }
    }
    catch (error) {
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
//# sourceMappingURL=index.js.map