// BCM AI DevOps VS Code Extension  
const vscode = require('vscode');
const axios = require('axios');

function activate(context) {
    console.log('🚀 BCM AI DevOps activated!');

    // Команда анализа конфигурации
    const analyzeConfig = vscode.commands.registerCommand('bcm.analyzeConfig', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('Откройте файл для анализа');
            return;
        }

        const content = editor.document.getText();
        const config = vscode.workspace.getConfiguration('bcm');
        const aiOrchestrator = config.get('aiOrchestrator');

        try {
            vscode.window.showInformationMessage('🧠 AI анализирует конфигурацию...');
            
            const response = await axios.post(`${aiOrchestrator}/claude/analyze-changes`, {
                changes: content,
                context: { type: 'docker-compose', file: editor.document.fileName }
            });

            const analysis = response.data.analysis;
            
            const panel = vscode.window.createWebviewPanel(
                'bcmAnalysis',
                '🧠 BCM AI Analysis',
                vscode.ViewColumn.Beside,
                {}
            );

            panel.webview.html = `
                <h1>🧠 AI Analysis Results</h1>
                <h2>📊 Risk: ${analysis.deployment_risk || 'Unknown'}</h2>
                <h2>🚀 Strategy: ${analysis.recommended_strategy || 'Standard'}</h2>
                <h2>⏱️ Time: ${analysis.estimated_deployment_time || 'N/A'}</h2>
                <h2>💡 Recommendations:</h2>
                <ul>
                    ${(analysis.optimizations || []).map(opt => `<li>${opt}</li>`).join('')}
                </ul>
                <p>🧠 Memory sources: ${analysis.memory_sources || 0}</p>
            `;
        } catch (error) {
            vscode.window.showErrorMessage(`AI analysis failed: ${error.message}`);
        }
    });

    // Команда чата с AI
    const chatAI = vscode.commands.registerCommand('bcm.chatAI', () => {
        const panel = vscode.window.createWebviewPanel(
            'bcmChat',
            '💬 BCM AI Chat',
            vscode.ViewColumn.Beside,
            { enableScripts: true }
        );

        panel.webview.html = `
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    .chat { height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-bottom: 20px; }
                    .message { margin-bottom: 10px; padding: 8px; border-radius: 5px; }
                    .user { background: #007acc; color: white; text-align: right; }
                    .ai { background: #f0f0f0; }
                </style>
            </head>
            <body>
                <h2>🧠 BCM AI DevOps Assistant</h2>
                <div class="chat" id="chat">
                    <div class="message ai">AI: Привет! Спрашивайте о развертывании, архитектуре, оптимизации!</div>
                </div>
                <input type="text" id="input" placeholder="Ваш вопрос..." style="width: 80%;">
                <button onclick="send()">Отправить</button>
                
                <script>
                    function send() {
                        const input = document.getElementById('input');
                        const chat = document.getElementById('chat');
                        const message = input.value;
                        
                        if (message) {
                            chat.innerHTML += '<div class="message user">Вы: ' + message + '</div>';
                            chat.innerHTML += '<div class="message ai">AI: Анализирую ваш запрос... 🤖</div>';
                            input.value = '';
                            chat.scrollTop = chat.scrollHeight;
                        }
                    }
                    
                    document.getElementById('input').addEventListener('keypress', (e) => {
                        if (e.key === 'Enter') send();
                    });
                </script>
            </body>
            </html>`;
    });

    context.subscriptions.push(analyzeConfig, chatAI);
    
    vscode.window.showInformationMessage('🧠 BCM AI DevOps ready! Команды: Ctrl+Shift+P → BCM AI');
}

function deactivate() {}

module.exports = { activate, deactivate };