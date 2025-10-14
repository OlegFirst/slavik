#!/usr/bin/env python3
"""
Code Watcher Service for Project Agent
Monitors code changes and automatically triggers analysis and test generation
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Set, List, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('code_watcher.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CodeChangeHandler(FileSystemEventHandler):
    """
    Handles file system events for Python code changes
    """

    def __init__(self,
                 project_root: Path,
                 debounce_seconds: int = 5,
                 auto_generate_tests: bool = True,
                 auto_run_security: bool = True,
                 auto_run_quality: bool = False):
        self.project_root = project_root
        self.debounce_seconds = debounce_seconds
        self.auto_generate_tests = auto_generate_tests
        self.auto_run_security = auto_run_security
        self.auto_run_quality = auto_run_quality

        # Track pending changes (debouncing)
        self.pending_changes: Dict[str, float] = {}

        # Directories to watch
        self.watch_dirs = [
            'intelligent-core',
            'platform-services',
            'infrastructure'
        ]

        # Directories to ignore
        self.ignore_patterns = {
            '__pycache__',
            '.pytest_cache',
            '.git',
            'node_modules',
            'venv',
            'env',
            '.venv',
            'tests/generated'  # Don't watch generated tests
        }

    def should_process_file(self, file_path: str) -> bool:
        """Check if file should be processed"""
        path = Path(file_path)

        # Only process Python files
        if path.suffix != '.py':
            return False

        # Check if in watched directories
        try:
            relative_path = path.relative_to(self.project_root)
            if not any(str(relative_path).startswith(d) for d in self.watch_dirs):
                return False
        except ValueError:
            return False

        # Check ignore patterns
        for part in path.parts:
            if part in self.ignore_patterns:
                return False

        return True

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events"""
        if event.is_directory:
            return

        if not self.should_process_file(event.src_path):
            return

        # Add to pending changes with timestamp
        self.pending_changes[event.src_path] = time.time()
        logger.info(f"📝 Detected change: {event.src_path}")

    def on_created(self, event: FileSystemEvent):
        """Handle file creation events"""
        if event.is_directory:
            return

        if not self.should_process_file(event.src_path):
            return

        self.pending_changes[event.src_path] = time.time()
        logger.info(f"✨ New file created: {event.src_path}")

    def process_pending_changes(self):
        """Process pending changes after debounce period"""
        current_time = time.time()
        files_to_process = []

        for file_path, timestamp in list(self.pending_changes.items()):
            if current_time - timestamp >= self.debounce_seconds:
                files_to_process.append(file_path)
                del self.pending_changes[file_path]

        if files_to_process:
            logger.info(f"🔄 Processing {len(files_to_process)} changed files...")

            for file_path in files_to_process:
                self.analyze_file(file_path)

    def analyze_file(self, file_path: str):
        """Run analysis on a single file"""
        logger.info(f"🔍 Analyzing: {file_path}")

        results = {
            'file': file_path,
            'timestamp': datetime.utcnow().isoformat(),
            'tests_generated': False,
            'security_checked': False,
            'quality_checked': False,
            'errors': []
        }

        # Generate tests
        if self.auto_generate_tests:
            try:
                logger.info(f"🧪 Generating tests for: {file_path}")
                result = subprocess.run(
                    ['python', '-m', 'agent.test_generator', '--file', file_path],
                    cwd=self.project_root / 'infrastructure/tools/project-agent',
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info(f"✅ Tests generated successfully")
                    results['tests_generated'] = True
                else:
                    logger.warning(f"⚠️  Test generation failed: {result.stderr}")
                    results['errors'].append(f"Test generation: {result.stderr}")
            except subprocess.TimeoutExpired:
                logger.error(f"❌ Test generation timeout for: {file_path}")
                results['errors'].append("Test generation timeout")
            except Exception as e:
                logger.error(f"❌ Test generation error: {e}")
                results['errors'].append(f"Test generation error: {e}")

        # Run security check
        if self.auto_run_security:
            try:
                logger.info(f"🔒 Running security check for: {file_path}")
                result = subprocess.run(
                    ['python', '-m', 'agent.security', '--file', file_path],
                    cwd=self.project_root / 'infrastructure/tools/project-agent',
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info(f"✅ Security check passed")
                    results['security_checked'] = True
                else:
                    logger.warning(f"⚠️  Security issues found: {result.stderr}")
                    results['errors'].append(f"Security: {result.stderr}")
            except Exception as e:
                logger.error(f"❌ Security check error: {e}")
                results['errors'].append(f"Security error: {e}")

        # Run quality check
        if self.auto_run_quality:
            try:
                logger.info(f"📊 Running quality check for: {file_path}")
                result = subprocess.run(
                    ['python', '-m', 'agent.quality', '--file', file_path],
                    cwd=self.project_root / 'infrastructure/tools/project-agent',
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info(f"✅ Quality check passed")
                    results['quality_checked'] = True
                else:
                    logger.warning(f"⚠️  Quality issues found: {result.stderr}")
                    results['errors'].append(f"Quality: {result.stderr}")
            except Exception as e:
                logger.error(f"❌ Quality check error: {e}")
                results['errors'].append(f"Quality error: {e}")

        # Log summary
        self.log_analysis_summary(results)

    def log_analysis_summary(self, results: Dict[str, Any]):
        """Log analysis summary"""
        logger.info("="*60)
        logger.info(f"📋 Analysis Summary for: {results['file']}")
        logger.info(f"   Timestamp: {results['timestamp']}")
        logger.info(f"   Tests Generated: {'✅' if results['tests_generated'] else '❌'}")
        logger.info(f"   Security Checked: {'✅' if results['security_checked'] else '❌'}")
        logger.info(f"   Quality Checked: {'✅' if results['quality_checked'] else '❌'}")

        if results['errors']:
            logger.warning(f"   Errors: {len(results['errors'])}")
            for error in results['errors']:
                logger.warning(f"     - {error}")

        logger.info("="*60)


class CodeWatcher:
    """
    Main code watcher service
    """

    def __init__(self,
                 project_root: str = None,
                 config_file: str = None):
        self.project_root = Path(project_root or os.getenv('PROJECT_ROOT', '/Users/MD/AI-Platform-ISO'))
        self.config = self.load_config(config_file)

        self.handler = CodeChangeHandler(
            project_root=self.project_root,
            debounce_seconds=self.config.get('debounce_seconds', 5),
            auto_generate_tests=self.config.get('auto_generate_tests', True),
            auto_run_security=self.config.get('auto_run_security', True),
            auto_run_quality=self.config.get('auto_run_quality', False)
        )

        self.observer = Observer()

    def load_config(self, config_file: str = None) -> Dict[str, Any]:
        """Load configuration"""
        default_config = {
            'debounce_seconds': 5,
            'auto_generate_tests': True,
            'auto_run_security': True,
            'auto_run_quality': False,
            'check_interval': 1
        }

        if config_file and Path(config_file).exists():
            import json
            with open(config_file) as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def start(self):
        """Start watching for code changes"""
        logger.info("="*60)
        logger.info("🚀 Project Agent Code Watcher Starting...")
        logger.info(f"📁 Project Root: {self.project_root}")
        logger.info(f"⏱️  Debounce: {self.config.get('debounce_seconds')}s")
        logger.info(f"🧪 Auto Generate Tests: {self.config.get('auto_generate_tests')}")
        logger.info(f"🔒 Auto Security Check: {self.config.get('auto_run_security')}")
        logger.info(f"📊 Auto Quality Check: {self.config.get('auto_run_quality')}")
        logger.info("="*60)

        # Setup observers for watched directories
        for watch_dir in self.handler.watch_dirs:
            dir_path = self.project_root / watch_dir
            if dir_path.exists():
                self.observer.schedule(self.handler, str(dir_path), recursive=True)
                logger.info(f"👁️  Watching: {dir_path}")
            else:
                logger.warning(f"⚠️  Directory not found: {dir_path}")

        self.observer.start()
        logger.info("✅ Code watcher is running. Press Ctrl+C to stop.")

        try:
            while True:
                time.sleep(self.config.get('check_interval', 1))
                self.handler.process_pending_changes()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop watching"""
        logger.info("🛑 Stopping code watcher...")
        self.observer.stop()
        self.observer.join()
        logger.info("✅ Code watcher stopped")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Project Agent Code Watcher - Automatic code analysis and test generation'
    )
    parser.add_argument(
        '--project-root',
        help='Project root directory',
        default=None
    )
    parser.add_argument(
        '--config',
        help='Configuration file path',
        default=None
    )
    parser.add_argument(
        '--no-tests',
        action='store_true',
        help='Disable automatic test generation'
    )
    parser.add_argument(
        '--no-security',
        action='store_true',
        help='Disable automatic security checks'
    )
    parser.add_argument(
        '--enable-quality',
        action='store_true',
        help='Enable automatic quality checks'
    )

    args = parser.parse_args()

    # Override config with CLI args
    config_overrides = {}
    if args.no_tests:
        config_overrides['auto_generate_tests'] = False
    if args.no_security:
        config_overrides['auto_run_security'] = False
    if args.enable_quality:
        config_overrides['auto_run_quality'] = True

    watcher = CodeWatcher(
        project_root=args.project_root,
        config_file=args.config
    )

    # Apply CLI overrides
    watcher.config.update(config_overrides)

    watcher.start()


if __name__ == '__main__':
    main()
