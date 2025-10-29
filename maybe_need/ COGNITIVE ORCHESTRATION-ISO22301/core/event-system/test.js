/**
 * Test Meta-aware Event System
 */

import eventSystem from './index.js';

console.log('🧠 Testing Meta-aware Event System\n');

// 1. Subscribe to events with meta-tracking
console.log('1. Setting up intelligent subscribers...');

eventSystem.subscribe('user:action', async (event) => {
    console.log('  User action received:', event.data);
    return { processed: true, timestamp: Date.now() };
});

eventSystem.subscribe('system:error', async (event) => {
    console.log('  System error:', event.data);
    throw new Error('Simulated handler error');
});

eventSystem.subscribe('*', (event) => {
    console.log(`  [Meta-Observer] Event: ${event.type}`);
});

// Subscribe to meta-events
eventSystem.subscribe('system:insight_generated', (event) => {
    console.log('\n💡 INSIGHT GENERATED:', event.data.recommendation);
});

eventSystem.subscribe('system:handler_failure', (event) => {
    console.log('\n⚠️ HANDLER FAILURE:', event.data);
});

// 2. Register intelligence hooks
console.log('\n2. Registering intelligence hooks...');

eventSystem.registerHook('patternDetected', (pattern) => {
    console.log('\n🔍 PATTERN DETECTED:', pattern.sequence, `(${pattern.count} times)`);
});

eventSystem.registerHook('anomalyDetected', (anomaly) => {
    console.log('\n⚡ ANOMALY DETECTED:', anomaly);
});

// 3. Generate events to create patterns
console.log('\n3. Generating events to create patterns...\n');

async function simulateUserBehavior() {
    // Normal user flow
    for (let i = 0; i < 5; i++) {
        await eventSystem.publish('user:login', { userId: i });
        await eventSystem.publish('user:action', { action: 'view_dashboard' });
        await eventSystem.publish('user:action', { action: 'check_metrics' });
        await eventSystem.publish('user:logout', { userId: i });

        await new Promise(resolve => setTimeout(resolve, 100));
    }

    // Error pattern
    for (let i = 0; i < 4; i++) {
        await eventSystem.publish('system:error', { code: 'TIMEOUT' });
        await eventSystem.publish('system:retry', { attempt: i });
        await new Promise(resolve => setTimeout(resolve, 50));
    }

    // Anomaly: Rapid events
    for (let i = 0; i < 10; i++) {
        await eventSystem.publish('user:action', { action: 'rapid_clicks' });
    }
}

// 4. Run simulation
console.log('4. Running simulation...\n');

await simulateUserBehavior();

// 5. Check meta state
console.log('\n5. Meta State Analysis:\n');

const metaState = eventSystem.getMetaState();

console.log('📊 Statistics:');
console.log('  Total Events:', metaState.totalEvents);
console.log('  Patterns Found:', metaState.patterns.length);
console.log('  Insights Generated:', metaState.insights.length);
console.log('  Active Correlations:', metaState.correlationCount);
console.log('  System Health:', metaState.health);

// 6. Predict next events
console.log('\n6. Predictions for next event:');

const predictions = eventSystem.predictNextEvent();
console.log('  Predictions:', predictions.slice(0, 3));

// 7. Get correlation chain example
console.log('\n7. Correlation Chain Example:');

const correlations = Array.from(eventSystem.correlations.keys());
if (correlations.length > 0) {
    const chain = eventSystem.getCorrelationChain(correlations[0]);
    console.log('  Events in chain:', chain.map(e => e.type).join(' -> '));
}

console.log('\n✅ Meta-aware Event System is working with intelligence!\n');