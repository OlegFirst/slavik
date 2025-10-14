"""
Example Usage - Примеры использования Process Framework

Демонстрирует:
- Регистрацию процессов
- Запуск процесса BIA
- Взаимодействие с пользователем через формы
- Генерацию стандартизированных документов
"""

from pathlib import Path
from datetime import datetime
from process_framework import get_process_framework, ProcessStatus
from bcm_processes import register_all_bcm_processes
from document_templates import get_document_library


def example_1_register_processes():
    """Пример 1: Регистрация стандартных BCM процессов"""
    print("="*60)
    print("ПРИМЕР 1: Регистрация процессов")
    print("="*60)

    # Получить фреймворк
    framework = get_process_framework(Path("./processes"))

    # Зарегистрировать все BCM процессы
    count = register_all_bcm_processes(framework)

    print(f"\nЗарегистрировано процессов: {count}")
    print("\nДоступные процессы:")
    for process_id, process in framework.processes.items():
        print(f"  - {process_id}: {process.name}")
        print(f"    ISO Clause: {process.iso_clause}")
        print(f"    Шагов: {len(process.steps)}")


def example_2_start_bia_process():
    """Пример 2: Запуск процесса BIA"""
    print("\n" + "="*60)
    print("ПРИМЕР 2: Запуск процесса BIA")
    print("="*60)

    framework = get_process_framework()
    register_all_bcm_processes(framework)

    # Запустить процесс BIA
    instance = framework.start_process(
        process_id="bcm_bia_v1",
        started_by="john.doe@company.com",
        initial_data={
            "organization": "Acme Corporation",
            "department": "IT Department"
        }
    )

    print(f"\n✅ Процесс запущен!")
    print(f"   Instance ID: {instance.id}")
    print(f"   Статус: {instance.status.value}")
    print(f"   Текущий шаг: {instance.current_step_id}")

    return instance


def example_3_get_form_for_user():
    """Пример 3: Получение формы для пользователя"""
    print("\n" + "="*60)
    print("ПРИМЕР 3: Получение формы текущего шага")
    print("="*60)

    framework = get_process_framework()
    register_all_bcm_processes(framework)

    # Запустить процесс
    instance = framework.start_process(
        process_id="bcm_bia_v1",
        started_by="john.doe@company.com"
    )

    # Получить форму для текущего шага
    form = framework.get_current_step_form(instance.id)

    print(f"\nТекущий шаг: {form['step_name']}")
    print(f"Описание: {form['description']}")
    print(f"\nПоля формы ({len(form['fields'])}):")

    for field in form['fields']:
        print(f"\n  - {field['label']} ({field['name']})")
        print(f"    Тип: {field['type']}")
        print(f"    Обязательное: {field['required']}")
        if field['description']:
            print(f"    Описание: {field['description']}")
        if field['help_text']:
            print(f"    Подсказка: {field['help_text']}")

    return instance, form


def example_4_submit_form_data():
    """Пример 4: Заполнение формы пользователем"""
    print("\n" + "="*60)
    print("ПРИМЕР 4: Заполнение и отправка формы")
    print("="*60)

    framework = get_process_framework()
    register_all_bcm_processes(framework)

    # Запустить процесс
    instance = framework.start_process(
        process_id="bcm_bia_v1",
        started_by="john.doe@company.com"
    )

    print(f"\nТекущий шаг: {instance.current_step_id}")

    # Симуляция заполнения формы пользователем
    form_data = {
        "bia_scope": """
        Данный Business Impact Analysis охватывает следующие критичные области:
        1. IT Infrastructure Services
        2. Customer Support Operations
        3. Financial Transaction Processing
        4. Supply Chain Management
        5. Data Center Operations

        Анализ фокусируется на определении RTO/RPO и финансового воздействия
        для каждой из этих областей.
        """,
        "bia_objectives": """
        Цели данного BIA:
        1. Идентифицировать все критичные бизнес-функции
        2. Определить RTO и RPO для каждой функции
        3. Оценить финансовое воздействие прерывания
        4. Определить минимальные требования к ресурсам для восстановления
        5. Сформировать базу для разработки BC планов
        """,
        "stakeholders": """
        John Doe - CIO
        Jane Smith - CFO
        Bob Johnson - Head of Operations
        Alice Williams - Risk Manager
        Charlie Brown - IT Director
        """,
        "timeline": "2025-11-15"
    }

    print("\nДанные формы:")
    for key, value in form_data.items():
        print(f"  {key}: {value[:100]}..." if len(str(value)) > 100 else f"  {key}: {value}")

    # Отправить данные
    success, error, next_step = framework.execute_step(
        instance_id=instance.id,
        step_data=form_data,
        executed_by="john.doe@company.com"
    )

    if success:
        print(f"\n✅ Шаг выполнен успешно!")
        print(f"   Следующий шаг: {next_step}")

        # Проверить обновленный статус
        status = framework.get_process_status(instance.id)
        print(f"   Прогресс: {status['progress_percent']:.1f}%")
    else:
        print(f"\n❌ Ошибка: {error}")

    return instance


