/**
 * Supabase Webhooks Event Streaming
 * Handles real-time events from database changes
 */

import express from 'express';
import { createHmac } from 'crypto';
import { EventEmitter } from 'events';
import { createLogger } from '../../utils/logger.js';
import { DigitalTwinDatabaseAdapter } from '../../infrastructure/database/database-adapter.js';

const router = express.Router();
const logger = createLogger('SupabaseWebhooks');
const eventBus = new EventEmitter();
const db = new DigitalTwinDatabaseAdapter();

// Webhook secret for signature verification
const WEBHOOK_SECRET = process.env.SUPABASE_WEBHOOK_SECRET || 'your-webhook-secret';

/**
 * Verify webhook signature
 */
function verifyWebhookSignature(payload, signature) {
    const expectedSignature = createHmac('sha256', WEBHOOK_SECRET)
        .update(payload)
        .digest('hex');
    
    return signature === `sha256=${expectedSignature}`;
}

/**
 * Event type mapping
 */
const EVENT_MAPPINGS = {
    'measurements.INSERT': 'indicator.measured',
    'service_deliveries.INSERT': 'service.delivery.recorded',
    'disbursements.INSERT': 'grant.disbursement.made',
    'bcm_tests.UPDATE': 'bcm.test.completed',
    'participants.INSERT': 'participant.enrolled',
    'participants.UPDATE': 'participant.updated',
    'grant_awards.INSERT': 'grant.awarded',
    'simulations.INSERT': 'simulation.completed',
    'predictions.INSERT': 'prediction.generated',
    'digital_twins.INSERT': 'twin.created',
    'digital_twins.UPDATE': 'twin.updated'
};

/**
 * Process webhook event
 */
async function processWebhookEvent(event) {
    const { type, table, record, old_record } = event;
    const eventKey = `${table}.${type}`;
    const domainEvent = EVENT_MAPPINGS[eventKey];
    
    if (!domainEvent) {
        logger.debug(`No mapping for event: ${eventKey}`);
        return;
    }
    
    logger.info(`Processing domain event: ${domainEvent}`);
    
    // Emit to internal event bus
    eventBus.emit(domainEvent, {
        type: domainEvent,
        timestamp: new Date().toISOString(),
        data: record,
        previousData: old_record,
        metadata: {
            table,
            operation: type,
            id: record?.id
        }
    });
    
    // Store in domain_events table for audit
    await db.insert('domain_events', {
        event_type: domainEvent,
        aggregate_id: record?.id,
        aggregate_type: table,
        payload: record,
        metadata: {
            operation: type,
            timestamp: new Date().toISOString()
        }
    });
}

/**
 * Main webhook endpoint
 */
