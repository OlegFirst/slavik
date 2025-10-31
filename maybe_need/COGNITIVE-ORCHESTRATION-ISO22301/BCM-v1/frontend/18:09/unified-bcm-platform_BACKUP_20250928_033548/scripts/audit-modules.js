#!/usr/bin/env node

// Module Audit Runner Script

const { runModuleAudit } = require('../tools/module-audit')
const { getAPIImplementationStatus, generateAPIDocumentation } = require('../lib/odoo-api-mapper')
const fs = require('fs')
const path = require('path')

async function main() {
  console.log('========================================')
  console.log('BCM Platform Comprehensive Audit')
  console.log('========================================\n')

  // Run module completeness audit
  console.log('1. Module Completeness Audit')
  console.log('----------------------------')
  await runModuleAudit()

  // Check API implementation status
  console.log('\n2. API Implementation Status')
  console.log('----------------------------')
  const apiStatus = getAPIImplementationStatus()
  console.log(`Total Endpoints: ${apiStatus.total}`)
  console.log(`Mock Implemented: ${apiStatus.mockImplemented} (${apiStatus.percentMock}%)`)
  console.log(`Real Implemented: ${apiStatus.realImplemented} (${apiStatus.percentReal}%)`)

  // Generate comprehensive report
  console.log('\n3. Generating Documentation')
  console.log('---------------------------')

  const apiDoc = generateAPIDocumentation()
  fs.writeFileSync(path.join(process.cwd(), 'api-documentation.md'), apiDoc)
  console.log('API documentation saved to: api-documentation.md')

  // Summary
  console.log('\n========================================')
  console.log('Audit Complete')
  console.log('========================================')
  console.log('\nGenerated files:')
  console.log('- module-audit-report.md')
  console.log('- api-documentation.md')

  // Exit code based on completeness
  const completenessThreshold = 50 // Minimum acceptable completeness
  if (apiStatus.percentMock < completenessThreshold) {
    console.log(`\n⚠ Warning: Mock implementation below ${completenessThreshold}%`)
    process.exit(1)
  }

  process.exit(0)
}

main().catch(error => {
  console.error('Audit failed:', error)
  process.exit(1)
})