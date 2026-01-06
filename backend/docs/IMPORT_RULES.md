# Import Rules Quick Reference

## ✅ DO - Use These Import Patterns

```python
# Top-level packages - use absolute imports
from services.llm_service import LLMService
from services.github_service import GitHubService
from services.context_manager import ContextManager
from db.vector_client import VectorClient
from utils.logger import get_logger
from utils.config import Config, load_config
from monitoring import get_monitoring_service
```

## ❌ DON'T - Avoid These Patterns

```python
# ❌ NO relative imports with .. in top-level packages
from ..utils.logger import get_logger           # BREAKS in Choreo
from ..db.vector_client import VectorClient     # BREAKS in Choreo
from .llm_service import LLMService             # BREAKS in Choreo

# ❌ NO backend. prefix
from backend.utils.logger import get_logger     # BREAKS in Choreo
from backend.services.llm_service import LLM    # BREAKS in Choreo
from backend.db.vector_client import Vector     # BREAKS in Choreo
```

## ℹ️ Exceptions (Sub-packages Only)

Relative imports are OK **within** self-contained sub-packages:

```python
# Inside monitoring/ package - OK to use relative imports
from ..interfaces.metrics_interface import IMetrics
from .prometheus_exporter import PrometheusExporter

# Inside wiki_ingestion/ package - OK to use relative imports
from ..models.wiki_page import WikiPage
from .wiki_chunking_service import WikiChunking

# Inside diagram_processor/ package - OK to use relative imports
from ..utils.logger import get_logger
from ..models import EmbeddingRecord
```

## Why This Matters

In Choreo deployment:
- Working directory = `/workspace`
- Top-level packages: `services/`, `utils/`, `db/`, `monitoring/`
- There is **NO** `backend/` package
- Python can't go "above" the top level with `..`

## Quick Test

Before committing, test your imports:
```bash
cd backend
python -c "import app; print('✓ Imports OK')"
```

## Deployment Directory Structure

```
/workspace/                    ← Top level in Choreo
├── app.py                    ← Main app
├── start.py                  ← Startup script
├── services/                 ← Top-level package
│   ├── llm_service.py
│   ├── github_service.py
│   └── ...
├── utils/                    ← Top-level package
│   ├── logger.py
│   ├── config.py
│   └── ...
├── db/                       ← Top-level package
│   └── vector_client.py
└── monitoring/               ← Top-level package (can use internal relative imports)
    ├── interfaces/
    ├── collectors/
    └── ...
```

## Remember

**Start all imports from the top level: `services`, `utils`, `db`, `monitoring`**

No dots (`.`), no double dots (`..`), no `backend.` prefix!

---
Last Updated: January 5, 2026

