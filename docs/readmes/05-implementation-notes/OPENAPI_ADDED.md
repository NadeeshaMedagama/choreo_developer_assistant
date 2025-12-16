# OpenAPI Specification Added ✅

## What Was Created

**New files in `.choreo/` directory:**

1. **`.choreo/openapi.yaml`** - Complete OpenAPI 3.0 specification
2. **`.choreo/README.md`** - OpenAPI documentation and usage guide
3. **`.choreo/component.yaml`** - Updated to reference openapi.yaml

## OpenAPI Specification Highlights

### Documented Endpoints (11 total)

#### Health & Status
- `GET /` - Root endpoint
- `GET /health` - Health check (legacy)
- `GET /api/health` - Health check with Pinecone status

#### AI Query Endpoints
- `POST /api/ask` - Ask question (standard RAG)
- `POST /ask` - Ask question (legacy)
- `POST /api/ask_graph` - Ask question (LangGraph RAG)
- `POST /ask_graph` - Ask question (legacy)

#### Data Ingestion
- `POST /api/ingest/github` - Ingest single repository
- `POST /api/ingest/github/with-images` - Ingest with image processing
- `POST /api/ingest/org` - Bulk ingest organization repos
- `POST /ingest/github` - Ingest repo (legacy)

#### Webhooks
- `POST /api/webhook/github` - GitHub webhook handler

### Features Included

✅ **Complete Request/Response Schemas**
- All parameters documented
- Request body schemas
- Response models with examples

✅ **Tags for Organization**
- Health
- Query
- Ingestion  
- Webhooks

✅ **Examples for Every Endpoint**
- Real-world request examples
- Sample responses
- Error scenarios

✅ **Server Definitions**
- Production: `https://your-component-url.choreo.dev`
- Development: `http://localhost:9090`

## How to Use

### View the Specification

```bash
# Using Swagger UI (install first)
npm install -g swagger-ui-watcher
swagger-ui-watcher .choreo/openapi.yaml
```

### Validate the Spec

```bash
# Install validator
npm install -g @apidevtools/swagger-cli

# Validate
swagger-cli validate .choreo/openapi.yaml
```

### In Choreo Console

After deployment:
1. Go to your component in Choreo Console
2. Navigate to **API Management**
3. See auto-generated interactive documentation
4. Test APIs directly in browser

## Benefits for Choreo Deployment

### 1. Auto-Generated Documentation
Choreo reads `openapi.yaml` and creates:
- Interactive API documentation
- "Try it out" functionality
- Code examples in multiple languages

### 2. API Management
- API gateway integration
- Rate limiting
- Access control
- Analytics

### 3. Developer Portal
- Public API documentation
- Client SDK generation
- API versioning

### 4. Testing & Validation
- Request/response validation
- API testing tools
- Mock server generation

## Example API Calls

### Health Check
```bash
curl https://your-component-url.choreo.dev/api/health
```

Response:
```json
{
  "status": "healthy",
  "pinecone": "connected"
}
```

### Ask a Question
```bash
curl -X POST "https://your-component-url.choreo.dev/api/ask?question=What%20is%20Choreo%3F"
```

Response:
```json
{
  "answer": "Choreo is an internal developer platform that enables developers to build, deploy, and manage cloud-native applications with ease.",
  "context_count": 5
}
```

### Ingest Organization Repos
```bash
curl -X POST "https://your-component-url.choreo.dev/api/ingest/org?org=wso2-enterprise&keyword=choreo&max_repos=5"
```

Response:
```json
{
  "status": "completed",
  "total_repos": 5,
  "processed_repos": 5,
  "total_files": 234,
  "total_chunks": 1567,
  "total_embeddings": 1567,
  "duration_seconds": 180.5
}
```

## File Structure

```
.choreo/
├── component.yaml      # Choreo component configuration
│                       # - References openapi.yaml for API spec
├── openapi.yaml        # OpenAPI 3.0 specification
│                       # - Complete API documentation
│                       # - Request/response schemas
│                       # - Examples for all endpoints
└── README.md           # OpenAPI usage guide
                        # - How to view/validate spec
                        # - Choreo integration details
                        # - Best practices
```

## Configuration in component.yaml

The `component.yaml` now includes:

```yaml
endpoints:
  - name: api
    port: 9090
    type: REST
    networkVisibility: public
    context: /
    schemaFilePath: openapi.yaml  # ← References OpenAPI spec
```

This tells Choreo:
1. Load the OpenAPI specification
2. Generate API documentation
3. Enable API management features
4. Validate requests against schema

## Next Steps

### 1. Commit to Git
```bash
git add .choreo/
git commit -m "Add OpenAPI specification for Choreo deployment"
git push origin main
```

### 2. Deploy to Choreo
When you deploy, Choreo will:
- ✅ Read `component.yaml`
- ✅ Load `openapi.yaml`
- ✅ Generate API documentation
- ✅ Enable API management
- ✅ Create developer portal

### 3. View Documentation
After deployment:
- Go to Choreo Console → Your Component → API Management
- See interactive API documentation
- Test endpoints directly in browser

### 4. Share API Docs
- API documentation is automatically public
- Developers can generate client SDKs
- OpenAPI spec can be exported

## Troubleshooting

### Validate Locally
```bash
# Check for syntax errors
swagger-cli validate .choreo/openapi.yaml

# Expected output:
# .choreo/openapi.yaml is valid
```

### View Locally
```bash
# Option 1: Swagger UI
swagger-ui-watcher .choreo/openapi.yaml

# Option 2: Online editor
# Go to https://editor.swagger.io/
# Copy/paste openapi.yaml content
```

### Common Issues

**Issue**: "Schema file not found"  
**Fix**: Ensure `openapi.yaml` is in `.choreo/` directory

**Issue**: "Invalid OpenAPI specification"  
**Fix**: Run `swagger-cli validate .choreo/openapi.yaml`

**Issue**: "API docs not showing in Choreo"  
**Fix**: Redeploy the component after committing openapi.yaml

## Documentation

For detailed information, see:
- **`.choreo/README.md`** - Complete OpenAPI guide
- **`.choreo/openapi.yaml`** - The specification itself
- **`.choreo/component.yaml`** - Choreo configuration

## Summary

✅ **Created** comprehensive OpenAPI 3.0 specification  
✅ **Documented** all 11 API endpoints  
✅ **Included** request/response schemas  
✅ **Added** examples for every endpoint  
✅ **Updated** component.yaml to reference spec  
✅ **Ready** for Choreo deployment with auto-docs

Your API is now fully documented and ready for Choreo! 🚀

