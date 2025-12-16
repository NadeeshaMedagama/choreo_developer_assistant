# ✅ CORRECTED: Choreo Repository URLs - Separate Repositories

## 🎯 Final Clarification

Each Choreo component has its **OWN SEPARATE REPOSITORY** - there is **NO monorepo** called "choreo-iam".

---

## ✅ CORRECT URL Format

```
https://github.com/wso2/choreo-{component-name}
```

### Examples:
- `https://github.com/wso2/choreo-console` ✅
- `https://github.com/wso2/choreo-runtime` ✅
- `https://github.com/wso2/choreo-telemetry` ✅

---

## ❌ INCORRECT Formats (DO NOT USE)

```
❌ https://github.com/wso2/choreo-iam/tree/main/choreo-console
❌ https://github.com/wso2/choreo-iam/choreo-console
❌ https://github.com/wso2-enterprise/choreo-console (use wso2, not wso2-enterprise)
```

**There is NO "choreo-iam" monorepo!**

---

## 🧪 Test Results

```bash
$ python3 test_separate_repos.py

✓ ALL TESTS PASSED

Summary:
  ✓ All 32 components use SEPARATE repository format
  ✓ URLs: github.com/wso2/choreo-{component}
  ✓ NO monorepo or choreo-iam references
  ✓ wso2-enterprise converted to wso2
```

---

## 📋 All 32 Choreo Components

Each has its own repository in the wso2 organization:

1. https://github.com/wso2/choreo-console
2. https://github.com/wso2/choreo-runtime
3. https://github.com/wso2/choreo-telemetry
4. https://github.com/wso2/choreo-obsapi
5. https://github.com/wso2/choreo-linker
6. https://github.com/wso2/choreo-negotiator
7. https://github.com/wso2/choreo-apim
8. https://github.com/wso2/choreo-logging
9. https://github.com/wso2/choreo-email
10. https://github.com/wso2/choreo-testbase
11. https://github.com/wso2/choreo-lang-server
12. https://github.com/wso2/choreo-ai-performance-analyzer
13. https://github.com/wso2/choreo-ai-anomaly-detector
14. https://github.com/wso2/choreo-ai-program-analyzer
15. https://github.com/wso2/choreo-ai-deployment-optimizer
16. https://github.com/wso2/choreo-ai-data-mapper
17. https://github.com/wso2/choreo-ai-capacity-planner
18. https://github.com/wso2/choreo-analytics-apim
19. https://github.com/wso2/choreo-apim-devportal
20. https://github.com/wso2/choreo-sys-obsapi
21. https://github.com/wso2/choreo
22. https://github.com/wso2/choreo-control-plane
23. https://github.com/wso2/choreo-observability
24. https://github.com/wso2/choreo-ci-tools
25. https://github.com/wso2/choreo-www
26. https://github.com/wso2/choreo-common-pipeline-templates
27. https://github.com/wso2/choreo-performance
28. https://github.com/wso2/choreo-idp
29. https://github.com/wso2/choreo-deployment
30. https://github.com/wso2/choreo-default-backend
31. https://github.com/wso2/choreo-ai-data-mapper-vscode-plugin
32. https://github.com/wso2/ballerina-registry-control-plane

---

## 🚀 What the System Does Now

1. **Registry**: Contains 32 components, each with its own repo URL
2. **Validation**: Checks if URLs exist and are accessible
3. **Fixing**: Converts wso2-enterprise → wso2
4. **System Prompts**: Guide LLM to use correct separate repo format

---

## 📝 Key Points

✅ **Each component = Separate repository**
✅ **Organization = wso2 (not wso2-enterprise)**
✅ **Format = github.com/wso2/choreo-{component}**
❌ **NO monorepo**
❌ **NO choreo-iam**
❌ **NO /tree/main/ paths**

---

## 🎉 Status: FIXED AND TESTED

The AI assistant will now provide correct URLs in this format:
```
https://github.com/wso2/choreo-{component-name}
```

Run `python3 test_separate_repos.py` to verify!

