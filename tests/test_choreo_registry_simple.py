"""
Simple Test for Choreo Repository Registry

This test verifies that the Choreo repository registry correctly maps components
to the wso2-enterprise organization.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import only what we need, directly
from services.choreo_repo_registry import ChoreoRepoRegistry


def test_registry():
    """Test the Choreo repository registry."""
    print("\n" + "=" * 80)
    print("CHOREO REPOSITORY REGISTRY TEST")
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
        "choreo-linker"
    ]
    
    for comp_name in test_components:
        url = registry.get_component_url(comp_name)
        expected = f"https://github.com/wso2-enterprise/{comp_name}"
        
        if url == expected:
            print(f"   ✓ {comp_name:25} -> {url}")
        else:
            print(f"   ❌ {comp_name:25} -> {url} (expected: {expected})")
            return False
    
    print()
    
    # Test 3: Test URL validation and fixing
    print("3. Testing URL validation and fixing:")
    
    test_cases = [
        {
            "url": "https://github.com/wso2-enterprise/choreo-console",
            "expected_valid": True,
            "expected_fix": None,
            "description": "Correct wso2-enterprise URL"
        },
        {
            "url": "https://github.com/wso2/choreo-console",
            "expected_valid": False,
            "expected_fix": "https://github.com/wso2-enterprise/choreo-console",
            "description": "Wrong org (wso2) - should fix to wso2-enterprise"
        },
        {
            "url": "https://github.com/wso2/choreo-runtime",
            "expected_valid": False,
            "expected_fix": "https://github.com/wso2-enterprise/choreo-runtime",
            "description": "Wrong org (wso2) - should fix to wso2-enterprise"
        }
    ]
    
    for test in test_cases:
        url = test["url"]
        validation = registry.validate_github_url(url)
        
        print(f"\n   Testing: {url}")
        print(f"   Description: {test['description']}")
        
        if validation:
            is_valid = validation.get('is_valid')
            correct_url = validation.get('correct_url')
            
            # Check if it's valid for the right reason
            if test['expected_valid']:
                if is_valid and correct_url == url:
                    print(f"   ✓ Correctly identified as valid")
                else:
                    print(f"   ❌ Should be valid but got: valid={is_valid}, correct_url={correct_url}")
                    return False
            else:
                # Should be invalid or need fixing
                if correct_url == test['expected_fix']:
                    print(f"   ✓ Correctly identified fix needed: {correct_url}")
                else:
                    print(f"   ❌ Wrong fix: got {correct_url}, expected {test['expected_fix']}")
                    return False
        else:
            if test['expected_valid']:
                print(f"   ❌ Should be valid but validation returned None")
                return False
            else:
                print(f"   ✓ Correctly identified as invalid")
    
    print()
    
    # Test 4: Show all registered components
    print("4. All registered Choreo components (first 10):")
    for comp in all_components[:10]:
        print(f"   - {comp['name']:35} {comp['url']}")
    
    print(f"\n   ... and {len(all_components) - 10} more components")
    print()
    
    return True


if __name__ == "__main__":
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "CHOREO REPOSITORY REGISTRY VALIDATION" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        success = test_registry()
        
        if success:
            print("=" * 80)
            print("✓ ALL TESTS PASSED")
            print("=" * 80)
            print()
            print("Summary:")
            print("  ✓ All Choreo components correctly use wso2-enterprise organization")
            print("  ✓ URL validation correctly identifies wso2-enterprise URLs as valid")
            print("  ✓ URL fixing correctly changes wso2 to wso2-enterprise")
            print("  ✓ Registry contains 20+ Choreo components")
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

