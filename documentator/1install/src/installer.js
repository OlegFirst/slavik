const { ipcRenderer } = require('electron');

// Поточний крок інсталятора
let currentStep = 0;
const steps = ['welcome', 'system-check', 'config', 'install', 'complete'];

// Системна інформація
let systemInfo = null;

// Ініціалізація інсталятора
document.addEventListener('DOMContentLoaded', () => {
  console.log('Installer loaded');
  showStep(0);
  setupEventListeners();
});

// Налаштування слухачів подій
function setupEventListeners() {
  // IPC події
  ipcRenderer.on('installation-progress', (event, data) => {
    updateInstallationProgress(data);
  });

  ipcRenderer.on('installation-log', (event, data) => {
    appendLog(data);
  });

  // Події інтерфейсу
  document.addEventListener('change', (e) => {
    if (e.target.type === 'checkbox') {
      updateConfigFromUI();
    }
  });
}

// Відображення кроку
function showStep(stepIndex) {
  // Приховати всі екрани
  document.querySelectorAll('.screen').forEach(screen => {
    screen.classList.remove('active');
  });

  // Показати поточний екран
  const currentScreen = document.getElementById(`${steps[stepIndex]}-screen`);
  if (currentScreen) {
    currentScreen.classList.add('active');
  }

  // Оновити кнопки навігації
  updateNavigationButtons();

  // Виконати специфічні дії для кроку
  switch (steps[stepIndex]) {
    case 'system-check':
      checkSystem();
      break;
    case 'config':
      loadConfiguration();
      break;
    case 'install':
      // Приховати кнопки навігації, показати кнопку встановлення
      break;
  }

  currentStep = stepIndex;
}

// Оновлення кнопок навігації
function updateNavigationButtons() {
  const backBtn = document.getElementById('back-btn');
  const nextBtn = document.getElementById('next-btn');
  const installBtn = document.getElementById('install-btn');
  const finishBtn = document.getElementById('finish-btn');

  // Скинути видимість всіх кнопок
  [nextBtn, installBtn, finishBtn].forEach(btn => btn.style.display = 'none');

  // Кнопка "Назад"
  backBtn.disabled = currentStep === 0;

  // Кнопки залежно від кроку
  switch (steps[currentStep]) {
    case 'welcome':
    case 'system-check':
    case 'config':
      nextBtn.style.display = 'inline-block';
      break;
    case 'install':
      installBtn.style.display = 'inline-block';
      break;
    case 'complete':
      finishBtn.style.display = 'inline-block';
      break;
  }
}

// Наступний крок
function nextStep() {
  if (currentStep < steps.length - 1) {
    showStep(currentStep + 1);
  }
}

// Попередній крок
function previousStep() {
  if (currentStep > 0) {
    showStep(currentStep - 1);
  }
}

// Перевірка системи
async function checkSystem() {
  try {
    setSystemCheckStatus('loading');
    systemInfo = await ipcRenderer.invoke('get-system-info');
    displaySystemInfo(systemInfo);
    setSystemCheckStatus('completed');
  } catch (error) {
    console.error('System check failed:', error);
    setSystemCheckStatus('error');
  }
}

// Встановлення статусу перевірки системи
function setSystemCheckStatus(status) {
  const statusElements = document.querySelectorAll('.dep-status .status-icon');

  switch (status) {
    case 'loading':
      statusElements.forEach(el => {
        el.textContent = '⏳';
        el.className = 'status-icon';
      });
      break;
    case 'completed':
      // Статуси оновлюються в displaySystemInfo
      break;
    case 'error':
      statusElements.forEach(el => {
        el.textContent = '❌';
        el.className = 'status-icon status-error';
      });
      break;
  }
}

