#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BCM Incident Module Migration Script
====================================

Migrates data from old bcm_incident + bcm_incident_management modules
to the new unified bcm_incident module.

This script handles:
- Data migration from old incident tables
- Field mapping and data transformation
- Backward compatibility preservation
- Error handling and rollback

Usage:
    python migration_script.py [options]

Options:
    --dry-run    : Show what would be migrated without executing
    --backup     : Create backup before migration
    --force      : Force migration even if target tables exist
    --verbose    : Enable verbose logging
"""

import argparse
import sys
import logging
import psycopg2
from datetime import datetime
import json

class BCMIncidentMigration:
    """BCM Incident Migration Handler"""

    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None
        self.cursor = None
        self.logger = self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'bcm_migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)

    def connect(self):
        """Connect to database"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            self.logger.info("Database connection established")
            return True
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from database"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.logger.info("Database connection closed")

    def check_old_tables(self):
        """Check if old incident tables exist"""
        tables_to_check = [
            'bcm_incident_old',
            'bcm_incident_management',
            'bcm_incident_backup'
        ]

        existing_tables = {}

        for table in tables_to_check:
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = %s
                );
            """, (table,))
            existing_tables[table] = self.cursor.fetchone()[0]

        self.logger.info(f"Table existence check: {existing_tables}")
        return existing_tables

    def backup_current_data(self):
        """Create backup of current incident data"""
        try:
            # Create backup table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS bcm_incident_backup AS
                SELECT * FROM bcm_incident WHERE 1=0;
            """)

            # Copy current data
            self.cursor.execute("""
                INSERT INTO bcm_incident_backup
                SELECT * FROM bcm_incident;
            """)

            backup_count = self.cursor.rowcount
            self.logger.info(f"Backed up {backup_count} current incident records")

            return True

        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False

    def migrate_basic_incidents(self):
        """Migrate basic incident data"""
        try:
            # Check if old incident table exists
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'bcm_incident_old'
                );
            """)

            if not self.cursor.fetchone()[0]:
                self.logger.info("No bcm_incident_old table found, skipping basic migration")
                return 0

            # Get column mapping
            old_columns = self._get_table_columns('bcm_incident_old')
            new_columns = self._get_table_columns('bcm_incident')

            # Create column mapping
            column_mapping = self._create_column_mapping(old_columns, new_columns)

            # Build migration query
            select_cols = []
            for new_col, old_col in column_mapping.items():
                if old_col:
                    select_cols.append(f"{old_col} as {new_col}")
                else:
                    # Set default values for new columns
                    default_values = {
                        'ai_classification_confidence': '75.0',
                        'ai_risk_score': '50.0',
                        'digital_twin_sync': 'false',
                        'escalation_level': '1',
                        'response_team_activated': 'false'
                    }
                    default_val = default_values.get(new_col, 'NULL')
                    select_cols.append(f"{default_val} as {new_col}")

            # Execute migration
            migration_query = f"""
                INSERT INTO bcm_incident ({', '.join(column_mapping.keys())})
                SELECT {', '.join(select_cols)}
                FROM bcm_incident_old
                WHERE NOT EXISTS (
                    SELECT 1 FROM bcm_incident
                    WHERE bcm_incident.incident_number = bcm_incident_old.incident_number
                );
            """

            self.cursor.execute(migration_query)
            migrated_count = self.cursor.rowcount

            self.logger.info(f"Migrated {migrated_count} basic incident records")
            return migrated_count

        except Exception as e:
            self.logger.error(f"Basic incident migration failed: {e}")
            raise

    def migrate_management_data(self):
        """Migrate incident management data"""
        try:
            # Check if management table exists
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'bcm_incident_management'
                );
            """)

            if not self.cursor.fetchone()[0]:
                self.logger.info("No bcm_incident_management table found, skipping management migration")
                return 0

            # Update existing incidents with management data
            self.cursor.execute("""
                UPDATE bcm_incident
                SET
                    response_team_activated = COALESCE(im.response_team_activated, false),
                    escalation_level = COALESCE(im.escalation_level, 1),
                    communication_plan = im.communication_plan,
                    stakeholder_notification = COALESCE(im.stakeholder_notification, false),
                    expected_rto = COALESCE(im.expected_rto, 0),
                    actual_rto = COALESCE(im.actual_rto, 0),
                    business_impact = COALESCE(im.business_impact, ''),
                    affected_systems = COALESCE(im.affected_systems, ''),
                    recovery_actions = COALESCE(im.recovery_actions, ''),
                    lessons_learned = COALESCE(im.lessons_learned, '')
                FROM bcm_incident_management im
                WHERE bcm_incident.incident_number = im.incident_number
                   OR bcm_incident.id = im.incident_id;
            """)

            updated_count = self.cursor.rowcount
            self.logger.info(f"Updated {updated_count} incidents with management data")
            return updated_count

        except Exception as e:
            self.logger.error(f"Management data migration failed: {e}")
            raise

    def migrate_ai_data(self):
        """Migrate and initialize AI-related data"""
        try:
            # Set default AI values for incidents without them
            self.cursor.execute("""
                UPDATE bcm_incident
                SET
                    ai_classification_confidence = CASE
                        WHEN status IN ('closed', 'resolved') THEN 85.0
                        WHEN severity = 'critical' THEN 90.0
                        WHEN severity = 'high' THEN 80.0
                        WHEN severity = 'medium' THEN 70.0
                        ELSE 60.0
                    END,
                    ai_risk_score = CASE
                        WHEN severity = 'critical' THEN 90.0
                        WHEN severity = 'high' THEN 75.0
                        WHEN severity = 'medium' THEN 50.0
                        ELSE 25.0
                    END,
                    digital_twin_sync = false
                WHERE ai_classification_confidence IS NULL
                   OR ai_risk_score IS NULL
                   OR digital_twin_sync IS NULL;
            """)

            updated_count = self.cursor.rowcount
            self.logger.info(f"Initialized AI data for {updated_count} incidents")
            return updated_count

        except Exception as e:
            self.logger.error(f"AI data migration failed: {e}")
            raise

    def _get_table_columns(self, table_name):
        """Get column names for a table"""
        self.cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))

        return [row[0] for row in self.cursor.fetchall()]

    def _create_column_mapping(self, old_columns, new_columns):
        """Create mapping between old and new columns"""
        mapping = {}

        # Direct mappings
        direct_maps = {
            'name': 'name',
            'incident_number': 'incident_number',
            'description': 'description',
            'incident_type': 'incident_type',
            'severity': 'severity',
            'status': 'status',
            'create_date': 'create_date',
            'write_date': 'write_date',
            'create_uid': 'create_uid',
            'write_uid': 'write_uid',
            'company_id': 'company_id',
            'active': 'active'
        }

        # Create mapping for existing columns
        for new_col in new_columns:
            if new_col in direct_maps and direct_maps[new_col] in old_columns:
                mapping[new_col] = direct_maps[new_col]
            else:
                mapping[new_col] = None  # Will get default value

        return mapping

    def validate_migration(self):
        """Validate migration results"""
        try:
            # Count records in each table
            self.cursor.execute("SELECT COUNT(*) FROM bcm_incident;")
            new_count = self.cursor.fetchone()[0]

            # Check for duplicate incident numbers
            self.cursor.execute("""
                SELECT incident_number, COUNT(*)
                FROM bcm_incident
                GROUP BY incident_number
                HAVING COUNT(*) > 1;
            """)
            duplicates = self.cursor.fetchall()

            # Check for missing required fields
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM bcm_incident
                WHERE name IS NULL OR incident_number IS NULL;
            """)
            missing_required = self.cursor.fetchone()[0]

            # Report validation results
            self.logger.info(f"Validation Results:")
            self.logger.info(f"  Total incidents: {new_count}")
            self.logger.info(f"  Duplicate incident numbers: {len(duplicates)}")
            self.logger.info(f"  Missing required fields: {missing_required}")

            if duplicates:
                self.logger.warning(f"Found duplicate incident numbers: {duplicates}")

            if missing_required > 0:
                self.logger.error(f"Found {missing_required} incidents with missing required fields")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return False

    def run_migration(self, dry_run=False, backup=True):
        """Run the complete migration process"""
        try:
            self.logger.info("Starting BCM Incident migration")

            if not self.connect():
                return False

            # Check existing tables
            existing_tables = self.check_old_tables()

            if not any(existing_tables.values()):
                self.logger.info("No old tables found, migration not needed")
                return True

            if dry_run:
                self.logger.info("DRY RUN MODE - No changes will be made")
                self._simulate_migration()
                return True

            # Create backup if requested
            if backup:
                if not self.backup_current_data():
                    return False

            # Begin transaction
            self.conn.autocommit = False

            try:
                # Run migration steps
                basic_count = self.migrate_basic_incidents()
                mgmt_count = self.migrate_management_data()
                ai_count = self.migrate_ai_data()

                # Validate results
                if not self.validate_migration():
                    raise Exception("Migration validation failed")

                # Commit transaction
                self.conn.commit()

                self.logger.info("Migration completed successfully")
                self.logger.info(f"Summary: {basic_count} basic, {mgmt_count} management, {ai_count} AI records")

                return True

            except Exception as e:
                # Rollback on error
                self.conn.rollback()
                self.logger.error(f"Migration failed, rolled back: {e}")
                return False

        except Exception as e:
            self.logger.error(f"Migration setup failed: {e}")
            return False

        finally:
            self.disconnect()

    def _simulate_migration(self):
        """Simulate migration for dry run"""
        existing_tables = self.check_old_tables()

        for table, exists in existing_tables.items():
            if exists:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = self.cursor.fetchone()[0]
                self.logger.info(f"Would migrate {count} records from {table}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='BCM Incident Migration Script')
    parser.add_argument('--dry-run', action='store_true', help='Simulate migration without changes')
    parser.add_argument('--backup', action='store_true', default=True, help='Create backup before migration')
    parser.add_argument('--no-backup', action='store_false', dest='backup', help='Skip backup creation')
    parser.add_argument('--force', action='store_true', help='Force migration even if issues exist')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')

    # Database connection arguments
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--port', default='5432', help='Database port')
    parser.add_argument('--database', required=True, help='Database name')
    parser.add_argument('--user', required=True, help='Database user')
    parser.add_argument('--password', help='Database password')

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Database configuration
    db_config = {
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user,
        'password': args.password or input('Database password: ')
    }

    # Run migration
    migration = BCMIncidentMigration(db_config)
    success = migration.run_migration(dry_run=args.dry_run, backup=args.backup)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()