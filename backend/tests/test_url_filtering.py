#!/usr/bin/env python3
"""
Test script to verify URL filtering functionality
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from services.url_validator import URLValidator


def test_wso2_doc_url_filtering():
    """Test that invalid WSO2 documentation URLs with paths are removed."""

    validator = URLValidator(enable_validation=False)

    # Test cases with invalid URLs
    test_cases = [
        {
            "input": "Check out https://wso2.com/choreo/docs/cli/ for more info",
            "expected": "Check out https://wso2.com/choreo/docs for more info",
            "description": "Plain URL with /cli/ path"
        },
        {
            "input": "Visit https://wso2.com/choreo/docs/devops/ci-pipelines/ for details",
            "expected": "Visit https://wso2.com/choreo/docs for details",
            "description": "URL with /devops/ci-pipelines/ path"
        },
        {
            "input": "See [CLI documentation](https://wso2.com/choreo/docs/cli/) here",
            "expected": "See [CLI documentation](https://wso2.com/choreo/docs) here",
            "description": "Markdown link with path"
        },
        {
            "input": "For more info, visit https://wso2.com/choreo/docs/",
            "expected": "For more info, visit https://wso2.com/choreo/docs/",
            "description": "Valid base URL (should not change)"
        },
        {
            "input": "Multiple URLs: https://wso2.com/choreo/docs/devops/ and https://wso2.com/choreo/docs/testing/guide/",
            "expected": "Multiple URLs: https://wso2.com/choreo/docs and https://wso2.com/choreo/docs",
            "description": "Multiple invalid URLs"
        }
    ]

    print("Testing WSO2 Documentation URL Filtering")
    print("=" * 60)

    all_passed = True
    for i, test in enumerate(test_cases, 1):
        result = validator.remove_invalid_wso2_doc_urls(test["input"])
        passed = result == test["expected"]

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\nTest {i}: {test['description']}")
        print(f"Status: {status}")
        print(f"Input:    {test['input']}")
        print(f"Expected: {test['expected']}")
        print(f"Got:      {result}")

        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(test_wso2_doc_url_filtering())
