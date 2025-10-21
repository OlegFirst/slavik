#!/usr/bin/env node

/**
 * NASH 4.0 Digital Twin CLI
 * Quick setup and management tool
 */

import { program } from 'commander';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';

const execAsync = promisify(exec);
const __dirname = path.dirname(fileURLToPath(import.meta.url));

program
    .name('nash-digital-twin')
    .description('NASH 4.0 Digital Twin MCP Connector')
    .version('1.0.0');

program
    .command('setup')
    .description('Setup MCP connector for Claude Desktop')
    .action(async () => {
        const setupPath = path.join(__dirname, '..', 'setup.js');
        await execAsync(`node ${setupPath}`);
    });

program
    .command('start')
    .description('Start MCP server')
    .action(async () => {
        const serverPath = path.join(__dirname, '..', 'index.js');
        await execAsync(`node ${serverPath}`);
    });

program
    .command('test')
    .description('Test connection to Digital Twin API')
    .action(async () => {
        try {
            const response = await fetch('http://localhost:3000/health');
            if (response.ok) {
                console.log(' Connection successful');
            } else {
                console.log(' Connection failed');
            }
        } catch (error) {
            console.log(' Server not running');
            console.log('Start with: npm start');
        }
    });

program.parse();