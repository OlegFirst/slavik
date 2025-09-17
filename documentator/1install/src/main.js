const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs').promises;
const { exec, spawn } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);
const os = require('os');
const sudo = require('sudo-prompt');

let mainWindow;
let installationPath = 'C:\\Program Files\\Digital Office Hub';
let installConfig = {
  installPath: installationPath,
  createDesktopShortcut: true,
  createStartMenuShortcut: true,
  configureClaude: true,
  installNodejs: false,
  installGit: false,
  components: {
    core: true,
    agents: true,
    integrations: true,
    examples: true
  }
};

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    icon: path.join(__dirname, '../assets/icon.ico'),
    resizable: false,
    frame: false,
    backgroundColor: '#1e1e1e'
  });

  mainWindow.loadFile(path.join(__dirname, 'installer.html'));

  // Developer tools для дебагу (видалити в продакшн)
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC Handlers

// Отримати системну інформацію
ipcMain.handle('get-system-info', async () => {
  const homeDir = os.homedir();
  const platform = os.platform();
  const arch = os.arch();
  const nodeVersion = process.version;

  // Перевірка наявності Node.js
  let nodeInstalled = false;
  let nodeVersionSystem = null;
  try {
    const { stdout } = await execPromise('node --version');
    nodeInstalled = true;
    nodeVersionSystem = stdout.trim();
  } catch (e) {
    nodeInstalled = false;
  }

  // Перевірка наявності Git
  let gitInstalled = false;
  try {
    await execPromise('git --version');
    gitInstalled = true;
  } catch (e) {
    gitInstalled = false;
  }

  // Пошук Claude Desktop config
  let claudeConfigPath = null;
  const possiblePaths = [
    path.join(homeDir, 'AppData', 'Roaming', 'Claude', 'claude_desktop_config.json'),
    path.join(homeDir, '.claude', 'claude_desktop_config.json'),
    path.join(homeDir, 'Library', 'Application Support', 'Claude', 'claude_desktop_config.json')
  ];

  for (const configPath of possiblePaths) {
    try {
      await fs.access(configPath);
      claudeConfigPath = configPath;
      break;
    } catch (e) {
      // Файл не знайдено
    }
  }

  return {
    platform,
    arch,
    homeDir,
    nodeInstalled,
    nodeVersionSystem,
    nodeVersionElectron: nodeVersion,
    gitInstalled,
    claudeConfigPath,
    suggestedPath: installationPath,
    diskSpace: await checkDiskSpace()
  };
});

// Перевірка вільного місця
async function checkDiskSpace() {
  if (process.platform === 'win32') {
    try {
      const { stdout } = await execPromise('wmic logicaldisk get size,freespace,caption');
      const lines = stdout.trim().split('\n').slice(1);
      for (const line of lines) {
        const parts = line.trim().split(/\s+/);
        if (parts[0] && parts[0].startsWith('C:')) {
          const free = parseInt(parts[1]) || 0;
          return {
            free: Math.floor(free / (1024 * 1024 * 1024)), // GB
            required: 0.5 // 500MB потрібно
          };
        }
      }
    } catch (e) {
      console.error('Disk space check failed:', e);
    }
  }
  return { free: 999, required: 0.5 };
}

// Вибір папки встановлення
ipcMain.handle('select-install-path', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory', 'createDirectory'],
    defaultPath: installConfig.installPath
  });

  if (!result.canceled && result.filePaths.length > 0) {
    installConfig.installPath = result.filePaths[0];
    return result.filePaths[0];
  }
  return null;
});

// Оновити конфігурацію
ipcMain.handle('update-config', async (event, config) => {
  installConfig = { ...installConfig, ...config };
  return true;
});

