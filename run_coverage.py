import os
import subprocess
import sys
from pathlib import Path

def get_most_recent_test_file():
    test_dir = Path("tests") #hello
    # Match files ending with _tests.py
    test_files = list(test_dir.glob("*_tests.py"))
    
    if not test_files:
        print("No test files found.")
        sys.exit(1)
    
    # Sort by last modified time (newest first)
    most_recent_file = max(test_files, key=lambda f: f.stat().st_mtime)
    return str(most_recent_file)

def run_coverage():
    most_recent_test_file = get_most_recent_test_file()
    print(f"Running tests on: {most_recent_test_file}")

    cmd = [
        "pytest",
        "--cov=.",
        "--cov-report=html",
        "--cov-report=term",
        most_recent_test_file
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\nCoverage report generated successfully!")
        print("HTML report is available in the htmlcov directory")
    except subprocess.CalledProcessError as e:
        print(f"Error running coverage: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_coverage()
