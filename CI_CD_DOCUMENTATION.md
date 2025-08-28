# ReliQuary CI/CD Pipeline Documentation

## Overview

This document provides comprehensive documentation for the ReliQuary CI/CD pipeline system. The pipeline automates building, testing, security scanning, and deployment of all components including the core platform, SDKs, and website.

## Pipeline Components

### 1. Build and Test Pipeline

The build and test pipeline ensures code quality and functionality across all components:

- **Languages Supported**: Python, JavaScript/TypeScript, Go, Java
- **Testing Frameworks**: pytest, Jest, Go testing, JUnit
- **Linting**: flake8, ESLint, Go fmt, Checkstyle
- **Code Coverage**: Codecov integration

### 2. Security Scanning

Security is integrated at every stage:

- **Dependency Scanning**: Safety, npm audit, Go vulnerability detection
- **Container Scanning**: Trivy for Docker image scanning
- **Code Analysis**: CodeQL for static analysis
- **Secrets Detection**: GitHub secret scanning

### 3. Semantic Versioning

The pipeline uses conventional commits for automatic version bumping:

- **Version Format**: MAJOR.MINOR.PATCH
- **Release Branches**: `main` for production releases
- **Pre-release Branches**: `develop` for beta releases
- **Changelog Generation**: Automatic changelog creation

### 4. Multi-Platform Builds

All Docker images are built for multiple architectures:

- **AMD64**: Standard x86_64 processors
- **ARM64**: Apple Silicon, AWS Graviton, Raspberry Pi
- **ARM/v7**: 32-bit ARM devices

### 5. SDK Publishing

Automated publishing to all major package repositories:

- **Python**: PyPI
- **JavaScript**: npm
- **Java**: Maven Central
- **Go**: GitHub Tags

### 6. Deployment Strategies

Multiple deployment strategies are supported:

- **Blue-Green Deployment**: Zero-downtime deployments with instant rollback
- **Canary Releases**: Gradual traffic shifting for risk mitigation
- **Rolling Updates**: Standard Kubernetes deployment pattern
- **Staging Environment**: Pre-production validation

## Workflow Triggers

### Automated Triggers

1. **Push to `main` branch**: Full CI/CD pipeline with production deployment
2. **Push to `develop` branch**: CI/CD pipeline with staging deployment
3. **Pull Requests**: Build and test validation
4. **Scheduled Builds**: Weekly security updates

### Manual Triggers

1. **Workflow Dispatch**: Manual triggering of any pipeline
2. **Release Creation**: Manual release creation

## Environment Variables

The following environment variables are used across workflows:

| Variable                | Description                              | Required |
| ----------------------- | ---------------------------------------- | -------- |
| `GITHUB_TOKEN`          | GitHub authentication token              | Yes      |
| `PYPI_API_TOKEN`        | PyPI API token for Python SDK publishing | Yes      |
| `NPM_TOKEN`             | npm token for JavaScript SDK publishing  | Yes      |
| `OSSRH_USERNAME`        | Maven Central username                   | Yes      |
| `OSSRH_TOKEN`           | Maven Central token                      | Yes      |
| `MAVEN_GPG_PRIVATE_KEY` | GPG key for Java SDK signing             | Yes      |
| `MAVEN_GPG_PASSPHRASE`  | GPG passphrase                           | Yes      |
| `SLACK_WEBHOOK_URL`     | Slack webhook for notifications          | No       |

## Docker Images

The pipeline builds and publishes several Docker images:

1. **Platform Image**: Main ReliQuary platform
2. **Orchestrator Image**: Agent orchestrator service
3. **Website Image**: ReliQuary marketing website
4. **Minimal Images**: Smaller footprint images for constrained environments

Images are published to:

- GitHub Container Registry (GHCR)
- Docker Hub
- Amazon ECR (if configured)

## Monitoring and Observability

The CI/CD pipeline integrates with monitoring systems:

- **Build Metrics**: Duration, success/failure rates
- **Test Coverage**: Code coverage reporting
- **Security Alerts**: Vulnerability notifications
- **Deployment Status**: Success/failure notifications

## Rollback Procedures

In case of deployment failures:

1. **Blue-Green Rollback**: Instant traffic switch to previous version
2. **Canary Rollback**: Immediate traffic shift back to stable version
3. **Manual Rollback**: Kubernetes deployment rollback command

## Performance Testing

Performance benchmarks are run on every build:

- **Response Time**: API response time measurements
- **Throughput**: Requests per second testing
- **Resource Usage**: CPU and memory consumption
- **Scalability**: Load testing with increasing concurrency

## Best Practices

### Code Quality

1. All code must pass linting checks
2. Test coverage must be maintained above 80%
3. Security vulnerabilities must be addressed immediately
4. Documentation must be updated with code changes

### Git Workflow

1. Use conventional commits for clear changelogs
2. Create feature branches for all changes
3. Open pull requests for code review
4. Squash merge after approval

### Security

1. Never commit secrets to the repository
2. Regularly update dependencies
3. Run security scans on all pull requests
4. Follow the principle of least privilege

## Troubleshooting

### Common Issues

1. **Build Failures**: Check logs for specific error messages
2. **Test Failures**: Run tests locally to reproduce
3. **Deployment Failures**: Check Kubernetes events and pod logs
4. **Security Scan Failures**: Address reported vulnerabilities

### Contact

For issues with the CI/CD pipeline, contact the DevOps team or create an issue in the repository.