// Основний процес встановлення
ipcMain.handle('start-installation', async () => {
  const steps = [];

  try {
    // Крок 1: Створення директорій
    steps.push({ step: 'create-dirs', status: 'running', message: 'Створення директорій...' });
    mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);

    await createDirectories();
    steps[steps.length - 1].status = 'completed';
    mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);

    // Крок 2: Копіювання файлів
    steps.push({ step: 'copy-files', status: 'running', message: 'Копіювання файлів проекту...' });
    mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);

    await copyProjectFiles();
    steps[steps.length - 1].status = 'completed';
    mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);

    // Крок 3: Встановлення Node.js (якщо потрібно)
    if (installConfig.installNodejs) {
      steps.push({ step: 'install-node', status: 'running', message: 'Встановлення Node.js...' });
      mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);

      await installNodeJS();
      steps[steps.length - 1].status = 'completed';
      mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);
    }

    // Крок 4: Встановлення залежностей
    steps.push({ step: 'install-deps', status: 'running', message: 'Встановлення залежностей npm...' });
    mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);

    await installDependencies();
    steps[steps.length - 1].status = 'completed';
    mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);

    // Крок 5: Компіляція TypeScript
    steps.push({ step: 'compile', status: 'running', message: 'Компіляція TypeScript...' });
    mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);

    await compileTypeScript();
    steps[steps.length - 1].status = 'completed';
    mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);

    // Крок 6: Налаштування Claude Desktop
    if (installConfig.configureClaude) {
      steps.push({ step: 'configure-claude', status: 'running', message: 'Налаштування Claude Desktop...' });
      mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);

      await configureClaudeDesktop();
      steps[steps.length - 1].status = 'completed';
      mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);
    }

    // Крок 7: Створення ярликів
    if (installConfig.createDesktopShortcut || installConfig.createStartMenuShortcut) {
      steps.push({ step: 'create-shortcuts', status: 'running', message: 'Створення ярликів...' });
      mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);

      await createShortcuts();
      steps[steps.length - 1].status = 'completed';
      mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);
    }

    // Крок 8: Реєстрація в системі
    steps.push({ step: 'register', status: 'running', message: 'Реєстрація в системі...' });
    mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);

    await registerInSystem();
    steps[steps.length - 1].status = 'completed';
    mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);

    // Успішне завершення
    return { success: true, message: 'Встановлення завершено успішно!' };

  } catch (error) {
    console.error('Installation error:', error);

    if (steps.length > 0 && steps[steps.length - 1].status === 'running') {
      steps[steps.length - 1].status = 'error';
      steps[steps.length - 1].error = error.message;
      mainWindow.webContents.send('installation-progress', steps[steps.length - 1]);
    }

    return { success: false, message: error.message };
  }
});

// Функції встановлення

async function createDirectories() {
  const dirs = [
    installConfig.installPath,
    path.join(installConfig.installPath, 'src'),
    path.join(installConfig.installPath, 'dist'),
    path.join(installConfig.installPath, 'data'),
    path.join(installConfig.installPath, 'logs'),
    path.join(installConfig.installPath, 'docs')
  ];

  for (const dir of dirs) {
    await fs.mkdir(dir, { recursive: true });
  }
}

async function copyProjectFiles() {
  const appPath = app.isPackaged
    ? path.join(process.resourcesPath, 'app')
    : path.join(__dirname, '../../');

  // Копіюємо основні файли проекту
  const filesToCopy = [
    'package.json',
    'tsconfig.json',
    'README.md',
    '.env.example'
  ];

  const dirsToCopy = [];

  if (installConfig.components.core) {
    dirsToCopy.push('src');
  }

  if (installConfig.components.examples) {
    dirsToCopy.push('examples');
  }

  if (installConfig.components.integrations) {
    dirsToCopy.push('docs');
  }

  // Копіюємо файли
  for (const file of filesToCopy) {
    const srcFile = path.join(appPath, file);
    const destFile = path.join(installConfig.installPath, file);
    try {
      await fs.copyFile(srcFile, destFile);
    } catch (e) {
      console.log(`Файл ${file} не знайдено, пропускаємо`);
    }
  }

  // Копіюємо директорії
  for (const dir of dirsToCopy) {
    const srcDir = path.join(appPath, dir);
    const destDir = path.join(installConfig.installPath, dir);
    await copyDirectory(srcDir, destDir);
  }
}

