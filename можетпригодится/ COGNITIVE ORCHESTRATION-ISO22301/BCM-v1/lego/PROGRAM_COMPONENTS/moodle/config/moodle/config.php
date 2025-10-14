<?php  // Moodle configuration file for BCM Platform Integration

unset($CFG);
global $CFG;
$CFG = new stdClass();

// Database settings
$CFG->dbtype    = 'pgsql';
$CFG->dblibrary = 'native';
$CFG->dbhost    = getenv('MOODLE_DATABASE_HOST') ?: 'moodle-postgres';
$CFG->dbname    = getenv('MOODLE_DATABASE_NAME') ?: 'moodle';
$CFG->dbuser    = getenv('MOODLE_DATABASE_USER') ?: 'moodleuser';
$CFG->dbpass    = getenv('MOODLE_DATABASE_PASSWORD') ?: 'moodle_secure_pass';
$CFG->prefix    = 'mdl_';
$CFG->dboptions = array (
  'dbpersist' => 0,
  'dbport' => getenv('MOODLE_DATABASE_PORT') ?: '5432',
  'dbsocket' => '',
  'dbcollation' => 'utf8_unicode_ci',
);

// Site settings
$CFG->wwwroot   = getenv('MOODLE_URL') ?: 'http://localhost:8080';
$CFG->dataroot  = '/var/www/moodledata';
$CFG->admin     = 'admin';

// BCM Platform specific settings
$CFG->fullname = 'BCM Training Platform';
$CFG->shortname = 'BCM-LMS';
$CFG->summary = 'Business Continuity Management Training and Competency Platform based on ISO 22301';

// Performance settings
$CFG->directorypermissions = 0777;
$CFG->passwordsaltmain = getenv('MOODLE_PASSWORD_SALT') ?: 'bcm_platform_salt_change_in_production';

// Session settings
$CFG->sessiontimeout = 7200;  // 2 hours
$CFG->sessioncookietimeout = 7200;
$CFG->sessioncookiepath = '/';
$CFG->sessioncookiesecure = false;  // Set to true in production with HTTPS
$CFG->sessioncookiesamesite = 'Lax';

// Cache settings - Redis
$CFG->session_handler_class = '\core\session\redis';
$CFG->session_redis_host = 'moodle-redis';
$CFG->session_redis_port = 6379;
$CFG->session_redis_auth = getenv('MOODLE_REDIS_PASSWORD') ?: 'redis_secure_pass';
$CFG->session_redis_database = 0;
$CFG->session_redis_acquire_lock_timeout = 120;

// Application cache - Redis
$CFG->cachestores = [
    'redis' => [
        'class' => 'cachestore_redis',
        'configuration' => [
            'server' => 'moodle-redis:6379',
            'password' => getenv('MOODLE_REDIS_PASSWORD') ?: 'redis_secure_pass',
            'database' => 1,
        ]
    ]
];

// Web services for BCM Platform integration
$CFG->enablewebservices = 1;
$CFG->webserviceprotocols = 'rest,soap';

// Mobile app support
$CFG->enablemobilewebservice = 1;

// Competency framework enabled for BCM
$CFG->enablecompetencies = 1;

// Grade aggregation for BCM assessments
$CFG->grade_aggregations_visible = 'mean,weighted_mean,simple_weighted_mean,min,max';

// Course completion tracking
$CFG->enablecompletion = 1;
$CFG->completiondefault = 1;

// Badges for BCM certifications
$CFG->enablebadges = 1;

// BCM Platform custom settings
$CFG->bcm_platform = [
    'webhook_url' => getenv('BCM_WEBHOOK_URL') ?: 'http://moodle-webhook-receiver:8093/webhook/moodle',
    'api_token' => getenv('MOODLE_API_TOKEN') ?: '',
    'company_isolation' => true,
    'competency_framework' => 'ISO_22301_BCM',
    'default_timezone' => 'Europe/Kiev',
    'language_pack' => 'en,uk,ru',
    'certificate_templates' => '/var/www/html/local/bcm/certificates/',
    'exercise_integration' => true,
    'thehive_sync' => getenv('THEHIVE_INTEGRATION_ENABLED') ?: false
];

// File uploads
$CFG->maxbytes = 52428800;  // 50MB
$CFG->userquota = 104857600;  // 100MB per user
$CFG->coursefilesenabled = 1;

// Security settings
$CFG->passwordpolicy = 1;
$CFG->minpasswordlength = 8;
$CFG->minpassworddigits = 1;
$CFG->minpasswordlower = 1;
$CFG->minpasswordupper = 1;
$CFG->minpasswordnonalphanum = 1;
$CFG->maxconsecutiveidentchars = 2;

