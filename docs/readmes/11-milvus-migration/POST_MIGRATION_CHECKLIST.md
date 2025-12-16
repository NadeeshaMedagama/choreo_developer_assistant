# Post-Migration Checklist ✅

## Immediate Actions

### 1. Verify Installation
- [ ] Run `python verify_milvus_migration.py`
- [ ] Check all tests pass
- [ ] Verify Milvus collection exists

### 2. Test Backend
- [ ] Start backend: `cd backend && uvicorn app:app --reload`
- [ ] Check health endpoint: `curl http://localhost:8000/api/health`
- [ ] Verify Milvus connection in health response

### 3. Test Frontend
- [ ] Start frontend: `cd frontend && npm run dev`
- [ ] Open http://localhost:5173
- [ ] Test chat interface

### 4. Test Data Ingestion
- [ ] Ingest a small test repository
- [ ] Verify data appears in Milvus Cloud console
- [ ] Check collection row count increases

### 5. Test Querying
- [ ] Ask a simple question
- [ ] Verify response includes sources
- [ ] Check streaming works (progressive text)

---

## Optional Actions

### Update Deployment Secrets (if using Kubernetes)
```bash
cd backend/k8s/scripts
./update-secrets.sh
```

### Re-ingest Existing Data
If you had data in Pinecone:
- [ ] Export data from Pinecone (manual)
- [ ] Re-run ingestion scripts for all repositories
- [ ] Verify all data is available

### Update CI/CD Pipelines
- [ ] Update environment variables in CI/CD
- [ ] Replace PINECONE_* with MILVUS_* variables
- [ ] Update deployment scripts

### Monitor Performance
- [ ] Check `/metrics` endpoint
- [ ] Monitor Milvus Cloud dashboard
- [ ] Review application logs

---

## Verification Commands

```bash
# 1. Verify migration
python verify_milvus_migration.py

# 2. Check configuration
python -c "from backend.utils.config import load_config; c = load_config(); print('Collection:', c['MILVUS_COLLECTION_NAME'])"

# 3. Test connection
cd backend
python -c "from db.vector_client import VectorClient; from utils.config import load_config; config = load_config(); vc = VectorClient(uri=config['MILVUS_URI'], token=config['MILVUS_TOKEN'], collection_name=config['MILVUS_COLLECTION_NAME']); print('✅ Connected')"

# 4. Check for Pinecone references (should be 0)
grep -r "PINECONE" backend/ --include="*.py" | wc -l
```

---

## Troubleshooting

### If something doesn't work:

1. **Check .env file**
   ```bash
   cat backend/.env | grep MILVUS
   ```

2. **Verify collection name**
   - Must use underscores: `choreo_developer_assistant`
   - Cannot use hyphens: `choreo-developer-assistant`

3. **Check dimension**
   - Should be 1536 for Azure OpenAI

4. **Review logs**
   ```bash
   tail -f backend/logs/app.log
   ```

5. **Re-run verification**
   ```bash
   python verify_milvus_migration.py
   ```

---

## Documentation Reference

- **Quick Reference:** `MILVUS_QUICK_REF.md`
- **Full Migration Details:** `MIGRATION_SUMMARY.md`
- **Migration Report:** `MILVUS_MIGRATION_COMPLETE.md`

---

## Success Criteria

✅ All verification tests pass  
✅ Backend starts without errors  
✅ Health endpoint shows Milvus connected  
✅ Can ingest data successfully  
✅ Can query and get responses  
✅ Streaming works properly  
✅ No Pinecone references in logs  

---

## Status Tracking

Mark items as completed:
- [x] Migration complete
- [x] Configuration updated
- [x] Code updated
- [x] Documentation updated
- [ ] Backend tested
- [ ] Frontend tested
- [ ] Data ingestion tested
- [ ] Queries tested
- [ ] Production deployment updated

---

**When all items are checked, your migration is complete!** 🎉