def example_5_complete_bia_process():
    """Пример 5: Полное прохождение процесса BIA"""
    print("\n" + "="*60)
    print("ПРИМЕР 5: Полное прохождение BIA")
    print("="*60)

    framework = get_process_framework()
    register_all_bcm_processes(framework)

    # Запустить процесс
    instance = framework.start_process(
        process_id="bcm_bia_v1",
        started_by="john.doe@company.com"
    )

    # Шаг 1: Инициация BIA
    step1_data = {
        "bia_scope": "IT Infrastructure and Customer Service operations across all regions",
        "bia_objectives": "Identify critical functions, determine RTO/RPO, assess financial impact",
        "stakeholders": "CIO, CFO, Head of Operations, Risk Manager",
        "timeline": "2025-11-15"
    }

    success, _, next_step = framework.execute_step(instance.id, step1_data, "john.doe")
    print(f"\n✅ Шаг 1 (Инициация): Выполнен → {next_step}")

    # Шаг 2: Критичные функции
    step2_data = {
        "business_functions": """
Customer Support System
Online Payment Processing
Order Management System
Inventory Management
Data Backup Services
        """,
        "function_dependencies": "Customer Support depends on CRM; Payment depends on Banking API"
    }

    success, _, next_step = framework.execute_step(instance.id, step2_data, "john.doe")
    print(f"✅ Шаг 2 (Критичные функции): Выполнен → {next_step}")

    # Шаг 3: Анализ воздействия
    step3_data = {
        "rto": 4,  # 4 часа
        "rpo": 60,  # 60 минут
        "financial_impact": "high",
        "reputational_impact": "critical",
        "regulatory_impact": "high",
        "impact_justification": """
Финансовое воздействие оценивается как высокое (High) так как прерывание Customer Support
и Payment Processing приведет к потере около $500K USD в день.

Репутационное воздействие критическое (Critical) - длительный простой Customer Support
приведет к массовому оттоку клиентов и негативному освещению в социальных сетях.

Регуляторное воздействие высокое (High) - нарушение SLA с клиентами может привести
к штрафам и судебным искам.

RTO установлен в 4 часа как компромисс между стоимостью решения и приемлемым риском.
RPO в 60 минут обеспечивает минимальную потерю транзакционных данных.
        """
    }

    success, _, next_step = framework.execute_step(instance.id, step3_data, "analyst")
    print(f"✅ Шаг 3 (Анализ воздействия): Выполнен → {next_step}")

    # Шаг 4: Требования к ресурсам
    step4_data = {
        "personnel_required": 25,
        "technology_required": """
- Hot standby data center
- Redundant network connectivity (2x ISPs)
- Cloud backup systems (AWS S3)
- Load balancer cluster
- Database replication (real-time)
        """,
        "facilities_required": """
- Primary: Main office (100 workstations)
- Backup: Remote work from home capability for all staff
- Alternate: Co-location facility in different city
        """,
        "third_party_dependencies": """
- AWS (cloud hosting)
- Twilio (communication services)
- Stripe (payment processing)
- MongoDB Atlas (database)
        """
    }

    success, _, next_step = framework.execute_step(instance.id, step4_data, "analyst")
    print(f"✅ Шаг 4 (Требования к ресурсам): Выполнен → {next_step}")

    # Шаг 5: Генерация отчета
    step5_data = {
        "report_format": "pdf",
        "include_recommendations": True
    }

    success, _, next_step = framework.execute_step(instance.id, step5_data, "manager")
    print(f"✅ Шаг 5 (Генерация отчета): Выполнен → {next_step}")

    # Шаг 6: Утверждение
    step6_data = {
        "approval_decision": "approved",
        "approval_comments": """
Отчет BIA рассмотрен и утвержден. Выводы и рекомендации соответствуют текущей
стратегии управления рисками. Рекомендовано приступить к разработке BC плана
на основе результатов данного анализа.
        """,
        "approver_name": "Michael Johnson",
        "approver_position": "Chief Information Officer"
    }

    success, _, next_step = framework.execute_step(instance.id, step6_data, "cio")
    print(f"✅ Шаг 6 (Утверждение): Выполнен → {next_step}")

    # Проверить финальный статус
    final_status = framework.get_process_status(instance.id)
    print(f"\n📊 Финальный статус процесса:")
    print(f"   Статус: {final_status['status']}")
    print(f"   Прогресс: {final_status['progress_percent']:.1f}%")
    print(f"   Начало: {final_status['started_at']}")
    print(f"   Окончание: {final_status['completed_at']}")

    return instance


