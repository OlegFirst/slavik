# Digital Office Hub - Installer

This directory contains the Windows installer for Digital Office Hub - an automated desktop installer that simplifies deployment and configuration.

## Features

- **Professional GUI installer** with multi-step wizard
- **Automated system requirements check**
- **Node.js auto-installation** if missing
- **Claude Desktop integration** with automatic MCP configuration
- **Desktop and Start Menu shortcuts**
- **Progress tracking** with detailed logging
- **Administrator privileges handling**
- **Automatic dependency installation**

## Building the Installer

### Prerequisites

- Node.js 18+ installed
- Windows development environment
- Administrator privileges (for testing)

### Quick Build

```bash
# Windows Command Prompt
build.bat

# PowerShell or Linux/macOS
npm run build
```

### Manual Build Steps

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Build the installer**:
   ```bash
   npm run build:installer
   ```

3. **Find the installer**:
   - Location: `dist/DigitalOfficeHub-Setup-1.0.0.exe`
   - Size: ~150-200MB (includes Node.js runtime)

### Build Scripts Available

- `npm run build` - Full production build
- `npm run build:dev` - Development build (no publishing)
- `npm run build:win32` - 32-bit Windows build
- `npm run build:win64` - 64-bit Windows build
- `npm run clean` - Clean build artifacts
- `npm start` - Run installer in development mode

## Installer Architecture

### Main Components

1. **Electron App** (`src/main.js`)
   - Window management
   - Installation logic
   - System requirements checking
   - File operations

2. **User Interface** (`src/installer.html/css/js`)
   - Multi-step wizard
   - Progress tracking
   - Configuration options
   - Status feedback

3. **PowerShell Scripts** (`scripts/`)
   - System requirements validation
   - Claude Desktop configuration
   - Windows-specific operations

4. **NSIS Configuration** (`scripts/installer.nsh`)
   - Advanced Windows installer features
   - Registry operations
   - Shortcut creation

### Installation Process

1. **Welcome Screen** - Introduction and feature overview
2. **System Check** - Validate requirements, check for Node.js/Git/Claude
3. **Configuration** - Choose install path, components, and options
4. **Installation** - Extract files, install dependencies, compile code
5. **Completion** - Success confirmation and next steps

## Customization

### Changing the Icon

1. Replace `assets/icon.ico` with your custom icon
2. Icon should be 256x256 pixels, ICO format
3. Rebuild the installer

### Modifying Installation Options

Edit `src/installer.html` to add/remove:
- Component selection checkboxes
- Configuration options
- Installation paths

### Adding Custom Installation Steps

1. Update `src/main.js` - Add step to installation process
2. Update `src/installer.js` - Add UI handling for the step
3. Update progress tracking arrays

## Troubleshooting

### Build Issues

**Error: "Cannot find module 'electron'"**
```bash
npm install
```

**Error: "NSIS not found"**
- Electron Builder automatically downloads NSIS
- Ensure internet connection during first build

**Error: "Icon file not found"**
- Create `assets/icon.ico` or remove icon references from package.json

### Installation Issues

**Installer blocked by Windows Defender**
- This is normal for unsigned installers
- Users can click "More info" → "Run anyway"
- For production: Consider code signing certificate

**Node.js installation fails**
- Check internet connection
- Run installer as administrator
- Manual fallback: Download Node.js from nodejs.org

**Claude Desktop configuration fails**
- Claude Desktop must be installed first
- Check paths in `scripts/configure-claude.ps1`
- Manual configuration instructions provided

## Distribution

### File Structure
```
dist/
├── DigitalOfficeHub-Setup-1.0.0.exe    # Main installer
├── latest.yml                           # Auto-updater metadata
├── release-info.json                    # Build information
├── INSTALLATION.md                      # User instructions
└── release.html                         # Release info page
```

### Sharing the Installer

1. **Upload** `DigitalOfficeHub-Setup-1.0.0.exe` to your distribution method
2. **Include** `INSTALLATION.md` with instructions
3. **Test** on clean Windows systems before distributing
4. **Document** system requirements clearly

## Security Considerations

- Installer requires administrator privileges
- Downloads Node.js from official nodejs.org
- Modifies Claude Desktop configuration files
- Creates system-wide shortcuts and registry entries
- All operations are logged for troubleshooting

## Development

### Testing the Installer

```bash
# Run installer in development mode
npm start

# Build and test full installer
npm run build:dev
dist\DigitalOfficeHub-Setup-1.0.0.exe
```

### File Structure

```
1install/
├── src/                    # Installer application source
│   ├── main.js            # Electron main process
│   ├── installer.html     # User interface
│   ├── installer.css      # Styling
│   └── installer.js       # Frontend logic
├── scripts/               # Build and configuration scripts
│   ├── installer.nsh      # NSIS configuration
│   ├── check-system.ps1   # System requirements check
│   ├── configure-claude.ps1 # Claude Desktop setup
│   ├── prepare-build.js   # Pre-build script
│   └── post-build.js      # Post-build script
├── assets/               # Icons and resources
├── dist/                 # Build output
├── package.json         # Installer configuration
├── build.bat           # Windows build script
├── build.sh           # Unix build script
└── README.md          # This file
```

## Version History

**v1.0.0** - Initial Release
- Complete Windows installer with GUI
- Automated Node.js installation
- Claude Desktop MCP integration
- System requirements validation
- Desktop shortcuts and Start Menu integration

---

For support or questions about the installer, check the main project documentation or the generated `INSTALLATION.md` file.