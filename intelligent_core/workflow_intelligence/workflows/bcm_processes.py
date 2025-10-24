"""
BCM Standard Processes - Стандартные процессы BCM

Готовые определения процессов для:
- Business Impact Analysis (BIA)
- Risk Assessment
- Business Continuity Plan Development
- Recovery Plan Development
- BC Exercise Planning and Execution
"""

from ..infrastructure.process_framework import (
    ProcessDefinition, ProcessStep, StepType,
    FormField, FieldValidation, ValidationRule
)


def create_bia_process() -> ProcessDefinition:
    """
    Создать процесс Business Impact Analysis

    Соответствует ISO 22301 Clause 8.2.2
    """
    process = ProcessDefinition(
        id="bcm_bia_v1",
        name="Business Impact Analysis",
        version="1.0",
        description="Формализованный процесс проведения Business Impact Analysis в соответствии с ISO 22301",
        category="bcm_analysis",
        iso_clause="8.2.2",
        compliance_requirements=[
            "ISO 22301:2019 - Clause 8.2.2",
            "ISO 22313:2020 - BIA Guidelines"
        ]
    )

    # Шаг 1: Инициация BIA
    step1 = ProcessStep(
        id="bia_initiation",
        name="Инициация BIA",
        step_type=StepType.FORM_INPUT,
        description="Определение scope и целей Business Impact Analysis",
        form_fields=[
            FormField(
                name="bia_scope",
                label="Область анализа (Scope)",
                field_type="textarea",
                description="Опишите, какие бизнес-процессы/функции будут проанализированы",
                required=True,
                validations=[
                    FieldValidation(
                        rule=ValidationRule.REQUIRED,
                        value=True,
                        error_message="Область анализа обязательна для заполнения"
                    ),
                    FieldValidation(
                        rule=ValidationRule.MIN_LENGTH,
                        value=50,
                        error_message="Описание должно содержать минимум 50 символов"
                    )
                ],
                help_text="Укажите конкретные подразделения, процессы или функции"
            ),
            FormField(
                name="bia_objectives",
                label="Цели BIA",
                field_type="textarea",
                description="Какие цели должен достичь данный анализ?",
                required=True,
                validations=[
                    FieldValidation(
                        rule=ValidationRule.REQUIRED,
                        value=True,
                        error_message="Цели BIA обязательны"
                    )
                ]
            ),
            FormField(
                name="stakeholders",
                label="Ключевые заинтересованные стороны",
                field_type="textarea",
                description="Перечислите лиц, которые должны участвовать в BIA",
                required=True,
                placeholder="Например: CFO, Head of Operations, IT Director"
            ),
            FormField(
                name="timeline",
                label="Планируемый срок завершения",
                field_type="date",
                required=True,
                help_text="Рекомендуемый срок: 2-4 недели"
            )
        ],
        next_steps=["critical_functions_identification"],
        allowed_roles=["bcm_manager", "bcm_coordinator", "admin"],
        sla_hours=24
    )

    # Шаг 2: Идентификация критичных функций
    step2 = ProcessStep(
        id="critical_functions_identification",
        name="Идентификация критичных бизнес-функций",
        step_type=StepType.FORM_INPUT,
        description="Определение и классификация критичных бизнес-функций организации",
        form_fields=[
            FormField(
                name="business_functions",
                label="Бизнес-функции для анализа",
                field_type="textarea",
                description="Перечислите все бизнес-функции (по одной на строку)",
                required=True,
                validations=[
                    FieldValidation(
                        rule=ValidationRule.REQUIRED,
                        value=True,
                        error_message="Необходимо указать хотя бы одну бизнес-функцию"
                    )
                ],
                help_text="Например:\n- Прием заказов\n- Доставка товаров\n- Обслуживание клиентов"
            ),
            FormField(
                name="function_dependencies",
                label="Зависимости между функциями",
                field_type="textarea",
                description="Опишите, как функции зависят друг от друга",
                required=False
            )
        ],
        next_steps=["impact_analysis"],
        allowed_roles=["bcm_manager", "process_owner", "admin"],
        sla_hours=48
    )

    # Шаг 3: Анализ воздействия
    step3 = ProcessStep(
        id="impact_analysis",
        name="Анализ воздействия нарушений",
        step_type=StepType.ANALYSIS,
        description="Оценка последствий прерывания каждой критичной функции",
        form_fields=[
            FormField(
                name="rto",
                label="RTO (Recovery Time Objective)",
                field_type="number",
                description="Максимально допустимое время простоя (в часах)",
                required=True,
                validations=[
                    FieldValidation(
                        rule=ValidationRule.REQUIRED,
                        value=True,
                        error_message="RTO обязателен"
                    ),
                    FieldValidation(
                        rule=ValidationRule.NUMERIC_RANGE,
                        value=(0, 720),  # 0-30 дней
                        error_message="RTO должен быть от 0 до 720 часов"
                    )
                ],
                help_text="0-4 часа: критично, 4-24 часа: высокий приоритет, >24 часов: средний/низкий"
            ),
            FormField(
                name="rpo",
                label="RPO (Recovery Point Objective)",
                field_type="number",
                description="Максимально допустимая потеря данных (в минутах)",
                required=True,
                validations=[
                    FieldValidation(
                        rule=ValidationRule.NUMERIC_RANGE,
                        value=(0, 10080),  # 0-7 дней в минутах
                        error_message="RPO должен быть от 0 до 10080 минут"
                    )
                ]
            ),
            FormField(
                name="financial_impact",
                label="Финансовое воздействие",
                field_type="select",
                required=True,
                options=[
                    {"value": "critical", "label": "Критическое (>1M USD/день)"},
                    {"value": "high", "label": "Высокое (100K-1M USD/день)"},
                    {"value": "medium", "label": "Среднее (10K-100K USD/день)"},
                    {"value": "low", "label": "Низкое (<10K USD/день)"}
                ]
            ),
            FormField(
                name="reputational_impact",
                label="Репутационное воздействие",
                field_type="select",
                required=True,
                options=[
                    {"value": "critical", "label": "Критическое (потеря доверия клиентов)"},
                    {"value": "high", "label": "Высокое (негативное освещение в СМИ)"},
                    {"value": "medium", "label": "Среднее (локальное недовольство)"},
                    {"value": "low", "label": "Низкое (минимальный эффект)"}
                ]
            ),
            FormField(
                name="regulatory_impact",
                label="Регуляторное воздействие",
                field_type="select",
                required=True,
                options=[
                    {"value": "critical", "label": "Критическое (штрафы, лицензии)"},
                    {"value": "high", "label": "Высокое (нарушение compliance)"},
                    {"value": "medium", "label": "Среднее (предупреждения)"},
                    {"value": "low", "label": "Низкое (нет регуляторных последствий)"}
                ]
            ),
            FormField(
                name="impact_justification",
                label="Обоснование оценок",
                field_type="textarea",
                description="Поясните, почему были выбраны эти оценки воздействия",
                required=True,
                validations=[
                    FieldValidation(
                        rule=ValidationRule.MIN_LENGTH,
                        value=100,
                        error_message="Обоснование должно содержать минимум 100 символов"
                    )
                ]
            )
        ],
        next_steps=["resource_requirements"],
        allowed_roles=["bcm_analyst", "process_owner", "admin"],
        ai_agent="analytics_specialist",
        sla_hours=72
    )

    # Шаг 4: Определение требований к ресурсам
    step4 = ProcessStep(
        id="resource_requirements",
        name="Определение требований к ресурсам",
        step_type=StepType.FORM_INPUT,
        description="Определение минимальных ресурсов для восстановления",
        form_fields=[
            FormField(
                name="personnel_required",
                label="Необходимый персонал",
                field_type="number",
                description="Минимальное количество сотрудников для восстановления функции",
                required=True
            ),
            FormField(
                name="technology_required",
                label="Требуемые технологии/системы",
                field_type="textarea",
                description="Перечислите критичные IT системы, приложения, инфраструктуру",
                required=True
            ),
            FormField(
                name="facilities_required",
                label="Требуемые помещения/локации",
                field_type="textarea",
                description="Минимальные требования к рабочим местам",
                required=True
            ),
            FormField(
                name="third_party_dependencies",
                label="Зависимости от третьих сторон",
                field_type="textarea",
                description="Поставщики, партнеры, от которых зависит функция",
                required=False
            )
        ],
        next_steps=["bia_report_generation"],
        allowed_roles=["bcm_analyst", "resource_manager", "admin"],
        sla_hours=48
    )

    # Шаг 5: Генерация отчета BIA
    step5 = ProcessStep(
        id="bia_report_generation",
        name="Генерация отчета BIA",
        step_type=StepType.DOCUMENT_GENERATION,
        description="Автоматическая генерация отчета Business Impact Analysis",
        form_fields=[
            FormField(
                name="report_format",
                label="Формат отчета",
                field_type="select",
                required=True,
                default_value="pdf",
                options=[
                    {"value": "pdf", "label": "PDF Document"},
                    {"value": "docx", "label": "Microsoft Word"},
                    {"value": "html", "label": "HTML Report"}
                ]
            ),
            FormField(
                name="include_recommendations",
                label="Включить рекомендации",
                field_type="checkbox",
                default_value=True,
                help_text="AI сгенерирует рекомендации по улучшению"
            )
        ],
        next_steps=["bia_approval"],
        allowed_roles=["bcm_manager", "admin"],
        document_template="bia_report_template.docx",
        ai_agent="document_generator",
        auto_approve=False
    )

    # Шаг 6: Утверждение BIA
    step6 = ProcessStep(
        id="bia_approval",
        name="Утверждение BIA",
        step_type=StepType.APPROVAL,
        description="Утверждение результатов Business Impact Analysis руководством",
        form_fields=[
            FormField(
                name="approval_decision",
                label="Решение",
                field_type="select",
                required=True,
                options=[
                    {"value": "approved", "label": "Утверждено"},
                    {"value": "approved_with_changes", "label": "Утверждено с изменениями"},
                    {"value": "rejected", "label": "Отклонено"}
                ]
            ),
            FormField(
                name="approval_comments",
                label="Комментарии",
                field_type="textarea",
                description="Укажите причины решения или необходимые изменения",
                required=True,
                validations=[
                    FieldValidation(
                        rule=ValidationRule.MIN_LENGTH,
                        value=20,
                        error_message="Комментарии должны содержать минимум 20 символов"
                    )
                ]
            ),
            FormField(
                name="approver_name",
                label="ФИО утверждающего",
                field_type="text",
                required=True
            ),
            FormField(
                name="approver_position",
                label="Должность",
                field_type="text",
                required=True
            )
        ],
        next_steps=["END"],
        allowed_roles=["senior_management", "ceo", "cfo", "admin"],
        sla_hours=48
    )

    # Добавить шаги в процесс
    process.add_step(step1)
    process.add_step(step2)
    process.add_step(step3)
    process.add_step(step4)
    process.add_step(step5)
    process.add_step(step6)

    # Установить стартовый и конечный шаги
    process.start_step_id = "bia_initiation"
    process.end_step_ids = ["END"]

    return process


