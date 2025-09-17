; Digital Office Hub Installer NSIS Script
; Custom installer configuration for NSIS

; Додаткові налаштування для встановлення
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "WinVer.nsh"

; Константи
!define PRODUCT_NAME "Digital Office Hub"
!define PRODUCT_VERSION "1.0.0"
!define PRODUCT_PUBLISHER "Digital Office"
!define PRODUCT_WEB_SITE "https://github.com/digital-office/hub"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\DigitalOfficeHub.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"

; Вимоги до системи
!define MIN_WIN_VER "10.0"
!define MIN_DISK_SPACE 524288000  ; 500MB в байтах

; Макроси для перевірки
!macro CheckSystemRequirements
  ; Перевірка версії Windows
  ${IfNot} ${AtLeastWin10}
    MessageBox MB_ICONEXCLAMATION|MB_OK "Digital Office Hub потребує Windows 10 або новішу версію."
    Abort
  ${EndIf}

  ; Перевірка вільного місця
  ${GetRoot} "$INSTDIR" $R0
  ${DriveSpace} "$R0" "/D=F /S=M" $R1
  IntOp $R1 $R1 * 1048576  ; Конвертація в байти
  ${If} $R1 < ${MIN_DISK_SPACE}
    MessageBox MB_ICONEXCLAMATION|MB_OK "Недостатньо вільного місця на диску. Потрібно мінімум 500 MB."
    Abort
  ${EndIf}

  ; Перевірка прав адміністратора
  UserInfo::GetAccountType
  Pop $R0
  ${If} $R0 != "admin"
    MessageBox MB_ICONEXCLAMATION|MB_YESNO "Для встановлення потрібні права адміністратора. Продовжити?" IDYES +2
    Abort
  ${EndIf}
!macroend

; Функція перевірки Node.js
!macro CheckNodeJS
  ; Перевірка наявності Node.js
  nsExec::ExecToStack 'cmd /c node --version'
  Pop $R0
  Pop $R1

  ${If} $R0 != 0
    MessageBox MB_ICONQUESTION|MB_YESNO "Node.js не знайдено. Встановити автоматично?" IDYES InstallNodeJS IDNO SkipNodeJS

    InstallNodeJS:
      DetailPrint "Завантаження Node.js..."
      inetc::get "https://nodejs.org/dist/v20.10.0/node-v20.10.0-x64.msi" "$TEMP\nodejs-installer.msi"
      Pop $R0
      ${If} $R0 == "OK"
        DetailPrint "Встановлення Node.js..."
        ExecWait 'msiexec /i "$TEMP\nodejs-installer.msi" /quiet /norestart'
        Delete "$TEMP\nodejs-installer.msi"

        ; Оновити PATH
        SendMessage ${HWND_BROADCAST} ${WM_WININICHANGE} 0 "STR:Environment" /TIMEOUT=5000

        ; Перевірити встановлення
        nsExec::ExecToStack 'cmd /c node --version'
        Pop $R0
        ${If} $R0 != 0
          MessageBox MB_ICONEXCLAMATION|MB_OK "Не вдалося встановити Node.js. Встановіть вручну з nodejs.org"
        ${Else}
          DetailPrint "Node.js успішно встановлено"
        ${EndIf}
      ${Else}
        MessageBox MB_ICONEXCLAMATION|MB_OK "Не вдалося завантажити Node.js. Перевірте інтернет-з'єднання."
      ${EndIf}

    SkipNodeJS:
  ${Else}
    DetailPrint "Node.js знайдено: $R1"
  ${EndIf}
!macroend

; Функція пошуку Claude Desktop config
!macro FindClaudeConfig
  StrCpy $R9 ""  ; Змінна для шляху config

  ; Можливі шляхи до конфігурації Claude
  StrCpy $R0 "$PROFILE\AppData\Roaming\Claude\claude_desktop_config.json"
  ${If} ${FileExists} "$R0"
    StrCpy $R9 "$R0"
    Goto ClaudeFound
  ${EndIf}

  StrCpy $R0 "$PROFILE\.claude\claude_desktop_config.json"
  ${If} ${FileExists} "$R0"
    StrCpy $R9 "$R0"
    Goto ClaudeFound
  ${EndIf}

  StrCpy $R0 "$LOCALAPPDATA\Claude\claude_desktop_config.json"
  ${If} ${FileExists} "$R0"
    StrCpy $R9 "$R0"
    Goto ClaudeFound
  ${EndIf}

  DetailPrint "Claude Desktop config не знайдено"
  Goto ClaudeNotFound

  ClaudeFound:
    DetailPrint "Claude Desktop config знайдено: $R9"

  ClaudeNotFound:
