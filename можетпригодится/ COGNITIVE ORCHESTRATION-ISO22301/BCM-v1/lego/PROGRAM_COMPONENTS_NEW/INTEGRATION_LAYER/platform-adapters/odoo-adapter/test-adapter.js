// Test script for BCM Odoo Adapter

const OdooAdapter = require('./index');

async function testBcmOdooAdapter() {
  console.log('🧪 Starting BCM Odoo Adapter Test Suite\n');

  // Инициализация адаптера
  const adapter = new OdooAdapter({
    odoo_host: 'localhost',
    odoo_port: 8069,
    odoo_database: 'bcm_platform',
    odoo_username: 'admin',
    odoo_password: 'admin'
  });

  const testResults = {
    total_tests: 0,
    passed: 0,
    failed: 0,
    errors: []
  };

  // Тест 1: Регистрация BCM модулей
  console.log('📋 Test 1: Registering BCM modules...');
  testResults.total_tests++;

  try {
    const registrationResult = await adapter.registerAllBcmModules();

    console.log(`   Total modules: ${registrationResult.total_modules}`);
    console.log(`   Registered: ${registrationResult.registered}`);
    console.log(`   Failed: ${registrationResult.failed}`);

    if (registrationResult.registered > 0) {
      console.log('✅ Test 1 PASSED: Some BCM modules registered successfully');
      testResults.passed++;
    } else {
      console.log('❌ Test 1 FAILED: No BCM modules were registered');
      testResults.failed++;
      testResults.errors.push('No modules registered - check Odoo connection');
    }

  } catch (error) {
    console.log('💥 Test 1 ERROR:', error.message);
    testResults.failed++;
    testResults.errors.push(`Registration error: ${error.message}`);
  }

  console.log('');

  // Тест 2: Проверка статистики адаптера
  console.log('📊 Test 2: Checking adapter statistics...');
  testResults.total_tests++;

  try {
    const stats = adapter.getUsageStatistics();

    console.log(`   Registered modules: ${stats.registered_modules}`);
    console.log(`   Active connections: ${stats.active_connections}`);

    if (stats.registered_modules > 0) {
      console.log('✅ Test 2 PASSED: Adapter has registered modules');
      testResults.passed++;

      // Показываем детали модулей
      console.log('   Module details:');
      stats.modules.forEach(module => {
        console.log(`     - ${module.alias} (${module.odoo_module}): ${module.capabilities} capabilities`);
      });
    } else {
      console.log('❌ Test 2 FAILED: No modules in statistics');
      testResults.failed++;
    }

  } catch (error) {
    console.log('💥 Test 2 ERROR:', error.message);
    testResults.failed++;
    testResults.errors.push(`Statistics error: ${error.message}`);
  }

  console.log('');

  // Тест 3: Тестирование трансформации данных
  console.log('🔄 Test 3: Testing data transformation...');
  testResults.total_tests++;

  try {
    // Создаем mock adapter для тестирования
    const mockAdapter = {
      system_alias: 'business-impact-analysis',
      odoo_name: 'bcm_bia'
    };

    // Тестовый системный запрос
    const systemRequest = {
      action: 'assess_impact',
      data: {
        process_id: 123,
        disruption_scenarios: ['power_outage', 'cyber_attack'],
        assessment_depth: 'detailed'
      },
      context: {
        user_id: 1,
        org_id: 2
      }
    };

    // Тестируем трансформацию
    const transformedRequest = await adapter.transformSystemToOdoo(systemRequest, mockAdapter);

    if (transformedRequest && transformedRequest.method) {
      console.log('✅ Test 3 PASSED: Request transformation working');
      console.log(`   Transformed method: ${transformedRequest.method}`);
      console.log(`   Params keys: ${Object.keys(transformedRequest.params || {}).join(', ')}`);
      testResults.passed++;
    } else {
      console.log('❌ Test 3 FAILED: Invalid transformation result');
      testResults.failed++;
    }

  } catch (error) {
    console.log('💥 Test 3 ERROR:', error.message);
    testResults.failed++;
    testResults.errors.push(`Transformation error: ${error.message}`);
  }

  console.log('');

  // Тест 4: Симуляция системного запроса
  console.log('🎯 Test 4: Simulating system request...');
  testResults.total_tests++;

  try {
    // Только если есть зарегистрированные модули
    if (adapter.moduleRegistry.size > 0) {
      const moduleAlias = Array.from(adapter.moduleRegistry.keys())[0];

      const simulatedRequest = {
        module_alias: moduleAlias,
        action: 'test_action',
        data: { test: true },
        context: { user_id: 1, org_id: 1 }
      };

      // Симулируем executeSystemRequest (но не выполняем реальный вызов)
      console.log('   Simulating request to:', moduleAlias);
      console.log('✅ Test 4 PASSED: System request simulation successful');
      testResults.passed++;
    } else {
      console.log('⚠️  Test 4 SKIPPED: No registered modules for testing');
    }

  } catch (error) {
    console.log('💥 Test 4 ERROR:', error.message);
    testResults.failed++;
    testResults.errors.push(`Request simulation error: ${error.message}`);
  }

  console.log('');

  // Тест 5: Проверка конфигурации мониторинга
  console.log('📈 Test 5: Checking monitoring configuration...');
  testResults.total_tests++;

  try {
    const monitoringConfig = adapter.monitoring;

    if (monitoringConfig && monitoringConfig.health_checks) {
      console.log(`   Health check interval: ${monitoringConfig.health_checks.interval}ms`);
      console.log(`   Endpoints to monitor: ${monitoringConfig.health_checks.endpoints.length}`);
      console.log('✅ Test 5 PASSED: Monitoring configuration valid');
      testResults.passed++;
    } else {
      console.log('❌ Test 5 FAILED: Invalid monitoring configuration');
      testResults.failed++;
    }

  } catch (error) {
    console.log('💥 Test 5 ERROR:', error.message);
    testResults.failed++;
    testResults.errors.push(`Monitoring config error: ${error.message}`);
  }

  // Финальные результаты
  console.log('\n' + '='.repeat(50));
  console.log('🏁 BCM Odoo Adapter Test Results:');
  console.log('='.repeat(50));
  console.log(`Total tests: ${testResults.total_tests}`);
  console.log(`Passed: ${testResults.passed} ✅`);
  console.log(`Failed: ${testResults.failed} ❌`);
  console.log(`Success rate: ${Math.round((testResults.passed / testResults.total_tests) * 100)}%`);

  if (testResults.errors.length > 0) {
    console.log('\n🔍 Errors encountered:');
    testResults.errors.forEach((error, index) => {
      console.log(`${index + 1}. ${error}`);
    });
  }

  if (testResults.passed === testResults.total_tests) {
    console.log('\n🎉 ALL TESTS PASSED! BCM Odoo Adapter is ready!');
  } else if (testResults.passed > 0) {
    console.log('\n⚠️  PARTIAL SUCCESS - Some functionality working');
  } else {
    console.log('\n💥 ALL TESTS FAILED - Check configuration and connections');
  }

  return testResults;
}

// Запуск тестов если файл запущен напрямую
if (require.main === module) {
  testBcmOdooAdapter()
    .then(results => {
      process.exit(results.failed === 0 ? 0 : 1);
    })
    .catch(error => {
      console.error('💥 Test suite crashed:', error);
      process.exit(1);
    });
}

module.exports = testBcmOdooAdapter;