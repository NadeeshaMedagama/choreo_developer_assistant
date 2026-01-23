"""
Choreo Repository Registry

This module maintains a registry of official Choreo components and their GitHub repository locations.
It provides URL validation and resolution for Choreo-related repositories.

Supports both LOCAL and CLOUD (Choreo) deployments:
- Local: Can dynamically fetch repositories from GitHub API if GITHUB_TOKEN is available
- Cloud: Falls back to hardcoded OFFICIAL_REPOS list if GitHub API is unavailable

Now supports dynamic fetching of ALL repositories from wso2-enterprise organization via GitHub API.
"""

from typing import Dict, Optional, List
import re
import logging
import os

logger = logging.getLogger(__name__)

# Deployment environment detection
def is_choreo_deployment() -> bool:
    """
    Detect if running in Choreo cloud deployment environment.
    Checks for common Choreo/Kubernetes environment variables.
    """
    choreo_indicators = [
        'CHOREO_COMPONENT',
        'CHOREO_ENVIRONMENT',
        'KUBERNETES_SERVICE_HOST',
        'CHOREO_ORG',
        'CHOREO_PROJECT',
    ]
    return any(os.getenv(var) for var in choreo_indicators)

# Check deployment mode at module load
IS_CLOUD_DEPLOYMENT = is_choreo_deployment()
if IS_CLOUD_DEPLOYMENT:
    logger.info("🌐 Running in CLOUD (Choreo) deployment mode")
else:
    logger.info("💻 Running in LOCAL deployment mode")