!macroend

; Функція налаштування Claude Desktop
!macro ConfigureClaudeDesktop
  ${If} $R9 != ""
    DetailPrint "Налаштування Claude Desktop..."

    ; Читаємо існуючий config
    FileOpen $R1 "$R9" r
    ${If} $R1 != ""
      FileRead $R1 $R2 1000000  ; Читаємо до 1MB
      FileClose $R1

      ; Додаємо Digital Office Hub до конфігурації
      ; Простий спосіб - додати в кінець файлу перед останнім }
      StrCpy $R3 "$R2"

      ; Перевіряємо чи вже налаштовано
      ${StrLoc} $R4 "$R3" "digital-office" ">"
      ${If} $R4 == ""
        ; Додаємо конфігурацію
        StrCpy $R5 `$\n  "digital-office": {$\n    "command": "node",$\n    "args": ["$INSTDIR\dist\index-new.js"],$\n    "env": {$\n      "NODE_ENV": "production"$\n    }$\n  }`

        ; Знаходимо останні фігурні дужки
        ${StrLoc} $R6 "$R3" "}" "<"
        ${If} $R6 != ""
          StrCpy $R7 "$R3" $R6
          StrCpy $R8 "$R3" "" $R6

          ; Додаємо наш сервіс
          StrCpy $R3 "$R7,$R5$R8"

          ; Записуємо оновлений config
          FileOpen $R1 "$R9" w
          ${If} $R1 != ""
            FileWrite $R1 "$R3"
            FileClose $R1
            DetailPrint "Claude Desktop налаштовано успішно"
          ${Else}
            DetailPrint "Помилка запису в файл конфігурації"
          ${EndIf}
        ${EndIf}
      ${Else}
        DetailPrint "Digital Office вже налаштовано в Claude Desktop"
      ${EndIf}
    ${Else}
      DetailPrint "Помилка читання конфігурації Claude Desktop"
    ${EndIf}
  ${EndIf}
!macroend

; Функція створення ярликів
!macro CreateApplicationShortcuts
  DetailPrint "Створення ярликів..."

  ; Ярлик на робочому столі
  CreateShortCut "$DESKTOP\Digital Office Hub.lnk" \
    "cmd.exe" '/c cd /d "$INSTDIR" && npm start' \
    "$INSTDIR\assets\icon.ico" 0 SW_SHOWMINIMIZED \
    "" "Digital Office Hub - MCP Integration Platform"

  ; Ярлики в меню Пуск
  CreateDirectory "$SMPROGRAMS\Digital Office Hub"
  CreateShortCut "$SMPROGRAMS\Digital Office Hub\Digital Office Hub.lnk" \
    "cmd.exe" '/c cd /d "$INSTDIR" && npm start' \
    "$INSTDIR\assets\icon.ico" 0 SW_SHOWMINIMIZED \
    "" "Digital Office Hub - MCP Integration Platform"

  CreateShortCut "$SMPROGRAMS\Digital Office Hub\Documentation.lnk" \
    "$INSTDIR\docs\README.md" "" "" 0 SW_SHOWNORMAL \
    "" "Digital Office Hub Documentation"

  CreateShortCut "$SMPROGRAMS\Digital Office Hub\Uninstall.lnk" \
    "$INSTDIR\uninstall.exe" "" "" 0 SW_SHOWNORMAL \
    "" "Видалити Digital Office Hub"
!macroend

