# Kubernetes Deployment - Reorganized Structure

## 📁 New Directory Structure

```
k8s/
├── base/                           # Base Kubernetes manifests
│   ├── config/                     # Configuration resources
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   └── secret.yaml
│   ├── deployments/                # Application deployments
│   │   ├── backend-deployment.yaml
│   │   └── frontend-deployment.yaml
│   ├── services/                   # Networking resources
│   │   ├── backend-service.yaml
│   │   ├── frontend-service.yaml
│   │   └── ingress.yaml
│   ├── storage/                    # Persistent storage
│   │   └── pvc.yaml
│   ├── security/                   # Security resources
│   │   ├── rbac.yaml
│   │   └── networkpolicy.yaml
│   ├── policies/                   # Resource policies
│   │   ├── hpa.yaml
│   │   ├── pdb.yaml
│   │   └── resource-quota.yaml
│   └── monitoring/                 # Monitoring resources
│       └── prometheus-servicemonitor.yaml
│
├── environments/                   # Environment-specific configs
│   ├── dev/                        # Development environment
│   │   ├── kustomization.yaml
│   │   └── patches/
│   ├── production/                 # Production environment
│   │   ├── kustomization.yaml
│   │   └── patches/
│   └── README.md
│
├── scripts/                        # Deployment scripts
│   ├── build-images.sh
│   ├── deploy.sh
│   ├── cleanup.sh
│   ├── status.sh
│   └── update-secrets.sh
│
├── docs/                           # Documentation
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── DEPLOYMENT_SUMMARY.md
│   └── FILE_INDEX.md
│
├── kustomization.yaml              # Main kustomize config
├── Makefile                        # Make targets
└── .gitignore                      # Git ignore rules
```

## 🎯 Quick Start

### Using Scripts
```bash
cd backend/k8s

# Build images
./scripts/build-images.sh

# Update secrets
./scripts/update-secrets.sh

# Deploy
./scripts/deploy.sh

# Check status
./scripts/status.sh

# Cleanup
./scripts/cleanup.sh
```

### Using Make
```bash
cd backend/k8s

make build      # Build Docker images
make secrets    # Update secrets
make deploy     # Deploy to cluster
make status     # Check deployment status
make logs       # View logs
make clean      # Remove all resources
```

### Using kubectl/kustomize
```bash
# Deploy base configuration
kubectl apply -k .

# Deploy to dev environment
kubectl apply -k environments/dev/

# Deploy to production
kubectl apply -k environments/production/
```

## 📂 Directory Purposes

### base/
Contains all base Kubernetes manifests organized by type:

- **config/** - Configuration resources (namespace, configmap, secrets)
- **deployments/** - Application deployments (backend, frontend)
- **services/** - Networking (services, ingress)
- **storage/** - Persistent volumes and claims
- **security/** - RBAC, network policies
- **policies/** - HPA, PDB, resource quotas
- **monitoring/** - Prometheus ServiceMonitor

### environments/
Environment-specific configurations using Kustomize overlays:

- **dev/** - Development settings (1 replica, smaller resources)
- **production/** - Production settings (3 replicas, larger resources, enhanced security)

### scripts/
Helper shell scripts for common operations:

- **build-images.sh** - Build Docker images
- **deploy.sh** - Deploy to Kubernetes
- **update-secrets.sh** - Manage secrets
- **status.sh** - Check deployment status
- **cleanup.sh** - Remove all resources

### docs/
Comprehensive documentation:

- **README.md** - Main documentation (this file is copied here)
- **QUICKSTART.md** - Quick start guide
- **DEPLOYMENT_SUMMARY.md** - Deployment summary
- **FILE_INDEX.md** - Complete file index

## 🔧 Configuration

### Update Secrets
Edit `base/config/secret.yaml` or use the helper script:
```bash
./scripts/update-secrets.sh
```

### Modify Resources
- **Deployments**: `base/deployments/`
- **Services**: `base/services/`
- **Storage**: `base/storage/`
- **Policies**: `base/policies/`

### Environment-Specific Changes
- **Development**: `environments/dev/patches/`
- **Production**: `environments/production/patches/`

## ✅ Validation

All manifests have been validated and tested:

```bash
# Validate base
kubectl apply --dry-run=client -k .

# Validate dev
kubectl apply --dry-run=client -k environments/dev/

# Validate production
kubectl apply --dry-run=client -k environments/production/
```

## 📊 Benefits of New Structure

1. **Organization** - Files grouped by type and purpose
2. **Clarity** - Easy to find specific resources
3. **Scalability** - Easy to add new resources
4. **Maintainability** - Logical separation of concerns
5. **Clean Root** - Only essential files in root directory

## 🚀 Next Steps

1. Review the new structure
2. Update secrets in `base/config/secret.yaml`
3. Build images: `make build`
4. Deploy: `make deploy`
5. Verify: `make status`

## 📚 Documentation

- Full README: `docs/README.md`
- Quick Start: `docs/QUICKSTART.md`
- File Index: `docs/FILE_INDEX.md`
- Deployment Summary: `docs/DEPLOYMENT_SUMMARY.md`

---

**The k8s directory has been reorganized for better clarity and maintainability!** ✨

