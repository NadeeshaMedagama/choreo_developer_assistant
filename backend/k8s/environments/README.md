# Choreo AI Assistant - Kubernetes Environments

This directory contains environment-specific configurations.

## Structure

```
environments/
├── dev/
│   ├── kustomization.yaml
│   └── patches/
├── staging/
│   ├── kustomization.yaml
│   └── patches/
└── production/
    ├── kustomization.yaml
    └── patches/
```

## Usage

### Development Environment
```bash
kubectl apply -k backend/k8s/environments/dev/
```

### Staging Environment
```bash
kubectl apply -k backend/k8s/environments/staging/
```

### Production Environment
```bash
kubectl apply -k backend/k8s/environments/production/
```

## Customizations

Each environment can override:
- Replica counts
- Resource limits
- Environment variables
- Image tags
- Ingress domains
- Storage sizes