class ChoreoRepoRegistry:
    """Registry of official Choreo repositories and components."""

    # Official Choreo components and their repository locations
    # Complete list of ALL 147 repositories with 'choreo' keyword from wso2-enterprise organization
    # Format: component_name -> (organization, repo_name, description)
    OFFICIAL_REPOS = {
        # Main Choreo repository
        "choreo": ("wso2-enterprise", "choreo", "Main Choreo repository"),

        # Choreo Console and UI
        "choreo-console": ("wso2-enterprise", "choreo-console", "Choreo web console"),
        "choreo-graphiql-explorer": ("wso2-enterprise", "choreo-graphiql-explorer", "GraphiQL explorer client for Choreo related GraphQL APIs"),

        # Admin and Management
        "choreo-admin-api": ("wso2-enterprise", "choreo-admin-api", "Choreo Admin API provides the admin functionalities of Choreo"),
        "choreo-product-management": ("wso2-enterprise", "choreo-product-management", "Choreo product management repository keeps track of the high level roadmap and customer commitments"),

        # AI Services
        "choreo-ai-anomaly-detector": ("wso2-enterprise", "choreo-ai-anomaly-detector", "AI service to detect performance related anomalies in Choreo"),
        "choreo-ai-api-test-agent": ("wso2-enterprise", "choreo-ai-api-test-agent", "AI agent backend service to try out Choreo user APIs"),
        "choreo-ai-autotrainer": ("wso2-enterprise", "choreo-ai-autotrainer", "Pipeline to automatically retrain the AI models"),
        "choreo-ai-capacity-planner": ("wso2-enterprise", "choreo-ai-capacity-planner", "AI based capacity planning for systems"),
        "choreo-ai-copilot": ("wso2-enterprise", "choreo-ai-copilot", "Copilot to assist Choreo users to communicate with Choreo AI assistants"),
        "choreo-ai-data-collector": ("wso2-enterprise", "choreo-ai-data-collector", "Service to collect data for AI models from Choreo front-end"),
        "choreo-ai-docbot": ("wso2-enterprise", "choreo-ai-docbot", "An AI based service for answering questions related to Choreo"),
        "choreo-ai-insight-assistant": ("wso2-enterprise", "choreo-ai-insight-assistant", "Choreo Insights Assistant to interact with the Choreo API Insights data with natural language queries"),
        "choreo-ai-low-code-suggestions": ("wso2-enterprise", "choreo-ai-low-code-suggestions", "Provides low-code suggestions for Choreo low-code editor"),
        "choreo-ai-multivariate-anomaly-detector": ("wso2-enterprise", "choreo-ai-multivariate-anomaly-detector", "AI service to detect performance related anomalies in Choreo services by monitoring multiple types of metrics"),
        "choreo-ai-obs-assistant": ("wso2-enterprise", "choreo-ai-obs-assistant", "Choreo AI observability assistant for interactive natural language queries"),
        "choreo-ai-test-assistant": ("wso2-enterprise", "choreo-ai-test-assistant", "Repository for the AI-based testing solutions of Choreo"),
        "choreo-ai-data-mapper": ("wso2-enterprise", "choreo-ai-data-mapper", "AI-powered data mapping"),
        "choreo-ai-data-mapper-vscode-plugin": ("wso2-enterprise", "choreo-ai-data-mapper-vscode-plugin", "VS Code plugin for data mapper"),
        "choreo-ai-performance-analyzer": ("wso2-enterprise", "choreo-ai-performance-analyzer", "AI-powered performance analysis"),
        "choreo-ai-program-analyzer": ("wso2-enterprise", "choreo-ai-program-analyzer", "AI-powered program analysis"),
        "choreo-ai-deployment-optimizer": ("wso2-enterprise", "choreo-ai-deployment-optimizer", "AI-powered deployment optimization"),

        # Alerting and Notifications
        "choreo-alert-notification-service": ("wso2-enterprise", "choreo-alert-notification-service", "Microservice that accepts notifications from multiple components"),
        "choreo-alert-router": ("wso2-enterprise", "choreo-alert-router", "Azure function app to handle alerts generated by the streaming job"),
        "choreo-alert-streaming": ("wso2-enterprise", "choreo-alert-streaming", "Azure streaming analytics implementation to process alerts"),
        "choreo-alerting": ("wso2-enterprise", "choreo-alerting", "Implementation of dataplane based alerting"),
        "choreo-application-alerts-publisher": ("wso2-enterprise", "choreo-application-alerts-publisher", "Alert publisher that processes Azure Log Analytics logs"),

        # API Management (APIM)
        "choreo-api": ("wso2-enterprise", "choreo-api", "API definitions of all Choreo resources"),
        "choreo-apim": ("wso2-enterprise", "choreo-apim", "Choreo API Management work"),
        "choreo-apim-analytics-alert-api": ("wso2-enterprise", "choreo-apim-analytics-alert-api", "Alert APIs used to subscribe and retrieve alert configuration"),
        "choreo-apim-analytics-api": ("wso2-enterprise", "choreo-apim-analytics-api", "GraphQL APIs used to retrieve analytics data from Azure ADX"),
        "choreo-apim-analytics-auth-api": ("wso2-enterprise", "choreo-apim-analytics-auth-api", "Authentication APIs for Azure event hub details"),
        "choreo-apim-analytics-control-plane": ("wso2-enterprise", "choreo-apim-analytics-control-plane", "Analytics for Choreo API Management"),
        "choreo-apim-analytics-deployment-iac": ("wso2-enterprise", "choreo-apim-analytics-deployment-iac", "Terraform scripts and infrastructure preparation code"),
        "choreo-apim-analytics-email": ("wso2-enterprise", "choreo-apim-analytics-email", "Email client service for Choreo Analytics Alerts"),
        "choreo-apim-analytics-email-trigger": ("wso2-enterprise", "choreo-apim-analytics-email-trigger", "Email trigger for APIM analytics"),
        "choreo-apim-analytics-portal": ("wso2-enterprise", "choreo-apim-analytics-portal", "APIM analytics portal and dashboards"),
        "choreo-apim-analytics-streaming": ("wso2-enterprise", "choreo-apim-analytics-streaming", "APIM analytics streaming"),
        "choreo-apim-analytics-token-proxy": ("wso2-enterprise", "choreo-apim-analytics-token-proxy", "Token proxy API for choreo IDP"),
        "choreo-apim-devportal": ("wso2-enterprise", "choreo-apim-devportal", "Choreo APIM DevPortal developer portal"),
        "choreo-apim-mediation-code-generator": ("wso2-enterprise", "choreo-apim-mediation-code-generator", "Tool for generating Ballerina services for proxies with mediations"),
        "choreo-apim-mediation-module": ("wso2-enterprise", "choreo-apim-mediation-module", "Ballerina package for authoring mediation policies in Choreo"),
        "choreo-apim-proxy-deployer": ("wso2-enterprise", "choreo-apim-proxy-deployer", "Proxy deployer component for proxy APIs and mediation"),
        "choreo-apimgt-extensions": ("wso2-enterprise", "choreo-apimgt-extensions", "Extensions for choreo apim product"),
        "choreo-analytics-apim": ("wso2-enterprise", "choreo-analytics-apim", "API Manager analytics integration"),
        "choreo-product-apim": ("wso2-enterprise", "choreo-product-apim", "API Manager distribution for Choreo"),

        # Application and Gateway
        "choreo-app-gateway-oauth-agent": ("wso2-enterprise", "choreo-app-gateway-oauth-agent", "Node.js OAuth Agent for handling OIDC, OAuth2 flows"),
        "choreo-app-insight-action": ("wso2-enterprise", "choreo-app-insight-action", "App-insight events when user commits from code editor"),
        "choreo-gateway": ("wso2-enterprise", "choreo-gateway", "Choreo gateway related components and extensions"),
        "choreo-cp-gateway-adapter": ("wso2-enterprise", "choreo-cp-gateway-adapter", "Gateway Adapter Service for API and artifact deployment"),
        "choreo-connect-global-adapter": ("wso2-enterprise", "choreo-connect-global-adapter", "Global adapter component for Choreo Connect deployment"),

        # Authorization and Security
        "choreo-appdev-authorization": ("wso2-enterprise", "choreo-appdev-authorization", "Authorization service for Choreo In-built STS"),
        "choreo-appdev-user-mgt": ("wso2-enterprise", "choreo-appdev-user-mgt", "User management service for Choreo internal developers"),
        "choreo-resource-authorization-service": ("wso2-enterprise", "choreo-resource-authorization-service", "Relationship-based access control service"),
        "choreo-sts": ("wso2-enterprise", "choreo-sts", "Choreo built-in Security Token Service"),
        "choreo-iam": ("wso2-enterprise", "choreo-iam", "Choreo IAM related components"),
        "choreo-idp": ("wso2-enterprise", "choreo-idp", "Choreo Identity Provider"),

        # Audit and Logging
        "choreo-audit-logging": ("wso2-enterprise", "choreo-audit-logging", "Choreo audit logging API"),
        "choreo-logging": ("wso2-enterprise", "choreo-logging", "Logging infrastructure"),
        "choreo-log-controller": ("wso2-enterprise", "choreo-log-controller", "Control logs of Choreo components"),

        # Billing and Subscriptions
        "choreo-billing": ("wso2-enterprise", "choreo-billing", "Choreo Billing service"),
        "choreo-subscriptions": ("wso2-enterprise", "choreo-subscriptions", "Choreo Subscriptions Service"),
        "choreo-subscription-mgt": ("wso2-enterprise", "choreo-subscription-mgt", "Choreo subscription management service"),

        # Build and CI/CD
        "choreo-buildpacks": ("wso2-enterprise", "choreo-buildpacks", "Cloud-native build packs for choreo"),
        "choreo-ci-tools": ("wso2-enterprise", "choreo-ci-tools", "Choreo CI and maintenance tools"),
        "choreo-common-pipeline-templates": ("wso2-enterprise", "choreo-common-pipeline-templates", "Shared Azure pipeline templates"),
        "choreo-external-component-builder": ("wso2-enterprise", "choreo-external-component-builder", "Configs for third party charts and images"),
        "choreo-external-image-scan": ("wso2-enterprise", "choreo-external-image-scan", "Scheduled approval pipeline for scanning remote images"),
        "choreo-userapp-image-deleter": ("wso2-enterprise", "choreo-userapp-image-deleter", "Delete unused userapps images from Azure Container Registry"),

        # CLI and Developer Tools
        "choreo-cli": ("wso2-enterprise", "choreo-cli", "Boost Developer Efficiency: A CLI for WSO2 Choreo"),
        "choreo-lang-server": ("wso2-enterprise", "choreo-lang-server", "WebSocket based ballerina lang server for Choreo low code editor"),
        "choreo-compiler-plugins": ("wso2-enterprise", "choreo-compiler-plugins", "Ballerina compiler plugins for Choreo"),
        "choreo-compiler-security": ("wso2-enterprise", "choreo-compiler-security", "Ballerina compiler security extension"),

        # Connectors
        "choreo-built-in-connector-service": ("wso2-enterprise", "choreo-built-in-connector-service", "Services for Choreo's built-in connectors like SMS, Email, WhatsApp"),
        "choreo-connector-builder": ("wso2-enterprise", "choreo-connector-builder", "CRUD operations for custom user connectors"),
        "choreo-connector-data-service": ("wso2-enterprise", "choreo-connector-data-service", "Provide context driven data/suggestions to lowcode editor"),

        # Control Plane
        "choreo-control-plane": ("wso2-enterprise", "choreo-control-plane", "Choreo control plane scripts and configuration"),
        "choreo-cp-configuration-service": ("wso2-enterprise", "choreo-cp-configuration-service", "Shared service API for storing and sharing configurations"),
        "choreo-cp-declarative-api": ("wso2-enterprise", "choreo-cp-declarative-api", "Service for managing declarative configurations of Choreo resources"),
        "choreo-cp-env-overlay": ("wso2-enterprise", "choreo-cp-env-overlay", "Environment overlays of choreo control plane"),
        "choreo-cp-graphql": ("wso2-enterprise", "choreo-cp-graphql", "GraphQL server for project concept"),
        "choreo-cp-resiliency-framework": ("wso2-enterprise", "choreo-cp-resiliency-framework", "Choreo control plane resilient invoker service"),

        # Dashboards
        "choreo-cio-dashboard": ("wso2-enterprise", "choreo-cio-dashboard", "Choreo CIO Dashboard visualizes organizational efficiency"),
        "choreo-devops-portal": ("wso2-enterprise", "choreo-devops-portal", "Choreo DevOps Portal"),
        "choreo-devops-portal-api": ("wso2-enterprise", "choreo-devops-portal-api", "API integration proxy/service for Choreo Devops Portal"),

        # Datadog Integration
        "choreo-datadog-integration": ("wso2-enterprise", "choreo-datadog-integration", "Datadog integration for Choreo"),

        # Default Services
        "choreo-default-backend": ("wso2-enterprise", "choreo-default-backend", "Deploy static error pages for nginx controller"),

        # Delete and Cleanup
        "choreo-delete-manager": ("wso2-enterprise", "choreo-delete-manager", "Handle delete requests in choreo"),
        "choreo-org-cleanup-service": ("wso2-enterprise", "choreo-org-cleanup-service", "Remove organization specific data in registered components"),

        # Demo and Training
        "choreo-demo-resources": ("wso2-enterprise", "choreo-demo-resources", "Backends used in Choreo demonstrations and training"),
        "choreo-demo-tools": ("wso2-enterprise", "choreo-demo-tools", "Choreo Observability sample data generator"),
        "choreo-customer-pocs": ("wso2-enterprise", "choreo-customer-pocs", "Choreo Customer PoCs"),
        "choreo-devrel": ("wso2-enterprise", "choreo-devrel", "Marketing and Dev Rel activities related to Choreo"),

        # DevOps and Infrastructure
        "choreo-devops-iac": ("wso2-enterprise", "choreo-devops-iac", "WSO2 Choreo DevOps Terraform scripts"),
        "choreo-kustomize-custom-plugins": ("wso2-enterprise", "choreo-kustomize-custom-plugins", "Custom plugins used with Kustomize"),

        # Email Service
        "choreo-email": ("wso2-enterprise", "choreo-email", "Email service used by Choreo components"),

        # Engineering Efficiency
        "choreo-engineering-efficiency": ("wso2-enterprise", "choreo-engineering-efficiency", "Choreo Engineering Efficiency recording tools"),

        # Event Publisher
        "choreo-event-publisher": ("wso2-enterprise", "choreo-event-publisher", "Common library for publishing Choreo events"),

        # Global Adapter
        "choreo-ga-health-check-client": ("wso2-enterprise", "choreo-ga-health-check-client", "Health check client for the Global Adapter"),

        # Governance
        "choreo-governance-service": ("wso2-enterprise", "choreo-governance-service", "Managing all API governance-related tasks"),

        # Hubble
        "choreo-hubble-exporter": ("wso2-enterprise", "choreo-hubble-exporter", "Intermediary component between Hubble and message broker"),

        # Image Services
        "choreo-image-share-service": ("wso2-enterprise", "choreo-image-share-service", "Upload images onto public azure blob storage for social media"),
        "choreo-shared-image-viewer": ("wso2-enterprise", "choreo-shared-image-viewer", "Next.js app to embed low-code images for social media"),

        # Key-Value Storage
        "choreo-key-value-storage": ("wso2-enterprise", "choreo-key-value-storage", "Choreo Key Value Storage Connector functionality"),

        # Linker and Negotiator
        "choreo-linker": ("wso2-enterprise", "choreo-linker", "Service linking and orchestration"),
        "choreo-negotiator": ("wso2-enterprise", "choreo-negotiator", "Service negotiation and discovery"),

        # Linter
        "choreo-linter-service": ("wso2-enterprise", "choreo-linter-service", "Uses Spectral to lint YAML/JSON content"),

        # Maintenance and Testing
        "choreo-maintenance-regression-tests": ("wso2-enterprise", "choreo-maintenance-regression-tests", "Tests for determining impact on end users due to infrastructure maintenance"),

        # Marketplace
        "choreo-marketplace": ("wso2-enterprise", "choreo-marketplace", "Choreo Marketplace service implementation"),

        # Moesif
        "choreo-moesif-microservice": ("wso2-enterprise", "choreo-moesif-microservice", "Retrieve auth keys of Moesif analytics platform"),

        # Monitoring
        "choreo-monitor-uptime-services": ("wso2-enterprise", "choreo-monitor-uptime-services", "Azure function for choreo monitors in Site24x7"),
        "choreo-site24x7-monitor-automation": ("wso2-enterprise", "choreo-site24x7-monitor-automation", "Automation of Site24x7 monitors"),
        "choreo-site24x7-uptime-components": ("wso2-enterprise", "choreo-site24x7-uptime-components", "Components for Choreo uptime metrics in Site24x7"),

        # Observability
        "choreo-obs-manager": ("wso2-enterprise", "choreo-obs-manager", "Control plane logic for observability"),
        "choreo-obsapi": ("wso2-enterprise", "choreo-obsapi", "Observability API for Choreo"),
        "choreo-sys-obsapi": ("wso2-enterprise", "choreo-sys-obsapi", "API which retrieves system metrics of choreo user apps"),
        "choreo-observability": ("wso2-enterprise", "choreo-observability", "Observability infrastructure"),
        "choreo-telemetry": ("wso2-enterprise", "choreo-telemetry", "Telemetry and monitoring for Choreo"),

        # Organization Management
        "choreo-organization-management": ("wso2-enterprise", "choreo-organization-management", "Choreo organization management functionalities"),

        # Performance
        "choreo-performance": ("wso2-enterprise", "choreo-performance", "Choreo performance related tools, scripts & artifacts"),

        # Pixie
        "choreo-pixie-control-plane": ("wso2-enterprise", "choreo-pixie-control-plane", "Common Kustomize patches for pixie cloud and pixie dp"),
        "choreo-pixie-cp-env-overlay": ("wso2-enterprise", "choreo-pixie-cp-env-overlay", "Environment specific configurations for Pixie"),

        # Platform Services
        "choreo-platform-services-manager": ("wso2-enterprise", "choreo-platform-services-manager", "Manages platform services (databases, caches, queues, etc)"),

        # Private Data Plane (PDP)
        "choreo-pdp-manager": ("wso2-enterprise", "choreo-pdp-manager", "Control plane service for registering and managing Choreo private data planes"),
        "choreo-pdp-cch": ("wso2-enterprise", "choreo-pdp-cch", "Helm Configs for CCH PDP"),
        "choreo-pdp-exxonmobil": ("wso2-enterprise", "choreo-pdp-exxonmobil", "ExxonMobil PDP Helm Configs"),
        "choreo-pdp-fatorseguradora": ("wso2-enterprise", "choreo-pdp-fatorseguradora", "Fator Seguradora PDP Helm Configs"),
        "choreo-pdp-medinet": ("wso2-enterprise", "choreo-pdp-medinet", "Medinet PDP Helm Configs"),
        "choreo-pdp-uoe": ("wso2-enterprise", "choreo-pdp-uoe", "University of Edinburgh PDP Helm Configs"),
        "choreo-pdp-wso2": ("wso2-enterprise", "choreo-pdp-wso2", "Helm configs and Terraform IaC for WSO2 Internal PDPs"),
        "choreo-byo-pdp-helm": ("wso2-enterprise", "choreo-byo-pdp-helm", "Helm chart for Personal Private Dataplane (PPDP)"),
        "choreo-private-dataplane-aws-iac": ("wso2-enterprise", "choreo-private-dataplane-aws-iac", "Terraform IAC scripts for AWS Based Choreo private dataplanes"),
        "choreo-private-dataplane-azure-iac": ("wso2-enterprise", "choreo-private-dataplane-azure-iac", "Terraform IAC scripts for Azure Based Choreo private dataplanes"),
        "choreo-private-dataplane-gcp-iac": ("wso2-enterprise", "choreo-private-dataplane-gcp-iac", "Terraform IAC scripts for GCP Based Choreo private dataplanes"),
        "choreo-private-dataplane-helm": ("wso2-enterprise", "choreo-private-dataplane-helm", "Helm artifacts for private dataplane"),
        "choreo-private-dataplane-task-automation": ("wso2-enterprise", "choreo-private-dataplane-task-automation", "Scripts for automation of Choreo private data plane deployments"),
        "choreo-private-dataplane-tools": ("wso2-enterprise", "choreo-private-dataplane-tools", "Tools and utilities for managing Choreo Private Dataplanes"),
        "choreo-privatedp-central-manifests": ("wso2-enterprise", "choreo-privatedp-central-manifests", "Base manifests required by private dataplane deployments"),
        "choreo-privatedp-sample-overlay": ("wso2-enterprise", "choreo-privatedp-sample-overlay", "Sample overlay for Choreo private data-planes"),

        # Runtime
        "choreo-runtime": ("wso2-enterprise", "choreo-runtime", "Components related to choreo runtime"),
        "choreodp-rudder": ("wso2-enterprise", "choreodp-rudder", "Choreo dataplane rudder"),
        "choreodp-shared-container-registry-proxy": ("wso2-enterprise", "choreodp-shared-container-registry-proxy", "Proxy in front of ACR with sub-request authentication"),

        # Samples
        "choreo-sample-app-components": ("wso2-enterprise", "choreo-sample-app-components", "Source code of Choreo sample app"),
        "choreo-sample-data": ("wso2-enterprise", "choreo-sample-data", "Services/data required to write samples for Choreo"),
        "choreo-samples": ("wso2-enterprise", "choreo-samples", "A collection of samples for Choreo"),

        # Synapse
        "choreo-synapse-resource-generator": ("wso2-enterprise", "choreo-synapse-resource-generator", "Generate resources for Choreo component deployment from Integration Studio projects"),

        # System APIs
        "choreo-system-apis": ("wso2-enterprise", "choreo-system-apis", "System API definitions for choreo"),

        # Testing
        "choreo-test-manager": ("wso2-enterprise", "choreo-test-manager", "Responsible for triggering tests upon build/promotion"),
        "choreo-testbase": ("wso2-enterprise", "choreo-testbase", "Micro service enabling users to test their application"),

        # URL Management
        "choreo-url-management": ("wso2-enterprise", "choreo-url-management", "API for URL customizations in Choreo"),

        # Workflow Management
        "choreo-workflow-mgt": ("wso2-enterprise", "choreo-workflow-mgt", "Service for managing approval workflows in Choreo"),

        # Healthcare
        "open-healthcare-choreo": ("wso2-enterprise", "open-healthcare-choreo", "Open Healthcare Choreo/Ballerina Packages, Templates and Tools"),

        # Other Related Repositories (Non-Choreo but included in search)
        "apim-ai-deployments": ("wso2-enterprise", "apim-ai-deployments", "Deployments on Choreo Control Plane for AI features of on-prem API manager"),
        "bfsi-demo-samples": ("wso2-enterprise", "bfsi-demo-samples", "BFSI demo samples on choreo"),
        "wso2-baremetal-kube-cluster-provisioner": ("wso2-enterprise", "wso2-baremetal-kube-cluster-provisioner", "Baremetal kubernetes cluster provisioning scripts for choreo"),
        "ballerina-registry-control-plane": ("wso2-enterprise", "ballerina-registry-control-plane", "Ballerina registry control plane"),

        # Data Plane Components (from Important links.docx)
        "choreodp-auth-module": ("wso2-enterprise", "choreodp-auth-module", "Choreo dataplane authentication module"),
        "choreodp-cicd": ("wso2-enterprise", "choreodp-cicd", "Choreo dataplane CI/CD components and Argo workflows"),
        "choreodp-secret-manager": ("wso2-enterprise", "choreodp-secret-manager", "Choreo dataplane secret manager"),
        "choreodp-mizzen": ("wso2-enterprise", "choreodp-mizzen", "Choreo dataplane mizzen and mizzen-agent"),
        "choreodp-project-manager": ("wso2-enterprise", "choreodp-project-manager", "Choreo dataplane project manager"),
        "choreodp-cloud-manager": ("wso2-enterprise", "choreodp-cloud-manager", "Choreo dataplane cloud manager"),
        "choreodp-garbage-collector": ("wso2-enterprise", "choreodp-garbage-collector", "Choreo dataplane garbage collector"),
        "choreodp-kv-resolver": ("wso2-enterprise", "choreodp-kv-resolver", "Choreo dataplane key-value resolver"),
        "choreodp-git-runners": ("wso2-enterprise", "choreodp-git-runners", "Choreo dataplane GitHub runners"),

        # Microgateway
        "product-microgateway": ("wso2-enterprise", "product-microgateway", "WSO2 Microgateway used by Choreo"),

        # Alert Configuration
        "choreo-alert-configuration-service": ("wso2-enterprise", "choreo-alert-configuration-service", "Service for configuring alerts in Choreo"),

        # Metered Usage
        "choreo-metered-usage-handler": ("wso2-enterprise", "choreo-metered-usage-handler", "Service for handling metered usage in Choreo"),

        # Growth Hacking
        "growth-hacking": ("wso2-enterprise", "growth-hacking", "Growth hacking tools including BigQuery data pipeline"),
    }

    # Known aliases for components
    ALIASES = {
        "console": "choreo-console",
        "telemetry": "choreo-telemetry",
        "obs-api": "choreo-obsapi",
        "obsapi": "choreo-obsapi",
        "runtime": "choreo-runtime",
        "linker": "choreo-linker",
        "negotiator": "choreo-negotiator",
    }

    # Service name to Repository mapping
    # Maps deployed service names to their source repositories
    # Source: https://github.com/wso2-enterprise/choreo-ci-tools/blob/main/ci-webhook-server/cmd/server/build.go
    SERVICE_TO_REPO = {
        # AI Services
        "anomaly-detector": "choreo-ai-anomaly-detector",
        "anomaly-detector-init": "choreo-ai-anomaly-detector",
        "capacity-planner": "choreo-ai-capacity-planner",
        "capacity-planner-init": "choreo-ai-capacity-planner",
        "datamapper": "choreo-ai-data-mapper",
        "datamapper-balo-extractor": "choreo-ai-data-mapper",
        "datamapper-init": "choreo-ai-data-mapper",
        "deployment-optimizer": "choreo-ai-deployment-optimizer",
        "deployment-optimizer-init": "choreo-ai-deployment-optimizer",
        "data-collector": "choreo-ai-data-collector",
        "lowcode-parser": "choreo-ai-data-collector",
        "multivariate-anomaly-detector-notification-manager": "choreo-ai-multivariate-anomaly-detector",
        "perfanalyzer-estimator": "choreo-ai-performance-analyzer",
        "perfanalyzer-updater": "choreo-ai-performance-analyzer",
        "programanalyzer": "choreo-ai-program-analyzer",
        "test-assistant": "choreo-ai-test-assistant",
        "test-assistant-init": "choreo-ai-test-assistant",
        "choreo-ai-insights-assistant": "choreo-ai-insight-assistant",
        "architect-agent-api-design": "choreo-ai-copilot",
        "copilot-datacollector": "choreo-ai-copilot",

        # Runtime Services
        "api-server": "choreo-runtime",
        "app-deployer": "choreo-runtime",
        "app-service": "choreo-runtime",
        "workspace-manager": "choreo-runtime",
        "code-server-default-backend": "choreo-runtime",

        # CI/CD Tools
        "ast-archive": "choreo-ci-tools",
        "ast-archiver": "choreo-ci-tools",
        "choreo-programcleaner": "choreo-ci-tools",

        # Connector Services
        "choreo-connectords": "choreo-connector-data-service",

        # APIM Services
        "choreo-apim-service": "choreo-apim",
        "choreo-mgw-adapter": "product-microgateway",
        "choreo-mgw-enforcer": "product-microgateway",
        "choreo-mgw-router": "product-microgateway",
        "choreo-apk-adapter": "choreo-product-apim",
        "choreo-apk-common-controller": "choreo-product-apim",
        "choreo-apk-enforcer": "choreo-product-apim",
        "choreo-apk-rate-limiter": "choreo-product-apim",
        "choreo-apk-router": "choreo-product-apim",
        "choreo-apk-config-deployer-service": "choreo-product-apim",
        "choreo-analytics-api": "choreo-apim-analytics-api",

        # Email and Notifications
        "email-service": "choreo-email",
        "alert-notification-service": "choreo-alert-notification-service",
        "alert-configuration-service": "choreo-alert-configuration-service",

        # Language Server
        "lang-server": "choreo-lang-server",

        # Observability
        "observability-api": "choreo-obsapi",
        "observability-api-dp": "choreo-obsapi",
        "observability-data-generator": "choreo-demo-tools",
        "choreo-sys-obsapi-dp": "choreo-sys-obsapi",
        "choreo-alerting-api": "choreo-alerting",

        # Data Plane Services
        "dp-auth-module": "choreodp-auth-module",
        "dp-cicd": "choreodp-cicd",
        "dp-cicd-runners-cleaner": "choreodp-cicd",
        "dp-cicd-build-status-cleaner": "choreodp-cicd",
        "argo-base-image": "choreodp-cicd",
        "argo-checkov-scan": "choreodp-cicd",
        "argo-environment-cleanup": "choreodp-cicd",
        "argo-environment-setup": "choreodp-cicd",
        "argo-validations": "choreodp-cicd",
        "argo-buildpack-build": "choreodp-cicd",
        "argo-docker-build": "choreodp-cicd",
        "argo-image-push": "choreodp-cicd",
        "argo-trivy-scan": "choreodp-cicd",
        "dp-rudder": "choreodp-rudder",
        "dp-rudder-migration-service": "choreodp-rudder",
        "dp-rudder-cilium": "choreodp-rudder",
        "dp-secret-manager": "choreodp-secret-manager",
        "dp-mizzen": "choreodp-mizzen",
        "dp-mizzen-agent": "choreodp-mizzen",
        "dp-project-manager": "choreodp-project-manager",
        "dp-cloud-manager": "choreodp-cloud-manager",
        "dp-garbage-collector": "choreodp-garbage-collector",
        "dp-kv-resolver": "choreodp-kv-resolver",
        "kube-rbac-proxy": "choreodp-kv-resolver",
        "gh-runner": "choreodp-git-runners",

        # Console
        "choreo-console-next": "choreo-console",

        # Delete and Cleanup
        "delete-manager": "choreo-delete-manager",
        "choreo-userapps-image-deleter": "choreo-userapp-image-deleter",

        # Subscription and Billing
        "analytics-subscription-mgt": "choreo-subscription-mgt",
        "billing-service": "choreo-billing",
        "choreo-aws-marketplace-client": "choreo-billing",
        "stripe-salesforce-integrator": "choreo-billing",
        "cost-optimizer": "choreo-billing",
        "cost-optimizer-cp-service": "choreo-billing",
        "cost-optimizer-cronjobs": "choreo-billing",
        "cost-optimizer-dp-daily-cron": "choreo-billing",
        "cost-optimizer-dp-monthly-cron": "choreo-billing",
        "cloud-billing-api-service": "choreo-billing",
        "cloud-billing-infra-publisher": "choreo-billing",

        # CIO Dashboard
        "cio-incident-configurator": "choreo-cio-dashboard",
        "cio-incident-data-scraper": "choreo-cio-dashboard",
        "cio-query-api": "choreo-cio-dashboard",
        "cio-event-collector-service": "choreo-cio-dashboard",

        # OpenTelemetry
        "choreo-opentelemetry-collector": "choreo-opentelemetry",

        # DevOps Portal
        "choreo-devops-portal-api-native": "choreo-devops-portal-api",

        # Global Adapter
        "choreo-connect-global-adapter-v2": "choreo-connect-global-adapter",

        # Marketplace
        "endpoint-resolver": "choreo-marketplace",
        "marketplace": "choreo-marketplace",
        "resource-registry-service": "choreo-marketplace",
        "connection-service": "choreo-marketplace",
        "choreo-contract-service": "choreo-marketplace",

        # PDP Manager
        "pdp-manager": "choreo-pdp-manager",

        # Platform Services
        "platform-services-manager": "choreo-platform-services-manager",

        # App Gateway
        "app-gateway-oauth-agent": "choreo-app-gateway-oauth-agent",

        # User Management and Authorization
        "app-dev-user-mgt": "choreo-appdev-user-mgt",
        "appdev-authorization": "choreo-appdev-authorization",

        # Metered Usage
        "metered-usage-handler-crons": "choreo-metered-usage-handler",
        "metered-usage-handler-service": "choreo-metered-usage-handler",

        # Control Plane Resiliency
        "choreo-cp-sis": "choreo-cp-resiliency-framework",
        "choreo-cp-rrs": "choreo-cp-resiliency-framework",
        "choreo-cp-rrs-go": "choreo-cp-resiliency-framework",
        "choreo-cp-resilient-invoker": "choreo-cp-resiliency-framework",

        # Telemetry
        "choreo-telemetry-go": "choreo-telemetry",

        # Logging
        "choreo-logging-dp": "choreo-logging",
        "choreo-opensearch": "choreo-logging",
        "choreo-logging-sidecar": "choreo-logging",
        "choreo-log-enricher": "choreo-logging",
        "choreo-logs-api": "choreo-logging",

        # APIM AI
        "marketplace-assistant": "apim-ai-deployments",
        "spec-populator": "apim-ai-deployments",
        "milvus-proxy": "apim-ai-deployments",

        # Control Plane Declarative API
        "choreo-cp-build-controller": "choreo-cp-declarative-api",
        "choreo-cp-choreo-api": "choreo-cp-declarative-api",
        "choreo-cp-environment-controller": "choreo-cp-declarative-api",
        "choreo-cp-deployment-controller": "choreo-cp-declarative-api",
        "choreo-cp-component-controller": "choreo-cp-declarative-api",
        "choreo-cp-project-controller": "choreo-cp-declarative-api",

        # Workflow Management
        "workflow-mgt-service": "choreo-workflow-mgt",

        # IAM
        "api-key-service": "choreo-iam",
        "sts-mgt-service": "choreo-iam",

        # STS
        "choreo-appdev-sts": "choreo-sts",

        # Configuration Service
        "configuration-schema-service": "choreo-cp-configuration-service",

        # Gateway Adapter
        "cp-gwadapter": "choreo-cp-gateway-adapter",

        # CLI
        "choreo-mcp-server-main": "choreo-cli",

        # Growth Hacking
        "choreo-bq-data-pipeline": "growth-hacking",
    }

    # Base GitHub URL
    GITHUB_BASE = "https://github.com"

    # Official Choreo documentation URLs
    OFFICIAL_DOCS = {
        "main": "https://wso2.com/choreo/",
        "docs": "https://wso2.com/choreo/docs/",
        "console": "https://console.choreo.dev",
    }

    # Internal documentation URLs for specific Choreo topics
    # These are the correct documentation sources for various Choreo features
    INTERNAL_DOCS = {
        # Choreo APIM Setup Guide For Development
        "apim": "https://docs.google.com/document/d/1qkonR2EG7ppgn5jhrNyd8aMhBjxlgzHtZ_1Wb1hrs1c/edit?tab=t.0#heading=h.44xczcdf40wf",
        "api-management": "https://docs.google.com/document/d/1qkonR2EG7ppgn5jhrNyd8aMhBjxlgzHtZ_1Wb1hrs1c/edit?tab=t.0#heading=h.44xczcdf40wf",
        "apim-setup": "https://docs.google.com/document/d/1qkonR2EG7ppgn5jhrNyd8aMhBjxlgzHtZ_1Wb1hrs1c/edit?tab=t.0#heading=h.44xczcdf40wf",

        # Choreo Light-Weight Security Token Service (STS)
        "security": "https://docs.google.com/document/d/19NUdAdhpO-AqpCBdd8v7EegAZLrLPfREY-0PozXv3g0/edit?tab=t.0",
        "sts": "https://docs.google.com/document/d/19NUdAdhpO-AqpCBdd8v7EegAZLrLPfREY-0PozXv3g0/edit?tab=t.0",
        "security-token-service": "https://docs.google.com/document/d/19NUdAdhpO-AqpCBdd8v7EegAZLrLPfREY-0PozXv3g0/edit?tab=t.0",
        "service-authentication": "https://docs.google.com/document/d/19NUdAdhpO-AqpCBdd8v7EegAZLrLPfREY-0PozXv3g0/edit?tab=t.0",
        "authentication": "https://docs.google.com/document/d/19NUdAdhpO-AqpCBdd8v7EegAZLrLPfREY-0PozXv3g0/edit?tab=t.0",
    }

    # Mapping of INVALID documentation URL patterns to their CORRECT URLs
    # These are URLs that LLMs commonly hallucinate but don't actually exist
    INVALID_DOC_URL_CORRECTIONS = {
        # Invalid API Management URLs -> Choreo APIM Setup Guide
        "wso2.com/choreo/docs/api-management": "https://docs.google.com/document/d/1qkonR2EG7ppgn5jhrNyd8aMhBjxlgzHtZ_1Wb1hrs1c/edit?tab=t.0#heading=h.44xczcdf40wf",

        # Invalid Security URLs -> Choreo Light-Weight STS doc
        "wso2.com/choreo/docs/security": "https://docs.google.com/document/d/19NUdAdhpO-AqpCBdd8v7EegAZLrLPfREY-0PozXv3g0/edit?tab=t.0",
        "wso2.com/choreo/docs/security/service-authentication": "https://docs.google.com/document/d/19NUdAdhpO-AqpCBdd8v7EegAZLrLPfREY-0PozXv3g0/edit?tab=t.0",
        "wso2.com/choreo/docs/api-management/security": "https://docs.google.com/document/d/19NUdAdhpO-AqpCBdd8v7EegAZLrLPfREY-0PozXv3g0/edit?tab=t.0",

        # Invalid Environment Management URLs -> Correct Choreo docs path
        "wso2.com/choreo/docs/environment-management": "https://wso2.com/choreo/docs/devops-and-ci-cd/manage-environments/",

        # Invalid Components Configuration URLs -> Correct Choreo docs path
        "wso2.com/choreo/docs/components/configuration": "https://wso2.com/choreo/docs/develop-components/use-configuration-form/",

        # Invalid CLI Documentation URL -> Correct Choreo CLI docs path
        "wso2.com/choreo/docs/cli": "https://wso2.com/choreo/docs/choreo-cli/choreo-cli-overview/",
        "wso2.com/choreo/docs/develop-components/cli": "https://wso2.com/choreo/docs/choreo-cli/choreo-cli-overview/",
        "wso2.com/choreo/docs/reference/cli": "https://wso2.com/choreo/docs/choreo-cli/choreo-cli-overview/",
        "wso2.com/choreo/docs/reference/faq/#choreo-cli": "https://wso2.com/choreo/docs/choreo-cli/choreo-cli-overview/",
        "wso2.com/choreo/docs/references/faq/#choreo-cli": "https://wso2.com/choreo/docs/choreo-cli/choreo-cli-overview/",
        "wso2.com/choreo/docs/getting-started/cli": "https://wso2.com/choreo/docs/choreo-cli/choreo-cli-overview/",
        "wso2.com/choreo/docs/getting-started/cli/": "https://wso2.com/choreo/docs/choreo-cli/choreo-cli-overview/",
    }

    # List of known INVALID documentation URL patterns (these don't exist)
    KNOWN_INVALID_DOC_PATTERNS = [
        "wso2.com/choreo/docs/ballerina",
        "wso2.com/choreo/docs/developer-tools",
        "wso2.com/choreo/docs/tutorials",
        "wso2.com/choreo/docs/guides",
        "wso2.com/choreo/docs/quick-start",
        "wso2.com/choreo/docs/api-reference",
        "wso2.com/choreo/docs/samples",
        "wso2.com/choreo/docs/examples",
        "wso2.com/choreo/docs/api-management",
        "wso2.com/choreo/docs/security",
        "wso2.com/choreo/docs/environment-management",
        "wso2.com/choreo/docs/components/configuration",
        "wso2.com/choreo/docs/cli",
        "wso2.com/choreo/docs/develop-components/cli",
        "wso2.com/choreo/docs/reference/cli",
        "wso2.com/choreo/docs/reference/faq/#choreo-cli",
        "wso2.com/choreo/docs/references/faq/#choreo-cli",
        "wso2.com/choreo/docs/getting-started/cli",
    ]

    def __init__(self):
        """Initialize the repository registry."""
        self._url_cache: Dict[str, str] = {}
        self._component_pattern = re.compile(r'choreo-[\w-]+', re.IGNORECASE)
        self._dynamic_repos: Optional[List[Dict[str, str]]] = None
        self._github_service = None

    def get_internal_doc_url(self, topic: str) -> Optional[str]:
        """
        Get the correct internal documentation URL for a given topic.

        Args:
            topic: Topic name (e.g., 'apim', 'security', 'sts')

        Returns:
            The correct documentation URL or None if not found
        """
        topic_lower = topic.lower().strip()
        return self.INTERNAL_DOCS.get(topic_lower)

    def is_invalid_doc_url(self, url: str) -> bool:
        """
        Check if a URL matches a known invalid documentation URL pattern.

        Args:
            url: URL to check

        Returns:
            True if URL is known to be invalid, False otherwise
        """
        url_lower = url.lower()
        for pattern in self.KNOWN_INVALID_DOC_PATTERNS:
            if pattern.lower() in url_lower:
                return True
        return False

    def get_correct_doc_url(self, invalid_url: str) -> Optional[str]:
        """
        Get the correct documentation URL for a known invalid URL.

        Args:
            invalid_url: The invalid URL to find a correction for

        Returns:
            The correct URL if a correction exists, None otherwise
        """
        invalid_url_lower = invalid_url.lower()

        # Regex-based corrections for common patterns
        # This catches ALL CLI-related invalid URLs regardless of exact path
        cli_pattern = re.compile(r'wso2\.com/choreo/docs/.*cli', re.IGNORECASE)
        if cli_pattern.search(invalid_url_lower):
            correct_url = "https://wso2.com/choreo/docs/choreo-cli/choreo-cli-overview/"
            logger.info(f"Found CLI URL correction (regex): {invalid_url} -> {correct_url}")
            return correct_url

        # Static pattern matching for other URLs
        for pattern, correct_url in self.INVALID_DOC_URL_CORRECTIONS.items():
            if pattern.lower() in invalid_url_lower:
                logger.info(f"Found doc URL correction: {invalid_url} -> {correct_url}")
                return correct_url
        return None

    def fix_invalid_doc_url(self, url: str) -> str:
        """
        Fix an invalid documentation URL by replacing it with the correct one.

        Args:
            url: URL to fix

        Returns:
            The corrected URL or the original if no correction is available
        """
        correct_url = self.get_correct_doc_url(url)
        if correct_url:
            return correct_url
        return url

    def get_repo_for_service(self, service_name: str) -> Optional[str]:
        """
        Get the repository name for a given service name.

        Args:
            service_name: The name of the service (e.g., 'anomaly-detector', 'api-server')

        Returns:
            The repository name or None if not found
        """
        service_lower = service_name.lower().strip()
        return self.SERVICE_TO_REPO.get(service_lower) or self.SERVICE_TO_REPO.get(service_name)

    def get_github_url_for_service(self, service_name: str) -> Optional[str]:
        """
        Get the GitHub URL for a given service name.

        Args:
            service_name: The name of the service

        Returns:
            The GitHub URL or None if not found
        """
        repo_name = self.get_repo_for_service(service_name)
        if repo_name:
            # Look up the organization from OFFICIAL_REPOS
            repo_info = self.OFFICIAL_REPOS.get(repo_name)
            if repo_info:
                org, repo, _ = repo_info
                return f"{self.GITHUB_BASE}/{org}/{repo}"
            # Default to wso2-enterprise if not in OFFICIAL_REPOS
            return f"{self.GITHUB_BASE}/wso2-enterprise/{repo_name}"
        return None

    def get_service_info(self, service_name: str) -> Optional[Dict[str, str]]:
        """
        Get comprehensive information about a service including its repository.

        Args:
            service_name: The name of the service

        Returns:
            Dictionary with service info or None if not found
        """
        repo_name = self.get_repo_for_service(service_name)
        if not repo_name:
            return None

        github_url = self.get_github_url_for_service(service_name)
        repo_info = self.OFFICIAL_REPOS.get(repo_name)

        return {
            "service_name": service_name,
            "repository": repo_name,
            "github_url": github_url,
            "description": repo_info[2] if repo_info else f"Repository for {service_name}",
            "organization": repo_info[0] if repo_info else "wso2-enterprise",
        }

    def search_services(self, query: str) -> List[Dict[str, str]]:
        """
        Search for services matching a query.

        Args:
            query: Search query (partial match on service name)

        Returns:
            List of matching service info dictionaries
        """
        query_lower = query.lower()
        results = []

        for service_name, repo_name in self.SERVICE_TO_REPO.items():
            if query_lower in service_name.lower() or query_lower in repo_name.lower():
                info = self.get_service_info(service_name)
                if info:
                    results.append(info)

        return results

    def _get_github_service(self):
        """
        Lazy load GitHub service with token from environment.

        In cloud deployment (Choreo), GitHub API access may be limited.
        Returns None if GitHub service cannot be initialized.
        """
        if self._github_service is None:
            try:
                # Try relative import first (works in most cases)
                try:
                    from services.github_service import GitHubService
                except ImportError:
                    # Fallback to absolute import for different deployment structures
                    try:
                        from backend.services.github_service import GitHubService
                    except ImportError:
                        logger.warning("Could not import GitHubService - dynamic repo fetching disabled")
                        return None

                github_token = os.getenv('GITHUB_TOKEN')

                if not github_token and IS_CLOUD_DEPLOYMENT:
                    logger.warning("🌐 Cloud deployment: GITHUB_TOKEN not set - using hardcoded repos only")
                    return None

                self._github_service = GitHubService(token=github_token)
                logger.info(f"GitHub service initialized {'with' if github_token else 'without'} token")

            except Exception as e:
                logger.error(f"Failed to initialize GitHub service: {e}")
                logger.warning("Dynamic repository fetching will be disabled - using hardcoded repos")
                return None

        return self._github_service

    def is_dynamic_fetch_available(self) -> bool:
        """
        Check if dynamic repository fetching from GitHub is available.

        Returns:
            True if GitHub API can be used, False otherwise
        """
        github_service = self._get_github_service()
        return github_service is not None

    def fetch_all_wso2_enterprise_repos(self, use_cache: bool = True) -> List[Dict[str, str]]:
        """
        Dynamically fetch ALL repositories from wso2-enterprise organization via GitHub API.

        This replaces the hardcoded OFFICIAL_REPOS list with live data from GitHub.
        In cloud deployment (Choreo), falls back to hardcoded list if GitHub API unavailable.

        Args:
            use_cache: If True, use cached results. If False, fetch fresh from GitHub.

        Returns:
            List of repository info dicts with name, url, description, etc.
        """
        # Return cached if available and requested
        if use_cache and self._dynamic_repos is not None:
            logger.info(f"Using cached repository list ({len(self._dynamic_repos)} repos)")
            return self._dynamic_repos

        # In cloud deployment without GitHub access, use hardcoded list directly
        github_service = self._get_github_service()
        if github_service is None:
            if IS_CLOUD_DEPLOYMENT:
                logger.info("🌐 Cloud deployment: Using hardcoded OFFICIAL_REPOS (GitHub API not available)")
            else:
                logger.warning("GitHub service not available - falling back to hardcoded repos")
            return self._get_hardcoded_repos_as_list()

        logger.info("Fetching ALL repositories from wso2-enterprise organization via GitHub API...")

        try:

            # Fetch all repos from wso2-enterprise org (no keyword filter to get ALL repos)
            all_repos = github_service.search_org_repositories(
                org="wso2-enterprise",
                keyword="",  # Empty keyword = get ALL repos
                per_page=100
            )

            logger.info(f"✅ Successfully fetched {len(all_repos)} repositories from wso2-enterprise")

            # Convert to our format
            formatted_repos = []
            for repo in all_repos:
                formatted_repos.append({
                    "name": repo.get("name", ""),
                    "full_name": repo.get("full_name", ""),
                    "organization": "wso2-enterprise",
                    "repository": repo.get("name", ""),
                    "description": repo.get("description", "") or "No description available",
                    "url": repo.get("url", ""),
                    "is_private": repo.get("is_private", True),
                    "language": repo.get("language", ""),
                    "updated_at": repo.get("updated_at", "")
                })

            # Cache the results
            self._dynamic_repos = formatted_repos

            return formatted_repos

        except Exception as e:
            logger.error(f"❌ Failed to fetch repositories from GitHub: {e}")
            logger.warning("Falling back to hardcoded OFFICIAL_REPOS list")
            # Fallback to hardcoded list
            return self._get_hardcoded_repos_as_list()

    def fetch_choreo_repos_only(self, use_cache: bool = True) -> List[Dict[str, str]]:
        """
        Fetch only repositories with 'choreo' keyword from wso2-enterprise organization.
        In cloud deployment (Choreo), falls back to hardcoded list if GitHub API unavailable.

        Args:
            use_cache: If True, use cached results. If False, fetch fresh from GitHub.

        Returns:
            List of Choreo-related repository info dicts
        """
        # In cloud deployment without GitHub access, use hardcoded list directly
        github_service = self._get_github_service()
        if github_service is None:
            if IS_CLOUD_DEPLOYMENT:
                logger.info("🌐 Cloud deployment: Using hardcoded Choreo repos (GitHub API not available)")
            else:
                logger.warning("GitHub service not available - falling back to hardcoded repos")
            # Filter hardcoded repos for choreo-related ones
            return [r for r in self._get_hardcoded_repos_as_list() if 'choreo' in r.get('name', '').lower()]

        logger.info("Fetching Choreo-related repositories from wso2-enterprise organization...")

        try:

            # Fetch repos with 'choreo' keyword
            choreo_repos = github_service.search_org_repositories(
                org="wso2-enterprise",
                keyword="choreo",
                per_page=100
            )

            logger.info(f"✅ Successfully fetched {len(choreo_repos)} Choreo repositories")

            # Convert to our format
            formatted_repos = []
            for repo in choreo_repos:
                formatted_repos.append({
                    "name": repo.get("name", ""),
                    "full_name": repo.get("full_name", ""),
                    "organization": "wso2-enterprise",
                    "repository": repo.get("name", ""),
                    "description": repo.get("description", "") or "No description available",
                    "url": repo.get("url", ""),
                    "is_private": repo.get("is_private", True),
                    "language": repo.get("language", ""),
                    "updated_at": repo.get("updated_at", "")
                })

            return formatted_repos

        except Exception as e:
            logger.error(f"❌ Failed to fetch Choreo repositories from GitHub: {e}")
            logger.warning("Falling back to hardcoded OFFICIAL_REPOS list")
            return self._get_hardcoded_repos_as_list()

    def _get_hardcoded_repos_as_list(self) -> List[Dict[str, str]]:
        """Convert hardcoded OFFICIAL_REPOS dict to list format for fallback."""
        repos = []
        for comp_name, (org, repo, desc) in self.OFFICIAL_REPOS.items():
            repos.append({
                "name": repo,
                "full_name": f"{org}/{repo}",
                "organization": org,
                "repository": repo,
                "description": desc,
                "url": f"{self.GITHUB_BASE}/{org}/{repo}",
                "is_private": True,
                "language": "",
                "updated_at": ""
            })
        return repos

    def get_component_url(self, component_name: str, use_dynamic: bool = True) -> Optional[str]:
        """
        Get the GitHub URL for a Choreo component repository.
        Now searches in dynamically fetched repos, not just hardcoded ones.

        Args:
            component_name: Name of the component (e.g., 'choreo-console' or 'project manager')
            use_dynamic: If True, search in all fetched repos. If False, use hardcoded only.

        Returns:
            Full GitHub URL or None if component not found
        """
        # Normalize component name
        component_name = component_name.lower().strip()

        # Check cache first
        cache_key = f"{component_name}_{use_dynamic}"
        if cache_key in self._url_cache:
            return self._url_cache[cache_key]

        # Check aliases (hardcoded shortcuts)
        if component_name in self.ALIASES:
            component_name = self.ALIASES[component_name]

        # First try exact match in hardcoded repos for performance
        if component_name in self.OFFICIAL_REPOS:
            org, repo, _ = self.OFFICIAL_REPOS[component_name]
            url = f"{self.GITHUB_BASE}/{org}/{repo}"
            self._url_cache[cache_key] = url
            return url

        # If not found and dynamic search enabled, search all repos
        if use_dynamic:
            search_results = self.search_components(component_name, use_dynamic=True)
            if search_results:
                # Return the best match
                best_match = search_results[0]
                url = best_match.get("url")
                if url:
                    self._url_cache[cache_key] = url
                    return url

        return None

    def get_component_info(self, component_name: str, use_dynamic: bool = True) -> Optional[Dict[str, str]]:
        """
        Get detailed information about a Choreo component.
        Now searches in dynamically fetched repos, not just hardcoded ones.

        Args:
            component_name: Name of the component
            use_dynamic: If True, search in all fetched repos. If False, use hardcoded only.

        Returns:
            Dictionary with component details or None if not found
        """
        component_name = component_name.lower().strip()

        # Check aliases
        if component_name in self.ALIASES:
            component_name = self.ALIASES[component_name]

        # First try hardcoded for exact matches
        if component_name in self.OFFICIAL_REPOS:
            org, repo, description = self.OFFICIAL_REPOS[component_name]
            base_url = f"{self.GITHUB_BASE}/{org}/{repo}"
            return {
                "name": component_name,
                "organization": org,
                "repository": repo,
                "description": description,
                "url": base_url,
                "issues_url": f"{base_url}/issues",
                "docs_url": f"{base_url}#readme"
            }

        # If not found and dynamic search enabled, search all repos
        if use_dynamic:
            search_results = self.search_components(component_name, use_dynamic=True)
            if search_results:
                # Return the best match
                best_match = search_results[0]
                base_url = best_match.get("url", "")
                return {
                    "name": best_match.get("name", ""),
                    "organization": best_match.get("organization", "wso2-enterprise"),
                    "repository": best_match.get("repository", ""),
                    "description": best_match.get("description", "No description available"),
                    "url": base_url,
                    "issues_url": f"{base_url}/issues" if base_url else "",
                    "docs_url": f"{base_url}#readme" if base_url else "",
                    "language": best_match.get("language", ""),
                    "is_private": best_match.get("is_private", True)
                }

        return None

    def is_valid_choreo_component(self, component_name: str) -> bool:
        """
        Check if a component name is a valid Choreo component.

        Args:
            component_name: Name to check

        Returns:
            True if valid Choreo component, False otherwise
        """
        component_name = component_name.lower().strip()

        # Check aliases
        if component_name in self.ALIASES:
            component_name = self.ALIASES[component_name]

        return component_name in self.OFFICIAL_REPOS

    def extract_components_from_text(self, text: str) -> List[str]:
        """
        Extract Choreo component names from text.

        Args:
            text: Text to search for component names

        Returns:
            List of found component names
        """
        matches = self._component_pattern.findall(text)
        # Deduplicate and normalize
        components = list(set(m.lower() for m in matches))
        # Filter to only valid components
        return [c for c in components if self.is_valid_choreo_component(c)]

    def get_all_components(self) -> List[Dict[str, str]]:
        """
        Get information about all registered Choreo components.

        Returns:
            List of component information dictionaries
        """
        components = []
        for component_name in sorted(self.OFFICIAL_REPOS.keys()):
            info = self.get_component_info(component_name)
            if info:
                components.append(info)
        return components

    def validate_github_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Validate if a GitHub URL corresponds to an official Choreo repository.
        Checks both wso2 and wso2-enterprise organizations, prefers wso2-enterprise.

        Args:
            url: GitHub URL to validate

        Returns:
            Component info if valid, None otherwise
        """
        # Extract org and repo from URL
        # Pattern: https://github.com/{org}/{repo}
        pattern = r'github\.com/([^/]+)/([^/]+?)(?:/|$|\?|#)'
        match = re.search(pattern, url)

        if not match:
            return None

        org, repo = match.groups()
        org = org.lower().strip()
        repo = repo.lower().strip()

        # Check if this matches any official repo
        for component_name, (official_org, official_repo, description) in self.OFFICIAL_REPOS.items():
            if repo == official_repo.lower():
                # Found matching repository name
                # Check if organization matches (wso2 or wso2-enterprise both acceptable)
                if org in ["wso2", "wso2-enterprise"]:
                    # Prefer wso2-enterprise over wso2 (has main Choreo information)
                    correct_org = "wso2-enterprise"
                    correct_url = f"{self.GITHUB_BASE}/{correct_org}/{official_repo}"

                    return {
                        "component": component_name,
                        "organization": correct_org,
                        "repository": official_repo,
                        "description": description,
                        "is_valid": True,
                        "correct_url": correct_url,
                        "needs_org_fix": org != correct_org
                    }

        return None

    def fix_github_url(self, url: str) -> Optional[str]:
        """
        Fix a potentially incorrect GitHub URL to point to the correct repository.
        Converts wso2-enterprise to wso2 organization if needed.

        Args:
            url: Potentially incorrect GitHub URL

        Returns:
            Corrected URL or None if cannot be fixed or already correct
        """
        validation = self.validate_github_url(url)
        if validation:
            correct_url = validation.get("correct_url")
            needs_fix = validation.get("needs_org_fix", False)

            # If it needs organization fix or the URL is different, return corrected
            if needs_fix or (correct_url and correct_url != url):
                return correct_url

        return None

    def enrich_text_with_urls(self, text: str) -> str:
        """
        Enrich text by adding GitHub URLs next to component mentions.

        Args:
            text: Text containing component names

        Returns:
            Enriched text with URLs
        """
        components = self.extract_components_from_text(text)

        enriched_text = text
        for component in components:
            url = self.get_component_url(component)
            if url:
                # Add URL reference if component is mentioned without a link
                # Only add if the URL isn't already in the text
                if url not in enriched_text:
                    # Find the component mention and add URL
                    pattern = r'\b' + re.escape(component) + r'\b'
                    replacement = f"{component} ({url})"
                    enriched_text = re.sub(pattern, replacement, enriched_text, count=1, flags=re.IGNORECASE)

        return enriched_text

    def get_component_markdown_links(self) -> str:
        """
        Generate a markdown list of all components with links.

        Returns:
            Markdown formatted string
        """
        components = self.get_all_components()
        lines = ["# Choreo Components\n"]

        for comp in components:
            lines.append(f"- **{comp['name']}**: {comp['description']}")
            lines.append(f"  - Repository: [{comp['organization']}/{comp['repository']}]({comp['url']})")
            lines.append("")

        return "\n".join(lines)

    def search_components(self, query: str, use_dynamic: bool = True) -> List[Dict[str, str]]:
        """
        Search for components matching a query.
        Now uses dynamic repository fetching to search ALL repos, not just hardcoded ones.

        Args:
            query: Search query
            use_dynamic: If True, search in dynamically fetched repos. If False, use hardcoded list.

        Returns:
            List of matching component info sorted by relevance
        """
        query_lower = query.lower().strip()
        results = []

        # Get repos to search (dynamic or hardcoded)
        if use_dynamic:
            try:
                # Fetch all repos dynamically
                repos = self.fetch_all_wso2_enterprise_repos(use_cache=True)
            except Exception as e:
                logger.error(f"Failed to fetch dynamic repos for search, using hardcoded: {e}")
                repos = self._get_hardcoded_repos_as_list()
        else:
            repos = self._get_hardcoded_repos_as_list()

        # Search through all repos
        for repo in repos:
            repo_name = repo.get("name", "").lower()
            repo_desc = repo.get("description", "").lower()

            # Check if query matches name or description
            if (query_lower in repo_name or
                query_lower in repo_desc or
                self._fuzzy_match(query_lower, repo_name) or
                self._fuzzy_match(query_lower, repo_desc)):

                results.append({
                    "name": repo.get("name", ""),
                    "organization": repo.get("organization", "wso2-enterprise"),
                    "repository": repo.get("name", ""),
                    "description": repo.get("description", "No description available"),
                    "url": repo.get("url", ""),
                    "relevance_score": self._calculate_relevance(query_lower, repo_name, repo_desc),
                    "language": repo.get("language", ""),
                    "is_private": repo.get("is_private", True)
                })

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        logger.info(f"Search for '{query}' found {len(results)} matching repositories")

        return results

    def _fuzzy_match(self, query: str, text: str) -> bool:
        """
        Check if query words fuzzy match the text.

        Examples:
            - "project manager" matches "choreo-product-management"
            - "security token service" matches "choreo-sts" or "token-service"
        """
        query_words = query.split()
        text_lower = text.lower()

        # Check if all query words appear in text (in any order)
        matches = sum(1 for word in query_words if word in text_lower)

        # Enhanced synonym mapping for better matching
        synonyms = {
            'manager': ['management', 'mgmt', 'mgr', 'mgt'],
            'service': ['svc', 'srv', 'sts'],  # STS = Security Token Service
            'security': ['sec', 'auth', 'authz', 'authorization'],
            'token': ['tok'],
            'project': ['proj', 'product'],
            'built-in': ['builtin', 'built', 'internal'],
        }

        # Acronym detection for common patterns
        # "security token service" should match "sts"
        acronyms = {
            'sts': ['security token service', 'security token', 'token service'],
            'idp': ['identity provider'],
            'apim': ['api manager', 'api management'],
            'iam': ['identity access management'],
        }

        # Check if text contains an acronym that matches the query
        for acronym, expansions in acronyms.items():
            if acronym in text_lower:
                for expansion in expansions:
                    if expansion in query.lower():
                        matches += 3.0  # Strong match for acronym expansion
                        break

        # Check synonyms
        for word in query_words:
            if word in synonyms:
                for syn in synonyms[word]:
                    if syn in text_lower:
                        matches += 0.8  # Higher weight for synonyms

        # Return True if at least half the query words match
        return matches >= len(query_words) * 0.5

    def _calculate_relevance(self, query: str, name: str, description: str) -> float:
        """Calculate relevance score for search results."""
        score = 0.0
        query_lower = query.lower()
        name_lower = name.lower()
        description_lower = description.lower()

        # Exact match in name (highest priority)
        if query_lower == name_lower:
            score += 100.0
        # Query is in name
        elif query_lower in name_lower:
            score += 50.0

        # Exact match in description (high priority for finding specific services)
        if query_lower in description_lower:
            score += 30.0

        # Check for exact phrase match in description (very important)
        if query_lower in description_lower:
            score += 40.0

        # Bonus for choreo-prefixed repos when query contains "choreo"
        if 'choreo' in query_lower and name_lower.startswith('choreo-'):
            score += 25.0

        # Word matching
        query_words = set(query_lower.split())
        name_words = set(name_lower.replace('-', ' ').replace('_', ' ').split())
        desc_words = set(description_lower.split())

        common_with_name = len(query_words & name_words)
        common_with_desc = len(query_words & desc_words)

        score += common_with_name * 15.0
        score += common_with_desc * 10.0

        # Bonus for matching all query words
        if query_words.issubset(name_words):
            score += 60.0
        if query_words.issubset(desc_words):
            score += 50.0

        # Enhanced synonym and acronym matching
        synonyms = {
            'manager': ['management', 'mgmt', 'mgr', 'mgt'],
            'service': ['svc', 'srv', 'sts'],
            'security': ['sec', 'auth', 'authz'],
            'token': ['tok'],
            'project': ['proj', 'product'],
            'product': ['proj', 'project'],  # Bidirectional synonym
        }

        # Acronym bonus (very important for matching like "sts" to "security token service")
        acronyms = {
            'sts': 'security token service',
            'idp': 'identity provider',
            'apim': 'api manager',
        }

        # Check if name contains acronym and query is the expansion
        for acronym, expansion in acronyms.items():
            if acronym in name_lower and expansion in query_lower:
                score += 80.0  # Very high score for acronym match
            if acronym in name_lower and any(word in query_lower for word in expansion.split()):
                score += 40.0  # Partial acronym match

        # Check synonyms with higher weights
        for word in query_words:
            if word in synonyms:
                for syn in synonyms[word]:
                    if syn in name_lower:
                        score += 20.0
                    if syn in description_lower:
                        score += 15.0

        return score

    def generate_system_prompt_urls(self, use_dynamic: bool = True) -> str:
        """
        Generate a comprehensive system prompt section with all Choreo repository URLs.
        This ensures the LLM always uses the correct wso2-enterprise organization URLs.

        Args:
            use_dynamic: If True, fetch repos dynamically from GitHub. If False, use hardcoded list.

        Returns:
            Formatted string with repository URL instructions
        """
        prompt = """REPOSITORY URLS - CRITICAL RULES:
