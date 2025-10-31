#!/usr/bin/env node

/**
 * NASH 4.0 Digital Twin - One-Click Setup
 * Автоматическая настройка для Claude Desktop
 */

import inquirer from 'inquirer';
import chalk from 'chalk';
import ora from 'ora';
import fs from 'fs/promises';
import path from 'path';
import os from 'os';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

class SetupWizard {
    constructor() {
        this.platform = process.platform;
        this.configPath = this.getConfigPath();
        this.nash4Dir = path.join(os.homedir(), '.nash4');
    }

    getConfigPath() {
        switch (this.platform) {
            case 'darwin': // macOS
                return path.join(
                    os.homedir(),
                    'Library',
                    'Application Support',
                    'Claude',
                    'claude_desktop_config.json'
                );
            case 'win32': // Windows
                return path.join(
                    process.env.APPDATA,
                    'Claude',
                    'claude_desktop_config.json'
                );
            case 'linux':
                return path.join(
                    os.homedir(),
                    '.config',
                    'Claude',
                    'claude_desktop_config.json'
                );
            default:
                throw new Error('Unsupported platform');
        }
    }

    async run() {
        console.clear();
        console.log(chalk.cyan.bold(`
╔════════════════════════════════════════════╗
║     NASH 4.0 Digital Twin MCP Setup       ║
║        Настройка для Claude Desktop        ║
╚════════════════════════════════════════════╝
        `));

        try {
            // Step 1: Check Claude Desktop
            await this.checkClaudeDesktop();

            // Step 2: Get setup preferences
            const answers = await this.askQuestions();

            // Step 3: Setup authentication if needed
            if (answers.needsAuth) {
                await this.setupAuthentication(answers);
            }

            // Step 4: Configure MCP
            await this.configureMCP(answers);

            // Step 5: Test connection
            if (answers.testConnection) {
                await this.testConnection(answers);
            }

            // Success!
            this.showSuccess(answers);

        } catch (error) {
            console.error(chalk.red('Setup failed:'), error.message);
            process.exit(1);
        }
    }

    async checkClaudeDesktop() {
        const spinner = ora('Checking Claude Desktop installation...').start();
        
        try {
            // Check if config directory exists
            const configDir = path.dirname(this.configPath);
            await fs.access(configDir);
            spinner.succeed('Claude Desktop found');
        } catch {
            spinner.fail('Claude Desktop not found');
            
            const { install } = await inquirer.prompt([{
                type: 'confirm',
                name: 'install',
                message: 'Claude Desktop not detected. Open download page?',
                default: true
            }]);

            if (install) {
                const openCmd = this.platform === 'darwin' ? 'open' : 
                               this.platform === 'win32' ? 'start' : 'xdg-open';
                await execAsync(`${openCmd} https://claude.ai/download`);
                console.log(chalk.yellow('Please install Claude Desktop and run setup again.'));
                process.exit(0);
            }
        }
    }

    async askQuestions() {
        return inquirer.prompt([
            {
                type: 'list',
                name: 'mode',
                message: 'Select setup mode / Выберите режим:',
                choices: [
                    { name: '🚀 Quick Setup (Demo Mode)', value: 'demo' },
                    { name: '🏢 Organization Setup', value: 'org' },
                    { name: '🔧 Custom Configuration', value: 'custom' }
                ]
            },
            {
                type: 'confirm',
                name: 'needsAuth',
                message: 'Enable authentication? (Required for real organizations)',
                default: false,
                when: (answers) => answers.mode !== 'demo'
            },
            {
                type: 'input',
                name: 'organizationName',
                message: 'Organization name:',
                when: (answers) => answers.mode === 'org'
            },
            {
                type: 'input',
                name: 'email',
                message: 'Admin email:',
                when: (answers) => answers.needsAuth,
                validate: (input) => {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    return emailRegex.test(input) || 'Please enter a valid email';
                }
            },
            {
                type: 'password',
                name: 'password',
                message: 'Create password (min 8 characters):',
                when: (answers) => answers.needsAuth,
                validate: (input) => input.length >= 8 || 'Password must be at least 8 characters'
            },
            {
                type: 'input',
                name: 'apiUrl',
                message: 'API URL:',
                default: 'http://localhost:3000',
                when: (answers) => answers.mode === 'custom'
            },
            {
                type: 'confirm',
                name: 'localSetup',
                message: 'Setup local Digital Twin server?',
                default: true,
                when: (answers) => answers.mode !== 'custom'
            },
            {
                type: 'confirm',
                name: 'testConnection',
                message: 'Test connection after setup?',
                default: true
            }
        ]);
    }

    async setupAuthentication(answers) {
        const spinner = ora('Setting up authentication...').start();

        try {
            // Create .nash4 directory
            await fs.mkdir(this.nash4Dir, { recursive: true });

            // Save auth config
            const authConfig = {
                email: answers.email,
                organizationName: answers.organizationName,
                createdAt: new Date().toISOString()
            };

            await fs.writeFile(
                path.join(this.nash4Dir, 'auth.json'),
                JSON.stringify(authConfig, null, 2)
            );

            // Note: In production, this would register with actual auth service
            spinner.succeed('Authentication configured');
        } catch (error) {
            spinner.fail('Authentication setup failed');
            throw error;
        }
    }

