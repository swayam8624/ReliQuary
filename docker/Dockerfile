# ReliQuary Container Registry Setup
# Multi-Architecture Docker Builds and Publishing

# Official Docker Hub images for ReliQuary Platform
# Supports AMD64, ARM64, and ARMv7 architectures

FROM --platform=$BUILDPLATFORM golang:1.21-alpine AS builder

# Build arguments
ARG TARGETOS
ARG TARGETARCH
ARG VERSION=latest
ARG BUILD_DATE
ARG VCS_REF

# Install build dependencies
RUN apk add --no-cache \
    git \
    ca-certificates \
    tzdata \
    gcc \
    musl-dev \
    linux-headers \
    make

# Set working directory
WORKDIR /build

# Copy go mod and sum files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=1 GOOS=${TARGETOS} GOARCH=${TARGETARCH} \
    go build -ldflags="-w -s -X main.version=${VERSION} -X main.buildDate=${BUILD_DATE} -X main.gitCommit=${VCS_REF}" \
    -o reliquary ./cmd/reliquary

# Production image
FROM alpine:3.18

# Install runtime dependencies
RUN apk --no-cache add \
    ca-certificates \
    tzdata \
    curl \
    jq \
    openssl \
    && addgroup -g 1001 -S reliquary \
    && adduser -u 1001 -S reliquary -G reliquary

# Set up directories
RUN mkdir -p /app/config /app/data /app/logs \
    && chown -R reliquary:reliquary /app

# Copy binary from builder
COPY --from=builder /build/reliquary /usr/local/bin/reliquary
RUN chmod +x /usr/local/bin/reliquary

# Copy configuration templates
COPY --chown=reliquary:reliquary configs/docker/ /app/config/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Switch to non-root user
USER reliquary

# Set working directory
WORKDIR /app

# Expose port
EXPOSE 8080

# Environment variables
ENV RELIQUARY_CONFIG_PATH="/app/config/config.yaml" \
    RELIQUARY_DATA_DIR="/app/data" \
    RELIQUARY_LOG_LEVEL="info" \
    RELIQUARY_LOG_FORMAT="json"

# Labels for metadata
LABEL \
    org.opencontainers.image.title="ReliQuary Platform" \
    org.opencontainers.image.description="Enterprise-Grade Cryptographic Memory Platform" \
    org.opencontainers.image.vendor="ReliQuary Team" \
    org.opencontainers.image.version="${VERSION}" \
    org.opencontainers.image.created="${BUILD_DATE}" \
    org.opencontainers.image.revision="${VCS_REF}" \
    org.opencontainers.image.source="https://github.com/reliquary/reliquary-platform" \
    org.opencontainers.image.documentation="https://docs.reliquary.io" \
    org.opencontainers.image.licenses="MIT"

# Entry point
ENTRYPOINT ["reliquary"]
CMD ["server", "--config", "/app/config/config.yaml"]