⚠️ ALWAYS use wso2-enterprise organization for ALL Choreo repositories
⚠️ NEVER use github.com/wso2/{repo} - it's WRONG and leads to 404 errors
⚠️ Each Choreo component has its OWN separate repository

CORRECT URL FORMAT:
https://github.com/wso2-enterprise/{repository-name}

"""

        # Get repositories dynamically or from hardcoded list
        if use_dynamic:
            try:
                repos = self.fetch_all_wso2_enterprise_repos(use_cache=True)
                prompt += f"ALL WSO2-ENTERPRISE REPOSITORIES ({len(repos)} total, dynamically fetched):\n"
            except Exception as e:
                logger.error(f"Failed to fetch dynamic repos, using hardcoded list: {e}")
                repos = self._get_hardcoded_repos_as_list()
                prompt += f"ALL WSO2-ENTERPRISE REPOSITORIES ({len(repos)} total, from fallback list):\n"
        else:
            repos = self._get_hardcoded_repos_as_list()
            prompt += f"ALL WSO2-ENTERPRISE REPOSITORIES ({len(repos)} total, from static list):\n"

        # Group repos for better readability
        choreo_repos = [r for r in repos if 'choreo' in r['name'].lower()]
        other_repos = [r for r in repos if 'choreo' not in r['name'].lower()]

        if choreo_repos:
            prompt += "\nChoreo Platform Repositories:\n"
            for repo in sorted(choreo_repos, key=lambda x: x['name']):
                desc = repo.get('description', 'No description')
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                prompt += f"  • {repo['name']}: {repo['url']}\n    ({desc})\n"

        if other_repos:
            prompt += f"\nOther wso2-enterprise Repositories ({len(other_repos)}):\n"
            for repo in sorted(other_repos[:20], key=lambda x: x['name']):  # Limit to first 20 to avoid prompt overflow
                prompt += f"  • {repo['name']}: {repo['url']}\n"
            if len(other_repos) > 20:
                prompt += f"  ... and {len(other_repos) - 20} more repositories\n"

        prompt += """

