#!/usr/bin/env python3
"""
Test runner for Google Sheets access and authentication tests.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.test_sheets_access import run_all_tests


def main():
    """Run all tests and provide a summary."""
    print("🧪 Google Sheets Access Test Suite")
    print("=" * 50)
    
    # Check if virtual environment is activated
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Virtual environment not detected - consider activating .venv")
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
