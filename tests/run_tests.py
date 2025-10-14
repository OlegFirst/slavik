#!/usr/bin/env python3
"""
Python Test Runner for AI-Platform-ISO

Provides Python API for running tests programmatically.
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Optional


class TestRunner:
    """Test runner with convenient methods"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.tests_dir = self.project_root / "tests"

    def run_pytest(
        self,
        test_path: str = "tests/",
        markers: Optional[List[str]] = None,
        coverage: bool = False,
        verbose: bool = True,
        extra_args: Optional[List[str]] = None
    ) -> int:
        """
        Run pytest with specified options

        Args:
            test_path: Path to tests (relative to project root)
            markers: List of pytest markers (e.g., ['unit', 'not slow'])
            coverage: Whether to generate coverage report
            verbose: Verbose output
            extra_args: Additional pytest arguments

        Returns:
            Exit code (0 = success, non-zero = failure)
        """
        cmd = ["pytest"]

        # Add test path
        cmd.append(str(self.project_root / test_path))

        # Add markers
        if markers:
            cmd.extend(["-m", " and ".join(markers)])

        # Add verbosity
        if verbose:
            cmd.append("-v")

        # Add coverage
        if coverage:
            cmd.extend([
                "--cov=platform-services",
                "--cov=intelligent-core",
                "--cov=infrastructure",
                "--cov-report=html",
                "--cov-report=term-missing"
            ])

        # Add extra args
        if extra_args:
            cmd.extend(extra_args)

        print(f"Running: {' '.join(cmd)}")
        return subprocess.call(cmd, cwd=self.project_root)

    def run_all(self) -> int:
        """Run all tests"""
        return self.run_pytest()

    def run_unit(self) -> int:
        """Run unit tests only"""
        return self.run_pytest("tests/unit/", markers=["unit"])

    def run_integration(self) -> int:
        """Run integration tests only"""
        return self.run_pytest("tests/integration/", markers=["integration"])

    def run_e2e(self) -> int:
        """Run end-to-end tests only"""
        return self.run_pytest("tests/e2e/", markers=["e2e"])

    def run_platform_services(self) -> int:
        """Run all platform services tests"""
        return self.run_pytest("tests/unit/platform-services/")

    def run_intelligent_core(self) -> int:
        """Run all intelligent core tests"""
        return self.run_pytest("tests/unit/intelligent-core/")

    def run_infrastructure(self) -> int:
        """Run all infrastructure tests"""
        return self.run_pytest("tests/unit/infrastructure/")

    def run_fast(self) -> int:
        """Run fast tests (exclude slow)"""
        return self.run_pytest(markers=["not slow"])

    def run_with_coverage(self) -> int:
        """Run all tests with coverage report"""
        return self.run_pytest(coverage=True)

    def run_failed(self) -> int:
        """Re-run only failed tests from last run"""
        return self.run_pytest(extra_args=["--lf"])

    def run_specific(self, test_path: str) -> int:
        """Run specific test file or directory"""
        return self.run_pytest(test_path)


def main():
    """Main CLI entrypoint"""
    runner = TestRunner()

    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [command]")
        print("Commands: all, unit, integration, e2e, platform, intelligent, infrastructure")
        print("          fast, coverage, failed, specific <path>")
        return 1

    command = sys.argv[1]

    commands = {
        "all": runner.run_all,
        "unit": runner.run_unit,
        "integration": runner.run_integration,
        "e2e": runner.run_e2e,
        "platform": runner.run_platform_services,
        "intelligent": runner.run_intelligent_core,
        "infrastructure": runner.run_infrastructure,
        "fast": runner.run_fast,
        "coverage": runner.run_with_coverage,
        "failed": runner.run_failed,
    }

    if command == "specific":
        if len(sys.argv) < 3:
            print("Error: Please specify test path")
            print("Usage: python run_tests.py specific <path>")
            return 1
        return runner.run_specific(sys.argv[2])

    if command in commands:
        return commands[command]()
    else:
        print(f"Unknown command: {command}")
        print(f"Available commands: {', '.join(commands.keys())}, specific")
        return 1


if __name__ == "__main__":
    sys.exit(main())
