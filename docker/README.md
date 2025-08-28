# ReliQuary Platform - Docker Images

![Docker Pulls](https://img.shields.io/docker/pulls/reliquary/platform)
![Docker Image Size](https://img.shields.io/docker/image-size/reliquary/platform)
![Docker Stars](https://img.shields.io/docker/stars/reliquary/platform)

Enterprise-Grade Cryptographic Memory Platform with Post-Quantum Security, Multi-Agent Consensus, and Zero-Knowledge Proofs.

## Quick Start

### One-Line Deployment

```bash
# Production ready with all components
docker run -d \
  --name reliquary \
  -p 8080:8080 \
  -e RELIQUARY_LOG_LEVEL=info \
  reliquary/platform:latest
```

### Docker Compose (Recommended)

```bash
# Download production configuration
curl -sSL https://raw.githubusercontent.com/reliquary/reliquary-platform/main/docker/docker-compose.prod.yml -o docker-compose.yml

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Deploy
docker-compose up -d
```

## Available Images

### Standard Image (`latest`)

- **Size**: ~50MB compressed
- **Base**: Alpine Linux
- **Architecture**: `linux/amd64`, `linux/arm64`, `linux/arm/v7`
- **Use Case**: Production deployments

```bash
docker pull reliquary/platform:latest
```

### Minimal Image (`minimal`)

- **Size**: ~15MB compressed
- **Base**: `scratch`
- **Architecture**: `linux/amd64`, `linux/arm64`, `linux/arm/v7`
- **Use Case**: Resource-constrained environments

```bash
docker pull reliquary/platform:minimal
```

### Development Image (`dev`)

- **Size**: ~200MB compressed
- **Base**: Full Go environment
- **Architecture**: `linux/amd64`, `linux/arm64`
- **Use Case**: Development and debugging

```bash
docker pull reliquary/platform:dev
```

## Configuration

### Environment Variables

| Variable                   | Description                              | Default                   | Required |
| -------------------------- | ---------------------------------------- | ------------------------- | -------- |
| `RELIQUARY_LOG_LEVEL`      | Logging level (debug, info, warn, error) | `info`                    | No       |
| `RELIQUARY_LOG_FORMAT`     | Log format (json, text)                  | `json`                    | No       |
| `RELIQUARY_CONFIG_PATH`    | Configuration file path                  | `/app/config/config.yaml` | No       |
| `RELIQUARY_DATA_DIR`       | Data directory                           | `/app/data`               | No       |
| `RELIQUARY_DATABASE_URL`   | PostgreSQL connection string             | -                         | Yes      |
| `RELIQUARY_REDIS_URL`      | Redis connection string                  | -                         | Yes      |
| `RELIQUARY_JWT_SECRET`     | JWT signing secret                       | -                         | Yes      |
| `RELIQUARY_ENCRYPTION_KEY` | Data encryption key (32 bytes)           | -                         | Yes      |

### Volumes

| Path          | Description             |
| ------------- | ----------------------- |
| `/app/data`   | Persistent data storage |
| `/app/logs`   | Application logs        |
| `/app/config` | Configuration files     |

### Ports

| Port   | Description                     |
| ------ | ------------------------------- |
| `8080` | HTTP API server                 |
| `2345` | Delve debugger (dev image only) |

## Security

### Running as Non-Root

All images run as a non-root user (`reliquary:reliquary`, UID/GID 1001) by default.

### Health Checks

Built-in health checks monitor service availability:

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Manual health check
docker exec reliquary reliquary health
```

### Secret Management

Use Docker secrets or external secret management:

```bash
# Using Docker secrets
echo "your-jwt-secret" | docker secret create jwt_secret -
docker service create \
  --name reliquary \
  --secret jwt_secret \
  -e RELIQUARY_JWT_SECRET_FILE=/run/secrets/jwt_secret \
  reliquary/platform:latest
```

## Examples

### Development Setup

```bash
# Clone the repository
git clone https://github.com/reliquary/reliquary-platform.git
cd reliquary-platform

# Start development environment
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f reliquary
```

### Production with PostgreSQL and Redis

```yaml
version: "3.8"
services:
  reliquary:
    image: reliquary/platform:latest
    ports:
      - "8080:8080"
    environment:
      - RELIQUARY_DATABASE_URL=postgres://user:pass@postgres:5432/reliquary
      - RELIQUARY_REDIS_URL=redis://redis:6379/0
      - RELIQUARY_JWT_SECRET=your-secure-jwt-secret
      - RELIQUARY_ENCRYPTION_KEY=your-32-byte-encryption-key-here
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=reliquary
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes

volumes:
  postgres_data:
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: reliquary
spec:
  replicas: 3
  selector:
    matchLabels:
      app: reliquary
  template:
    metadata:
      labels:
        app: reliquary
    spec:
      containers:
        - name: reliquary
          image: reliquary/platform:latest
          ports:
            - containerPort: 8080
          env:
            - name: RELIQUARY_LOG_LEVEL
              value: "info"
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
```

## Building Custom Images

### Build Arguments

| Argument     | Description         | Default        |
| ------------ | ------------------- | -------------- |
| `VERSION`    | Application version | `latest`       |
| `BUILD_DATE` | Build timestamp     | Current time   |
| `VCS_REF`    | Git commit hash     | Current commit |

### Custom Build

```bash
# Build with custom version
docker build \
  --build-arg VERSION=v1.0.0 \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VCS_REF=$(git rev-parse HEAD) \
  -t my-reliquary:v1.0.0 \
  -f docker/Dockerfile .

# Multi-architecture build
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --push \
  -t my-reliquary:v1.0.0 \
  -f docker/Dockerfile .
```

## Monitoring and Observability

### Prometheus Metrics

Metrics available at `/metrics` endpoint:

- Request counts and latencies
- Error rates
- Database connection pool stats
- Cryptographic operation metrics

### Structured Logging

JSON formatted logs with correlation IDs:

```bash
# View structured logs
docker logs reliquary | jq '.'

# Filter by log level
docker logs reliquary | jq 'select(.level == "error")'
```

### Tracing

Jaeger tracing support with OpenTelemetry:

```bash
# Enable tracing
docker run -d \
  -e RELIQUARY_TRACING_ENABLED=true \
  -e RELIQUARY_JAEGER_ENDPOINT=http://jaeger:14268/api/traces \
  reliquary/platform:latest
```

## Support and Documentation

- **Documentation**: https://docs.reliquary.io
- **API Reference**: https://api.reliquary.io/docs
- **GitHub**: https://github.com/reliquary/reliquary-platform
- **Issues**: https://github.com/reliquary/reliquary-platform/issues
- **Security**: security@reliquary.io

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/reliquary/reliquary-platform/blob/main/LICENSE) file for details.

## Tags and Versions

### Stable Releases

- `latest` - Latest stable release
- `v1.0.0`, `v1.0`, `v1` - Semantic version tags
- `minimal` - Latest minimal build

### Development Builds

- `dev` - Latest development build
- `main-<commit>` - Main branch builds
- `develop-<commit>` - Development branch builds

### Multi-Architecture Support

All images support multiple architectures:

- `linux/amd64` (Intel/AMD 64-bit)
- `linux/arm64` (ARM 64-bit, Apple Silicon, AWS Graviton)
- `linux/arm/v7` (ARM 32-bit, Raspberry Pi)

---

**ReliQuary Platform** - Securing the future of data with post-quantum cryptography and zero-knowledge proofs.