def create_risk_assessment_process() -> ProcessDefinition:
    """Создать процесс Risk Assessment (ISO 22301 Clause 8.2.3)"""
    process = ProcessDefinition(
        id="bcm_risk_assessment_v1",
        name="Risk Assessment",
        version="1.0",
        description="Процесс оценки рисков для непрерывности бизнеса",
        category="bcm_analysis",
        iso_clause="8.2.3"
    )

    # Simplified - основные шаги
    step1 = ProcessStep(
        id="risk_identification",
        name="Идентификация рисков",
        step_type=StepType.FORM_INPUT,
        description="Определение потенциальных рисков для непрерывности бизнеса",
        form_fields=[
            FormField(
                name="risk_name",
                label="Название риска",
                field_type="text",
                required=True
            ),
            FormField(
                name="risk_description",
                label="Описание риска",
                field_type="textarea",
                required=True
            ),
            FormField(
                name="risk_category",
                label="Категория риска",
                field_type="select",
                required=True,
                options=[
                    {"value": "natural_disaster", "label": "Природные катастрофы"},
                    {"value": "technological", "label": "Технологические сбои"},
                    {"value": "human_error", "label": "Человеческий фактор"},
                    {"value": "cyber_security", "label": "Кибербезопасность"},
                    {"value": "supply_chain", "label": "Цепочка поставок"},
                    {"value": "regulatory", "label": "Регуляторные изменения"}
                ]
            )
        ],
        next_steps=["risk_analysis"],
        allowed_roles=["risk_manager", "bcm_manager", "admin"]
    )

    step2 = ProcessStep(
        id="risk_analysis",
        name="Анализ рисков",
        step_type=StepType.ANALYSIS,
        description="Оценка вероятности и воздействия рисков",
        form_fields=[
            FormField(
                name="likelihood",
                label="Вероятность (Likelihood)",
                field_type="select",
                required=True,
                options=[
                    {"value": "5", "label": "5 - Почти наверняка (>80%)"},
                    {"value": "4", "label": "4 - Вероятно (60-80%)"},
                    {"value": "3", "label": "3 - Возможно (40-60%)"},
                    {"value": "2", "label": "2 - Маловероятно (20-40%)"},
                    {"value": "1", "label": "1 - Редко (<20%)"}
                ]
            ),
            FormField(
                name="impact",
                label="Воздействие (Impact)",
                field_type="select",
                required=True,
                options=[
                    {"value": "5", "label": "5 - Катастрофическое"},
                    {"value": "4", "label": "4 - Критическое"},
                    {"value": "3", "label": "3 - Значительное"},
                    {"value": "2", "label": "2 - Умеренное"},
                    {"value": "1", "label": "1 - Незначительное"}
                ]
            ),
            FormField(
                name="risk_score_justification",
                label="Обоснование оценок",
                field_type="textarea",
                required=True
            )
        ],
        next_steps=["risk_treatment"],
        ai_agent="risk_analyst"
    )

    step3 = ProcessStep(
        id="risk_treatment",
        name="Обработка рисков",
        step_type=StepType.DECISION,
        description="Определение стратегии обработки рисков",
        form_fields=[
            FormField(
                name="treatment_strategy",
                label="Стратегия обработки",
                field_type="select",
                required=True,
                options=[
                    {"value": "mitigate", "label": "Снижение (Mitigate)"},
                    {"value": "transfer", "label": "Передача (Transfer)"},
                    {"value": "accept", "label": "Принятие (Accept)"},
                    {"value": "avoid", "label": "Избежание (Avoid)"}
                ]
            ),
            FormField(
                name="treatment_actions",
                label="Конкретные действия",
                field_type="textarea",
                required=True,
                help_text="Опишите конкретные меры по обработке риска"
            ),
            FormField(
                name="responsible_person",
                label="Ответственный",
                field_type="text",
                required=True
            ),
            FormField(
                name="target_date",
                label="Срок реализации",
                field_type="date",
                required=True
            )
        ],
        next_steps=["END"],
        allowed_roles=["risk_manager", "senior_management"]
    )

    process.add_step(step1)
    process.add_step(step2)
    process.add_step(step3)

    process.start_step_id = "risk_identification"
    process.end_step_ids = ["END"]

    return process


