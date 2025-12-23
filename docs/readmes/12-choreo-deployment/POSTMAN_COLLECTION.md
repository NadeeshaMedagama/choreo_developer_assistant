# 📮 Postman Collection - Choreo AI Assistant Backend

## 🏥 Health Check Endpoints

### **1. Root Health Check** ✅
```
GET {{BASE_URL}}/
```

**Response (200 OK):**
```json
{
  "message": "Choreo AI Assistant (Azure LLM + Milvus) is running.",
  "status": "ok"
}
```

---

### **2. Detailed Health Check**
```
GET {{BASE_URL}}/api/health
```

**Response (200 OK):**
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

---

## 🌐 Environment Variables

Create these environments in Postman:

### **Local Development:**
```
BASE_URL = http://localhost:9090
```

### **Choreo Production:**
```
BASE_URL = https://your-app-name.choreoapis.dev
```

---

## 📋 Full API Endpoints

### **Health & Status:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root health check |
| GET | `/api/health` | Detailed health check |

### **Main API:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ask` | Ask AI question |
| POST | `/api/webhook/github` | GitHub webhook handler |

---

## 📝 Example Requests

### **1. Health Check (Simple)**
```http
GET {{BASE_URL}}/
```

**No headers required**

---

### **2. Health Check (Detailed)**
```http
GET {{BASE_URL}}/api/health
```

**No headers required**

---

### **3. Ask Question**
```http
POST {{BASE_URL}}/ask
Content-Type: application/json

{
  "question": "What is Choreo?",
  "conversation_history": [],
  "max_history_tokens": 4000,
  "enable_summarization": true
}
```

**Headers:**
- `Content-Type: application/json`

**Body (raw JSON):**
```json
{
  "question": "What is Choreo?"
}
```

**Response (200 OK):**
```json
{
  "answer": "Choreo is a cloud-native platform...",
  "sources": [
    {
      "content": "...",
      "metadata": {...}
    }
  ],
  "conversation_id": "uuid-here"
}
```

---

## 🚀 Quick Test Steps

### **After Local Startup:**

1. Start backend: `cd backend && python3 start.py`
2. Open Postman
3. Send: `GET http://localhost:9090/`
4. Verify: Response shows `"status": "ok"`

### **After Choreo Deployment:**

1. Get your Choreo URL from dashboard
2. Update Postman environment variable
3. Send: `GET {{BASE_URL}}/`
4. Verify: Response shows `"status": "ok"`

---

## ✅ Expected Responses

### **Success:**
- Status Code: `200 OK`
- Response contains: `"status": "ok"` or `"status": "healthy"`

### **Service Starting:**
- Status Code: `503 Service Unavailable` (wait 90 seconds)
- Retry after initial delay

### **Error:**
- Status Code: `500 Internal Server Error`
- Check logs in Choreo dashboard

---

## 📊 Postman Collection Structure

```
Choreo AI Assistant
├── 📁 Health Checks
│   ├── GET / (Root)
│   └── GET /api/health (Detailed)
│
└── 📁 API Endpoints
    └── POST /ask (Ask Question)
```

---

## 🔧 Import to Postman

### **Option 1: Manual Setup**

1. Create new collection: "Choreo AI Assistant"
2. Add environment variables
3. Create requests as shown above

### **Option 2: Collection JSON**

```json
{
  "info": {
    "name": "Choreo AI Assistant",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Root Health Check",
      "request": {
        "method": "GET",
        "url": "{{BASE_URL}}/"
      }
    },
    {
      "name": "Detailed Health Check",
      "request": {
        "method": "GET",
        "url": "{{BASE_URL}}/api/health"
      }
    },
    {
      "name": "Ask Question",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"question\": \"What is Choreo?\"\n}"
        },
        "url": "{{BASE_URL}}/ask"
      }
    }
  ]
}
```

---

**Created:** December 22, 2025  
**Health Check URL:** `/`  
**Base URL (Local):** `http://localhost:9090`  
**Base URL (Choreo):** `https://your-app.choreoapis.dev`

