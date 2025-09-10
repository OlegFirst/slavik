#!/usr/bin/env node
"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.setupDocumentator = setupDocumentator;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
const os = __importStar(require("os"));
async function setupDocumentator() {
    console.log('🚀 Documentator Setup');
    console.log('===================');
    try {
        // Створюємо папку projects в домашній директорії
        const projectsDir = path.join(os.homedir(), 'projects');
        await fs.ensureDir(projectsDir);
        console.log(`✅ Створено директорію: ${projectsDir}`);
        // Створюємо приклад проекту
        const exampleDir = path.join(projectsDir, 'example-reports');
        await fs.ensureDir(exampleDir);
        // Створюємо простий приклад шаблону
        const exampleTemplate = `# {{title}}

**Автор:** {{author}}
**Дата:** {{date|{{new Date().toLocaleDateString('uk-UA')}}}}

## Зміст

{{content|Основний зміст звіту}}

## Висновки

{{conclusions|Висновки будуть додані пізніше}}

---
*Створено за допомогою Documentator*`;
        await fs.writeFile(path.join(exampleDir, 'simple-report.md'), exampleTemplate);
        console.log(`✅ Створено приклад проекту: ${exampleDir}`);
        console.log(`✅ Додано шаблон: simple-report.md`);
        // Інструкції для Claude Desktop
        console.log('\n📋 Налаштування Claude Desktop:');
        console.log('================================');
        const configExample = {
            mcpServers: {
                documentator: {
                    command: "documentator"
                }
            }
        };
        console.log('Додайте це до вашого claude_desktop_config.json:');
        console.log(JSON.stringify(configExample, null, 2));
        console.log('\n📁 Розташування конфігурації:');
        if (process.platform === 'win32') {
            console.log(`Windows: %APPDATA%\\Claude\\claude_desktop_config.json`);
        }
        else if (process.platform === 'darwin') {
            console.log(`macOS: ~/Library/Application Support/Claude/claude_desktop_config.json`);
        }
        else {
            console.log(`Linux: ~/.config/claude/claude_desktop_config.json`);
        }
        console.log('\n🎯 Тестування:');
        console.log('==============');
        console.log('1. Перезапустіть Claude Desktop');
        console.log('2. Напишіть: "Покажи мені всі проекти"');
        console.log('3. Напишіть: "Проаналізуй проект example-reports"');
        console.log('\n✨ Готово! Ви можете почати створювати свої проекти в:');
        console.log(projectsDir);
    }
    catch (error) {
        console.error('❌ Помилка налаштування:', error);
        process.exit(1);
    }
}
if (require.main === module) {
    setupDocumentator();
}
//# sourceMappingURL=setup.js.map