# OpenAPI Specification for Choreo Deployment

## Overview

The `openapi.yaml` file in the `.choreo/` directory defines the API contract for the Choreo AI Assistant backend service.

## What is OpenAPI?

OpenAPI Specification (formerly Swagger) is a standard way to describe REST APIs. It provides:
- **API Documentation** - Human and machine-readable API docs
- **Client Generation** - Auto-generate client SDKs
- **Server Validation** - Validate requests/responses
- **API Testing** - Test tools can use the spec
- **Choreo Integration** - Choreo uses it for API management

## Files Created

```
.choreo/
├── component.yaml    # Choreo component configuration
└── openapi.yaml      # API specification (NEW!)
```

## What's Defined in openapi.yaml

### 1. API Information
- **Title**: Choreo AI Assistant API
- **Version**: 1.0.0
- **Description**: RAG-based AI assistant for Choreo documentation

### 2. Servers
- **Production**: `https://your-component-url.choreo.dev`
- **Development**: `http://localhost:9090`

### 3. Endpoints Documented

#### Health Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Root/welcome message |
| `/health` | GET | Health check (legacy) |
| `/api/health` | GET | Health check with Milvus status |

#### Query Endpoints (AI Q&A)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ask` | POST | Ask question (standard RAG) |
| `/ask` | POST | Ask question (legacy) |
| `/api/ask_graph` | POST | Ask question (LangGraph RAG) |
| `/ask_graph` | POST | Ask question (legacy LangGraph) |

#### Ingestion Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ingest/github` | POST | Ingest single GitHub repo |
| `/api/ingest/github/with-images` | POST | Ingest repo with image processing |
| `/api/ingest/org` | POST | Bulk ingest organization repos |
| `/ingest/github` | POST | Ingest repo (legacy) |

#### Webhook Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/webhook/github` | POST | GitHub webhook handler |

### 4. Request/Response Schemas

All endpoints have detailed schemas defining:
- **Parameters** - Query params, path params, request bodies
- **Responses** - Success and error responses
- **Examples** - Real-world usage examples

## How Choreo Uses openapi.yaml

### 1. API Management
- Choreo reads the OpenAPI spec to understand your API
- Creates API documentation automatically
- Enables API gateway features

### 2. Developer Portal
- Generates interactive API documentation
- Provides "Try it out" functionality
- Shows request/response examples

### 3. API Governance
- Validates API design
- Enforces naming conventions
- Tracks API versions

### 4. Client Generation
- Developers can generate client SDKs
- Supports multiple languages
- Auto-updated when spec changes

## Testing the OpenAPI Spec

### Option 1: Swagger UI (Local)

```bash
# Install swagger-ui
npm install -g swagger-ui-watcher

# View the spec
swagger-ui-watcher .choreo/openapi.yaml
```

Then open: http://localhost:8000

### Option 2: Swagger Editor Online

1. Go to https://editor.swagger.io/
2. Copy contents of `openapi.yaml`
3. Paste into editor
4. View rendered documentation

### Option 3: VS Code Extension

Install the **OpenAPI (Swagger) Editor** extension:
```bash
code --install-extension 42Crunch.vscode-openapi
```

Then open `openapi.yaml` in VS Code for syntax highlighting and validation.

## Validating the Spec

### Check for Errors

```bash
# Install validator
npm install -g @apidevtools/swagger-cli

# Validate the spec
swagger-cli validate .choreo/openapi.yaml
```

Expected output:
```
.choreo/openapi.yaml is valid
```

## Example API Usage

### 1. Health Check

```bash
curl https://your-component-url.choreo.dev/api/health
```

Response:
```json
{
  "status": "healthy",
  "milvus": "connected"
}
```

### 2. Ask a Question

```bash
curl -X POST "https://your-component-url.choreo.dev/api/ask?question=What%20is%20Choreo%3F"
```

Response:
```json
{
  "answer": "Choreo is an internal developer platform...",
  "context_count": 5
}
```

### 3. Ingest Repository

