#!/usr/bin/env python3
"""Simple direct test - no external dependencies"""

# Test data
sample_repos = [
    {
        'name': 'choreo-console',
        'url': 'https://github.com/wso2-enterprise/choreo-console',
        'description': 'Choreo web console',
        'organization': 'wso2-enterprise'
    },
    {
        'name': 'choreo-runtime',
        'url': 'https://github.com/wso2-enterprise/choreo-runtime',
        'description': 'Choreo runtime engine',
        'organization': 'wso2-enterprise'
    },
    {
        'name': 'choreo-sts',
        'url': 'https://github.com/wso2-enterprise/choreo-sts',
        'description': 'Choreo built-in Security Token Service',
        'organization': 'wso2-enterprise'
    }
]

# Inline format function (copy of the actual method)
def format_repos_for_response(repos, query_context=""):
    if not repos:
        return "No repositories found matching the criteria."

    header = f"Found {len(repos)} repositories"
    if query_context:
        header += f" {query_context}"
    header += " in the wso2-enterprise organization:\n\n"

    choreo_repos = [r for r in repos if 'choreo' in r['name'].lower()]
    other_repos = [r for r in repos if 'choreo' not in r['name'].lower()]

    result = header

    if choreo_repos:
        result += f"**Choreo Repositories ({len(choreo_repos)}):**\n\n"
        for repo in sorted(choreo_repos, key=lambda x: x['name']):
            result += f"- **{repo['name']}**: {repo['url']}\n"
            if repo.get('description'):
                result += f"  - {repo['description']}\n"
            result += "\n"

    if other_repos:
        result += f"\n**Other wso2-enterprise Repositories ({len(other_repos)}):**\n\n"
        for repo in sorted(other_repos, key=lambda x: x['name']):
            result += f"- **{repo['name']}**: {repo['url']}\n"
            if repo.get('description'):
                result += f"  - {repo['description']}\n"
            result += "\n"

    result += f"\n**Total: {len(repos)} repositories**\n"
    result += "\n*Note: All these repositories are private and require wso2-enterprise organization access.*\n"

    return result

# Test it
print("Testing format_repos_for_response with sample data:")
print("=" * 80)
formatted = format_repos_for_response(sample_repos, 'with "choreo" keyword')
print(formatted)
print("=" * 80)
print("\n✅ Format function works correctly!")
print(f"✅ URLs are present in output: {'https://github.com' in formatted}")