def example_6_generate_bia_document():
    """Пример 6: Генерация документа BIA Report"""
    print("\n" + "="*60)
    print("ПРИМЕР 6: Генерация документа BIA Report")
    print("="*60)

    # Получить библиотеку шаблонов
    library = get_document_library()

    # Подготовить данные для документа
    # (в реальной системе эти данные берутся из instance.data)
    document_data = {
        "organization_name": "Acme Corporation",
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "prepared_by": "John Doe, BCM Manager",
        "status": "Approved",
        "confidentiality_level": "Internal - Confidential",
        "distribution_list": "Senior Management, BCM Team",
        "review_date": "2026-10-11",

        "key_findings": """
- 5 critical business functions identified
- Average RTO: 6 hours
- Average RPO: 90 minutes
- High dependency on third-party cloud services
- Adequate backup capabilities in place
        """,

        "critical_functions_count": 5,
        "average_rto": 6,
        "average_rpo": 90,

        "scope": """
This BIA covers IT infrastructure services, customer-facing operations,
and financial transaction processing across all geographical regions.
Excludes: HR administrative functions, non-critical marketing activities.
        """,

        "objectives": """
- Identify critical business functions and their interdependencies
- Determine recovery time and point objectives
- Assess potential impacts of disruptions
- Define minimum resource requirements for recovery
- Establish foundation for Business Continuity Planning
        """,

        "methodology": """
The BIA was conducted using:
1. Stakeholder interviews (15 participants)
2. Process mapping and dependency analysis
3. Financial impact modeling
4. IT systems inventory review
5. Third-party risk assessment
        """,

        "critical_functions": """
1. **Customer Support System** - RTO: 4h, RPO: 1h
2. **Online Payment Processing** - RTO: 2h, RPO: 30min
3. **Order Management System** - RTO: 8h, RPO: 2h
4. **Inventory Management** - RTO: 12h, RPO: 4h
5. **Data Backup Services** - RTO: 24h, RPO: 24h
        """,

        "function_dependencies": """
Critical dependencies identified:
- Customer Support System → CRM Database, Phone System
- Payment Processing → Banking API, Fraud Detection Service
- Order Management → Inventory Database, Shipping API
        """,

        "rto_summary": """
| Function | RTO | Justification |
|----------|-----|---------------|
| Customer Support | 4h | High customer impact after 4 hours |
| Payment Processing | 2h | Revenue loss $250K/hour |
| Order Management | 8h | Can use manual processes temporarily |
| Inventory Management | 12h | Impact increases gradually |
| Data Backup | 24h | Not customer-facing |
        """,

        "rpo_summary": """
Payment Processing: 30 minutes (financial transactions)
Customer Support: 1 hour (ticket data)
Others: 2-4 hours (acceptable data loss window)
        """,

        "financial_impact": """
**Direct Costs per Hour of Downtime:**
- Lost revenue: $250,000/hour
- Recovery operations: $50,000/hour
- Penalty payments (SLA): $100,000/day

**Estimated Total Impact:**
- 4 hours downtime: $1.6M
- 24 hours downtime: $7.2M
- 1 week downtime: $50M+
        """,

        "reputational_impact": """
**Short-term (< 8 hours):** Manageable with proactive communication
**Medium-term (8-24 hours):** Significant social media backlash expected
**Long-term (> 24 hours):** Permanent loss of customer trust, media coverage
        """,

        "regulatory_impact": """
- PCI DSS compliance at risk after 4 hours
- GDPR data protection requirements
- Contractual SLA obligations with major clients
- Potential fines: $500K - $2M depending on duration
        """,

        "impact_assessment": """
Overall risk level: **HIGH**

The combination of high financial impact, critical reputational risk,
and regulatory exposure places this in the high-priority category for
BC planning and investment.
        """,

        "personnel_requirements": """
Minimum staffing levels for recovery:
- Customer Support: 20 agents (40% of normal capacity)
- IT Operations: 5 engineers (24/7 coverage)
- Management: 2 incident managers
- Total minimum: 27 personnel
        """,

        "technology_requirements": """
- Hot standby data center with real-time replication
- Redundant network connectivity (multi-ISP)
- Cloud backup and recovery systems
- Load balancing and failover capabilities
- Real-time monitoring and alerting
        """,

        "facilities_requirements": """
- Primary site: Corporate headquarters (current)
- Backup site: Work-from-home capability for 100% of staff
- Alternative site: Co-location facility 50km away
- Minimum workspace: Laptop + VPN + phone for each critical role
        """,

        "third_party_dependencies": """
Critical vendors identified:
1. AWS - Infrastructure hosting (HIGH criticality)
2. Twilio - Communication services (HIGH)
3. Stripe - Payment processing (CRITICAL)
4. MongoDB Atlas - Database services (CRITICAL)
5. Cloudflare - CDN and DDoS protection (MEDIUM)

All vendors assessed for BC capabilities.
        """,

        "recommendations": """
Based on this analysis, we recommend:

1. **Immediate Actions (0-3 months):**
   - Implement hot standby for payment processing
   - Enhance monitoring and alerting
   - Document recovery procedures for all critical functions

2. **Short-term (3-6 months):**
   - Conduct tabletop exercise of BC plans
   - Establish alternate work location arrangements
   - Review and update vendor contracts for BC clauses

3. **Medium-term (6-12 months):**
   - Build redundant infrastructure
   - Train recovery teams
   - Implement automated failover capabilities
        """,

        "priority_actions": """
1. Hot standby for Payment Processing - **CRITICAL**
2. Document recovery procedures - **HIGH**
3. Vendor BC assessment - **HIGH**
4. Alternate site preparation - **MEDIUM**
5. Team training - **MEDIUM**
        """,

        "resource_allocation_recommendations": """
Proposed budget:
- Infrastructure improvements: $500K
- Alternate site setup: $200K
- Training and exercises: $50K
- Consulting and external support: $100K
- **Total: $850K**

ROI: Prevents potential $7M+ loss from 24_hour outage.
        """,

        "approver_name": "Michael Johnson",
        "approver_position": "Chief Information Officer",
        "approval_date": datetime.now().strftime("%Y-%m-%d"),
        "approval_comments": """
This BIA provides a solid foundation for our BC planning efforts.
The analysis is thorough and the recommendations are actionable.
Approved for implementation.
        """,

        "generation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "next_review_date": "2026-10-11"
    }

    # Сгенерировать документ
    document_content = library.generate_document(
        template_id="bia_report_v1",
        variables=document_data
    )

    print("\n📄 Документ сгенерирован!")
    print("\n" + "="*60)
    print(document_content[:2000])  # Первые 2000 символов
    print("\n... (document continues) ...\n")
    print("="*60)

    # Сохранить в файл
    output_path = Path("./generated_documents/BIA_Report_Acme_Corp.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(document_content)

    print(f"\n✅ Документ сохранен: {output_path}")

    return document_content


def main():
    """Запустить все примеры"""
    print("\n" + "="*60)
    print("PROCESS FRAMEWORK - ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ")
    print("="*60)

    # Пример 1: Регистрация процессов
    example_1_register_processes()

    # Пример 2: Запуск процесса
    example_2_start_bia_process()

    # Пример 3: Получение формы
    example_3_get_form_for_user()

    # Пример 4: Заполнение формы
    example_4_submit_form_data()

    # Пример 5: Полное прохождение процесса
    example_5_complete_bia_process()

    # Пример 6: Генерация документа
    example_6_generate_bia_document()

    print("\n" + "="*60)
    print("ВСЕ ПРИМЕРЫ ВЫПОЛНЕНЫ!")
    print("="*60)


if __name__ == "__main__":
    main()