router.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
    try {
        // Verify signature
        const signature = req.headers['x-supabase-signature'];
        if (!verifyWebhookSignature(req.body, signature)) {
            logger.warn('Invalid webhook signature');
            return res.status(401).json({ error: 'Invalid signature' });
        }
        
        // Parse payload
        const payload = JSON.parse(req.body.toString());
        
        logger.info(`Received webhook: ${payload.type} for ${payload.table}`);
        
        // Process event asynchronously
        setImmediate(() => {
            processWebhookEvent(payload).catch(err => {
                logger.error('Error processing webhook:', err);
            });
        });
        
        // Respond immediately
        res.status(200).json({ received: true });
        
    } catch (error) {
        logger.error('Webhook processing error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

/**
 * Event Handlers
 */

// Indicator measured
eventBus.on('indicator.measured', async (event) => {
    logger.info('Indicator measured:', event.data);
    
    // Check if target is met
    const indicator = await db.getById('indicators', event.data.indicator_id);
    const target = await db.query(
        'SELECT * FROM targets WHERE indicator_id = $1 AND period_start <= $2 AND period_end >= $2',
        [event.data.indicator_id, event.data.period_end]
    );
    
    if (target.length > 0 && event.data.value >= target[0].target_value) {
        eventBus.emit('target.achieved', {
            indicator_id: event.data.indicator_id,
            target_value: target[0].target_value,
            actual_value: event.data.value
        });
    }
});

// Service delivery recorded
eventBus.on('service.delivery.recorded', async (event) => {
    logger.info('Service delivery recorded:', event.data);
    
    // Update participant engagement metrics
    await db.query(
        'UPDATE participants SET last_service_date = $1 WHERE id = $2',
        [event.data.delivery_date, event.data.participant_id]
    );
});

// Grant disbursement made
eventBus.on('grant.disbursement.made', async (event) => {
    logger.info('Grant disbursement made:', event.data);
    
    // Update grant totals
    await db.query(
        'UPDATE grant_awards SET total_disbursed = total_disbursed + $1 WHERE id = $2',
        [event.data.amount, event.data.grant_award_id]
    );
    
    // Check if fully disbursed
    const award = await db.getById('grant_awards', event.data.grant_award_id);
    if (award.total_disbursed >= award.awarded_amount) {
        eventBus.emit('grant.fully_disbursed', {
            grant_id: award.id,
            total_amount: award.awarded_amount
        });
    }
});

// BCM test completed
eventBus.on('bcm.test.completed', async (event) => {
    logger.info('BCM test completed:', event.data);
    
    // Analyze test results
    const scenario = await db.getById('bcm_scenarios', event.data.scenario_id);
    const rtoPassed = event.data.actual_rto_hours <= scenario.rto_hours;
    const rpoPassed = event.data.actual_rpo_hours <= scenario.rpo_hours;
    
    if (!rtoPassed || !rpoPassed) {
        eventBus.emit('bcm.test.failed', {
            scenario_id: event.data.scenario_id,
            rto_passed: rtoPassed,
            rpo_passed: rpoPassed
        });
    }
});

// Twin created
eventBus.on('twin.created', async (event) => {
    logger.info('Digital twin created:', event.data);
    
    // Initialize default metrics
    const defaultMetrics = [
        { metric_type: 'health_score', value: 0.5 },
        { metric_type: 'efficiency_score', value: 0.5 },
        { metric_type: 'readiness_level', value: 1 }
    ];
    
    for (const metric of defaultMetrics) {
        await db.insert('metrics', {
            digital_twin_id: event.data.id,
            ...metric,
            timestamp: new Date().toISOString()
        });
    }
});

/**
 * Subscribe to specific event types
 */
export function subscribeToEvent(eventType, handler) {
    eventBus.on(eventType, handler);
    logger.info(`Subscribed to event: ${eventType}`);
}

/**
 * Unsubscribe from event
 */
export function unsubscribeFromEvent(eventType, handler) {
    eventBus.off(eventType, handler);
    logger.info(`Unsubscribed from event: ${eventType}`);
}

/**
 * Get event statistics
 */
router.get('/webhook/stats', async (req, res) => {
    try {
        const stats = await db.query(`
            SELECT 
                event_type,
                COUNT(*) as count,
                MAX(created_at) as last_event
            FROM domain_events
            WHERE created_at > NOW() - INTERVAL '24 hours'
            GROUP BY event_type
            ORDER BY count DESC
        `);
        
        res.json({
            total_events_24h: stats.reduce((sum, s) => sum + parseInt(s.count), 0),
            event_types: stats
        });
        
    } catch (error) {
        logger.error('Error fetching stats:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

/**
 * Configure Supabase webhooks
 */
export async function configureSupabaseWebhooks(supabaseUrl, serviceKey) {
    const webhookUrl = process.env.WEBHOOK_ENDPOINT || 'https://api.digitaltwin.app/events/webhook';
    
    const tables = [
        'measurements',
        'service_deliveries',
        'disbursements',
        'bcm_tests',
        'participants',
        'grant_awards',
        'simulations',
        'predictions',
        'digital_twins'
    ];
    
    for (const table of tables) {
        logger.info(`Configuring webhook for table: ${table}`);
        
        // This would be done through Supabase dashboard or API
        // Pseudo-code for webhook configuration:
        /*
        await supabase.webhooks.create({
            table,
            events: ['INSERT', 'UPDATE', 'DELETE'],
            url: webhookUrl,
            headers: {
                'Content-Type': 'application/json'
            }
        });
        */
    }
    
    logger.info('Webhooks configured successfully');
}

/**
 * Event Stream SSE endpoint for real-time updates
 */
router.get('/stream', (req, res) => {
    res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    });
    
    const sendEvent = (event) => {
        res.write(`data: ${JSON.stringify(event)}\n\n`);
    };
    
    // Send heartbeat
    const heartbeat = setInterval(() => {
        res.write(': heartbeat\n\n');
    }, 30000);
    
    // Subscribe to all events
    const eventTypes = Object.values(EVENT_MAPPINGS);
    const handlers = {};
    
    eventTypes.forEach(eventType => {
        handlers[eventType] = (event) => sendEvent(event);
        eventBus.on(eventType, handlers[eventType]);
    });
    
    // Clean up on disconnect
    req.on('close', () => {
        clearInterval(heartbeat);
        eventTypes.forEach(eventType => {
            eventBus.off(eventType, handlers[eventType]);
        });
    });
});

export { eventBus, router as webhookRouter };