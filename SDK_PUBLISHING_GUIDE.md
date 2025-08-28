# ReliQuary SDK Publishing Guide

This guide explains how to publish the ReliQuary SDKs to their respective package repositories.

## Prerequisites

Before publishing, you'll need to set up accounts and obtain API tokens for each repository:

1. **PyPI** - Python Package Index
2. **npm** - Node.js Package Manager
3. **Maven Central** - Java packages
4. **GitHub** - Go modules (tagged releases)

## Repository Setup

### PyPI Setup

1. Create an account at [pypi.org](https://pypi.org/)
2. Generate an API token:
   - Go to Account Settings → API tokens
   - Click "Add API token"
   - Give it a name like "reliquary-sdk"
   - Set scope to "Entire account" or specific project
   - Copy the token value

### npm Setup

1. Create an account at [npmjs.com](https://www.npmjs.com/)
2. Get your access token:
   - Go to Account Settings → Access Tokens
   - Click "Generate New Token"
   - Select "Automation" type
   - Copy the token value

### Maven Central Setup

1. Sign up for Sonatype OSSRH at [https://issues.sonatype.org](https://issues.sonatype.org)
2. Create a JIRA ticket to request access to io.reliquary groupId
3. Generate GPG keys for signing artifacts:
   ```bash
   gpg --gen-key
   gpg --armor --export-secret-keys YOUR_KEY_ID > private.key
   ```
4. Get your OSSRH credentials:
   - Username: Your Sonatype JIRA username
   - Password: Your Sonatype JIRA password

## GitHub Secrets Configuration

Add the following secrets to your GitHub repository settings:

1. **PYPI_API_TOKEN** - PyPI API token
2. **NPM_TOKEN** - npm access token
3. **OSSRH_USERNAME** - Sonatype OSSRH username
4. **OSSRH_TOKEN** - Sonatype OSSRH password
5. **MAVEN_GPG_PRIVATE_KEY** - GPG private key for signing
6. **MAVEN_GPG_PASSPHRASE** - Passphrase for GPG key

## Publishing Process

### Manual Publishing

To manually publish a new version:

1. Update version numbers in all SDK configuration files:

   - Python: `sdk/python/pyproject.toml`
   - JavaScript: `sdk/javascript/package.json`
   - Java: `sdk/java/pom.xml`

2. Create a Git tag:

   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

3. Run the publishing workflows manually from GitHub Actions.

### Automated Publishing

The publishing workflows are triggered automatically when you create a new GitHub Release:

1. Go to GitHub → Releases → Draft a new release
2. Create a new tag (e.g., v1.0.0)
3. Fill in release notes
4. Publish release

This will automatically trigger all the publishing workflows.

## Package Verification

After publishing, verify that packages are available:

- **PyPI**: https://pypi.org/project/reliquary-sdk/
- **npm**: https://www.npmjs.com/package/@reliquary/sdk
- **Maven Central**: https://search.maven.org/artifact/io.reliquary/reliquary-sdk
- **Go**: `go get github.com/reliquary/go-sdk@latest`

## Troubleshooting

### Common Issues

1. **Authentication failures**: Check that all secrets are correctly configured
2. **Version conflicts**: Ensure version numbers are unique
3. **Build failures**: Check that all dependencies are correctly specified
4. **Publishing timeouts**: Increase timeout values in workflow files

### Getting Help

If you encounter issues:

1. Check workflow logs in GitHub Actions
2. Verify repository credentials
3. Ensure all required files are present
4. Contact the ReliQuary team for assistance
