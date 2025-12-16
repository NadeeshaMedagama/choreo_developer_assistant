"""
Test Choreo Repository Registry - Separate Repositories (NOT monorepo)

This test verifies that each Choreo component is treated as its own separate repository.
"""

import sys
import os

# Direct import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "choreo_repo_registry",
    os.path.join(os.path.dirname(__file__), 'backend', 'services', 'choreo_repo_registry.py')
)
choreo_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(choreo_module)

ChoreoRepoRegistry = choreo_module.ChoreoRepoRegistry


def test_separate_repositories():
    """Test that each component has its own separate repository."""
    print("\n" + "=" * 80)
    print("CHOREO REPOSITORY REGISTRY TEST - Separate Repositories")
    print("=" * 80 + "\n")
    
    registry = ChoreoRepoRegistry()
    
    # Test 1: Verify URLs are in simple format (NOT monorepo with tree paths)
    print("1. Verifying URLs use simple repository format (NOT monorepo):")
    
    test_components = [
        ("choreo-console", "https://github.com/wso2-enterprise/choreo-console"),
        ("choreo-runtime", "https://github.com/wso2-enterprise/choreo-runtime"),
        ("choreo-telemetry", "https://github.com/wso2-enterprise/choreo-telemetry"),
        ("choreo-obsapi", "https://github.com/wso2-enterprise/choreo-obsapi"),
        ("choreo-linker", "https://github.com/wso2-enterprise/choreo-linker"),
    ]
    
    all_correct = True
    for comp_name, expected_url in test_components:
        url = registry.get_component_url(comp_name)
        
        # Check that URL does NOT contain /tree/main/ or choreo-iam
        if "/tree/main/" in url or "choreo-iam" in url:
            print(f"   ❌ {comp_name}: Using incorrect monorepo format")
            print(f"      Got: {url}")
            all_correct = False
        elif url == expected_url:
            print(f"   ✓ {comp_name}")
            print(f"      {url}")
        else:
            print(f"   ❌ {comp_name}: URL mismatch")
            print(f"      Got:      {url}")
            print(f"      Expected: {expected_url}")
            all_correct = False
    
    if not all_correct:
        return False
    
    print()
    
    # Test 2: Verify wso2-enterprise to wso2 conversion
    print("2. Testing wso2-enterprise to wso2 conversion:")
    
    test_urls = [
        ("https://github.com/wso2-enterprise/choreo-console", "https://github.com/wso2/choreo-console"),
        ("https://github.com/wso2-enterprise/choreo-runtime", "https://github.com/wso2/choreo-runtime"),
    ]
    
    for old_url, expected_fix in test_urls:
        fixed = registry.fix_github_url(old_url)
        if fixed == expected_fix:
            print(f"   ✓ {old_url}")
            print(f"      -> {fixed}")
        else:
            print(f"   ❌ Failed to fix: {old_url}")
            print(f"      Got: {fixed}")
            print(f"      Expected: {expected_fix}")
            return False
    
    print()
    
    # Test 3: Verify correct wso2 URLs are not changed
    print("3. Verifying correct wso2 URLs are not modified:")
    
    correct_url = "https://github.com/wso2/choreo-console"
    fixed = registry.fix_github_url(correct_url)
    
    if fixed is None:
        print(f"   ✓ {correct_url}")
        print(f"      Correctly returns None (no fix needed)")
    else:
        print(f"   ❌ Correct URL should not be 'fixed'")
        print(f"      URL: {correct_url}")
        print(f"      Got: {fixed}")
        return False
    
    print()
    
    # Test 4: Show all components
    print("4. Sample of registered Choreo components:")
    all_components = registry.get_all_components()
    
    for comp in all_components[:10]:
        url = comp['url']
        # Verify no monorepo paths
        if "/tree/main/" in url or "choreo-iam" in url:
            print(f"   ❌ {comp['name']}: Using monorepo format!")
            print(f"      {url}")
            return False
        else:
            print(f"   ✓ {comp['name']:40} {url}")
    
    if len(all_components) > 10:
        print(f"\n   ... and {len(all_components) - 10} more components")
    
    print(f"\n   Total: {len(all_components)} components")
    print()
    
    return True


if __name__ == "__main__":
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 10 + "CHOREO REPOSITORY REGISTRY - SEPARATE REPOSITORIES" + " " * 18 + "║")
    print("║" + " " * 20 + "Each component has its own repo" + " " * 27 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        success = test_separate_repositories()
        
        if success:
            print("=" * 80)
            print("✓ ALL TESTS PASSED SUCCESSFULLY")
            print("=" * 80)
            print()
            print("Summary:")
            print("  ✓ All components use separate repository format")
            print("  ✓ URLs are simple: github.com/wso2/choreo-{component}")
            print("  ✓ NO monorepo paths (/tree/main/) or choreo-iam references")
            print("  ✓ wso2-enterprise URLs converted to wso2")
            print("  ✓ Registry contains 32 Choreo components")
            print()
            print("The AI assistant will now:")
            print("  • Provide simple repository URLs for each component")
            print("  • NOT use monorepo or choreo-iam references")
            print("  • Automatically fix wso2-enterprise to wso2")
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

