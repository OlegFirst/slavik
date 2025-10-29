const { EventEmitter } = require('events');

class AuthBridge extends EventEmitter {
  constructor() {
    super();
    this.domainPermissions = new Map();
    this.roleMapping = new Map();
  }

  // Адаптирует системную аутентификацию для BCM модулей
  adaptForBCM(systemAuth) {
    return {
      userId: systemAuth.sub,
      roles: this.mapSystemRolesToBCM(systemAuth.roles),
      permissions: this.getBCMPermissions(systemAuth),
      context: {
        organization: systemAuth.org,
        department: systemAuth.dept,
        bcmLevel: this.determineBCMLevel(systemAuth.roles)
      }
    };
  }

  // Маппинг системных ролей на BCM роли
  mapSystemRolesToBCM(systemRoles) {
    const bcmRoles = [];

    for (const role of systemRoles) {
      if (role === 'admin') bcmRoles.push('bcm_manager');
      if (role === 'user') bcmRoles.push('bcm_user');
      if (role === 'viewer') bcmRoles.push('bcm_viewer');
      if (role === 'analyst') bcmRoles.push('risk_analyst');
    }

    return bcmRoles;
  }

  // Определение BCM уровня доступа
  determineBCMLevel(roles) {
    if (roles.includes('admin')) return 'strategic';
    if (roles.includes('manager')) return 'tactical';
    return 'operational';
  }

  // Получение BCM-специфичных разрешений
  getBCMPermissions(systemAuth) {
    const permissions = [];

    if (systemAuth.permissions.includes('write')) {
      permissions.push('create_risk_assessment');
      permissions.push('update_bia');
      permissions.push('manage_incidents');
    }

    if (systemAuth.permissions.includes('read')) {
      permissions.push('view_risk_register');
      permissions.push('view_bia_results');
      permissions.push('view_incidents');
    }

    if (systemAuth.permissions.includes('execute')) {
      permissions.push('trigger_bcp');
      permissions.push('initiate_crisis_response');
    }

    return permissions;
  }

  // Валидация BCM-специфичных действий
  validateBCMAction(userContext, action, resource) {
    // Проверяем базовые права
    if (!userContext.permissions.includes(action)) {
      return { allowed: false, reason: 'insufficient_permissions' };
    }

    // Проверяем контекстные ограничения
    if (resource.criticality === 'high' && userContext.context.bcmLevel !== 'strategic') {
      return { allowed: false, reason: 'insufficient_bcm_level' };
    }

    // Проверяем департаментальные ограничения
    if (resource.department && resource.department !== userContext.context.department) {
      if (!userContext.roles.includes('bcm_manager')) {
        return { allowed: false, reason: 'cross_department_restriction' };
      }
    }

    return { allowed: true };
  }

  // Создание токена для BCM модулей
  createBCMToken(systemToken, moduleContext) {
    return {
      token: systemToken,
      bcmContext: {
        module: moduleContext.name,
        permissions: this.getBCMPermissions(systemToken),
        expires: new Date(Date.now() + 3600000)
      }
    };
  }
}

module.exports = AuthBridge;