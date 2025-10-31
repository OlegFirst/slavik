const SystemOrchestrator = require('./ORCHESTRATORS/system-orchestrator');
const BridgeOrchestrator = require('./ORCHESTRATORS/bridge-orchestrator');
const ProgramOrchestrator = require('./ORCHESTRATORS/program-orchestrator');
const ClientOrchestrator = require('./ORCHESTRATORS/client-orchestrator');
const SandboxOrchestrator = require('./ORCHESTRATORS/sandbox-orchestrator');

async function quickTest() {
    console.log('🧪 Быстрый тест всех оркестраторов...\n');

    const results = [];

    try {
        console.log('1️⃣ System Orchestrator...');
        const system = new SystemOrchestrator();
        await system.initialize();
        const health = await system.getHealthStatus();
        console.log(`✅ Сервисов: ${health.services.loaded}, статус: ${health.status}`);
        results.push({ name: 'System', status: '✅', services: health.services.loaded });
        await system.shutdown();
    } catch (error) {
        console.log(`❌ System: ${error.message}`);
        results.push({ name: 'System', status: '❌', error: error.message });
    }

    try {
        console.log('\n2️⃣ Bridge Orchestrator...');
        const bridge = new BridgeOrchestrator();
        await bridge.initialize();
        const health = await bridge.getHealthStatus();
        console.log(`✅ Сервисов: ${health.services.loaded}, статус: ${health.status}`);
        results.push({ name: 'Bridge', status: '✅', services: health.services.loaded });
        await bridge.shutdown();
    } catch (error) {
        console.log(`❌ Bridge: ${error.message}`);
        results.push({ name: 'Bridge', status: '❌', error: error.message });
    }

    try {
        console.log('\n3️⃣ Program Orchestrator...');
        const program = new ProgramOrchestrator();
        await program.initialize();
        const health = await program.getHealthStatus();
        console.log(`✅ Сервисов: ${health.services.loaded}, статус: ${health.status}`);
        results.push({ name: 'Program', status: '✅', services: health.services.loaded });
        await program.shutdown();
    } catch (error) {
        console.log(`❌ Program: ${error.message}`);
        results.push({ name: 'Program', status: '❌', error: error.message });
    }

    try {
        console.log('\n4️⃣ Client Orchestrator...');
        const client = new ClientOrchestrator();
        await client.initialize();
        const health = await client.getHealthStatus();
        console.log(`✅ Сервисов: ${health.services.loaded}, статус: ${health.status}`);
        results.push({ name: 'Client', status: '✅', services: health.services.loaded });
        await client.shutdown();
    } catch (error) {
        console.log(`❌ Client: ${error.message}`);
        results.push({ name: 'Client', status: '❌', error: error.message });
    }

    try {
        console.log('\n5️⃣ Sandbox Orchestrator...');
        const sandbox = new SandboxOrchestrator();
        await sandbox.initialize();
        const health = await sandbox.getHealthStatus();
        console.log(`✅ Сервисов: ${health.services.loaded}, статус: ${health.status}`);
        results.push({ name: 'Sandbox', status: '✅', services: health.services.loaded });
        await sandbox.shutdown();
    } catch (error) {
        console.log(`❌ Sandbox: ${error.message}`);
        results.push({ name: 'Sandbox', status: '❌', error: error.message });
    }

    console.log('\n📊 ИТОГОВЫЙ ОТЧЕТ:');
    console.log('='.repeat(40));

    const successful = results.filter(r => r.status === '✅').length;

    results.forEach(r => {
        if (r.status === '✅') {
            console.log(`${r.status} ${r.name}: ${r.services} сервисов`);
        } else {
            console.log(`${r.status} ${r.name}: ${r.error}`);
        }
    });

    console.log(`\n🎯 Результат: ${successful}/5 оркестраторов работают`);

    if (successful === 5) {
        console.log('🎉 ВСЕ ОРКЕСТРАТОРЫ ГОТОВЫ К РАБОТЕ!');
    } else {
        console.log('⚠️  Некоторые оркестраторы требуют исправления');
    }

    return successful === 5;
}

if (require.main === module) {
    quickTest().then(success => {
        process.exit(success ? 0 : 1);
    });
}

module.exports = quickTest;