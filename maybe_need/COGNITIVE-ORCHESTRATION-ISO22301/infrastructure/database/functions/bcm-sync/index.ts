// Supabase Edge Function: BCM-Odoo Sync
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    const { action, data } = await req.json()

    switch (action) {
      case 'sync_user_to_odoo':
        return await syncUserToOdoo(data)

      case 'log_activity':
        return await logUserActivity(supabase, data)

      case 'validate_company_access':
        return await validateCompanyAccess(supabase, data)

      default:
        return new Response(
          JSON.stringify({ error: 'Unknown action' }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        )
    }
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

async function syncUserToOdoo(userData: any) {
  // Sync Supabase user to Odoo
  const odooResponse = await fetch('http://localhost:8069/api/users/sync', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData)
  })

  return new Response(
    JSON.stringify({ success: true, data: await odooResponse.json() }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

async function logUserActivity(supabase: any, activityData: any) {
  const { error } = await supabase
    .from('user_activities')
    .insert(activityData)

  if (error) throw error

  return new Response(
    JSON.stringify({ success: true }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

async function validateCompanyAccess(supabase: any, { userId, companyId }: any) {
  const { data, error } = await supabase
    .from('bcm_users')
    .select('company_id, role')
    .eq('id', userId)
    .single()

  if (error) throw error

  const hasAccess = data.company_id === companyId || data.role === 'admin'

  return new Response(
    JSON.stringify({ hasAccess }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}