def create_bc_plan_process() -> ProcessDefinition:
    """Создать процесс разработки Business Continuity Plan"""
    process = ProcessDefinition(
        id="bcm_bc_plan_v1",
        name="Business Continuity Plan Development",
        version="1.0",
        description="Разработка плана обеспечения непрерывности бизнеса",
        category="bcm_planning",
        iso_clause="8.4"
    )

    step1 = ProcessStep(
        id="plan_initiation",
        name="Инициация разработки плана",
        step_type=StepType.FORM_INPUT,
        description="Определение scope и структуры BC Plan",
        form_fields=[
            FormField(
                name="plan_scope",
                label="Область применения плана",
                field_type="textarea",
                required=True
            ),
            FormField(
                name="critical_functions",
                label="Критичные функции (из BIA)",
                field_type="textarea",
                required=True,
                help_text="Импортируйте из завершенного BIA"
            )
        ],
        next_steps=["strategy_definition"]
    )

    step2 = ProcessStep(
        id="strategy_definition",
        name="Определение стратегии восстановления",
        step_type=StepType.FORM_INPUT,
        description="Разработка стратегий восстановления для каждой критичной функции",
        form_fields=[
            FormField(
                name="recovery_strategy",
                label="Стратегия восстановления",
                field_type="select",
                required=True,
                options=[
                    {"value": "hot_site", "label": "Hot Site (мгновенное переключение)"},
                    {"value": "warm_site", "label": "Warm Site (быстрое развертывание)"},
                    {"value": "cold_site", "label": "Cold Site (отложенное развертывание)"},
                    {"value": "work_from_home", "label": "Удаленная работа"},
                    {"value": "manual_workaround", "label": "Ручные процедуры"}
                ]
            ),
            FormField(
                name="alternative_location",
                label="Альтернативная локация",
                field_type="text",
                required=False
            ),
            FormField(
                name="recovery_procedures",
                label="Процедуры восстановления",
                field_type="textarea",
                required=True,
                help_text="Пошаговые инструкции по восстановлению функции"
            )
        ],
        next_steps=["roles_responsibilities"]
    )

    step3 = ProcessStep(
        id="roles_responsibilities",
        name="Роли и ответственности",
        step_type=StepType.FORM_INPUT,
        description="Определение команды восстановления и ролей",
        form_fields=[
            FormField(
                name="incident_manager",
                label="Менеджер инцидента",
                field_type="text",
                required=True
            ),
            FormField(
                name="recovery_team",
                label="Команда восстановления",
                field_type="textarea",
                required=True,
                help_text="Перечислите членов команды и их роли"
            ),
            FormField(
                name="contact_list",
                label="Контактный лист",
                field_type="textarea",
                required=True,
                help_text="ФИО, должность, телефон, email"
            )
        ],
        next_steps=["plan_document_generation"]
    )

    step4 = ProcessStep(
        id="plan_document_generation",
        name="Генерация документа плана",
        step_type=StepType.DOCUMENT_GENERATION,
        description="Автоматическая генерация BC Plan",
        form_fields=[],
        next_steps=["plan_approval"],
        document_template="bc_plan_template.docx",
        ai_agent="document_generator"
    )

    step5 = ProcessStep(
        id="plan_approval",
        name="Утверждение BC Plan",
        step_type=StepType.APPROVAL,
        description="Утверждение плана руководством",
        form_fields=[
            FormField(
                name="approval_decision",
                label="Решение",
                field_type="select",
                required=True,
                options=[
                    {"value": "approved", "label": "Утверждено"},
                    {"value": "rejected", "label": "Отклонено"}
                ]
            ),
            FormField(
                name="approval_comments",
                label="Комментарии",
                field_type="textarea",
                required=True
            )
        ],
        next_steps=["END"],
        allowed_roles=["senior_management", "admin"]
    )

    process.add_step(step1)
    process.add_step(step2)
    process.add_step(step3)
    process.add_step(step4)
    process.add_step(step5)

    process.start_step_id = "plan_initiation"
    process.end_step_ids = ["END"]

    return process


# Функция для регистрации всех BCM процессов
def register_all_bcm_processes(framework):
    """Зарегистрировать все стандартные BCM процессы"""
    processes = [
        create_bia_process(),
        create_risk_assessment_process(),
        create_bc_plan_process()
    ]

    for process in processes:
        success = framework.register_process(process)
        if success:
            print(f" Процесс {process.name} зарегистрирован")
        else:
            print(f" Ошибка регистрации процесса {process.name}")

    return len(processes)
