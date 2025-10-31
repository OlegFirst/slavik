# Setup ngrok tunnels for Vercel deployment

## 0. Setup ngrok configuration:

First, copy the example configuration and set your auth token:
```bash
# Copy the example configuration
cp ngrok.yml.example ngrok.yml

# Set your ngrok auth token as environment variable
export NGROK_TOKEN=your_ngrok_auth_token_here
```

**Important:** Never commit your actual `ngrok.yml` file with real tokens. The file is now in `.gitignore` for security.

### For GitHub Actions (if needed):
To use ngrok in GitHub Actions, add `NGROK_TOKEN` to your repository secrets and reference it in workflows:
```yaml
- name: Setup ngrok
  env:
    NGROK_TOKEN: ${{ secrets.NGROK_TOKEN }}
  run: |
    ngrok start --all
```

## 1. Start your backend services locally:
```bash
# Terminal 1 - EventBus
cd backend/event_bus
python app.py  # Should run on port 8001

# Terminal 2 - Orchestrator  
cd backend/orchestrator
python app.py  # Should run on port 8002

# Terminal 3 - Odoo (if needed)
# Usually runs on port 8069
```

## 2. Create ngrok tunnels:

You can either use individual commands or the configuration file:

### Option A: Individual tunnels
```bash
# Terminal 4 - EventBus tunnel
ngrok http 8001

# Terminal 5 - Orchestrator tunnel
ngrok http 8002  

# Terminal 6 - Odoo tunnel (if needed)
ngrok http 8069
```

### Option B: Using configuration file (recommended)
```bash
# Start all tunnels at once using the configuration file
ngrok start --all
```

This will start all tunnels defined in `ngrok.yml` simultaneously.

## 3. Update vercel.json with ngrok URLs:

Replace the placeholders in `frontend/web_portal/vercel.json`:
- `YOUR-EVENTBUS-HOST` → your ngrok URL for port 8001 (e.g., `abc123.ngrok-free.app`)
- `YOUR-ORCHESTRATOR-HOST` → your ngrok URL for port 8002 (e.g., `def456.ngrok-free.app`)
- `YOUR-ODOO-HOST` → your ngrok URL for port 8069 (e.g., `ghi789.ngrok-free.app`)

## 4. Commit and push:
```bash
git add -A
git commit -m "feat: Add backend proxy URLs"
git push
```

## 5. Vercel will automatically redeploy with working API proxies!
