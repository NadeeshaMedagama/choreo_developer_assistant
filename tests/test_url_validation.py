#!/usr/bin/env python3
"""
Test script for URL Validation feature

This script demonstrates how the URL validator works by testing
various URL validation scenarios.

Usage:
    python test_url_validation.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from services.url_validator import URLValidator


async def test_url_extraction():
    """Test URL extraction from text"""
    print("=" * 60)
    print("TEST 1: URL Extraction")
    print("=" * 60)
    
    validator = URLValidator(enable_validation=False)
    
    test_cases = [
        "Visit https://console.choreo.dev for deployment",
        "Check [documentation](https://wso2.com/choreo/docs) here",
        "Mixed: https://example.com and [link](https://test.com)",
        "No URLs in this text",
    ]
    
    for i, text in enumerate(test_cases, 1):
        urls = validator.extract_urls_from_text(text)
        print(f"\nCase {i}: {text[:50]}...")
        print(f"Extracted URLs: {urls}")


async def test_url_validation():
    """Test URL validation with real URLs"""
    print("\n" + "=" * 60)
    print("TEST 2: URL Validation")
    print("=" * 60)
    
    validator = URLValidator(timeout=5, enable_validation=True)
    
    test_urls = [
        "https://wso2.com/choreo/",  # Valid
        "https://console.choreo.dev",  # Valid
        "https://github.com",  # Valid
        "https://this-url-definitely-does-not-exist-12345.com",  # Invalid
        "https://httpstat.us/404",  # 404 error
    ]
    
    print(f"\nValidating {len(test_urls)} URLs...")
    results = await validator.validate_urls(test_urls)
    
    print("\nResults:")
    for url, is_valid in results.items():
        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"  {status}: {url}")


async def test_answer_filtering():
    """Test filtering invalid URLs from answers"""
    print("\n" + "=" * 60)
    print("TEST 3: Answer Filtering")
    print("=" * 60)
    
    validator = URLValidator(timeout=5, enable_validation=True)
    
    # Answer with both valid and invalid URLs
    answer = """
To deploy to Choreo, visit https://console.choreo.dev for the console.

You can also check the documentation at https://wso2.com/choreo/docs

For older versions, see https://this-does-not-exist-404.com/old-docs
    """
    
    print("\nOriginal Answer:")
    print(answer)
    
    print("\nValidating URLs...")
    filtered_answer, validation_map = await validator.validate_answer_urls(answer)
    
    print("\nValidation Results:")
    for url, is_valid in validation_map.items():
        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"  {status}: {url}")
    
    print("\nFiltered Answer:")
    print(filtered_answer)


async def test_source_filtering():
    """Test filtering sources with invalid URLs"""
    print("\n" + "=" * 60)
    print("TEST 4: Source Filtering")
    print("=" * 60)
    
    validator = URLValidator(timeout=5, enable_validation=True)
    
    sources = [
        {
            "content": "Deployment guide...",
            "url": "https://wso2.com/choreo/docs/deploy",
            "score": 0.85,
            "repository": "choreo-docs"
        },
        {
            "content": "Console guide...",
            "url": "https://console.choreo.dev/guide",
            "score": 0.90,
            "repository": "choreo-console"
        },
        {
            "content": "Old documentation...",
            "url": "https://this-does-not-exist-404.com/docs",
            "score": 0.75,
            "repository": "old-docs"
        },
        {
            "content": "Internal notes...",
            "score": 0.70,
            "repository": "internal"
            # No URL
        }
    ]
    
    print(f"\nOriginal Sources: {len(sources)}")
    for i, source in enumerate(sources, 1):
        url = source.get('url', 'No URL')
        print(f"  {i}. {source['repository']} - {url}")
    
    print("\nValidating source URLs...")
    filtered_sources = await validator.validate_and_filter_sources(sources)
    
    print(f"\nFiltered Sources: {len(filtered_sources)}")
    for i, source in enumerate(filtered_sources, 1):
        url = source.get('url', 'No URL')
        print(f"  {i}. {source['repository']} - {url}")


async def test_markdown_links():
    """Test handling of markdown-formatted links"""
    print("\n" + "=" * 60)
    print("TEST 5: Markdown Link Handling")
    print("=" * 60)
    
    validator = URLValidator(timeout=5, enable_validation=True)
    
    answer = """
See the [deployment guide](https://wso2.com/choreo/docs/deploy) for details.

Also check the [old documentation](https://this-does-not-exist-404.com/old) (deprecated).

Visit [console](https://console.choreo.dev) to get started.
    """
    
    print("\nOriginal Answer:")
    print(answer)
    
    print("\nValidating URLs...")
    filtered_answer, validation_map = await validator.validate_answer_urls(answer)
    
    print("\nValidation Results:")
    for url, is_valid in validation_map.items():
        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"  {status}: {url}")
    
    print("\nFiltered Answer:")
    print(filtered_answer)


async def test_performance():
    """Test performance with multiple URLs"""
    print("\n" + "=" * 60)
    print("TEST 6: Performance Test")
    print("=" * 60)
    
    import time
    
    validator = URLValidator(timeout=3, max_concurrent=10, enable_validation=True)
    
    # Create a list of URLs to test concurrency
    test_urls = [
        "https://wso2.com",
        "https://github.com",
        "https://google.com",
        "https://stackoverflow.com",
        "https://python.org",
        "https://this-does-not-exist-1.com",
        "https://this-does-not-exist-2.com",
        "https://this-does-not-exist-3.com",
    ]
    
    print(f"\nValidating {len(test_urls)} URLs concurrently...")
    start_time = time.time()
    results = await validator.validate_urls(test_urls)
    duration = time.time() - start_time
    
    valid_count = sum(1 for v in results.values() if v)
    invalid_count = len(results) - valid_count
    
    print(f"\nPerformance Results:")
    print(f"  Total URLs: {len(test_urls)}")
    print(f"  Valid URLs: {valid_count}")
    print(f"  Invalid URLs: {invalid_count}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Avg per URL: {duration/len(test_urls):.3f}s")
    
    # Test cache performance
    print("\n\nTesting cache performance...")
    start_time = time.time()
    cached_results = await validator.validate_urls(test_urls)
    cached_duration = time.time() - start_time
    
    print(f"  Cached validation: {cached_duration:.3f}s")
    print(f"  Speedup: {duration/cached_duration:.1f}x faster")


async def test_disabled_validation():
    """Test with validation disabled"""
    print("\n" + "=" * 60)
    print("TEST 7: Disabled Validation")
    print("=" * 60)
    
    validator = URLValidator(enable_validation=False)
    
    answer = "Visit https://this-does-not-exist.com for info"
    
    print("\nOriginal Answer:")
    print(answer)
    
    print("\nValidation disabled - all URLs should pass through...")
    filtered_answer, validation_map = await validator.validate_answer_urls(answer)
    
    print("\nFiltered Answer (should be unchanged):")
    print(filtered_answer)
    print(f"\nValidation performed: {bool(validation_map)}")


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("URL VALIDATION TEST SUITE")
    print("=" * 60)
    
    try:
        await test_url_extraction()
        await test_url_validation()
        await test_answer_filtering()
        await test_source_filtering()
        await test_markdown_links()
        await test_performance()
        await test_disabled_validation()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

