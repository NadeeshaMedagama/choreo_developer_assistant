# Package Comparison: Failed vs Successful Build

## ❌ FAILED BUILD - Packages Being Installed

From your error log:
```
nvidia-cusparselt-cu12
nvidia-nvtx-cu12
nvidia-nvshmem-cu12
nvidia-nvjitlink-cu12
nvidia-nccl-cu12
nvidia-curand-cu12
nvidia-cufile-cu12
nvidia-cuda-runtime-cu12
nvidia-cuda-nvrtc-cu12
nvidia-cuda-cupti-cu12
nvidia-cublas-cu12
nvidia-cusparse-cu12
nvidia-cufft-cu12
nvidia-cudnn-cu12
nvidia-cusolver-cu12
triton
torch (with CUDA)
scipy
scikit-learn
transformers
sentence-transformers
langgraph
langgraph-checkpoint
langgraph-prebuilt
langgraph-sdk
langchain
langchain-classic
langchain-community
langchain-core
langchain-text-splitters
langchain-openai
google-cloud-vision
```

**Total Size**: ~8-10 GB  
**Result**: ❌ No space left on device

---

## ✅ SUCCESSFUL BUILD - Packages Installed

From the successful build log:
```
annotated-types
anyio
argon2-cffi
argon2-cffi-bindings
certifi
cffi
charset-normalizer
click
distro
environs
fastapi
grpcio
h11
httpcore
httpx
idna
marshmallow
minio
numpy (minimal version)
openai
pandas (minimal version)
prometheus-client
protobuf
psutil
pyarrow
pycparser
pycryptodome
pydantic
pydantic-core
pydantic-settings
pymilvus
python-dateutil
python-dotenv
pytz
requests
six
sniffio
starlette
tqdm
typing-extensions
tzdata
ujson
urllib3
uvicorn
```

**Total Size**: ~300-500 MB  
**Result**: ✅ Build completed successfully in 54 seconds

---

## Key Differences

### Removed (Causing Disk Space Issues)
| Package Category | Size Impact | Why Removed |
|-----------------|-------------|-------------|
| **NVIDIA CUDA libs** | ~6-7 GB | Not needed - using Azure OpenAI |
| **PyTorch** | ~800 MB | Not needed - using Azure OpenAI |
| **sentence-transformers** | ~200 MB | Using Azure OpenAI embeddings |
| **LangChain ecosystem** | ~500 MB | App has custom RAG implementation |
| **transformers** | ~400 MB | Using Azure OpenAI, not local models |
| **scipy/scikit-learn** | ~300 MB | Not used in application |
| **google-cloud-vision** | ~150 MB | Not used in application |
| **triton** | ~100 MB | GPU dependency, not needed |

**Total Saved**: ~8-10 GB

### Kept (Essential for Application)
| Package | Purpose | Size |
|---------|---------|------|
| **fastapi** | Web framework | ~10 MB |
| **uvicorn** | ASGI server | ~5 MB |
| **openai** | Azure OpenAI client | ~15 MB |
| **pymilvus** | Vector database | ~50 MB |
| **httpx** | HTTP client | ~10 MB |
| **prometheus-client** | Monitoring | ~5 MB |
| **pydantic** | Data validation | ~10 MB |

**Total Essential**: ~300-500 MB (including dependencies)

---

## Why the Original Build Failed

1. **Sentence-transformers pulled PyTorch**
   - PyTorch defaults to CUDA version
   - CUDA version includes 15+ NVIDIA libraries
   - Each NVIDIA library is 200-500 MB

2. **LangChain pulled many dependencies**
   - langchain-community pulled transformers
   - transformers pulled torch
   - Circular dependency hell

3. **Buildpack disk space limit**
   - Google Cloud Buildpacks have ~10 GB limit
   - CUDA packages alone exceed this
   - No room left for actual build

---

## Why the New Build Succeeds

1. **No local ML models**
   - Everything uses Azure OpenAI API
   - No PyTorch, no CUDA, no transformers

2. **Minimal dependencies**
   - Only what's actually imported by the code
   - No "nice to have" packages

3. **Within buildpack limits**
   - 300-500 MB is well under limits
   - Leaves room for build process
   - Completes in under 60 seconds

---

## Dependency Tree Visualization

### ❌ Before (Failed)
```
requirements.txt
├── sentence-transformers
│   ├── torch (PULLS CUDA!)
│   │   ├── nvidia-cuda-runtime-cu12 (500 MB)
│   │   ├── nvidia-cudnn-cu12 (800 MB)
│   │   ├── nvidia-cublas-cu12 (400 MB)
│   │   └── ... 12 more NVIDIA packages
│   ├── transformers (400 MB)
│   ├── scipy (200 MB)
│   └── scikit-learn (100 MB)
├── langchain
│   ├── langchain-community
│   │   └── transformers (pulls torch again!)
│   └── ... many more sub-packages
└── google-cloud-vision (150 MB)

TOTAL: ~10 GB ❌
```

### ✅ After (Success)
```
requirements.txt
├── fastapi (10 MB)
│   ├── starlette
│   └── pydantic
├── openai (15 MB)
│   └── httpx
├── pymilvus (50 MB)
│   ├── grpcio
│   └── pandas (minimal)
└── prometheus-client (5 MB)

TOTAL: ~500 MB ✅
```

---

## Verification Commands

### Check no CUDA packages
```bash
docker run --rm choreo-ai-assistant:minimal pip list | grep -i cuda
# Expected: No results
```

### Check no PyTorch
```bash
docker run --rm choreo-ai-assistant:minimal pip list | grep -i torch
# Expected: No results
```

### Check essential packages present
```bash
docker run --rm choreo-ai-assistant:minimal pip list | grep -E "(fastapi|openai|pymilvus)"
# Expected: All three packages listed
```

### Check image size
```bash
docker images choreo-ai-assistant:minimal
# Expected: <1 GB
```

---

## Conclusion

The build was failing because **sentence-transformers** pulled in the **entire CUDA/PyTorch ecosystem** (~8-10 GB), which exceeded the buildpack's disk space limit.

The solution was to **use Azure OpenAI exclusively** and remove all local ML dependencies, reducing the total package size to ~500 MB - well within limits.

**Your application loses ZERO functionality** because it was already configured to use Azure OpenAI - the local model dependencies were just unused bloat.

