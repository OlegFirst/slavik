/**
 * SEH-compliant API endpoints
 * Implements CRUD operations for SEH data models
 */

import express from 'express';
import { createClient } from '@supabase/supabase-js';

const router = express.Router();

// ============= PROGRAMS API =============

// Create program
router.post('/programs', async (req, res) => {
    try {
        const { supabase } = req;
        const { data, error } = await supabase
            .from('programs')
            .insert(req.body)
            .select()
            .single();
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Get programs
router.get('/programs', async (req, res) => {
    try {
        const { supabase } = req;
        const { organization_id, status, domain } = req.query;
        
        let query = supabase.from('programs').select('*');
        
        if (organization_id) query = query.eq('organization_id', organization_id);
        if (status) query = query.eq('status', status);
        if (domain) query = query.eq('domain', domain);
        
        const { data, error } = await query;
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// ============= SERVICES API =============

// Create service
router.post('/services', async (req, res) => {
    try {
        const { supabase } = req;
        const { data, error } = await supabase
            .from('services')
            .insert(req.body)
            .select()
            .single();
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Get services for a program
router.get('/programs/:programId/services', async (req, res) => {
    try {
        const { supabase } = req;
        const { programId } = req.params;
        
        const { data, error } = await supabase
            .from('services')
            .select('*')
            .eq('program_id', programId);
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// ============= SERVICE DELIVERY API =============

// Record service delivery
router.post('/service-deliveries', async (req, res) => {
    try {
        const { supabase } = req;
        const delivery = {
            ...req.body,
            delivered_at: req.body.delivered_at || new Date().toISOString()
        };
        
        const { data, error } = await supabase
            .from('service_deliveries')
            .insert(delivery)
            .select()
            .single();
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Get service deliveries with filters
router.get('/service-deliveries', async (req, res) => {
    try {
        const { supabase } = req;
        const { service_id, participant_id, start_date, end_date } = req.query;
        
        let query = supabase.from('service_deliveries').select(`
            *,
            services (name, unit, delivery_mode),
            participants (cohort, vulnerability_tags)
        `);
        
        if (service_id) query = query.eq('service_id', service_id);
        if (participant_id) query = query.eq('participant_id', participant_id);
        if (start_date) query = query.gte('delivered_at', start_date);
        if (end_date) query = query.lte('delivered_at', end_date);
        
        const { data, error } = await query;
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// ============= OUTCOMES & INDICATORS API =============

// Create outcome
router.post('/outcomes', async (req, res) => {
    try {
        const { supabase } = req;
        const { data, error } = await supabase
            .from('outcomes')
            .insert(req.body)
            .select()
            .single();
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Create indicator
router.post('/indicators', async (req, res) => {
    try {
        const { supabase } = req;
        const { data, error } = await supabase
            .from('indicators')
            .insert(req.body)
            .select()
            .single();
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Record measurement
router.post('/measurements', async (req, res) => {
    try {
        const { supabase } = req;
        const measurement = {
            ...req.body,
            collected_at: req.body.collected_at || new Date().toISOString()
        };
        
        const { data, error } = await supabase
            .from('measurements')
            .insert(measurement)
            .select()
            .single();
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Get measurements for indicator
router.get('/indicators/:indicatorId/measurements', async (req, res) => {
    try {
        const { supabase } = req;
        const { indicatorId } = req.params;
        const { start_date, end_date } = req.query;
        
        let query = supabase
            .from('measurements')
            .select(`
                *,
                targets (target_value, period_start, period_end)
            `)
            .eq('indicator_id', indicatorId)
            .order('period_end', { ascending: false });
        
        if (start_date) query = query.gte('period_start', start_date);
        if (end_date) query = query.lte('period_end', end_date);
        
        const { data, error } = await query;
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// ============= GRANT MANAGEMENT API =============

// Submit grant application
router.post('/grant-applications', async (req, res) => {
    try {
        const { supabase } = req;
        const application = {
            ...req.body,
            application_number: `APP-${Date.now()}`,
            status: 'draft'
        };
        
        const { data, error } = await supabase
            .from('grant_applications')
            .insert(application)
            .select()
            .single();
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Get grant applications
router.get('/grant-applications', async (req, res) => {
    try {
        const { supabase } = req;
        const { organization_id, status, funding_program_id } = req.query;
        
        let query = supabase.from('grant_applications').select(`
            *,
            funding_programs (name, funder_name, focus_areas),
            organization_profiles (name, org_code)
        `);
        
        if (organization_id) query = query.eq('organization_id', organization_id);
        if (status) query = query.eq('status', status);
        if (funding_program_id) query = query.eq('funding_program_id', funding_program_id);
        
        const { data, error } = await query;
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Get disbursements for grant
router.get('/grants/:grantId/disbursements', async (req, res) => {
    try {
        const { supabase } = req;
        const { grantId } = req.params;
        
        const { data, error } = await supabase
            .from('disbursements')
            .select('*')
            .eq('grant_award_id', grantId)
            .order('scheduled_date', { ascending: true });
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// ============= BCM API =============

// Create BCM scenario
router.post('/bcm-scenarios', async (req, res) => {
    try {
        const { supabase } = req;
        const { data, error } = await supabase
            .from('bcm_scenarios')
            .insert(req.body)
            .select()
            .single();
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Record BCM test
router.post('/bcm-tests', async (req, res) => {
    try {
        const { supabase } = req;
        const test = {
            ...req.body,
            test_date: req.body.test_date || new Date().toISOString()
        };
        
        const { data, error } = await supabase
            .from('bcm_tests')
            .insert(test)
            .select()
            .single();
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// ============= PROOF OF IMPACT API =============

// Submit PoI claim
router.post('/poi-claims', async (req, res) => {
    try {
        const { supabase } = req;
        const claim = {
            ...req.body,
            submission_date: new Date().toISOString(),
            status: 'submitted'
        };
        
        const { data, error } = await supabase
            .from('poi_claims')
            .insert(claim)
            .select()
            .single();
        
        if (error) throw error;
        
        // Add to immutable ledger
        await supabase.from('ledger_entries').insert({
            entry_type: 'claim_submitted',
            entry_ref_id: data.id,
            entry_data: data,
            hash: req.body.evidence_hash,
            timestamp: new Date().toISOString()
        });
        
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Verify PoI claim
router.post('/poi-claims/:claimId/verify', async (req, res) => {
    try {
        const { supabase } = req;
        const { claimId } = req.params;
        
        const verification = {
            claim_id: claimId,
            ...req.body,
            verification_date: new Date().toISOString()
        };
        
        const { data, error } = await supabase
            .from('poi_verifications')
            .insert(verification)
            .select()
            .single();
        
        if (error) throw error;
        
        // Update claim status
        await supabase
            .from('poi_claims')
            .update({ status: 'verified' })
            .eq('id', claimId);
        
        // Add to ledger
        await supabase.from('ledger_entries').insert({
            entry_type: 'verification_completed',
            entry_ref_id: data.id,
            entry_data: data,
            hash: req.body.verification_hash,
            timestamp: new Date().toISOString()
        });
        
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// Get verified claims (public)
router.get('/poi-claims/verified', async (req, res) => {
    try {
        const { supabase } = req;
        
        const { data, error } = await supabase
            .from('poi_claims')
            .select(`
                *,
                indicators (name, unit),
                poi_verifications (verification_result, confidence_score, verifier_organization)
            `)
            .eq('status', 'verified')
            .order('submission_date', { ascending: false });
        
        if (error) throw error;
        res.json({ success: true, data });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

// ============= ANALYTICS API =============

// Get program performance dashboard
router.get('/analytics/program-performance/:programId', async (req, res) => {
    try {
        const { supabase } = req;
        const { programId } = req.params;
        
        // Get program details
        const { data: program } = await supabase
            .from('programs')
            .select('*')
            .eq('id', programId)
            .single();
        
        // Get service delivery stats
        const { data: deliveries } = await supabase
            .from('service_deliveries')
            .select('*, services!inner(*)')
            .eq('services.program_id', programId);
        
        // Get outcome measurements
        const { data: measurements } = await supabase
            .from('measurements')
            .select('*, indicators!inner(*, outcomes!inner(*))')
            .eq('indicators.outcomes.program_id', programId);
        
        // Calculate metrics
        const totalDeliveries = deliveries?.length || 0;
        const uniqueParticipants = new Set(deliveries?.map(d => d.participant_id)).size;
        const avgQualityScore = deliveries?.reduce((sum, d) => sum + (d.quality_score || 0), 0) / totalDeliveries || 0;
        
        const dashboard = {
            program,
            metrics: {
                total_deliveries: totalDeliveries,
                unique_participants: uniqueParticipants,
                avg_quality_score: avgQualityScore.toFixed(2),
                measurements_count: measurements?.length || 0
            },
            recent_deliveries: deliveries?.slice(0, 10),
            latest_measurements: measurements?.slice(0, 5)
        };
        
        res.json({ success: true, data: dashboard });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
});

export default router;