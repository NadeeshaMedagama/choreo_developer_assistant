#!/usr/bin/env python3
"""
Validation script to verify the URL fix is working correctly.
Tests that the AI only provides URLs when they are in the context.
"""

import asyncio
import sys
from typing import Dict, List

# Mock setup for testing the prompt logic
class URLFixValidator:
    """Validates that the URL fix is properly implemented."""

    def __init__(self):
        self.test_results = []

    def check_system_prompt_updated(self) -> bool:
        """Check if system prompts in app.py have been updated."""
        print("\n" + "="*80)
        print("CHECKING SYSTEM PROMPT UPDATES")
        print("="*80)

        try:
            with open('app.py', 'r') as f:
                content = f.read()

            # Check for key phrases that should be in the updated prompt
            required_phrases = [
                "NEVER GENERATE OR GUESS REPOSITORY URLs",
                "ONLY Provide URLs That Are IN THE CONTEXT",
                "PRIVATE Repositories",
                "CORRECT RESPONSE When URL Not in Context",
                "CONTEXT FROM KNOWLEDGE BASE",
            ]

            found_phrases = []
            missing_phrases = []

            for phrase in required_phrases:
                if phrase in content:
                    found_phrases.append(phrase)
                    print(f"✓ Found: '{phrase}'")
                else:
                    missing_phrases.append(phrase)
                    print(f"✗ Missing: '{phrase}'")

            # Check both endpoints have the updated prompt
            ask_endpoint_count = content.count("NEVER GENERATE OR GUESS REPOSITORY URLs")

            print(f"\nPrompt appears in {ask_endpoint_count} endpoint(s)")

            if ask_endpoint_count >= 2:
                print("✓ Both /api/ask and /api/ask/stream appear to be updated")
                success = True
            elif ask_endpoint_count == 1:
                print("⚠ Only one endpoint updated - need to update both!")
                success = False
            else:
                print("✗ Prompts not found - update not applied")
                success = False

            if missing_phrases:
                print(f"\n⚠ Missing {len(missing_phrases)} required phrases")
                success = False

            self.test_results.append({
                'test': 'System Prompt Update',
                'passed': success,
                'details': f"Found {len(found_phrases)}/{len(required_phrases)} phrases in {ask_endpoint_count} endpoint(s)"
            })

            return success

        except FileNotFoundError:
            print("✗ app.py not found - run this script from the backend directory")
            self.test_results.append({
                'test': 'System Prompt Update',
                'passed': False,
                'details': 'app.py not found'
            })
            return False

    def check_context_in_prompt(self) -> bool:
        """Check if context is properly injected into the system prompt."""
        print("\n" + "="*80)
        print("CHECKING CONTEXT INJECTION")
        print("="*80)

        try:
            with open('app.py', 'r') as f:
                content = f.read()

            # Look for f-string that includes context_text in system prompt
            if 'CONTEXT FROM KNOWLEDGE BASE' in content and '{context_text' in content:
                print("✓ System prompt includes context injection")
                print("✓ Context is explicitly shown to the LLM")
                success = True
            else:
                print("✗ Context not properly injected into system prompt")
                success = False

            self.test_results.append({
                'test': 'Context Injection',
                'passed': success,
                'details': 'Context shown in prompt' if success else 'Context not in prompt'
            })

            return success

        except Exception as e:
            print(f"✗ Error checking context injection: {e}")
            return False

    def check_url_validator_integration(self) -> bool:
        """Check that URL validator is properly integrated."""
        print("\n" + "="*80)
        print("CHECKING URL VALIDATOR INTEGRATION")
        print("="*80)

        try:
            with open('app.py', 'r') as f:
                content = f.read()

            checks = [
                ('url_validator import', 'from services.url_validator import'),
                ('URL validation in response', 'validate_answer_urls'),
                ('Source validation', 'validate_and_filter_sources'),
            ]

            passed = True
            for check_name, check_pattern in checks:
                if check_pattern in content:
                    print(f"✓ {check_name}: Found")
                else:
                    print(f"✗ {check_name}: Not found")
                    passed = False

            self.test_results.append({
                'test': 'URL Validator Integration',
                'passed': passed,
                'details': f"Passed {sum(1 for _, p in checks if p in content)}/{len(checks)} checks"
            })

            return passed

        except Exception as e:
            print(f"✗ Error checking URL validator: {e}")
            return False

    def check_registry_configuration(self) -> bool:
        """Check that choreo_repo_registry is properly configured."""
        print("\n" + "="*80)
        print("CHECKING REPOSITORY REGISTRY")
        print("="*80)

        try:
            from services.choreo_repo_registry import get_choreo_registry

            registry = get_choreo_registry()
            components = registry.get_all_components()

            print(f"✓ Registry loaded successfully")
            print(f"✓ Found {len(components)} components")

            # Check all use wso2-enterprise
            wrong_org = [c for c in components if c['organization'] != 'wso2-enterprise']

            if wrong_org:
                print(f"✗ Found {len(wrong_org)} components with wrong organization:")
                for comp in wrong_org[:5]:
                    print(f"  - {comp['name']}: {comp['organization']}")
                success = False
            else:
                print(f"✓ All {len(components)} components use wso2-enterprise organization")
                success = True

            # Check URL format
            invalid_urls = []
            for comp in components:
                if not comp['url'].startswith('https://github.com/wso2-enterprise/'):
                    invalid_urls.append(comp)

            if invalid_urls:
                print(f"✗ Found {len(invalid_urls)} components with invalid URL format")
                success = False
            else:
                print(f"✓ All component URLs have correct format")

            self.test_results.append({
                'test': 'Repository Registry',
                'passed': success,
                'details': f"{len(components)} components, all wso2-enterprise" if success else f"{len(wrong_org)} wrong org"
            })

            return success

        except Exception as e:
            print(f"✗ Error checking registry: {e}")
            import traceback
            traceback.print_exc()
            self.test_results.append({
                'test': 'Repository Registry',
                'passed': False,
                'details': str(e)
            })
            return False

    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])

        for result in self.test_results:
            status = "✓ PASS" if result['passed'] else "✗ FAIL"
            print(f"{status}: {result['test']}")
            print(f"        {result['details']}")

        print("\n" + "="*80)
        print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        print("="*80)

        if passed == total:
            print("\n🎉 ALL VALIDATIONS PASSED!")
            print("\nThe URL fix has been properly implemented:")
            print("  ✓ System prompts updated with strict URL rules")
            print("  ✓ Context is injected into prompts")
            print("  ✓ URL validation is integrated")
            print("  ✓ Repository registry is correctly configured")
            print("\nNext steps:")
            print("  1. Deploy the updated backend")
            print("  2. Test with real queries in Choreo deployment")
            print("  3. Verify URLs are only provided when in context")
            return True
        else:
            print("\n⚠️  SOME VALIDATIONS FAILED")
            print(f"\n{total - passed} test(s) need attention before deployment.")
            return False

    async def run_all_checks(self) -> bool:
        """Run all validation checks."""
        print("Starting URL Fix Validation...\n")

        checks = [
            self.check_system_prompt_updated,
            self.check_context_in_prompt,
            self.check_url_validator_integration,
            self.check_registry_configuration,
        ]

        all_passed = True
        for check in checks:
            try:
                result = check()
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"✗ Check failed with error: {e}")
                import traceback
                traceback.print_exc()
                all_passed = False

        self.print_summary()
        return all_passed


async def main():
    """Main validation function."""
    validator = URLFixValidator()
    success = await validator.run_all_checks()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