async function copyDirectory(src, dest) {
  await fs.mkdir(dest, { recursive: true });
  const entries = await fs.readdir(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      await copyDirectory(srcPath, destPath);
    } else {
      await fs.copyFile(srcPath, destPath);
    }
  }
}

async function installNodeJS() {
  // Завантаження та встановлення Node.js
  const nodeUrl = 'https://nodejs.org/dist/v20.10.0/node-v20.10.0-x64.msi';
  // Тут буде код для завантаження та запуску MSI
  // Для прикладу просто показуємо повідомлення
  throw new Error('Автоматичне встановлення Node.js ще не реалізовано. Встановіть вручну з nodejs.org');
}

async function installDependencies() {
  return new Promise((resolve, reject) => {
    const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';
    const install = spawn(npm, ['install', '--production'], {
      cwd: installConfig.installPath,
      shell: true
    });

    install.stdout.on('data', (data) => {
      console.log(`npm: ${data}`);
      mainWindow.webContents.send('installation-log', data.toString());
    });

    install.stderr.on('data', (data) => {
      console.error(`npm error: ${data}`);
      mainWindow.webContents.send('installation-log', data.toString());
    });

    install.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`npm install failed with code ${code}`));
      }
    });
  });
}

async function compileTypeScript() {
  return new Promise((resolve, reject) => {
    const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';
    const build = spawn(npm, ['run', 'build'], {
      cwd: installConfig.installPath,
      shell: true
    });

    build.stdout.on('data', (data) => {
      console.log(`tsc: ${data}`);
      mainWindow.webContents.send('installation-log', data.toString());
    });

    build.stderr.on('data', (data) => {
      console.error(`tsc error: ${data}`);
      mainWindow.webContents.send('installation-log', data.toString());
    });

    build.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`TypeScript compilation failed with code ${code}`));
      }
    });
  });
}

async function configureClaudeDesktop() {
  const systemInfo = await ipcMain.handle('get-system-info');

  if (!systemInfo.claudeConfigPath) {
    console.log('Claude Desktop config not found, skipping...');
    return;
  }

  try {
    // Читаємо існуючу конфігурацію
    const configContent = await fs.readFile(systemInfo.claudeConfigPath, 'utf8');
    const config = JSON.parse(configContent);

    // Додаємо Digital Office Hub
    if (!config.mcpServers) {
      config.mcpServers = {};
    }

    config.mcpServers['digital-office'] = {
      command: 'node',
      args: [path.join(installConfig.installPath, 'dist', 'index-new.js').replace(/\\/g, '\\\\')],
      env: {
        NODE_ENV: 'production'
      }
    };

    // Зберігаємо оновлену конфігурацію
    await fs.writeFile(
      systemInfo.claudeConfigPath,
      JSON.stringify(config, null, 2),
      'utf8'
    );

    console.log('Claude Desktop configured successfully');
  } catch (error) {
    console.error('Failed to configure Claude Desktop:', error);
    throw new Error('Не вдалося налаштувати Claude Desktop: ' + error.message);
  }
}

