# Visual Example: Document Sources Feature

## 🎨 What It Looks Like

### Before (Old Version)
```
┌─────────────────────────────────────────────────┐
│ 👤 User                                          │
│ How do I deploy a service in Choreo?            │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 🤖 DevChoreo                                     │
│                                                  │
│ To deploy a service in Choreo, follow these     │
│ steps:                                           │
│                                                  │
│ 1. Create a new component...                    │
│ 2. Configure your deployment...                 │
│ 3. Click Deploy...                              │
│                                                  │
│ [Copy] [👍] [👎] [Share] [↻]                    │
└─────────────────────────────────────────────────┘
```

### After (New Version with Sources)
```
┌─────────────────────────────────────────────────┐
│ 👤 User                                          │
│ How do I deploy a service in Choreo?            │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ 🤖 DevChoreo                                     │
│                                                  │
│ To deploy a service in Choreo, follow these     │
│ steps:                                           │
│                                                  │
│ 1. Create a new component...                    │
│ 2. Configure your deployment...                 │
│ 3. Click Deploy...                              │
│                                                  │
│ [Copy] [👍] [👎] [Share] [↻]                    │
│                                                  │
│ ────────────────────────────────────────────────│
│ 🔽 Sources (3)                                  │
│                                                  │
│ ┌───────────────────────────────────────────┐   │
│ │ 📄 Deployment Guide                        │   │
│ │    Repository: wso2/docs-choreo-dev        │   │
│ │    Type: markdown                          │   │
│ │                                            │   │
│ │    "This comprehensive guide explains      │   │
│ │    how to deploy services in Choreo..."    │   │
│ │                                            │   │
│ │    View source ↗                           │   │
│ │    Relevance: 94.2%                        │   │
│ └───────────────────────────────────────────┘   │
│                                                  │
│ ┌───────────────────────────────────────────┐   │
│ │ 📄 Deploy API Reference                    │   │
│ │    Repository: wso2/choreo-api             │   │
│ │    Type: code                              │   │
│ │                                            │   │
│ │    "POST /api/v1/deploy - Deploys a        │   │
│ │    component to the specified environment" │   │
│ │                                            │   │
│ │    View source ↗                           │   │
│ │    Relevance: 87.5%                        │   │
│ └───────────────────────────────────────────┘   │
│                                                  │
│ ┌───────────────────────────────────────────┐   │
│ │ 📄 examples/deployment/basic-service.yaml  │   │
│ │    Repository: wso2/choreo-examples        │   │
│ │    Type: yaml                              │   │
│ │                                            │   │
│ │    "name: my-service\ndeploy:\n            │   │
│ │    environment: production..."             │   │
│ │                                            │   │
│ │    View source ↗                           │   │
│ │    Relevance: 82.1%                        │   │
│ └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## 🔄 Interactive States

### Collapsed State (Click to Show)
```
────────────────────────────────────────
🔼 Sources (3)
```

### Expanded State (Default)
```
────────────────────────────────────────
🔽 Sources (3)

[Source cards displayed as shown above]
```

## 🎨 Theme Support

### Light Mode
- Background: `bg-gray-50`
- Border: `border-gray-200`
- Text: `text-gray-900`
- Links: `text-blue-600`

### Dark Mode
- Background: `bg-gray-700/50`
- Border: `border-gray-600`
- Text: `text-gray-100`
- Links: `text-blue-400`

## 📱 Responsive Design

The sources section adapts to different screen sizes:
- Mobile: Stacked cards, full width
- Tablet: Same layout, better spacing
- Desktop: Optimal reading width (max-w-3xl)

## ✨ User Interactions

1. **Click source title/filename** → Shows full information
2. **Click "View source ↗"** → Opens URL in new tab
3. **Hover over cards** → Subtle highlight effect
4. **Click "Sources (3)"** → Toggle expand/collapse

## 🔍 Information Hierarchy

Each source card shows (in order):
1. **Title** (bold, prominent)
2. **Repository** (smaller, gray)
3. **Type** (smaller, gray)
4. **Content Preview** (italics, even smaller)
5. **Link** (blue, underlined on hover)
6. **Relevance** (smallest, gray)

## 💡 Smart Features

- **Auto-truncation**: Content previews are limited to ~200 chars
- **Fallback titles**: Uses file_path if no title provided
- **Conditional rendering**: Only shows fields that exist
- **Link safety**: All external links use `rel="noopener noreferrer"`
- **Score formatting**: Converts 0.89 → "89.0%"

## 🎯 Real-World Examples

### Example 1: Code Documentation
```
📄 ComponentAPI.ts
   Repository: wso2/choreo-sdk
   Type: typescript
   
   "export class ComponentAPI { constructor(config: Config) { ... "
   
   View source ↗
   Relevance: 91.3%
```

### Example 2: GitHub Issue
```
📄 Error when deploying webhook service
   Repository: wso2/choreo-platform
   Type: issue
   
   "Users are experiencing timeout errors when deploying webhook..."
   
   View source ↗
   Relevance: 88.7%
```

### Example 3: Markdown Documentation
```
📄 Webhook Configuration Guide
   Repository: wso2/docs-choreo-dev
   Type: markdown
   
   "## Configuring Webhooks\n\nWebhooks allow you to receive..."
   
   View source ↗
   Relevance: 95.1%
```

## 🚀 Benefits Illustrated

### For Users
- ✅ See exactly which documents were used
- ✅ Verify information from original sources
- ✅ Explore related documentation
- ✅ Build trust in AI responses

### For Developers
- ✅ Debug which documents are being retrieved
- ✅ Improve document quality based on usage
- ✅ Identify gaps in documentation
- ✅ Monitor relevance scores

