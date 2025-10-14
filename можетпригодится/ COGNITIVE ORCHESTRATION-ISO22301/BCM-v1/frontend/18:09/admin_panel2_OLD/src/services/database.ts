import axios from 'axios';

// PostgreSQL connection settings
const POSTGRES_CONFIG = {
  host: 'localhost',
  port: 5432,
  database: 'bcm_platform',
  user: 'postgres',
  password: 'postgres'
};

// Supabase configuration
const SUPABASE_URL = 'https://mvzlkpzakzlmmxyjjtvr.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12emxrcHpha3psbW14eWpqdHZyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA5OTIyMTgsImV4cCI6MjA2NjU2ODIxOH0.zJeHMNv15jPwe8bgEph4GzwtsE8anx-7ZpqCZa3axQA';

// Database service for direct queries
export const databaseService = {
  // Get AI organs status from database
  async getAIOrgansFromDB() {
    try {
      // Query through Odoo API
      const response = await axios.post('/api/dataset/call_kw/bcm.ai.lifecycle/search_read', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.ai.lifecycle',
          domain: [],
          fields: ['name', 'state', 'health_status', 'last_heartbeat', 'memory_usage', 'processing_load'],
          limit: 10,
          sort: 'id asc'
        },
        id: Date.now()
      });
      return response.data.result;
    } catch (error) {
      console.error('Failed to fetch AI organs from DB:', error);
      return [];
    }
  },

  // Get BCM incidents from database
  async getIncidentsFromDB() {
    try {
      const response = await axios.post('/api/dataset/call_kw/bcm.incident/search_read', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.incident',
          domain: [['state', 'in', ['new', 'in_progress']]],
          fields: ['name', 'description', 'severity', 'state', 'create_date'],
          limit: 20,
          sort: 'create_date desc'
        },
        id: Date.now()
      });
      return response.data.result;
    } catch (error) {
      console.error('Failed to fetch incidents from DB:', error);
      return [];
    }
  },

  // Get BCM plans from database
  async getPlansFromDB() {
    try {
      const response = await axios.post('/api/dataset/call_kw/bcm.plan/search_read', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.plan',
          domain: [['active', '=', true]],
          fields: ['name', 'plan_type', 'status', 'last_test_date', 'next_review_date'],
          limit: 50,
          sort: 'name asc'
        },
        id: Date.now()
      });
      return response.data.result;
    } catch (error) {
      console.error('Failed to fetch plans from DB:', error);
      return [];
    }
  },

  // Get system metrics from Supabase
  async getSystemMetricsFromSupabase() {
    try {
      const response = await axios.get(`${SUPABASE_URL}/rest/v1/system_metrics`, {
        headers: {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
        },
        params: {
          select: '*',
          order: 'created_at.desc',
          limit: 1
        }
      });
      return response.data[0];
    } catch (error) {
      console.error('Failed to fetch metrics from Supabase:', error);
      return null;
    }
  },

  // Get AI memory from Supabase
  async getAIMemoryFromSupabase() {
    try {
      const response = await axios.get(`${SUPABASE_URL}/rest/v1/ai_memory`, {
        headers: {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
        },
        params: {
          select: '*',
          order: 'created_at.desc',
          limit: 100
        }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch AI memory from Supabase:', error);
      return [];
    }
  }
};