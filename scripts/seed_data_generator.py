"""
Production Seed Data Generator

Генерирует realistic synthetic data для:
- BIA workflow cases (50+)
- Risk assessment cases (30+)
- Planning cases (20+)
- Community annotations (100+)

Usage:
    python scripts/seed_data_generator.py --cases 50 --output data/seed/
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path
import argparse

try:
    from faker import Faker
except ImportError:
    print("️  faker not installed. Installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "faker"])
    from faker import Faker


class SeedDataGenerator:
    """
    Comprehensive seed data generator

    Generates statistically realistic data based on:
    - Industry patterns from public BCM data
    - Typical organization sizes
    - Realistic timelines
    - Common challenges
    """

    def __init__(self, seed: int = 42):
        self.faker = Faker()
        random.seed(seed)
        Faker.seed(seed)

        # Industry templates
        self.industries = {
            'healthcare': {
                'processes': [
                    'Emergency Department Operations',
                    'Patient Records Management',
                    'Pharmacy Services',
                    'Laboratory Services',
                    'Radiology Services',
                    'Patient Admissions',
                    'Surgery Department',
                    'Intensive Care Unit'
                ],
                'dependencies': {
                    'people': ['Physicians', 'Nurses', 'Lab Technicians', 'Pharmacists'],
                    'technology': ['EMR System', 'PACS', 'Lab Information System', 'Pharmacy System'],
                    'facility': ['Emergency Room', 'Operating Rooms', 'ICU', 'Pharmacy'],
                    'supplier': ['Medical Supply Vendors', 'Pharmaceutical Suppliers', 'Equipment Vendors']
                },
                'challenges': [
                    'HIPAA compliance requirements added complexity',
                    'Clinical staff availability for interviews limited',
                    'Integration with existing safety protocols needed',
                    'Balancing patient care with BCM planning'
                ],
                'success_patterns': [
                    'Aligned BIA with patient safety framework',
                    'Engaged Chief Medical Officer as sponsor',
                    'Used clinical workflow analysis tools',
                    'Leveraged existing disaster preparedness plans',
                    'Conducted BIA during low-census period'
                ]
            },
            'finance': {
                'processes': [
                    'Transaction Processing',
                    'Customer Account Management',
                    'Compliance Reporting',
                    'Trading Operations',
                    'Loan Processing',
                    'Customer Service',
                    'Risk Management',
                    'Payment Settlement'
                ],
                'dependencies': {
                    'people': ['Traders', 'Compliance Officers', 'Account Managers', 'IT Staff'],
                    'technology': ['Core Banking System', 'Trading Platform', 'CRM', 'Payment Gateway'],
                    'facility': ['Trading Floor', 'Data Center', 'Branch Network'],
                    'supplier': ['Payment Processors', 'Data Providers', 'Cloud Services']
                },
                'challenges': [
                    'Regulatory reporting deadlines created pressure',
                    'Complex IT infrastructure difficult to map',
                    'Multiple regulatory requirements to consider',
                    'Cross-border operations added complexity'
                ],
                'success_patterns': [
                    'Integrated with existing risk framework',
                    'Used regulatory requirements as drivers',
                    'Engaged compliance team from start',
                    'Leveraged existing IT architecture documentation',
                    'Phased approach by business line'
                ]
            },
            'manufacturing': {
                'processes': [
                    'Production Line Operations',
                    'Supply Chain Management',
                    'Quality Control',
                    'Inventory Management',
                    'Order Fulfillment',
                    'Maintenance',
                    'Shipping & Receiving',
                    'Planning & Scheduling'
                ],
                'dependencies': {
                    'people': ['Production Staff', 'Quality Engineers', 'Maintenance Team', 'Planners'],
                    'technology': ['ERP System', 'MES', 'Quality Management System', 'Warehouse System'],
                    'facility': ['Production Floor', 'Warehouse', 'Maintenance Shop'],
                    'supplier': ['Raw Material Suppliers', 'Equipment Vendors', 'Logistics Providers']
                },
                'challenges': [
                    'Just-in-time manufacturing made dependencies complex',
                    'Multiple production lines to analyze',
                    'Seasonal demand variations to consider',
                    'Supplier dependency risks high'
                ],
                'success_patterns': [
                    'Used value stream mapping for process identification',
                    'Aligned with lean manufacturing principles',
                    'Engaged production floor supervisors',
                    'Leveraged existing FMEA data',
                    'Conducted during planned maintenance shutdown'
                ]
            }
        }

    def generate_complete_dataset(
        self,
        bia_cases: int = 50,
        risk_cases: int = 30,
        planning_cases: int = 20,
        annotations: int = 100
    ) -> Dict[str, Any]:
        """Generate complete seed dataset"""

        print(" Generating seed data...")

        dataset = {
            'bia_cases': [],
            'risk_cases': [],
            'planning_cases': [],
            'annotations': [],
            'benchmarks': {},
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'generator_version': '1.0.0',
                'total_cases': bia_cases + risk_cases + planning_cases,
                'seed': 42
            }
        }

        # Generate BIA cases
        print(f"  Generating {bia_cases} BIA cases...")
        for i in range(bia_cases):
            case = self._generate_bia_case(i)
            dataset['bia_cases'].append(case)

        # Generate Risk Assessment cases
        print(f"  Generating {risk_cases} Risk Assessment cases...")
        for i in range(risk_cases):
            case = self._generate_risk_case(i)
            dataset['risk_cases'].append(case)

        # Generate Planning cases
        print(f"  Generating {planning_cases} Planning cases...")
        for i in range(planning_cases):
            case = self._generate_planning_case(i)
            dataset['planning_cases'].append(case)

        # Generate annotations
        print(f"  Generating {annotations} community annotations...")
        dataset['annotations'] = self._generate_annotations(annotations)

        # Calculate benchmarks
        print("  Calculating benchmarks...")
        dataset['benchmarks'] = self._calculate_benchmarks(dataset)

        print(" Seed data generation complete!")
        return dataset

    def _generate_bia_case(self, index: int) -> Dict[str, Any]:
        """Generate realistic BIA case"""

        # Select industry and org size
        industry = random.choice(list(self.industries.keys()))
        org_size = random.choice(['small', 'medium', 'large'])

        industry_data = self.industries[industry]

        # Size-based parameters
        size_params = {
            'small': {
                'process_count': random.randint(3, 8),
                'employee_count': random.randint(50, 250),
                'base_duration_days': random.uniform(10, 25)
            },
            'medium': {
                'process_count': random.randint(8, 15),
                'employee_count': random.randint(250, 1000),
                'base_duration_days': random.uniform(20, 45)
            },
            'large': {
                'process_count': random.randint(15, 30),
                'employee_count': random.randint(1000, 5000),
                'base_duration_days': random.uniform(35, 90)
            }
        }

        params = size_params[org_size]

        # Select processes
        selected_processes = random.sample(
            industry_data['processes'],
            min(params['process_count'], len(industry_data['processes']))
        )

        # Generate journey
        journey = self._generate_journey(
            selected_processes,
            industry_data,
            params['base_duration_days'],
            org_size
        )

        # Calculate metrics
        total_duration = sum(stage.get('duration_hours', 0) for stage in journey) / 24
        ai_usage = sum(stage.get('ai_interventions', 0) for stage in journey)
        challenges = sum(len(stage.get('challenges', [])) for stage in journey)

        # Success patterns
        success_patterns = random.sample(
            industry_data['success_patterns'],
            random.randint(2, 4)
        )

        # Create case
        case = {
            'case_id': f"seed_bia_{index:04d}",
            'module': 'bia',
            'workflow_name': 'Business Impact Analysis',
            'organization_context': {
                'industry': industry,
                'size': org_size,
                'employee_count': params['employee_count'],
                'maturity_level': random.randint(1, 3),
                'region': random.choice(['europe', 'north_america', 'asia_pacific']),
                'regulatory_context': self._get_regulatory_context(industry)
            },
            'journey': journey,
            'processes': self._generate_process_details(selected_processes, industry_data),
            'metrics': {
                'total_duration_days': round(total_duration, 1),
                'processes_count': len(selected_processes),
                'ai_usage_count': ai_usage,
                'user_satisfaction': round(random.uniform(3.5, 5.0), 1),
                'challenges_encountered': challenges,
                'challenges_resolved': challenges,  # All resolved in successful cases
                'completed_successfully': True
            },
            'success_patterns': success_patterns,
            'lessons_learned': random.sample(industry_data['challenges'], random.randint(1, 3)),
            'features': {
                'used_ai_suggestions': ai_usage > 5,
                'had_external_consultant': random.random() > 0.7,
                'used_templates': random.random() > 0.5
            },
            'created_at': self._random_past_date(90, 365),
            'status': 'completed'
        }

        return case

    def _generate_journey(
        self,
        processes: List[str],
        industry_data: Dict,
        base_duration: float,
        org_size: str
    ) -> List[Dict]:
        """Generate realistic workflow journey"""

        stages = [
            'identify_processes',
            'analyze_dependencies',
            'assess_impact',
            'determine_rto',
            'review_results'
        ]

        # Stage complexity weights
        complexity_weights = {
            'identify_processes': 1.0,
            'analyze_dependencies': 1.5,
            'assess_impact': 1.3,
            'determine_rto': 1.0,
            'review_results': 0.5
        }

        journey = []
        current_date = datetime.utcnow() - timedelta(days=random.randint(30, 365))

        for stage in stages:
            # Calculate stage duration
            base_hours = (base_duration / len(stages)) * 24
            complexity = complexity_weights[stage]
            duration = base_hours * complexity * random.uniform(0.8, 1.2)

            # AI interventions (more in complex stages)
            ai_interventions = random.randint(0, int(complexity * 3))

            # Challenges (sometimes)
            challenges = []
            if random.random() > 0.6:
                challenges = random.sample(
                    industry_data['challenges'],
                    random.randint(1, 2)
                )

            stage_data = {
                'stage': stage,
                'started_at': current_date.isoformat(),
                'completed_at': (current_date + timedelta(hours=duration)).isoformat(),
                'duration_hours': round(duration, 2),
                'actions': self._generate_stage_actions(stage, len(processes)),
                'challenges': challenges,
                'ai_interventions': ai_interventions
            }

            journey.append(stage_data)
            current_date += timedelta(hours=duration)

        return journey

    def _generate_process_details(
        self,
        process_names: List[str],
        industry_data: Dict
    ) -> List[Dict]:
        """Generate detailed process information"""

        processes = []

        for i, name in enumerate(process_names):
            # Tier based on position (first few are tier 1)
            if i < len(process_names) * 0.3:
                tier = 'tier_1'
            elif i < len(process_names) * 0.6:
                tier = 'tier_2'
            else:
                tier = 'tier_3'

            process = {
                'id': f"proc_{i:03d}",
                'name': name,
                'description': f"{name} process for the organization",
                'tier': tier,
                'owner': self.faker.name(),
                'dependencies': self._generate_dependencies(industry_data),
                'impact': self._generate_impact(tier),
                'rto_hours': self._generate_rto(tier),
                'rpo_hours': self._generate_rpo(tier)
            }

            processes.append(process)

        return processes

    def _generate_dependencies(self, industry_data: Dict) -> List[Dict]:
        """Generate process dependencies"""

        dependencies = []

        for dep_type, options in industry_data['dependencies'].items():
            # Each process has 1-3 dependencies per type
            count = random.randint(1, 3)
            selected = random.sample(options, min(count, len(options)))

            for dep_name in selected:
                dependencies.append({
                    'type': dep_type,
                    'name': dep_name,
                    'criticality': random.choice(['critical', 'important', 'normal']),
                    'single_point_of_failure': random.random() > 0.7
                })

        return dependencies

    def _generate_impact(self, tier: str) -> Dict:
        """Generate impact assessment"""

        # Tier affects impact magnitude
        tier_multipliers = {
            'tier_1': (100000, 500000),
            'tier_2': (50000, 200000),
            'tier_3': (10000, 50000)
        }

        min_loss, max_loss = tier_multipliers[tier]

        return {
            'financial': {
                'hourly_loss': round(random.uniform(min_loss/24, max_loss/24), 2),
                'daily_loss': round(random.uniform(min_loss, max_loss), 2),
                'calculation_method': 'revenue_loss_plus_recovery_costs'
            },
            'operational': {
                'severity': random.choice(['low', 'medium', 'high', 'critical']),
                'description': 'Impact on operational capability',
                'affected_areas': random.sample(['customer_service', 'production', 'compliance', 'quality'], random.randint(1, 3))
            },
            'reputational': {
                'severity': random.choice(['low', 'medium', 'high']),
                'stakeholders_affected': random.sample(['customers', 'regulators', 'investors', 'employees'], random.randint(1, 3))
            },
            'regulatory': {
                'compliance_requirements': ['ISO22301', 'SOX'] if tier == 'tier_1' else [],
                'penalties': 'Potential regulatory fines' if tier == 'tier_1' else 'None'
            }
        }

    def _generate_rto(self, tier: str) -> int:
        """Generate realistic RTO"""

        rto_ranges = {
            'tier_1': (2, 8),
            'tier_2': (8, 24),
            'tier_3': (24, 72)
        }

        min_rto, max_rto = rto_ranges[tier]
        return random.randint(min_rto, max_rto)

    def _generate_rpo(self, tier: str) -> int:
        """Generate RPO (≤ RTO)"""

        rto = self._generate_rto(tier)
        return random.randint(1, rto)

    def _generate_stage_actions(self, stage: str, process_count: int) -> List[str]:
        """Generate actions taken in stage"""

        actions_map = {
            'identify_processes': [
                'reviewed_organizational_chart',
                f'interviewed_{random.randint(3, 10)}_managers',
                'analyzed_revenue_streams',
                f'mapped_{process_count}_processes'
            ],
            'analyze_dependencies': [
                'created_dependency_matrix',
                'mapped_it_systems',
                'identified_suppliers',
                f'documented_{random.randint(20, 50)}_dependencies'
            ],
            'assess_impact': [
                'calculated_financial_impacts',
                'assessed_operational_impacts',
                'evaluated_regulatory_requirements',
                f'completed_{process_count}_impact_assessments'
            ],
            'determine_rto': [
                'analyzed_recovery_costs',
                'reviewed_sla_requirements',
                'consulted_stakeholders',
                f'set_rto_for_{process_count}_processes'
            ],
            'review_results': [
                'management_presentation',
                'stakeholder_review',
                'final_report_generated'
            ]
        }

        return actions_map.get(stage, [])

    def _generate_risk_case(self, index: int) -> Dict:
        """Generate risk assessment case"""

        return {
            'case_id': f"seed_risk_{index:04d}",
            'module': 'risk',
            'workflow_name': 'Risk Assessment',
            'organization_context': self._random_org_context(),
            'risks_identified': random.randint(10, 30),
            'high_risks': random.randint(2, 8),
            'duration_days': round(random.uniform(10, 30), 1),
            'created_at': self._random_past_date(60, 365),
            'status': 'completed'
        }

    def _generate_planning_case(self, index: int) -> Dict:
        """Generate planning case"""

        return {
            'case_id': f"seed_plan_{index:04d}",
            'module': 'planning',
            'workflow_name': 'BC Planning',
            'organization_context': self._random_org_context(),
            'strategies_developed': random.randint(5, 15),
            'plans_created': random.randint(3, 10),
            'duration_days': round(random.uniform(20, 60), 1),
            'created_at': self._random_past_date(30, 365),
            'status': 'completed'
        }

    def _generate_annotations(self, count: int) -> List[Dict]:
        """Generate community annotations"""

        iso_clauses = [
            ('4.1', 'Understanding the organization and its context'),
            ('4.2', 'Understanding the needs and expectations of interested parties'),
            ('8.2.2', 'Business impact analysis and risk assessment'),
            ('8.3', 'Business continuity strategies and solutions'),
            ('8.4', 'Business continuity plans and procedures')
        ]

        annotations = []

        for i in range(count):
            clause = random.choice(iso_clauses)

            annotation = {
                'id': f"annot_{i:04d}",
                'clause_id': f"ISO22301_{clause[0]}",
                'clause_title': clause[1],
                'author_id': f"user_{random.randint(1, 20):03d}",
                'interpretation': self._generate_interpretation(clause),
                'industry_specific': random.choice(list(self.industries.keys())),
                'organization_size': random.choice(['small', 'medium', 'large']),
                'practical_examples': [self._generate_example()],
                'upvotes': random.randint(0, 50),
                'downvotes': random.randint(0, 10),
                'helpful_count': random.randint(0, 30),
                'created_at': self._random_past_date(10, 180)
            }

            annotations.append(annotation)

        return annotations

    def _generate_interpretation(self, clause: tuple) -> str:
        """Generate realistic clause interpretation"""

        templates = [
            f"In practice, {clause[1].lower()} means conducting workshops with key stakeholders to document their requirements and expectations.",
            f"For {clause[1].lower()}, we found it helpful to create a matrix mapping stakeholder groups to their specific needs.",
            f"Our approach to {clause[1].lower()} involved regular interviews and surveys to maintain current understanding."
        ]

        return random.choice(templates)

    def _generate_example(self) -> str:
        """Generate practical example"""

        examples = [
            "We held quarterly stakeholder meetings to review and update requirements",
            "Created a stakeholder register with contact details and communication preferences",
            "Used surveys to gather input from distributed teams",
            "Established a feedback loop with customers through regular reviews"
        ]

        return random.choice(examples)

    def _calculate_benchmarks(self, dataset: Dict) -> Dict:
        """Calculate benchmarks from generated data"""

        bia_cases = dataset['bia_cases']

        benchmarks = {}

        # Group by industry and size
        for industry in self.industries.keys():
            for size in ['small', 'medium', 'large']:
                filtered = [
                    c for c in bia_cases
                    if c['organization_context']['industry'] == industry
                    and c['organization_context']['size'] == size
                ]

                if filtered:
                    durations = [c['metrics']['total_duration_days'] for c in filtered]
                    ai_usage = [c['metrics']['ai_usage_count'] for c in filtered]

                    key = f"{industry}_{size}"
                    benchmarks[key] = {
                        'avg_duration_days': round(sum(durations) / len(durations), 1),
                        'avg_ai_usage': round(sum(ai_usage) / len(ai_usage), 1),
                        'sample_size': len(filtered)
                    }

        return benchmarks

    def _random_org_context(self) -> Dict:
        """Generate random org context"""

        industry = random.choice(list(self.industries.keys()))
        size = random.choice(['small', 'medium', 'large'])

        return {
            'industry': industry,
            'size': size,
            'maturity_level': random.randint(1, 3),
            'region': random.choice(['europe', 'north_america', 'asia_pacific'])
        }

    def _get_regulatory_context(self, industry: str) -> List[str]:
        """Get regulatory requirements for industry"""

        regulatory_map = {
            'healthcare': ['HIPAA', 'Joint Commission', 'State Health Dept'],
            'finance': ['SOX', 'GDPR', 'PCI-DSS', 'Basel III'],
            'manufacturing': ['ISO 9001', 'OSHA', 'EPA']
        }

        return regulatory_map.get(industry, ['ISO 22301'])

    def _random_past_date(self, min_days: int, max_days: int) -> str:
        """Generate random past date"""

        days_ago = random.randint(min_days, max_days)
        date = datetime.utcnow() - timedelta(days=days_ago)
        return date.isoformat()

    def save_to_files(self, dataset: Dict, output_dir: str):
        """Save dataset to JSON files"""

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save each component
        for key, data in dataset.items():
            if key != 'metadata':
                filename = output_path / f"{key}.json"
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"   Saved {filename}")

        # Save metadata
        with open(output_path / "metadata.json", 'w') as f:
            json.dump(dataset['metadata'], f, indent=2)

        print(f"\n All data saved to {output_dir}")


def main():
    """CLI entry point"""

    parser = argparse.ArgumentParser(description='Generate seed data for BCM platform')
    parser.add_argument('--bia-cases', type=int, default=50, help='Number of BIA cases')
    parser.add_argument('--risk-cases', type=int, default=30, help='Number of risk cases')
    parser.add_argument('--planning-cases', type=int, default=20, help='Number of planning cases')
    parser.add_argument('--annotations', type=int, default=100, help='Number of annotations')
    parser.add_argument('--output', type=str, default='data/seed/', help='Output directory')

    args = parser.parse_args()

    generator = SeedDataGenerator()

    dataset = generator.generate_complete_dataset(
        bia_cases=args.bia_cases,
        risk_cases=args.risk_cases,
        planning_cases=args.planning_cases,
        annotations=args.annotations
    )

    generator.save_to_files(dataset, args.output)

    print("\n Dataset Statistics:")
    print(f"   BIA Cases: {len(dataset['bia_cases'])}")
    print(f"   Risk Cases: {len(dataset['risk_cases'])}")
    print(f"   Planning Cases: {len(dataset['planning_cases'])}")
    print(f"   Annotations: {len(dataset['annotations'])}")
    print(f"   Benchmarks: {len(dataset['benchmarks'])} combinations")


if __name__ == "__main__":
    main()
