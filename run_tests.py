#!/usr/bin/env python3
"""
Test runner script for ReconciliationManager
This script provides convenient commands for running tests with different configurations.
"""

import os
import subprocess
import sys


def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print("=" * 50)

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, cwd=os.getcwd()
        )
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"Exit code: {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def main():
    """Main function to handle different test commands"""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py <command>")
        print("Commands:")
        print("  unit          - Run unit tests only")
        print("  coverage      - Run tests with coverage report")
        print("  html-cov      - Generate HTML coverage report")
        print("  verbose       - Run tests with verbose output")
        print("  quick         - Run tests without coverage (fast)")
        print("  setup         - Install test dependencies")
        return

    command = sys.argv[1]

    if command == "setup":
        success = run_command(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            "Installing dependencies",
        )
        if success:
            print("✅ Dependencies installed successfully")
        else:
            print("❌ Failed to install dependencies")
            sys.exit(1)

    elif command == "unit":
        success = run_command(
            [sys.executable, "-m", "pytest", "src/tests/", "-v", "-m", "unit"],
            "Running unit tests",
        )
        if success:
            print("✅ Unit tests passed")
        else:
            print("❌ Unit tests failed")
            sys.exit(1)

    elif command == "coverage":
        success = run_command(
            [
                sys.executable,
                "-m",
                "pytest",
                "src/tests/",
                "--cov=src",
                "--cov-report=term-missing",
                "-v",
            ],
            "Running tests with coverage",
        )
        if success:
            print("✅ Tests with coverage passed")
        else:
            print("❌ Tests with coverage failed")
            sys.exit(1)

    elif command == "html-cov":
        success = run_command(
            [
                sys.executable,
                "-m",
                "pytest",
                "src/tests/",
                "--cov=src",
                "--cov-report=html",
                "-v",
            ],
            "Generating HTML coverage report",
        )
        if success:
            print("✅ HTML coverage report generated")
            print("📁 Open htmlcov/index.html in your browser")
        else:
            print("❌ Failed to generate HTML coverage report")
            sys.exit(1)

    elif command == "verbose":
        success = run_command(
            [sys.executable, "-m", "pytest", "src/tests/", "-v", "-s"],
            "Running tests with verbose output",
        )
        if success:
            print("✅ Verbose tests passed")
        else:
            print("❌ Verbose tests failed")
            sys.exit(1)

    elif command == "quick":
        success = run_command(
            [sys.executable, "-m", "pytest", "src/tests/", "--tb=short"],
            "Running quick tests",
        )
        if success:
            print("✅ Quick tests passed")
        else:
            print("❌ Quick tests failed")
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        print("Available commands: unit, coverage, html-cov, verbose, quick, setup")
        sys.exit(1)


if __name__ == "__main__":
    main()