// Відображення системної інформації
function displaySystemInfo(info) {
  // Основна інформація
  document.getElementById('os-info').textContent = `${info.platform} ${info.arch}`;
  document.getElementById('arch-info').textContent = info.arch;
  document.getElementById('disk-space').textContent =
    `${info.diskSpace.free} GB вільно (потрібно ${info.diskSpace.required} GB)`;

  // Node.js
  const nodeStatus = document.getElementById('node-status').querySelector('.status-icon');
  const nodeVersion = document.getElementById('node-version');
  if (info.nodeInstalled) {
    nodeStatus.textContent = '✅';
    nodeStatus.className = 'status-icon status-ok';
    nodeVersion.textContent = info.nodeVersionSystem;
  } else {
    nodeStatus.textContent = '❌';
    nodeStatus.className = 'status-icon status-error';
    nodeVersion.textContent = 'Не встановлено';
    // Автоматично увімкнути опцію встановлення
    document.getElementById('opt-nodejs').checked = true;
  }

  // Git
  const gitStatus = document.getElementById('git-status').querySelector('.status-icon');
  const gitVersion = document.getElementById('git-version');
  if (info.gitInstalled) {
    gitStatus.textContent = '✅';
    gitStatus.className = 'status-icon status-ok';
    gitVersion.textContent = 'Встановлено';
  } else {
    gitStatus.textContent = '⚠️';
    gitStatus.className = 'status-icon status-warning';
    gitVersion.textContent = 'Не обов\'язково';
  }

  // Claude Desktop
  const claudeStatus = document.getElementById('claude-status').querySelector('.status-icon');
  const claudePath = document.getElementById('claude-path');
  if (info.claudeConfigPath) {
    claudeStatus.textContent = '✅';
    claudeStatus.className = 'status-icon status-ok';
    claudePath.textContent = 'Знайдено';
  } else {
    claudeStatus.textContent = '⚠️';
    claudeStatus.className = 'status-icon status-warning';
    claudePath.textContent = 'Не знайдено';
    // Вимкнути автоналаштування
    document.getElementById('opt-claude').checked = false;
  }

  // Перевірка мінімальних вимог
  checkMinimumRequirements(info);
}

// Перевірка мінімальних вимог
function checkMinimumRequirements(info) {
  const requirements = [];

  if (!info.nodeInstalled) {
    requirements.push('Node.js потрібен для роботи Digital Office Hub');
  }

  if (info.diskSpace.free < info.diskSpace.required) {
    requirements.push(`Недостатньо вільного місця. Потрібно ${info.diskSpace.required} GB`);
  }

  if (requirements.length > 0) {
    showWarningDialog('Попередження', requirements.join('\n\n'));
  }
}

// Завантаження конфігурації
function loadConfiguration() {
  if (systemInfo) {
    // Встановити шлях за замовчуванням
    document.getElementById('install-path').value = systemInfo.suggestedPath;

    // Налаштувати опції
    document.getElementById('opt-claude').disabled = !systemInfo.claudeConfigPath;
    if (!systemInfo.claudeConfigPath) {
      document.getElementById('opt-claude').checked = false;
    }
  }
}

// Вибір шляху встановлення
async function selectPath() {
  try {
    const path = await ipcRenderer.invoke('select-install-path');
    if (path) {
      document.getElementById('install-path').value = path;
      updateConfigFromUI();
    }
  } catch (error) {
    console.error('Path selection failed:', error);
  }
}

// Оновлення конфігурації з UI
function updateConfigFromUI() {
  const config = {
    installPath: document.getElementById('install-path').value,
    createDesktopShortcut: document.getElementById('opt-desktop').checked,
    createStartMenuShortcut: document.getElementById('opt-startmenu').checked,
    configureClaude: document.getElementById('opt-claude').checked,
    installNodejs: document.getElementById('opt-nodejs').checked,
    components: {
      core: document.getElementById('comp-core').checked,
      agents: document.getElementById('comp-agents').checked,
      integrations: document.getElementById('comp-integrations').checked,
      examples: document.getElementById('comp-examples').checked
    }
  };

  ipcRenderer.invoke('update-config', config);
}

// Початок встановлення
async function startInstallation() {
  try {
    // Оновити конфігурацію
    updateConfigFromUI();

    // Приховати кнопку встановлення
    document.getElementById('install-btn').style.display = 'none';

    // Почати встановлення
    const result = await ipcRenderer.invoke('start-installation');

    if (result.success) {
      // Перейти до екрану завершення
      document.getElementById('final-path').textContent =
        document.getElementById('install-path').value;
      document.getElementById('claude-configured').textContent =
        document.getElementById('opt-claude').checked ? 'Налаштовано' : 'Пропущено';

      showStep(4); // complete screen
      showSuccessMessage(result.message);
    } else {
      showErrorMessage(result.message);
      // Показати кнопку встановлення знову
      document.getElementById('install-btn').style.display = 'inline-block';
    }
  } catch (error) {
    console.error('Installation failed:', error);
    showErrorMessage('Помилка встановлення: ' + error.message);
    document.getElementById('install-btn').style.display = 'inline-block';
  }
}

