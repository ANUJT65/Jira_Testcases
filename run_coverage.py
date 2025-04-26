import os
import subprocess
import sys

def run_coverage():
    # Run pytest with coverage
    cmd = [
        "pytest",
        "--cov=.",
        "--cov-report=html",
        "--cov-report=term",
        "tests/"
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