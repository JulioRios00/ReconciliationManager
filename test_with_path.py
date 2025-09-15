#!/usr/bin/env python3
"""
Test runner with proper environment setup
"""

import os
import subprocess
import sys

#!/usr/bin/env python3
"""
Test runner with proper environment setup
"""

import os
import subprocess
import sys


def run_tests():
    """Run tests with proper Python path setup"""
    # Add src directory to Python path
    src_path = os.path.join(os.path.dirname(__file__), "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    # Set PYTHONPATH environment variable
    env = os.environ.copy()
    env["PYTHONPATH"] = src_path

    # Run pytest with the updated environment
    cmd = [sys.executable, "-m", "pytest", "src/tests/", "-v", "--tb=short"]

    print(f"Running: {' '.join(cmd)}")
    print(f"PYTHONPATH: {env.get('PYTHONPATH', 'Not set')}")

    try:
        result = subprocess.run(cmd, env=env, cwd=os.path.dirname(__file__))
        return result.returncode == 0
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def main():
    """Main function"""
    success = run_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
