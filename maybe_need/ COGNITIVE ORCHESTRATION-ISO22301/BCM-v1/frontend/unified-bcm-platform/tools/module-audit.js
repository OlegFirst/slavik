#!/usr/bin/env node

const fs = require('fs')
const path = require('path')

// Expected modules structure based on current implementation
const EXPECTED_MODULES = [
  { name: 'core', path: '/modules/core', expectedSections: ['overview', 'processes', 'lifecycle', 'organization', 'controls'] },
  { name: 'ai-control', path: '/modules/ai-control', expectedSections: ['overview', 'organs', 'coordination', 'monitoring', 'settings'] },
  { name: 'incidents', path: '/modules/incidents', expectedSections: ['overview', 'response', 'recovery', 'communications', 'reporting'] },
  { name: 'governance', path: '/modules/governance', expectedSections: ['overview', 'policies', 'framework', 'compliance', 'workflows'] },
  { name: 'plans', path: '/modules/plans', expectedSections: ['overview', 'continuity', 'response', 'recovery', 'communication'] },
  { name: 'reporting', path: '/modules/reporting', expectedSections: ['overview', 'dashboards', 'analytics', 'compliance', 'exports'] },
  { name: 'config', path: '/modules/config', expectedSections: ['overview', 'system', 'integrations', 'workflows', 'monitoring'] },
  { name: 'kpi', path: '/modules/kpi', expectedSections: ['overview', 'metrics', 'dashboards', 'analytics', 'reporting'] },
  { name: 'audit', path: '/modules/audit', expectedSections: ['overview', 'audits', 'findings', 'actions', 'reporting'] },
  { name: 'context', path: '/modules/context', expectedSections: ['overview', 'organization', 'environment', 'stakeholders', 'objectives'] },
  { name: 'training', path: '/modules/training', expectedSections: ['overview', 'courses', 'learners', 'records', 'planning'] },
  { name: 'templates', path: '/modules/templates', expectedSections: ['overview', 'templates', 'instances', 'categories', 'library'] },
  { name: 'clients', path: '/modules/clients', expectedSections: ['overview', 'clients', 'contracts', 'assessments', 'analytics'] },
  { name: 'exercise', path: '/modules/exercise', expectedSections: ['overview', 'exercises', 'scenarios', 'program', 'analytics'] },
  { name: 'bia', path: '/modules/bia', expectedSections: ['overview', 'analysis', 'dependencies', 'impacts', 'reporting'] },
  { name: 'risk', path: '/modules/risk', expectedSections: ['overview', 'assessment', 'treatment', 'monitoring', 'reporting'] }
]

async function runModuleAudit() {
  console.log('Running comprehensive module audit...')

  const auditResults = []
  let totalModules = EXPECTED_MODULES.length
  let completedModules = 0

  for (const module of EXPECTED_MODULES) {
    const result = await auditModule(module)
    auditResults.push(result)

    if (result.completeness >= 80) {
      completedModules++
    }

    console.log(`${module.name}: ${result.completeness}% complete - ${result.status}`)
  }

  // Generate summary
  const overallCompletion = Math.round((completedModules / totalModules) * 100)

  console.log(`\nAudit Summary:`)
  console.log(`Total modules: ${totalModules}`)
  console.log(`Modules ≥80% complete: ${completedModules}`)
  console.log(`Overall platform completion: ${overallCompletion}%`)

  // Generate detailed report
  const report = generateAuditReport(auditResults, overallCompletion)
  fs.writeFileSync(path.join(process.cwd(), 'module-audit-report.md'), report)
  console.log('Detailed report saved to: module-audit-report.md')

  return { overallCompletion, auditResults }
}