; Функція очищення при видаленні
!macro CleanupOnUninstall
  ; Видалити ярлики
  Delete "$DESKTOP\Digital Office Hub.lnk"
  RMDir /r "$SMPROGRAMS\Digital Office Hub"

  ; Видалити файли проекту
  RMDir /r "$INSTDIR\src"
  RMDir /r "$INSTDIR\dist"
  RMDir /r "$INSTDIR\docs"
  RMDir /r "$INSTDIR\node_modules"
  Delete "$INSTDIR\package.json"
  Delete "$INSTDIR\tsconfig.json"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\.env.example"

  ; Видалити файли інсталятора
  Delete "$INSTDIR\uninstall.exe"
  Delete "$INSTDIR\assets\icon.ico"

  ; Спробувати видалити папку встановлення
  RMDir "$INSTDIR\assets"
  RMDir "$INSTDIR"

  ; Видалити з реєстру
  DeleteRegKey HKLM "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  ; Показати повідомлення
  MessageBox MB_ICONINFORMATION|MB_OK "Digital Office Hub успішно видалено.$\n$\nЗауваження: Конфігурація Claude Desktop не змінювалася."
!macroend

; Функція для установки npm залежностей
!macro InstallNpmDependencies
  DetailPrint "Встановлення npm залежностей..."
  SetOutPath "$INSTDIR"

  nsExec::ExecToLog 'cmd /c npm install --production'
  Pop $R0
  ${If} $R0 != 0
    DetailPrint "Помилка встановлення npm залежностей"
    MessageBox MB_ICONEXCLAMATION|MB_OK "Не вдалося встановити залежності npm. Перевірте підключення до інтернету."
  ${Else}
    DetailPrint "npm залежності встановлено успішно"
  ${EndIf}
!macroend

; Функція компіляції TypeScript
!macro CompileTypeScript
  DetailPrint "Компіляція TypeScript..."
  SetOutPath "$INSTDIR"

  nsExec::ExecToLog 'cmd /c npm run build'
  Pop $R0
  ${If} $R0 != 0
    DetailPrint "Помилка компіляції TypeScript"
    MessageBox MB_ICONEXCLAMATION|MB_OK "Не вдалося скомпілювати TypeScript код."
  ${Else}
    DetailPrint "TypeScript код скомпільовано успішно"
  ${EndIf}
!macroend

; Функція створення даних директорій
!macro CreateDataDirectories
  DetailPrint "Створення робочих директорій..."
  CreateDirectory "$INSTDIR\data"
  CreateDirectory "$INSTDIR\data\integrations"
  CreateDirectory "$INSTDIR\data\store"
  CreateDirectory "$INSTDIR\logs"

  ; Створити базову конфігурацію
  FileOpen $R1 "$INSTDIR\.env" w
  ${If} $R1 != ""
    FileWrite $R1 "# Digital Office Hub Configuration$\r$\n"
    FileWrite $R1 "NODE_ENV=production$\r$\n"
    FileWrite $R1 "JWT_SECRET=change-this-in-production$\r$\n"
    FileWrite $R1 "API_PORT=4000$\r$\n"
    FileWrite $R1 "MCP_PORT=3000$\r$\n"
    FileClose $R1
    DetailPrint "Створено базову конфігурацію .env"
  ${EndIf}
!macroend

; Користувацькі сторінки інсталятора
!macro CustomWelcomePage
  !insertmacro MUI_PAGE_WELCOME
!macroend

!macro CustomLicensePage
  !insertmacro MUI_PAGE_LICENSE "assets\license.txt"
!macroend

!macro CustomComponentsPage
  !insertmacro MUI_PAGE_COMPONENTS
!macroend

!macro CustomDirectoryPage
  !insertmacro MUI_PAGE_DIRECTORY
!macroend

!macro CustomInstallFilesPage
  !insertmacro MUI_PAGE_INSTFILES
!macroend

!macro CustomFinishPage
  !insertmacro MUI_PAGE_FINISH
!macroend

; Функції які будуть викликані Electron Builder
Function .onInit
  !insertmacro CheckSystemRequirements
FunctionEnd

Function .onInstSuccess
  ; Виконується після успішного встановлення
  DetailPrint "Встановлення завершено успішно"
FunctionEnd

Function .onInstFailed
  ; Виконується при помилці встановлення
  DetailPrint "Встановлення не вдалося"
FunctionEnd