CRITICAL REMINDERS:
✓ ONLY use wso2-enterprise organization URLs
✓ Format: https://github.com/wso2-enterprise/{repository-name}
✗ NEVER use: https://github.com/wso2/{anything} (this is PUBLIC org, not Choreo)
✗ Do NOT make up URLs - only use the ones listed above

If you need to reference a repository not listed above, say you don't have the URL rather than guessing.
"""

        return prompt


# Singleton instance
_registry_instance: Optional[ChoreoRepoRegistry] = None


def get_choreo_registry() -> ChoreoRepoRegistry:
    """
    Get the singleton instance of the Choreo repository registry.
    Works in both local and cloud (Choreo) deployments.

    Returns:
        ChoreoRepoRegistry instance
    """
    global _registry_instance

    if _registry_instance is None:
        _registry_instance = ChoreoRepoRegistry()
        deployment_mode = "CLOUD (Choreo)" if IS_CLOUD_DEPLOYMENT else "LOCAL"
        dynamic_available = _registry_instance.is_dynamic_fetch_available()

        logger.info(f"Choreo repository registry initialized:")
        logger.info(f"  - Deployment mode: {deployment_mode}")
        logger.info(f"  - Hardcoded repos: {len(_registry_instance.OFFICIAL_REPOS)} components")
        logger.info(f"  - Dynamic GitHub fetch: {'Available' if dynamic_available else 'Not available (using hardcoded list)'}")

    return _registry_instance


def get_deployment_info() -> Dict[str, any]:
    """
    Get information about the current deployment environment.

    Returns:
        Dictionary with deployment details
    """
    registry = get_choreo_registry()
    return {
        "is_cloud_deployment": IS_CLOUD_DEPLOYMENT,
        "deployment_mode": "cloud" if IS_CLOUD_DEPLOYMENT else "local",
        "dynamic_fetch_available": registry.is_dynamic_fetch_available(),
        "hardcoded_repos_count": len(registry.OFFICIAL_REPOS),
        "internal_docs_count": len(registry.INTERNAL_DOCS),
        "url_corrections_count": len(registry.INVALID_DOC_URL_CORRECTIONS),
    }

