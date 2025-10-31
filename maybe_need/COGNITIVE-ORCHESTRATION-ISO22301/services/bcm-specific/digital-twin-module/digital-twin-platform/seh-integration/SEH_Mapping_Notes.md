# SEH Mapping Notes (DT ↔ Salesforce ↔ Sim/Impact)
Дата: 2025-08-16

## Core
- Program ↔ Program__c (PMM)
- Service ↔ Service__c (PMM)
- Participant ↔ Contact (PMM Engagement) или кастомная сущность
- ServiceDelivery ↔ Service_Delivery__c (PMM)
- Indicator/Target/Measurement ↔ Outcome/Indicator/Target/Measurement (Outcome Mgmt)
- FundingProgram/Application/Award/Disbursement ↔ Grantmaking объекты
- BCMScenario/BCMTest ↔ кастомные объекты BCM_*

## Events
- indicator.measured — из Measurement или CSV/IoT агрегаций
- service.delivery.recorded — из PMM Service Delivery
- grant.disbursement.made — из Disbursement
- bcm.test.completed — из BCM_Test

## Sim I/O
- /api/v1/sim/run — capacity_sweep, routing_vrp, disbursement, bcm_outage
- /api/v1/impact/optimize — policy search на ToC

