#!/bin/bash

# Create necessary directories
mkdir -p /app/logs /app/data /app/config

# Set proper permissions
chmod -R 777 /app/logs

# Start the application
python -m uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT --workers 2