```bash
curl -X POST "https://your-component-url.choreo.dev/api/ingest/github?repo_url=https://github.com/wso2/docs-choreo-dev.git&branch=main"
```

Response:
```json
{
  "repo_url": "https://github.com/wso2/docs-choreo-dev.git",
  "branch": "main",
  "status": "completed",
  "files_processed": 42,
  "chunks_created": 315,
  "embeddings_stored": 315
}
```

## Customizing the Spec

### Adding a New Endpoint

1. **Define the path** in `paths:` section:
```yaml
paths:
  /api/my-new-endpoint:
    post:
      summary: My new endpoint
      description: Does something cool
      tags:
        - Custom
      # ... rest of definition
```

2. **Add request/response schemas** in `components:`:
```yaml
components:
  schemas:
    MyNewResponse:
      type: object
      properties:
        result:
          type: string
```

3. **Update component.yaml** if needed (already configured):
```yaml
endpoints:
  - name: api
    schemaFilePath: openapi.yaml  # Already set!
```

### Versioning the API

When you make breaking changes:

1. Update version in `openapi.yaml`:
```yaml
info:
  version: 2.0.0  # Increment major version
```

2. Consider creating a new file:
```
.choreo/
├── openapi-v1.yaml
└── openapi-v2.yaml
```

## Choreo Deployment

### What Happens During Deployment

1. **Choreo reads** `.choreo/component.yaml`
2. **Finds** `schemaFilePath: openapi.yaml`
3. **Loads** the OpenAPI specification
4. **Validates** the spec
5. **Creates** API documentation
6. **Publishes** to developer portal

### Viewing in Choreo Console

After deployment:

1. Go to Choreo Console → Your Component
2. Navigate to **API Management** section
3. See auto-generated documentation
4. Test APIs directly in browser

## Best Practices

### 1. Keep Spec Updated
- Update `openapi.yaml` when adding new endpoints
- Keep descriptions accurate
- Update examples with real data

### 2. Use Tags for Organization
```yaml
tags:
  - name: Health
  - name: Query
  - name: Ingestion
  - name: Webhooks
```

### 3. Provide Examples
```yaml
examples:
  success:
    value:
      answer: "Choreo is..."
      context_count: 5
```

### 4. Document Error Responses
```yaml
responses:
  '200':
    description: Success
  '400':
    description: Bad request
  '500':
    description: Server error
```

### 5. Version Your API
```yaml
info:
  version: 1.0.0  # Use semantic versioning
```

## Troubleshooting

### Issue: "Invalid OpenAPI specification"

**Solution**: Validate the spec:
```bash
swagger-cli validate .choreo/openapi.yaml
```

### Issue: "Schema not found in Choreo"

**Solution**: Check `component.yaml`:
```yaml
endpoints:
  - name: api
    schemaFilePath: openapi.yaml  # Must be present
```

### Issue: "API documentation not showing"

**Solution**:
1. Ensure `openapi.yaml` is committed to Git
2. Redeploy the component
3. Check Choreo Console → API Management

## Additional Resources

### OpenAPI Specification
- **Official Docs**: https://swagger.io/specification/
- **Learn OpenAPI**: https://learn.openapis.org/
- **Best Practices**: https://swagger.io/resources/articles/best-practices-in-api-design/

### Tools
- **Swagger Editor**: https://editor.swagger.io/
- **Swagger UI**: https://swagger.io/tools/swagger-ui/
- **Postman**: Import OpenAPI spec for testing

### Choreo Documentation
- **API Management**: https://wso2.com/choreo/docs/api-management/
- **OpenAPI in Choreo**: Check Choreo documentation portal

## Summary

✅ **Created**: `.choreo/openapi.yaml` with complete API specification  
✅ **Updated**: `.choreo/component.yaml` to reference the spec  
✅ **Documented**: All 11 API endpoints  
✅ **Included**: Request/response schemas and examples  
✅ **Ready**: For Choreo deployment with auto-generated docs

Your API is now fully documented and ready for deployment to Choreo! 🚀

