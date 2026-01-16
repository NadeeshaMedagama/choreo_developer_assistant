#!/usr/bin/env python3
"""
Test script to verify that Choreo repository URL generation and fixing works correctly.
"""

from services.choreo_repo_registry import get_choreo_registry
from services.url_validator import get_url_validator

def test_repo_registry():
    """Test the Choreo repository registry functionality."""
    print("=" * 80)
    print("TESTING CHOREO REPOSITORY REGISTRY")
    print("=" * 80)

    registry = get_choreo_registry()

    # Test 1: Generate system prompt URLs
    print("\n1. Testing system prompt URL generation:")
    print("-" * 80)
    prompt = registry.generate_system_prompt_urls()
    print(prompt)

    # Test 2: Verify URLs in the prompt
    print("\n2. Verifying all URLs use wso2-enterprise:")
    print("-" * 80)
    # Check for incorrect pattern - but exclude the warning message itself
    lines = prompt.split('\n')
    incorrect_found = False
    for line in lines:
        if 'github.com/wso2/' in line and 'wso2-enterprise' not in line and 'NEVER use' not in line:
            print(f"❌ ERROR: Found incorrect wso2 public org URL in line: {line}")
            incorrect_found = True

    if not incorrect_found:
        print("✓ All URLs correctly use wso2-enterprise organization")

    # Test 3: Test URL validation
    print("\n3. Testing URL validation and fixing:")
    print("-" * 80)

    test_urls = [
        ("https://github.com/wso2-enterprise/choreo-console", "Already correct"),
        ("https://github.com/wso2/choreo-console", "Wrong org - should fix to wso2-enterprise"),
        ("https://github.com/wso2/choreo-runtime", "Wrong org - should fix to wso2-enterprise"),
    ]

    for url, description in test_urls:
        validation = registry.validate_github_url(url)
        if validation:
            print(f"\nURL: {url}")
            print(f"  Description: {description}")
            print(f"  Valid: {validation['is_valid']}")
            print(f"  Correct URL: {validation['correct_url']}")
            print(f"  Needs Fix: {validation['needs_org_fix']}")
        else:
            print(f"\nURL: {url}")
            print(f"  ❌ Not recognized as Choreo component")

    # Test 4: Test URL fixing
    print("\n4. Testing URL fixing:")
    print("-" * 80)

    wrong_urls = [
        "https://github.com/wso2/choreo-console",
        "https://github.com/wso2/choreo-runtime",
        "https://github.com/wso2/choreo-telemetry",
    ]

    for wrong_url in wrong_urls:
        fixed_url = registry.fix_github_url(wrong_url)
        if fixed_url:
            print(f"✓ Fixed: {wrong_url}")
            print(f"      → {fixed_url}")
        else:
            print(f"✗ Could not fix: {wrong_url}")

    # Test 5: Test auto-fix in text
    print("\n5. Testing auto-fix in text (URL Validator):")
    print("-" * 80)

    url_validator = get_url_validator(enable_validation=False)  # Disable validation for speed

    test_text = """
    The Choreo console is at https://github.com/wso2/choreo-console and 
    the runtime is at https://github.com/wso2/choreo-runtime.
    You can also check github.com/wso2/choreo-telemetry for telemetry.
    """

    print("Original text:")
    print(test_text)

    fixed_text = url_validator.auto_fix_all_choreo_urls(test_text)

    print("\nFixed text:")
    print(fixed_text)

    if "github.com/wso2/" in fixed_text and "choreo-" in fixed_text:
        print("\n❌ ERROR: Still contains incorrect wso2 public org URLs!")
    else:
        print("\n✓ All URLs successfully auto-fixed to wso2-enterprise")

    # Test 6: Count total repositories
    print("\n6. Repository Statistics:")
    print("-" * 80)
    components = registry.get_all_components()
    print(f"Total Choreo components: {len(components)}")

    wso2_enterprise_count = sum(1 for c in components if c['organization'] == 'wso2-enterprise')
    print(f"Components in wso2-enterprise: {wso2_enterprise_count}")

    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_repo_registry()