async function createShortcuts() {
  if (process.platform !== 'win32') {
    return; // Ярлики тільки для Windows
  }

  const shortcutScript = `
    $WshShell = New-Object -ComObject WScript.Shell

    # Desktop shortcut
    ${installConfig.createDesktopShortcut ? `
    $DesktopPath = [System.Environment]::GetFolderPath('Desktop')
    $Shortcut = $WshShell.CreateShortcut("$DesktopPath\\Digital Office Hub.lnk")
    $Shortcut.TargetPath = "cmd.exe"
    $Shortcut.Arguments = "/c cd /d \\"${installConfig.installPath}\\" && npm start"
    $Shortcut.WorkingDirectory = "${installConfig.installPath}"
    $Shortcut.IconLocation = "${path.join(installConfig.installPath, 'assets', 'icon.ico')}"
    $Shortcut.Description = "Digital Office Hub - MCP Integration Platform"
    $Shortcut.Save()
    ` : ''}

    # Start Menu shortcut
    ${installConfig.createStartMenuShortcut ? `
    $StartMenuPath = [System.Environment]::GetFolderPath('StartMenu')
    $ProgramsPath = "$StartMenuPath\\Programs\\Digital Office Hub"
    New-Item -ItemType Directory -Path $ProgramsPath -Force

    $Shortcut = $WshShell.CreateShortcut("$ProgramsPath\\Digital Office Hub.lnk")
    $Shortcut.TargetPath = "cmd.exe"
    $Shortcut.Arguments = "/c cd /d \\"${installConfig.installPath}\\" && npm start"
    $Shortcut.WorkingDirectory = "${installConfig.installPath}"
    $Shortcut.IconLocation = "${path.join(installConfig.installPath, 'assets', 'icon.ico')}"
    $Shortcut.Description = "Digital Office Hub - MCP Integration Platform"
    $Shortcut.Save()

    $Shortcut = $WshShell.CreateShortcut("$ProgramsPath\\Uninstall Digital Office Hub.lnk")
    $Shortcut.TargetPath = "${path.join(installConfig.installPath, 'uninstall.exe')}"
    $Shortcut.WorkingDirectory = "${installConfig.installPath}"
    $Shortcut.Description = "Uninstall Digital Office Hub"
    $Shortcut.Save()
    ` : ''}
  `;

  const scriptPath = path.join(app.getPath('temp'), 'create-shortcuts.ps1');
  await fs.writeFile(scriptPath, shortcutScript);

  return new Promise((resolve, reject) => {
    exec(`powershell -ExecutionPolicy Bypass -File "${scriptPath}"`, (error, stdout, stderr) => {
      if (error) {
        console.error('Shortcut creation error:', error);
        reject(error);
      } else {
        resolve();
      }
    });
  });
}

async function registerInSystem() {
  if (process.platform !== 'win32') {
    return;
  }

  // Додаємо в реєстр для видалення програм
  const regScript = `
    $registryPath = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\DigitalOfficeHub"
    New-Item -Path $registryPath -Force

    Set-ItemProperty -Path $registryPath -Name "DisplayName" -Value "Digital Office Hub"
    Set-ItemProperty -Path $registryPath -Name "DisplayVersion" -Value "1.0.0"
    Set-ItemProperty -Path $registryPath -Name "Publisher" -Value "Digital Office"
    Set-ItemProperty -Path $registryPath -Name "InstallLocation" -Value "${installConfig.installPath}"
    Set-ItemProperty -Path $registryPath -Name "UninstallString" -Value "${path.join(installConfig.installPath, 'uninstall.exe')}"
    Set-ItemProperty -Path $registryPath -Name "DisplayIcon" -Value "${path.join(installConfig.installPath, 'assets', 'icon.ico')}"
    Set-ItemProperty -Path $registryPath -Name "EstimatedSize" -Value 50000
    Set-ItemProperty -Path $registryPath -Name "NoModify" -Value 1
    Set-ItemProperty -Path $registryPath -Name "NoRepair" -Value 1
  `;

  const scriptPath = path.join(app.getPath('temp'), 'register-system.ps1');
  await fs.writeFile(scriptPath, regScript);

  return new Promise((resolve, reject) => {
    // Потребує адміністративних прав
    sudo.exec(
      `powershell -ExecutionPolicy Bypass -File "${scriptPath}"`,
      { name: 'Digital Office Hub Installer' },
      (error, stdout, stderr) => {
        if (error) {
          console.error('Registry error:', error);
          // Не критична помилка, продовжуємо
          resolve();
        } else {
          resolve();
        }
      }
    );
  });
}

// Відкрити папку встановлення
ipcMain.handle('open-install-folder', async () => {
  shell.openPath(installConfig.installPath);
});

// Запустити Digital Office Hub
ipcMain.handle('launch-app', async () => {
  const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';
  spawn(npm, ['start'], {
    cwd: installConfig.installPath,
    detached: true,
    shell: true,
    stdio: 'ignore'
  }).unref();
});

// Закрити інсталятор
ipcMain.handle('close-installer', () => {
  app.quit();
});