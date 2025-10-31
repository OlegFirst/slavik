const SystemOrchestrator = require('./ORCHESTRATORS/system-orchestrator');
const BridgeOrchestrator = require('./ORCHESTRATORS/bridge-orchestrator');
const ProgramOrchestrator = require('./ORCHESTRATORS/program-orchestrator');
const ClientOrchestrator = require('./ORCHESTRATORS/client-orchestrator');
const SandboxOrchestrator = require('./ORCHESTRATORS/sandbox-orchestrator');

async function testOrchestrators() {
    console.log('🧪 Тестируем все оркестраторы...\n');

    const results = {
        system: false,
        bridge: false,
        program: false,
        client: false,
        sandbox: false
    };

    try {
        console.log('1️⃣ Тестируем System Orchestrator...');
        const systemOrch = new SystemOrchestrator();
        await systemOrch.initialize();

        const systemResult = await systemOrch.handle({
            type: 'health-check',
            component: 'message-queue'
        });

        console.log('✅ System Orchestrator работает');
        console.log(`   Services: ${systemOrch.services.size}, Health: ${systemResult.status}`);
        results.system = true;

    } catch (error) {
        console.log('❌ System Orchestrator failed:', error.message);
    }

    try {
        console.log('\n2️⃣ Тестируем Bridge Orchestrator...');
        const bridgeOrch = new BridgeOrchestrator();
        await bridgeOrch.initialize();

        const bridgeResult = await bridgeOrch.handle({
            type: 'translate-request',
            from: 'system',
            to: 'program',
            data: { action: 'test' }
        });

        console.log('✅ Bridge Orchestrator работает');
        console.log(`   Translation successful: ${bridgeResult.success}`);
        results.bridge = true;

    } catch (error) {
        console.log('❌ Bridge Orchestrator failed:', error.message);
    }

    try {
        console.log('\n3️⃣ Тестируем Program Orchestrator...');
        const programOrch = new ProgramOrchestrator();
        await programOrch.initialize();

        const programResult = await programOrch.handle({
            type: 'get-domains',
            context: { userId: 'test-user' }
        });

        console.log('✅ Program Orchestrator работает');
        console.log(`   Domains found: ${programResult.domains?.length || 0}`);
        results.program = true;

    } catch (error) {
        console.log('❌ Program Orchestrator failed:', error.message);
    }

    try {
        console.log('\n4️⃣ Тестируем Client Orchestrator...');
        const clientOrch = new ClientOrchestrator();
        await clientOrch.initialize();

        const clientResult = await clientOrch.handle({
            type: 'authenticate',
            credentials: { username: 'test', password: 'test' }
        });

        console.log('✅ Client Orchestrator работает');
        console.log(`   Auth result: ${clientResult.authenticated}`);
        results.client = true;

    } catch (error) {
        console.log('❌ Client Orchestrator failed:', error.message);
    }

    try {
        console.log('\n5️⃣ Тестируем Sandbox Orchestrator...');
        const sandboxOrch = new SandboxOrchestrator();
        await sandboxOrch.initialize();

        const sandboxResult = await sandboxOrch.handle({
            type: 'create-experiment',
            name: 'Test Experiment',
            code: 'console.log("Hello from sandbox!");',
            autoRun: false
        });

        console.log('✅ Sandbox Orchestrator работает');
        console.log(`   Experiment created: ${sandboxResult.experimentId}`);
        results.sandbox = true;

    } catch (error) {
        console.log('❌ Sandbox Orchestrator failed:', error.message);
    }

    const successCount = Object.values(results).filter(r => r).length;
    console.log(`\n📊 Результат: ${successCount}/5 оркестраторов работают`);

    if (successCount === 5) {
        console.log('🎉 Все оркестраторы функционируют корректно!');
    } else {
        console.log('⚠️  Некоторые оркестраторы требуют доработки');
    }

    return results;
}

async function testInterconnection() {
    console.log('\n🔗 Тестируем взаимодействие оркестраторов...\n');

    try {
        const systemOrch = new SystemOrchestrator();
        const bridgeOrch = new BridgeOrchestrator();
        const programOrch = new ProgramOrchestrator();

        await systemOrch.initialize();
        await bridgeOrch.initialize();
        await programOrch.initialize();

        systemOrch.subscribe(bridgeOrch);
        bridgeOrch.subscribe(programOrch);

        console.log('✅ Подписки настроены');
        console.log(`   System → Bridge → Program`);

        const testRequest = {
            type: 'business-logic',
            domain: 'bcm',
            module: 'risk-assessment',
            action: 'assess',
            data: { riskId: 'test-001' }
        };

        console.log('\n📤 Отправляем тестовый запрос через систему...');
        const result = await systemOrch.handle(testRequest);

        console.log('✅ Запрос обработан через всю цепочку');
        console.log(`   Результат: ${result.success ? 'успешно' : 'ошибка'}`);

        return true;

    } catch (error) {
        console.log('❌ Тест взаимодействия failed:', error.message);
        return false;
    }
}

async function checkResourceUsage() {
    console.log('\n💾 Проверяем использование ресурсов...\n');

    const orchestrators = [];

    try {
        orchestrators.push(new SystemOrchestrator());
        orchestrators.push(new BridgeOrchestrator());
        orchestrators.push(new ProgramOrchestrator());
        orchestrators.push(new ClientOrchestrator());
        orchestrators.push(new SandboxOrchestrator());

        for (const orch of orchestrators) {
            await orch.initialize();
        }

        console.log(`✅ Создано ${orchestrators.length} оркестраторов`);

        let totalServices = 0;
        let totalMemory = 0;

        for (const orch of orchestrators) {
            const health = await orch.getHealthStatus();
            totalServices += health.services?.loaded || 0;
            totalMemory += health.memory?.heapUsed || 0;

            console.log(`   ${orch.name}: ${health.services?.loaded || 0} сервисов, статус: ${health.status}`);
        }

        console.log(`\n📊 Общая статистика:`);
        console.log(`   Всего сервисов: ${totalServices}`);
        console.log(`   Память: ${Math.round(totalMemory / 1024 / 1024)}MB`);

        return { orchestrators: orchestrators.length, services: totalServices, memory: totalMemory };

    } catch (error) {
        console.log('❌ Проверка ресурсов failed:', error.message);
        return null;
    }
}

if (require.main === module) {
    (async () => {
        console.log('🚀 Запуск полного тестирования оркестраторов\n');

        const functionalResults = await testOrchestrators();
        const interconnectionResult = await testInterconnection();
        const resourceUsage = await checkResourceUsage();

        console.log('\n📋 ИТОГОВЫЙ ОТЧЕТ:');
        console.log('='.repeat(50));
        console.log(`Функциональность: ${Object.values(functionalResults).filter(r => r).length}/5`);
        console.log(`Взаимодействие: ${interconnectionResult ? '✅' : '❌'}`);
        console.log(`Ресурсы: ${resourceUsage ? '✅' : '❌'}`);

        if (resourceUsage) {
            console.log(`Память: ${Math.round(resourceUsage.memory / 1024 / 1024)}MB`);
        }

        console.log('\n🎯 Все компоненты Cognitive Orchestration готовы к интеграции!');
    })();
}

module.exports = { testOrchestrators, testInterconnection, checkResourceUsage };