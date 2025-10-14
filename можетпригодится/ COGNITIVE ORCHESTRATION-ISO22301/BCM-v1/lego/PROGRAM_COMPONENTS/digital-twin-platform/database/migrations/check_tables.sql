-- Проверка созданных таблиц
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'organizations',
    'digital_twins', 
    'departments',
    'simulations',
    'metrics',
    'predictions',
    'audit_logs',
    'sessions',
    'reports',
    'scenarios'
)
ORDER BY table_name;