    async configureMCP(answers) {
        const spinner = ora('Configuring MCP connector...').start();

        try {
            // Create config directory if needed
            const configDir = path.dirname(this.configPath);
            await fs.mkdir(configDir, { recursive: true });

            // Read existing config or create new
            let config = {};
            try {
                const existing = await fs.readFile(this.configPath, 'utf8');
                config = JSON.parse(existing);
            } catch {
                config = { mcpServers: {} };
            }

            // Determine the connector path
            const connectorPath = answers.mode === 'custom' && answers.apiUrl ? 
                path.join(__dirname, 'index.js') :
                path.join(__dirname, 'index.js');

            // Add our MCP server
            config.mcpServers = config.mcpServers || {};
            config.mcpServers['nash-digital-twin'] = {
                command: 'node',
                args: [connectorPath],
                env: this.buildEnvConfig(answers)
            };

            // Save config
            await fs.writeFile(this.configPath, JSON.stringify(config, null, 2));

            // Save NASH config
            const nashConfig = {
                apiUrl: answers.apiUrl || 'http://localhost:3000',
                mode: answers.mode,
                auth: {
                    enabled: answers.needsAuth || false,
                    email: answers.email
                },
                features: {
                    experiments: 30,
                    adapters: ['simpy', 'mesa', 'epinow2', 'anylogic'],
                    scenarios: 22,
                    engines: 4
                }
            };

            await fs.writeFile(
                path.join(this.nash4Dir, 'digital-twin-config.json'),
                JSON.stringify(nashConfig, null, 2)
            );

            spinner.succeed('MCP connector configured');
        } catch (error) {
            spinner.fail('Configuration failed');
            throw error;
        }
    }

    buildEnvConfig(answers) {
        const env = {
            NODE_ENV: 'production',
            DIGITAL_TWIN_MODE: answers.mode
        };

        if (answers.apiUrl) {
            env.DIGITAL_TWIN_API = answers.apiUrl;
        }

        if (answers.needsAuth) {
            env.DIGITAL_TWIN_AUTH = 'enabled';
        }

        // Add adapter URLs if local setup
        if (answers.localSetup) {
            env.SIMPY_ADAPTER_URL = 'http://localhost:7001/run';
            env.MESA_ADAPTER_URL = 'http://localhost:7002/run';
            env.EPINOW2_ADAPTER_URL = 'http://localhost:7003/run';
            env.ANYLOGIC_ADAPTER_URL = 'http://localhost:7004/run';
        }

        return env;
    }

    async testConnection(answers) {
        const spinner = ora('Testing connection...').start();

        try {
            const apiUrl = answers.apiUrl || 'http://localhost:3000';
            const response = await fetch(`${apiUrl}/health`);
            
            if (response.ok) {
                spinner.succeed('Connection successful');
            } else {
                spinner.warn('Server not responding (may need to start it)');
            }
        } catch {
            spinner.warn('Server not running - start it with: npm start');
        }
    }

    showSuccess(answers) {
        console.log(chalk.green.bold('\n✅ Setup Complete!\n'));

        if (answers.mode === 'demo') {
            console.log(chalk.cyan('Demo Mode Instructions:'));
            console.log('1. Restart Claude Desktop');
            console.log('2. Look for the MCP icon in the bottom bar');
            console.log('3. Try: "Show me all 30 experiments"');
            console.log('4. Try: "Run demo with Hope Foundation"');
        } else if (answers.mode === 'org') {
            console.log(chalk.cyan(`Organization "${answers.organizationName}" Setup:`));
            console.log('1. Start the Digital Twin server: npm start');
            console.log('2. Restart Claude Desktop');
            console.log('3. Try: "Create my organization digital twin"');
            console.log('4. Try: "Run crisis simulation"');
        } else {
            console.log(chalk.cyan('Custom Configuration:'));
            console.log(`API endpoint: ${answers.apiUrl}`);
            console.log('MCP connector configured in Claude Desktop');
        }

        console.log(chalk.yellow('\n📚 Documentation:'));
        console.log('• Quick Start: https://nash4.digital-twin.org/quickstart');
        console.log('• All Experiments: https://nash4.digital-twin.org/experiments');
        console.log('• Support: support@nash4.org');

        console.log(chalk.magenta('\n🎯 Example Commands for Claude:'));
        console.log('• "Analyze my organization efficiency"');
        console.log('• "Run budget optimization simulation"');
        console.log('• "Predict donor behavior for next quarter"');
        console.log('• "Generate impact passport"');
        console.log('• "Run all 30 experiments showcase"');

        if (answers.localSetup && answers.mode !== 'custom') {
            console.log(chalk.blue('\n💡 Local Server:'));
            console.log('Start with: cd digital-twin-standalone && npm start');
        }
    }
}

// Run setup
const wizard = new SetupWizard();
wizard.run().catch(console.error);