// Оновлення прогресу встановлення
function updateInstallationProgress(data) {
  const stepElement = document.getElementById(`step-${data.step}`);
  if (!stepElement) return;

  const icon = stepElement.querySelector('.step-icon');
  const status = stepElement.querySelector('.step-status');

  // Очистити попередні класи
  stepElement.className = 'install-step';

  switch (data.status) {
    case 'running':
      stepElement.classList.add('running');
      icon.textContent = '⏳';
      status.textContent = 'Виконується...';
      updateProgressBar(data.step);
      updateProgressText(data.message);
      break;
    case 'completed':
      stepElement.classList.add('completed');
      icon.textContent = '✅';
      status.textContent = 'Завершено';
      break;
    case 'error':
      stepElement.classList.add('error');
      icon.textContent = '❌';
      status.textContent = 'Помилка';
      appendLog(`ПОМИЛКА: ${data.error || 'Невідома помилка'}`);
      break;
  }
}

// Оновлення прогрес-бару
function updateProgressBar(step) {
  const stepOrder = [
    'create-dirs', 'copy-files', 'install-deps',
    'compile', 'configure-claude', 'create-shortcuts', 'register'
  ];

  const currentIndex = stepOrder.indexOf(step);
  const progress = ((currentIndex + 1) / stepOrder.length) * 100;

  document.getElementById('progress-fill').style.width = `${progress}%`;
}

// Оновлення тексту прогресу
function updateProgressText(message) {
  document.getElementById('progress-text').textContent = message;
}

// Додавання в журнал
function appendLog(message) {
  const logOutput = document.getElementById('log-output');
  const timestamp = new Date().toLocaleTimeString();
  logOutput.textContent += `[${timestamp}] ${message}\n`;

  // Прокрутити вниз
  logOutput.scrollTop = logOutput.scrollHeight;
}

// Запуск додатку
async function launchApp() {
  try {
    await ipcRenderer.invoke('launch-app');
    showSuccessMessage('Digital Office Hub запущено!');

    // Затримка перед закриттям
    setTimeout(() => {
      closeInstaller();
    }, 2000);
  } catch (error) {
    console.error('Launch failed:', error);
    showErrorMessage('Не вдалося запустити додаток: ' + error.message);
  }
}

// Відкрити папку встановлення
async function openFolder() {
  try {
    await ipcRenderer.invoke('open-install-folder');
  } catch (error) {
    console.error('Open folder failed:', error);
  }
}

// Закрити інсталятор
async function closeInstaller() {
  await ipcRenderer.invoke('close-installer');
}

// Управління вікном
function minimizeWindow() {
  // Electron автоматично обробляє мінімізацію
}

function closeWindow() {
  closeInstaller();
}

// Повідомлення
function showSuccessMessage(message) {
  showNotification(message, 'success');
}

function showErrorMessage(message) {
  showNotification(message, 'error');
}

function showWarningDialog(title, message) {
  showNotification(`${title}: ${message}`, 'warning');
}

function showNotification(message, type = 'info') {
  // Створюємо повідомлення
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;

  // Стилі для повідомлення
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    border-radius: 4px;
    color: white;
    font-weight: 500;
    z-index: 9999;
    max-width: 300px;
    word-wrap: break-word;
    animation: slideIn 0.3s ease-out;
  `;

  // Кольори залежно від типу
  switch (type) {
    case 'success':
      notification.style.background = '#4caf50';
      break;
    case 'error':
      notification.style.background = '#f44336';
      break;
    case 'warning':
      notification.style.background = '#ff9800';
      break;
    default:
      notification.style.background = '#2196f3';
  }

  // Додати CSS анімацію
  if (!document.querySelector('#notification-styles')) {
    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = `
      @keyframes slideIn {
        from {
          transform: translateX(100%);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }

      @keyframes slideOut {
        from {
          transform: translateX(0);
          opacity: 1;
        }
        to {
          transform: translateX(100%);
          opacity: 0;
        }
      }
    `;
    document.head.appendChild(style);
  }

  // Додати на сторінку
  document.body.appendChild(notification);

  // Видалити через 5 секунд
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease-in';
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }, 5000);

  // Видалити при кліку
  notification.addEventListener('click', () => {
    notification.style.animation = 'slideOut 0.3s ease-in';
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  });
}