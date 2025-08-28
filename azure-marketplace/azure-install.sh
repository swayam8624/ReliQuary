#!/bin/bash

# ReliQuary Azure Installation Script
# This script installs and configures ReliQuary on an Azure VM

set -e

# Check if admin email is provided
if [ -z "$1" ]; then
    echo "Error: Admin email not provided"
    echo "Usage: $0 <admin-email>"
    exit 1
fi

ADMIN_EMAIL=$1

# Update system
echo "Updating system packages..."
apt-get update -y
apt-get upgrade -y

# Install Docker
echo "Installing Docker..."
apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
echo "Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Create reliquary user
echo "Creating reliquary user..."
useradd -m -s /bin/bash reliquary
usermod -aG docker reliquary

# Create installation directory
mkdir -p /opt/reliquary
chown reliquary:reliquary /opt/reliquary
cd /opt/reliquary

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  platform:
    image: ghcr.io/reliquary/platform:latest
    container_name: reliquary-platform
    ports:
      - "8080:8080"
    environment:
      - ADMIN_EMAIL=${ADMIN_EMAIL}
      - AZURE_REGION=${AZURE_REGION}
      - LOG_LEVEL=info
    volumes:
      - platform-data:/data
      - ./logs:/var/log/reliquary
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  orchestrator:
    image: ghcr.io/reliquary/orchestrator:latest
    container_name: reliquary-orchestrator
    ports:
      - "8081:8081"
    environment:
      - PLATFORM_URL=http://platform:8080
      - AZURE_REGION=${AZURE_REGION}
      - LOG_LEVEL=info
    depends_on:
      platform:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  nginx:
    image: nginx:alpine
    container_name: reliquary-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - platform
      - orchestrator
    restart: unless-stopped

volumes:
  platform-data:
EOF

# Set admin email in environment
echo "ADMIN_EMAIL=${ADMIN_EMAIL}" > .env
echo "AZURE_REGION=$(curl -s -H Metadata:true "http://169.254.169.254/metadata/instance?api-version=2021-02-01" | jq -r '.compute.location')" >> .env

# Create basic nginx configuration
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream reliquary_backend {
        server platform:8080;
    }
    
    upstream orchestrator_backend {
        server orchestrator:8081;
    }
    
    server {
        listen 80;
        server_name _;
        
        location / {
            proxy_pass http://reliquary_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        location /api/orchestrator/ {
            proxy_pass http://orchestrator_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

# Create log directory
mkdir -p logs
chown -R reliquary:reliquary logs

# Pull Docker images
echo "Pulling ReliQuary Docker images..."
sudo -u reliquary docker-compose pull

# Start services
echo "Starting ReliQuary services..."
sudo -u reliquary docker-compose up -d

# Install Azure CLI for monitoring
echo "Installing Azure CLI..."
curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Create health check script
cat > /opt/reliquary/health-check.sh << 'EOF'
#!/bin/bash

# Health check script for ReliQuary
ADMIN_EMAIL=$(grep ADMIN_EMAIL /opt/reliquary/.env | cut -d '=' -f2)

# Check if containers are running
if ! sudo docker-compose ps | grep -q "Up"; then
    echo "ReliQuary containers are not running properly"
    # Send alert via Azure CLI (would typically use Azure Monitor/SNS)
    echo "ReliQuary health check failed" | mail -s "ReliQuary Health Alert" $ADMIN_EMAIL
    exit 1
fi

# Check platform health endpoint
if ! curl -f http://localhost:8080/health >/dev/null 2>&1; then
    echo "ReliQuary platform health check failed"
    echo "ReliQuary platform health check failed" | mail -s "ReliQuary Health Alert" $ADMIN_EMAIL
    exit 1
fi

# Check orchestrator health endpoint
if ! curl -f http://localhost:8081/health >/dev/null 2>&1; then
    echo "ReliQuary orchestrator health check failed"
    echo "ReliQuary orchestrator health check failed" | mail -s "ReliQuary Health Alert" $ADMIN_EMAIL
    exit 1
fi

echo "All health checks passed"
exit 0
EOF

chmod +x /opt/reliquary/health-check.sh

# Set up cron job for health checks
echo "Setting up health check cron job..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/reliquary/health-check.sh") | crontab -

# Create systemd service for automatic startup
cat > /etc/systemd/system/reliquary.service << 'EOF'
[Unit]
Description=ReliQuary Platform
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/reliquary
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable reliquary.service

# Output completion message
echo "ReliQuary installation completed successfully!"
echo "Access your ReliQuary instance at: http://$(curl -s http://169.254.169.254/metadata/instance/network/interface/0/ipv4/ipAddress/0/publicIpAddress?api-version=2021-02-01&format=text)"
echo "API endpoint: http://$(curl -s http://169.254.169.254/metadata/instance/network/interface/0/ipv4/ipAddress/0/publicIpAddress?api-version=2021-02-01&format=text):8080"
echo "Admin email notifications will be sent to: ${ADMIN_EMAIL}"

# Final status check
echo "Performing final status check..."
sleep 30
sudo -u reliquary docker-compose ps