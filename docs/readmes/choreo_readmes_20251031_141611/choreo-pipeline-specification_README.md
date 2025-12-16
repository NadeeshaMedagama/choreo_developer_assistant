# Choreo Pipeline Specification

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/wso2/choreo-pipeline-specification/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](docs/)

The official specification for defining pipelines in the Choreo Internal Developer Platform (IDP). This specification provides a YAML-based configuration system built on top of Argo Workflows, supporting build pipelines, automation workflows, and general-purpose task orchestration while abstracting away Kubernetes complexity.

## Quick Start

Configure your pipeline in the Choreo Console:

```yaml
steps:
  - name: Build
    template: choreo/buildpack-build@v1
  
  - name: Test
    inlineScript: |
      #!/bin/bash
      npm test
  
  - name: Publish
    when: "{{BUILD_BRANCH}} == 'main'"
    template: choreo/artifact-upload@v1
```

**Get started with our [Quick Start Guide](docs/guides/quick-start.md) and [Examples](examples/README.md)**

## Documentation

### Core Documentation

- [**Overview**](docs/specification/overview.md) - Introduction to the pipeline specification
- [**Core Concepts**](docs/specification/concepts.md) - Fundamental concepts and architecture
- [**Configuration Guide**](docs/specification/pipeline-configuration.md) - Complete configuration reference
- [**API Reference**](docs/api-reference/index.md) - Detailed API documentation

### Examples

Browse our [example pipelines](examples/) organized by pipeline type:

- [**Build Pipelines**](examples/build/) - Pipelines for building and testing
  
- [**Automation Pipelines**](examples/automation/) - Scheduled and long-running tasks
- [**Choreo Templates**](examples/choreo-templates/) - Template usage examples

## Key Features

### Simple Yet Powerful

- **Declarative YAML** - Easy-to-understand configuration
- **Template Reusability** - Create and share pipeline components
- **Parallel Execution** - Optimize pipeline performance
- **Built-in Templates** - Pre-configured templates for common tasks

### Enterprise Ready

- **Security First** - Secure secrets management
- **Resource Management** - Fine-grained CPU/memory control
- **Retry Strategies** - Automatic error recovery
- **Conditional Execution** - Dynamic pipeline behavior

### Developer Friendly

- **Minimal Learning Curve** - Start simple, grow complex
- **Comprehensive Examples** - Learn by example
- **JSON Schema Validation** - Catch errors early
- **Extensive Documentation** - Everything you need to know

## Repository Structure

```
choreo-pipeline-specification/
├── docs/                      # Specification documentation
│   ├── specification/         # Core specification docs
│   ├── api-reference/         # API reference documentation
│   ├── choreo-templates/      # Choreo templates documentation
│   └── guides/                # How-to guides and migrations
├── examples/                  # Example pipelines
│   ├── build/                 # Build pipeline examples
│   ├── automation/            # Automation pipeline examples
│   └── choreo-templates/      # Template usage examples
├── tests/                     # Test files
├── CONTRIBUTING.md            # Contribution guidelines
└── README.md                  # This file
```

## Installation & Usage

### For Pipeline Developers

1. Open the Choreo Console
2. Navigate to your component settings
3. Configure your pipeline either by:
   - **Plain Text**: Paste your YAML configuration directly
   - **Repository**: Provide the repository location containing your pipeline YAML
4. Save to trigger pipeline execution


## Pipeline Components

### Steps

The basic building blocks of a pipeline:

```yaml
steps:
  - name: my-step
    inlineScript: |
      #!/bin/bash
      echo "Hello, World!"
```

### Templates

Reusable pipeline components:

```yaml
templates:
  - name: test-runner
    inlineScript: |
      #!/bin/bash
      npm test
```

### Environment Variables

Secure configuration management:

```yaml
env:
  - name: API_URL
    value: "{{VARIABLES.API_URL}}"
  - name: API_TOKEN
    value: "{{SECRETS.API_TOKEN}}"
```

### Resource Management

Control resource allocation:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "500m"
  limits:
    memory: "512Mi"
    cpu: "1000m"
```

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2024-01 | Initial release |

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- Reporting issues
- Suggesting enhancements
- Submitting pull requests
- Development setup
- Style guidelines

## Validation

Validate your pipeline configuration:

Pipeline configurations are automatically validated by the Choreo Console when you save them. The console provides:

- **Real-time syntax validation** - YAML syntax errors are highlighted immediately
- **Schema validation** - Configuration structure is validated against the specification
- **Template validation** - Template references and parameters are verified
- **Error reporting** - Clear error messages with line numbers and suggestions


## Status

- Core specification complete
- Basic examples available
- API reference documented
- JSON schema validation
- Advanced examples in progress
- Video tutorials planned

## Getting Help

- Read the [documentation](specification/overview.md)
- Browse [examples](examples/)
- Report [issues](https://github.com/wso2/choreo-pipeline-specification/issues)
- Start a [discussion](https://github.com/wso2/choreo-pipeline-specification/discussions)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## About WSO2

WSO2 is an open-source technology provider that delivers software to create and manage APIs and cloud-native applications.

---

**[Documentation](docs/)** | **[Examples](examples/)** | **[API Reference](docs/api-reference/)** | **[Choreo Templates](docs/choreo-templates/overview.md)** | **[Contributing](CONTRIBUTING.md)**
