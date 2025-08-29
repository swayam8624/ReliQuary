# Deploying ReliQuary to Render

## Prerequisites

1. A Render account (https://render.com)
2. This repository connected to your Render account

## Deployment Steps

### 1. Create a New Web Service

1. Log in to your Render account
2. Click the "New" button in the dashboard
3. Select "Web Service"

### 2. Connect Your Repository

1. Choose "GitHub" as the source
2. Find and select the "swayam8624/ReliQuary" repository
3. Select the "main" branch

### 3. Configure the Service

Set the following configuration:

- **Name**: reliquary-platform
- **Environment**: Docker
- **Dockerfile Path**: ./Dockerfile.platform
- **Root Directory**: . (current directory)

### 4. Set Environment Variables

In the "Environment Variables" section, add:

```
PORT=8000
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 5. Advanced Settings

- **Plan**: Free (or choose a paid plan for production)
- **Instance Count**: 1
- **Health Check Path**: /health

### 6. Deploy

Click "Create Web Service" to start the deployment.

## Post-Deployment

Once deployed, your ReliQuary platform will be accessible at a URL like:
`https://reliquary-platform-<random-string>.onrender.com`

You can test the deployment by visiting:

- Health check: `https://your-app-url.onrender.com/health`
- API docs: `https://your-app-url.onrender.com/docs`

## Troubleshooting

If you encounter issues:

1. **Build Failures**: Check the build logs in the Render dashboard
2. **Health Check Failures**: Ensure the PORT environment variable is set to 8000
3. **Startup Issues**: Check the application logs in the Render dashboard

## Scaling

For production use:

1. Upgrade to a paid plan for better performance
2. Increase instance count for high availability
3. Consider adding a custom domain
