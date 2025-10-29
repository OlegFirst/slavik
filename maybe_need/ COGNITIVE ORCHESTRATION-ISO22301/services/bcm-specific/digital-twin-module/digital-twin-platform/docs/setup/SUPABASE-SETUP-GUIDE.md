# SUPABASE SETUP GUIDE
## Digital Twin Standalone Module

**Version**: 2.0.0  
**Date**: 2025-01-15

---

## Quick Start

### 1. Database Setup

```bash
# Navigate to project
cd /Users/maksymdemchenko/claude_workspace_files/Development/digital-twin-standalone

# Run migrations in Supabase SQL Editor
# Copy content from these files:
database/migrations/001_initial_schema.sql
database/migrations/002_row_level_security.sql
```

### 2. Deploy Edge Functions

```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref xshqhyjhjudnvbfbvvrz

# Deploy Edge Functions
supabase functions deploy simulate --no-verify-jwt
supabase functions deploy predict --no-verify-jwt
```

### 3. Environment Configuration

Your `.env` file is already configured with Supabase credentials from the main NASH project:
- SUPABASE_URL
- SUPABASE_ANON_KEY  
- SUPABASE_SERVICE_ROLE_KEY

### 4. Test Connection

```bash
# Start the module
npm start

# Test MCP integration
npm run mcp:start
```

---

## Database Architecture

### Core Tables
- **organizations** - NPO profiles
- **digital_twins** - Twin instances
- **simulations** - Simulation runs
- **metrics** - Time-series data (partitioned)
- **predictions** - AI forecasts
- **audit_logs** - Activity tracking

### Security Features
- Row Level Security (RLS) enabled
- Service role bypass for backend
- User-based access control
- Audit trail for all operations

### Real-time Features
- Live twin updates
- Metric streaming
- Simulation progress tracking
- Collaborative features

---

## Integration Code

```javascript
// Example usage
import { supabaseIntegration } from './infrastructure/database/supabase-integration.js';

// Initialize
await supabaseIntegration.initialize();

// Create organization
const org = await supabaseIntegration.createOrganization({
    organization_id: 'npo-001',
    name: 'Green Future Foundation',
    type: 'charity',
    mission: 'Environmental conservation',
    size: 50,
    annual_budget: 2000000
});

// Create digital twin
const twin = await supabaseIntegration.createDigitalTwin({
    twin_id: 'twin-001',
    organization_id: org.id,
    name: 'GFF Digital Twin',
    configuration: {
        modules: ['financial', 'operations', 'impact']
    }
});

// Run simulation
const simulation = await supabaseIntegration.runSimulation(
    twin.id,
    'budget_optimization',
    { targetReduction: 0.1 }
);

// Subscribe to real-time updates
supabaseIntegration.subscribeToMetrics(twin.id, (metric) => {
    console.log('New metric:', metric);
});
```

---

## Edge Functions

### Simulate Function
Runs complex simulations for digital twins:
- Budget optimization
- Crisis management
- Scaling analysis
- Efficiency improvement
- Grant impact assessment
- Staff reorganization

### Predict Function
AI-powered predictions:
- Budget forecasting
- Staff turnover prediction
- Grant success probability
- Program impact projection
- Donor retention forecast
- Operational efficiency trends

---

## Monitoring & Maintenance

### Health Check
```javascript
const health = await supabaseIntegration.healthCheck();
console.log('Database health:', health);
```

### Metrics Dashboard
Access Supabase Dashboard:
https://supabase.com/dashboard/project/xshqhyjhjudnvbfbvvrz

### Backup Strategy
- Automatic daily backups (Supabase)
- Point-in-time recovery available
- Export via pg_dump for local backups

---

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check SUPABASE_URL and keys in .env
   - Verify network connectivity
   - Check Supabase project status

2. **Permission Denied**
   - Ensure RLS policies are created
   - Use SERVICE_ROLE_KEY for backend
   - Check user authentication

3. **Edge Function Errors**
   - View logs: `supabase functions logs simulate`
   - Check function deployment status
   - Verify JWT configuration

### Support
- Supabase Docs: https://supabase.com/docs
- Project Dashboard: https://supabase.com/dashboard
- GitHub Issues: Create issue in project repo

---

## Production Checklist

- [ ] Rotate API keys
- [ ] Enable SSL enforcement
- [ ] Configure backup schedule
- [ ] Set up monitoring alerts
- [ ] Review RLS policies
- [ ] Test Edge Functions
- [ ] Configure rate limiting
- [ ] Set up error tracking
- [ ] Document API endpoints
- [ ] Create runbooks

---

## Cost Optimization

### Free Tier Limits
- 500MB database
- 1GB file storage
- 2GB bandwidth
- 50K MAU

### Optimization Tips
- Use database indexes efficiently
- Implement client-side caching
- Batch metric insertions
- Archive old simulations
- Use Edge Functions for heavy computation

---

*Setup guide prepared according to PARTNERSHIP-EXCELLENCE standards*