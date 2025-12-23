# 🚀 Choreo Platform Configuration - Run Command

## ✅ Run Command for Backend

When Choreo asks for the **Run Command**, provide:

```bash
python3 start.py
```

---

## 📋 Complete Choreo Configuration

### **Build Configuration:**

| Field | Value |
|-------|-------|
| **Build Type** | Dockerfile |
| **Dockerfile Path** | `Dockerfile.minimal` |
| **Docker Context** | `.` (current directory) |

### **Runtime Configuration:**

| Field | Value |
|-------|-------|
| **Run Command** | `python3 start.py` |
| **Port** | `9090` (Choreo will override with its PORT env var) |
| **Container Port** | `9090` |

### **Health Check Configuration:**

| Field | Value |
|-------|-------|
| **Health Check Path** | `/` or `/api/health` |
| **Health Check Protocol** | HTTP |
| **Initial Delay** | 90 seconds |
| **Interval** | 30 seconds |
| **Timeout** | 30 seconds |
| **Retries** | 5 |

---

## 🏥 Health Check Endpoints

Your backend has **2 health check endpoints**:

### **1. Root Health Check (Recommended for Choreo)**
```
GET /
```

**Response:**
```json
{
  "message": "Choreo AI Assistant (Azure LLM + Milvus) is running.",
  "status": "ok"
}
```

**In Postman:**
- **Method:** `GET`
- **URL:** `http://localhost:9090/` (local) or `https://your-app.choreoapis.dev/` (Choreo)
- **Headers:** None required

---

### **2. Detailed Health Check**
```
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "checks": [
    {
      "name": "Milvus",
      "status": "healthy"
    },
    {
      "name": "Application",
      "status": "healthy"
    }
  ],
  "services_initialized": true
}
```

**In Postman:**
- **Method:** `GET`
- **URL:** `http://localhost:9090/api/health` (local) or `https://your-app.choreoapis.dev/api/health` (Choreo)
- **Headers:** None required

---

## 🔧 How It Works

### **The start.py Script:**

```python
# Reads PORT from environment variable (Choreo provides this)
port = os.environ.get('PORT', '9090')

# Starts uvicorn with dynamic port
uvicorn app:app --host 0.0.0.0 --port {PORT}
```

**Key Features:**
- ✅ Automatically reads `PORT` environment variable from Choreo
- ✅ Binds to `0.0.0.0` to accept external connections
- ✅ Falls back to port `9090` if PORT not set (for local development)
- ✅ Starts uvicorn server with your FastAPI app

---

## 📊 Testing in Postman

### **Collection Setup:**

**Environment Variables:**
```
BASE_URL_LOCAL = http://localhost:9090
BASE_URL_CHOREO = https://your-app.choreoapis.dev
```

### **Request 1: Root Health Check**
```
GET {{BASE_URL}}/
```

**Expected Response (200 OK):**
```json
{
  "message": "Choreo AI Assistant (Azure LLM + Milvus) is running.",
  "status": "ok"
}
```

### **Request 2: Detailed Health Check**
```
GET {{BASE_URL}}/api/health
```

**Expected Response (200 OK):**
```json
{
  "status": "healthy",
  "checks": [...],
  "services_initialized": true
}
```

### **Request 3: Ask Question (Main API)**
```
POST {{BASE_URL}}/ask
Content-Type: application/json

{
  "question": "What is Choreo?"
}
```

**Expected Response (200 OK):**
```json
{
  "answer": "Choreo is...",
  "sources": [...],
  "conversation_id": "..."
}
```

---

## ⚙️ Choreo Platform Settings

### **In Choreo Dashboard:**

1. **Component Type:** Service
2. **Implementation:** Dockerfile
3. **Dockerfile Path:** `Dockerfile.minimal`
4. **Run Command:** `python3 start.py` ✅
5. **Port:** 9090 (or leave auto-detect)
6. **Health Check Endpoint:** `/` ✅
7. **Health Check Protocol:** HTTP
8. **Initial Delay Seconds:** 90
9. **Period Seconds:** 30
10. **Timeout Seconds:** 30
11. **Success Threshold:** 1
12. **Failure Threshold:** 5

---

## 🔍 Verification Steps

### **After Deployment:**

1. **Check Deployment Logs:**
   ```
   Starting Choreo AI Assistant Backend on port 8080...
   Binding to 0.0.0.0:8080
   Command: uvicorn app:app --host 0.0.0.0 --port 8080
   ```

2. **Test Health Endpoint:**
   ```bash
   curl https://your-app.choreoapis.dev/
   ```

3. **Test in Postman:**
   - Import the health check endpoint
   - Send GET request
   - Verify 200 OK response

---

## 🚨 Common Issues

### **Issue 1: Port Binding Error**
**Symptom:** Container fails to start
**Solution:** Make sure Run Command is `python3 start.py` (not `uvicorn app:app`)

### **Issue 2: Health Check Failing**
**Symptom:** Deployment shows unhealthy
**Solution:** 
- Verify health check path is `/` or `/api/health`
- Increase initial delay to 90 seconds (services need time to initialize)

### **Issue 3: 404 Not Found**
**Symptom:** Health check returns 404
**Solution:**
- Check that `app.py` has `@app.get("/")` endpoint
- Verify Dockerfile copies all files correctly

---

## ✅ Quick Reference

**Run Command:** `python3 start.py`  
**Health Check:** `/`  
**Port:** Auto-detected from Choreo's PORT env var  
**Protocol:** HTTP  

---

## 📖 Related Files

- `backend/start.py` - Startup script (reads PORT and starts uvicorn)
- `backend/app.py` - FastAPI application with health endpoints
- `backend/Dockerfile.minimal` - Docker configuration (CMD = python3 start.py)
- `backend/.choreo/component.yaml` - Choreo component configuration

---

**Date:** December 22, 2025  
**Status:** ✅ Configuration ready for Choreo deployment