// BCM specific security
$CFG->forcelogin = 1;  // Force login for all content
$CFG->opentogoogle = 0;  // Disable Google indexing
$CFG->allowobjectembed = 0;  // Security - disable object embedding
$CFG->enabletrusttext = 0;  // Disable trusted content

// Logging for BCM compliance
$CFG->loggingenabled = 1;
$CFG->loglifetime = 365;  // Keep logs for 1 year
$CFG->logguests = 1;

// Email settings for BCM notifications
$CFG->smtphosts = getenv('SMTP_HOST') ?: 'localhost';
$CFG->smtpsecure = getenv('SMTP_SECURE') ?: 'tls';
$CFG->smtpuser = getenv('SMTP_USER') ?: '';
$CFG->smtppass = getenv('SMTP_PASSWORD') ?: '';
$CFG->smtpmaxbulk = 1;
$CFG->noreplyaddress = getenv('MOODLE_NOREPLY_EMAIL') ?: 'noreply@bcm-platform.local';

// Backup settings
$CFG->backup_auto_active = 1;
$CFG->backup_auto_weekdays = '0111110';  // Monday to Friday
$CFG->backup_auto_hour = 2;
$CFG->backup_auto_minute = 30;
$CFG->backup_auto_storage = 1;  // Keep backup files
$CFG->backup_auto_destination = '/var/www/moodledata/backups/';

// Multi-language support for international BCM compliance
$CFG->langmenu = 1;
$CFG->langlist = 'en,uk,ru,de,fr,es';

// Custom theme for BCM branding
$CFG->theme = 'bcm';
$CFG->themedir = '/var/www/html/theme';

// Custom fields for BCM data
$CFG->customfields_bcm = [
    'company_id' => [
        'type' => 'text',
        'required' => true,
        'description' => 'BCM Platform Company ID'
    ],
    'employee_id' => [
        'type' => 'text',
        'required' => false,
        'description' => 'Employee ID in BCM Platform'
    ],
    'department' => [
        'type' => 'select',
        'options' => ['IT', 'HR', 'Finance', 'Operations', 'Management'],
        'description' => 'Department for BCM training tracking'
    ],
    'bcm_role' => [
        'type' => 'select',
        'options' => ['bcm_coordinator', 'team_leader', 'team_member', 'stakeholder'],
        'description' => 'Role in BCM structure'
    ],
    'certification_level' => [
        'type' => 'select',
        'options' => ['foundation', 'practitioner', 'expert', 'lead_auditor'],
        'description' => 'BCM Certification Level'
    ]
];

// Plugin configurations for BCM
$CFG->forced_plugin_settings = [
    'enrol_manual' => ['status' => ENROL_INSTANCE_ENABLED],
    'enrol_self' => ['status' => ENROL_INSTANCE_ENABLED],
    'format_topics' => ['status' => true],
    'mod_quiz' => ['status' => true],
    'mod_scorm' => ['status' => true],
    'mod_certificate' => ['status' => true],
    'block_completionstatus' => ['status' => true],
    'block_progress' => ['status' => true],
    'report_completion' => ['status' => true],
    'tool_dataprivacy' => ['status' => true]  // GDPR compliance
];

// Elasticsearch for global search (if enabled)
if (getenv('MOODLE_SEARCH_ENGINE') === 'elasticsearch') {
    $CFG->searchengine = 'elasticsearch';
    $CFG->searchhostname = 'moodle-elasticsearch';
    $CFG->searchport = 9200;
    $CFG->searchindexname = 'moodle_bcm';
    $CFG->searchusername = '';
    $CFG->searchpassword = '';
}

// Development settings (remove in production)
if (getenv('MOODLE_DEBUG') === 'true') {
    $CFG->debug = (E_ALL | E_STRICT);
    $CFG->debugdisplay = 1;
    $CFG->debugsmtp = 1;
    $CFG->perfdebug = 15;
    $CFG->debugpageinfo = 1;
}

// BCM Platform webhook integration
$CFG->bcm_webhooks = [
    'enabled' => true,
    'events' => [
        'user_enrolled',
        'course_completed', 
        'competency_achieved',
        'certificate_issued',
        'grade_updated'
    ],
    'webhook_url' => getenv('BCM_WEBHOOK_URL') ?: 'http://moodle-webhook-receiver:8093/webhook/moodle',
    'secret' => getenv('MOODLE_WEBHOOK_SECRET') ?: 'change_in_production',
    'timeout' => 30,
    'retry_attempts' => 3
];

require_once(__DIR__ . '/lib/setup.php');

// End of config.php