async function auditModule(module) {
  const modulePath = path.join(process.cwd(), 'app', module.path)
  const componentPath = path.join(process.cwd(), 'components', 'modules')

  const result = {
    name: module.name,
    path: module.path,
    completeness: 0,
    status: 'Missing',
    details: {
      pageExists: false,
      componentExists: false,
      sectionsImplemented: 0,
      expectedSections: module.expectedSections.length,
      implementedSections: [],
      missingFeatures: []
    }
  }

  // Check if page exists
  const pageFile = path.join(modulePath, 'page.tsx')
  if (fs.existsSync(pageFile)) {
    result.details.pageExists = true
    result.completeness += 20 // 20% for page existence
  }

  // Check if component exists - map module names to actual component names
  const componentMapping = {
    'core': 'BCMCore.tsx',
    'ai-control': 'AIControlCenter.tsx',
    'incidents': 'IncidentManagement.tsx',
    'governance': 'Governance.tsx',
    'plans': 'PlansManagement.tsx',
    'reporting': 'Reporting.tsx',
    'config': 'Configuration.tsx',
    'kpi': 'KPIManagement.tsx',
    'audit': 'Audit.tsx',
    'context': 'ContextManagement.tsx',
    'training': 'Training.tsx',
    'templates': 'Templates.tsx',
    'clients': 'Clients.tsx',
    'exercise': 'Exercise.tsx',
    'bia': 'BIAModule.tsx',
    'risk': 'RiskManagement.tsx'
  }

  const componentFile = path.join(componentPath, componentMapping[module.name] || `${capitalizeFirstLetter(module.name)}.tsx`)
  const componentFileAlt = path.join(componentPath, `${module.name}.tsx`)

  if (fs.existsSync(componentFile) || fs.existsSync(componentFileAlt)) {
    result.details.componentExists = true
    result.completeness += 30 // 30% for component existence

    // Analyze component content for sections
    try {
      const componentContent = fs.readFileSync(
        fs.existsSync(componentFile) ? componentFile : componentFileAlt,
        'utf8'
      )

      // Check for expected sections in tabs
      for (const section of module.expectedSections) {
        if (componentContent.includes(section) ||
            componentContent.includes(capitalizeFirstLetter(section)) ||
            componentContent.includes(section.toLowerCase())) {
          result.details.implementedSections.push(section)
          result.details.sectionsImplemented++
        }
      }

      // Calculate section completeness (50% of total score)
      const sectionCompleteness = (result.details.sectionsImplemented / result.details.expectedSections) * 50
      result.completeness += sectionCompleteness

    } catch (error) {
      console.warn(`Could not analyze component for ${module.name}:`, error.message)
    }
  }

  // Determine status
  if (result.completeness >= 90) {
    result.status = 'Complete'
  } else if (result.completeness >= 80) {
    result.status = 'Good'
  } else if (result.completeness >= 60) {
    result.status = 'Partial'
  } else if (result.completeness >= 30) {
    result.status = 'Started'
  } else {
    result.status = 'Missing'
  }

  return result
}

function generateAuditReport(auditResults, overallCompletion) {
  const timestamp = new Date().toISOString()

  let report = `# BCM Platform Module Audit Report\n\n`
  report += `**Generated:** ${timestamp}\n`
  report += `**Overall Platform Completion:** ${overallCompletion}%\n\n`

  report += `## Executive Summary\n\n`
  report += `This audit evaluated ${auditResults.length} planned BCM platform modules.\n\n`

  const statusCounts = auditResults.reduce((acc, result) => {
    acc[result.status] = (acc[result.status] || 0) + 1
    return acc
  }, {})

  report += `### Status Distribution:\n`
  Object.entries(statusCounts).forEach(([status, count]) => {
    report += `- **${status}:** ${count} modules\n`
  })

  report += `\n## Detailed Module Analysis\n\n`

  auditResults.forEach(result => {
    report += `### ${result.name} (${result.completeness}% - ${result.status})\n`
    report += `- **Path:** ${result.path}\n`
    report += `- **Page exists:** ${result.details.pageExists ? '✅' : '❌'}\n`
    report += `- **Component exists:** ${result.details.componentExists ? '✅' : '❌'}\n`
    report += `- **Sections implemented:** ${result.details.sectionsImplemented}/${result.details.expectedSections}\n`

    if (result.details.implementedSections.length > 0) {
      report += `- **Implemented sections:** ${result.details.implementedSections.join(', ')}\n`
    }

    report += `\n`
  })

  report += `## Recommendations\n\n`

  const incompleteModules = auditResults.filter(r => r.completeness < 80)
  if (incompleteModules.length > 0) {
    report += `### Priority Fixes Required:\n`
    incompleteModules.forEach(module => {
      report += `- **${module.name}:** ${80 - module.completeness}% improvement needed\n`
    })
  }

  report += `\n### Next Steps:\n`
  report += `1. Address modules below 80% completion\n`
  report += `2. Implement missing sections in partial modules\n`
  report += `3. Conduct functional testing of completed modules\n`
  report += `4. Prepare for production deployment\n`

  return report
}

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1)
}

module.exports = { runModuleAudit, auditModule }