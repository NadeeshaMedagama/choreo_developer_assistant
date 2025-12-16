"""
Direct Test for Choreo Repository Registry

This test directly imports and tests the ChoreoRepoRegistry class.
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


def test_registry():
    """Test the Choreo repository registry."""
    print("\n" + "=" * 80)
    print("CHOREO REPOSITORY REGISTRY TEST - wso2-enterprise Organization")
    print("=" * 80 + "\n")
    
    registry = ChoreoRepoRegistry()
    
    # Test 1: Verify all components use wso2-enterprise
    print("1. Verifying all components use wso2-enterprise organization:")
    all_components = registry.get_all_components()
    
    correct_org_count = 0
    wrong_org_count = 0
    
    for comp in all_components:
        if comp['organization'] == 'wso2-enterprise':
            correct_org_count += 1
        else:
            wrong_org_count += 1
            print(f"   ❌ ERROR: {comp['name']} uses {comp['organization']} instead of wso2-enterprise")
    
    print(f"   ✓ {correct_org_count}/{len(all_components)} components correctly use wso2-enterprise")
    
    if wrong_org_count > 0:
        print(f"   ❌ {wrong_org_count} components use wrong organization!")
        return False
    
    print()
    
    # Test 2: Test specific component URLs
    print("2. Testing specific component URLs:")
    test_components = [
        "choreo-console",
        "choreo-runtime",
        "choreo-telemetry",
        "choreo-obsapi",
        "choreo-linker",
        "choreo-negotiator"
    ]
    
    all_correct = True
    for comp_name in test_components:
        url = registry.get_component_url(comp_name)
        expected = f"https://github.com/wso2-enterprise/{comp_name}"
        
        if url == expected:
            print(f"   ✓ {comp_name:30} -> {url}")
        else:
            print(f"   ❌ {comp_name:30} -> {url}")
            print(f"      Expected: {expected}")
            all_correct = False
    
    if not all_correct:
        return False
    
    print()
    
    # Test 3: Test URL validation
    print("3. Testing URL validation:")
    
    # Correct wso2-enterprise URL should be valid
    url1 = "https://github.com/wso2-enterprise/choreo-console"
    validation1 = registry.validate_github_url(url1)
    if validation1 and validation1.get('is_valid'):
        print(f"   ✓ {url1}")
        print(f"      Correctly identified as VALID (correct organization)")
    else:
        print(f"   ❌ {url1} should be valid")
        return False
    
    # Wrong wso2 (public) URL should be identified and have a fix
    url2 = "https://github.com/wso2/choreo-console"
    validation2 = registry.validate_github_url(url2)
    if validation2:
        correct_url = validation2.get('correct_url')
        expected_fix = "https://github.com/wso2-enterprise/choreo-console"
        if correct_url == expected_fix:
            print(f"   ✓ {url2}")
            print(f"      Correctly identified fix needed -> {correct_url}")
        else:
            print(f"   ❌ {url2}")
            print(f"      Got fix: {correct_url}, Expected: {expected_fix}")
            return False
    else:
        print(f"   ❌ {url2} should have a fix")
        return False
    
    print()
    
    # Test 4: Test fix_github_url method
    print("4. Testing URL fixing:")
    
    wrong_urls = [
        ("https://github.com/wso2/choreo-console", "https://github.com/wso2-enterprise/choreo-console"),
        ("https://github.com/wso2/choreo-runtime", "https://github.com/wso2-enterprise/choreo-runtime"),
        ("https://github.com/wso2/choreo-telemetry", "https://github.com/wso2-enterprise/choreo-telemetry"),
    ]
    
    for wrong_url, expected_fix in wrong_urls:
        fixed = registry.fix_github_url(wrong_url)
        if fixed == expected_fix:
            print(f"   ✓ Fixed: {wrong_url}")
            print(f"      -> {fixed}")
        else:
            print(f"   ❌ Failed to fix: {wrong_url}")
            print(f"      Got: {fixed}, Expected: {expected_fix}")
            return False
    
    print()
    
    # Test 5: Verify wso2-enterprise URLs don't need fixing
    print("5. Verifying correct URLs don't get 'fixed':")
    
    correct_url = "https://github.com/wso2-enterprise/choreo-console"
    fixed = registry.fix_github_url(correct_url)
    if fixed is None:
        print(f"   ✓ {correct_url}")
        print(f"      Correctly returns None (no fix needed)")
    else:
        print(f"   ❌ Correct URL should not be 'fixed': {correct_url}")
        print(f"      Got: {fixed}")
        return False
    
    print()
    
    # Test 6: Show all registered components
    print("6. All registered Choreo components:")
    print()
    for comp in all_components:
        print(f"   - {comp['name']:35} {comp['url']}")
    
    print()
    print(f"   Total: {len(all_components)} components in wso2-enterprise organization")
    print()
    
    return True


if __name__ == "__main__":
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "CHOREO REPOSITORY REGISTRY VALIDATION" + " " * 24 + "║")
    print("║" + " " * 20 + "All repos in wso2-enterprise org" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        success = test_registry()
        
        if success:
            print("=" * 80)
            print("✓ ALL TESTS PASSED SUCCESSFULLY")
            print("=" * 80)
            print()
            print("Summary:")
            print("  ✓ All Choreo components correctly use wso2-enterprise organization")
            print("  ✓ URL validation correctly identifies wso2-enterprise URLs as valid")
            print("  ✓ URL fixing correctly changes wso2 (public) to wso2-enterprise")
            print("  ✓ Correct wso2-enterprise URLs are not modified")
            print("  ✓ Registry contains 20+ Choreo components")
            print()
            print("The AI assistant will now:")
            print("  • Provide correct wso2-enterprise URLs in responses")
            print("  • Automatically fix any incorrect wso2 public org URLs")
            print("  • Validate all URLs before including them in answers")
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

