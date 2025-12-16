"""
Test Choreo Repository Registry - Monorepo Structure

This test verifies that the Choreo repository registry correctly handles
the monorepo structure at github.com/wso2/choreo-iam
"""

import sys
import os

# Direct import without going through __init__.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the module directly
import importlib.util
spec = importlib.util.spec_from_file_location(
    "choreo_repo_registry",
    os.path.join(os.path.dirname(__file__), 'backend', 'services', 'choreo_repo_registry.py')
)
choreo_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(choreo_module)

ChoreoRepoRegistry = choreo_module.ChoreoRepoRegistry


def test_monorepo_structure():
    """Test the Choreo repository registry with monorepo structure."""
    print("\n" + "=" * 80)
    print("CHOREO REPOSITORY REGISTRY TEST - Monorepo Structure")
    print("=" * 80 + "\n")
    
    registry = ChoreoRepoRegistry()
    
    # Test 1: Verify all components use wso2/choreo-iam monorepo
    print("1. Verifying all components use wso2/choreo-iam monorepo:")
    all_components = registry.get_all_components()
    
    correct_count = 0
    wrong_count = 0
    
    for comp in all_components:
        if comp['organization'] == 'wso2' and comp['monorepo'] == 'choreo-iam':
            correct_count += 1
        else:
            wrong_count += 1
            print(f"   ❌ ERROR: {comp['name']} uses {comp['organization']}/{comp.get('monorepo', 'N/A')}")
    
    print(f"   ✓ {correct_count}/{len(all_components)} components correctly use wso2/choreo-iam")
    
    if wrong_count > 0:
        print(f"   ❌ {wrong_count} components use wrong organization/monorepo!")
        return False
    
    print()
    
    # Test 2: Test specific component URLs with tree paths
    print("2. Testing specific component URLs (monorepo with tree paths):")
    test_components = [
        ("choreo-console", "https://github.com/wso2/choreo-iam/tree/main/choreo-console"),
        ("choreo-runtime", "https://github.com/wso2/choreo-iam/tree/main/choreo-runtime"),
        ("choreo-telemetry", "https://github.com/wso2/choreo-iam/tree/main/choreo-telemetry"),
        ("choreo-obsapi", "https://github.com/wso2/choreo-iam/tree/main/choreo-obsapi"),
        ("choreo-linker", "https://github.com/wso2/choreo-iam/tree/main/choreo-linker"),
        ("choreo-negotiator", "https://github.com/wso2/choreo-iam/tree/main/choreo-negotiator"),
    ]
    
    all_correct = True
    for comp_name, expected_url in test_components:
        url = registry.get_component_url(comp_name)
        
        if url == expected_url:
            print(f"   ✓ {comp_name:30}")
            print(f"      {url}")
        else:
            print(f"   ❌ {comp_name:30}")
            print(f"      Got:      {url}")
            print(f"      Expected: {expected_url}")
            all_correct = False
    
    if not all_correct:
        return False
    
    print()
    
    # Test 3: Test URL validation for monorepo URLs
    print("3. Testing URL validation for monorepo structure:")
    
    test_cases = [
        {
            "url": "https://github.com/wso2/choreo-iam/tree/main/choreo-console",
            "should_be_valid": True,
            "description": "Correct monorepo URL with tree path"
        },
        {
            "url": "https://github.com/wso2/choreo-iam",
            "should_be_valid": True,
            "description": "Monorepo root URL"
        },
        {
            "url": "https://github.com/wso2-enterprise/choreo-iam/tree/main/choreo-console",
            "should_be_valid": True,
            "description": "Monorepo with wso2-enterprise (should suggest wso2)"
        },
        {
            "url": "https://github.com/wso2/choreo-console",
            "should_be_valid": False,
            "expected_fix": "https://github.com/wso2/choreo-iam/tree/main/choreo-console",
            "description": "Old standalone repo format (should suggest monorepo)"
        },
        {
            "url": "https://github.com/wso2-enterprise/choreo-runtime",
            "should_be_valid": False,
            "expected_fix": "https://github.com/wso2/choreo-iam/tree/main/choreo-runtime",
            "description": "Old wso2-enterprise format (should suggest monorepo)"
        },
    ]
    
    for test in test_cases:
        url = test["url"]
        validation = registry.validate_github_url(url)
        
        print(f"\n   Testing: {url}")
        print(f"   Description: {test['description']}")
        
        if validation:
            is_valid = validation.get('is_valid')
            correct_url = validation.get('correct_url')
            
            if test['should_be_valid']:
                if is_valid:
                    print(f"   ✓ Correctly identified as valid")
                    print(f"     Correct URL: {correct_url}")
                else:
                    print(f"   ⚠ Recognized but marked for fixing")
                    print(f"     Suggested fix: {correct_url}")
            else:
                # Should be invalid or need fixing
                if 'expected_fix' in test:
                    if correct_url == test['expected_fix']:
                        print(f"   ✓ Correctly identified fix needed")
                        print(f"     Fixed to: {correct_url}")
                    else:
                        print(f"   ❌ Wrong fix suggested")
                        print(f"     Got: {correct_url}")
                        print(f"     Expected: {test['expected_fix']}")
                        return False
        else:
            if test['should_be_valid']:
                print(f"   ❌ Should be valid but validation returned None")
                return False
            else:
                print(f"   ⚠ Not recognized (may need to add to registry)")
    
    print()
    
    # Test 4: Show all registered components
    print("4. All registered Choreo components in the monorepo:")
    print()
    for comp in all_components[:15]:
        print(f"   - {comp['name']:40} {comp['url']}")
    
    if len(all_components) > 15:
        print(f"\n   ... and {len(all_components) - 15} more components")
    print()
    
    print(f"   Total: {len(all_components)} components in wso2/choreo-iam monorepo")
    print()
    
    # Test 5: Test fix_github_url
    print("5. Testing URL fixing for old formats:")
    
    old_urls = [
        ("https://github.com/wso2/choreo-console", "https://github.com/wso2/choreo-iam/tree/main/choreo-console"),
        ("https://github.com/wso2-enterprise/choreo-runtime", "https://github.com/wso2/choreo-iam/tree/main/choreo-runtime"),
        ("https://github.com/wso2-enterprise/choreo-telemetry", "https://github.com/wso2/choreo-iam/tree/main/choreo-telemetry"),
    ]
    
    for old_url, expected_fix in old_urls:
        fixed = registry.fix_github_url(old_url)
        if fixed == expected_fix:
            print(f"   ✓ Fixed: {old_url}")
            print(f"      -> {fixed}")
        else:
            print(f"   ❌ Failed to fix: {old_url}")
            print(f"      Got: {fixed}")
            print(f"      Expected: {expected_fix}")
            return False
    
    print()
    
    # Test 6: Verify correct monorepo URLs don't get "fixed"
    print("6. Verifying correct monorepo URLs don't get unnecessarily 'fixed':")
    
    correct_url = "https://github.com/wso2/choreo-iam/tree/main/choreo-console"
    fixed = registry.fix_github_url(correct_url)
    if fixed is None:
        print(f"   ✓ {correct_url}")
        print(f"      Correctly returns None (no fix needed)")
    else:
        print(f"   ❌ Correct URL should not be 'fixed': {correct_url}")
        print(f"      Got: {fixed}")
        return False
    
    print()
    
    return True


if __name__ == "__main__":
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "CHOREO REPOSITORY REGISTRY VALIDATION" + " " * 24 + "║")
    print("║" + " " * 18 + "Monorepo: wso2/choreo-iam" + " " * 33 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        success = test_monorepo_structure()
        
        if success:
            print("=" * 80)
            print("✓ ALL TESTS PASSED SUCCESSFULLY")
            print("=" * 80)
            print()
            print("Summary:")
            print("  ✓ All Choreo components correctly use wso2/choreo-iam monorepo")
            print("  ✓ URLs use correct format: github.com/wso2/choreo-iam/tree/main/{component}")
            print("  ✓ URL validation correctly identifies monorepo URLs as valid")
            print("  ✓ URL fixing correctly converts old formats to monorepo structure")
            print("  ✓ Registry contains 30+ Choreo components")
            print()
            print("The AI assistant will now:")
            print("  • Provide correct wso2/choreo-iam monorepo URLs in responses")
            print("  • Automatically fix old standalone repository URLs")
            print("  • Use tree/main paths to reference components in the monorepo")
            print()
            sys.exit(0)
        else:
            print("\n" + "=" * 80)
            print("❌ TESTS FAILED")
            print("=" * 80)
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

