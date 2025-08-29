# Deploying ReliQuary Website to Vercel

This guide explains how to deploy the ReliQuary website to Vercel for public access.

## Prerequisites

1. A Vercel account (free tier available)
2. The Vercel CLI installed (`npm install -g vercel`)
3. Git access to the ReliQuary repository

## Deployment Steps

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

### 3. Navigate to the Website Directory

```bash
cd website
```

### 4. Deploy to Vercel

For the first deployment:

```bash
vercel
```

For subsequent deployments:

```bash
vercel --prod
```

### 5. Configuration

The `vercel.json` file in the website directory contains the necessary configuration for deployment:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/"
    }
  ]
}
```

## Environment Variables

If you need to set environment variables for the website, you can do so in the Vercel dashboard or using the CLI:

```bash
vercel env add <ENV_VARIABLE_NAME>
```

## Custom Domain

To use a custom domain:

1. Add your domain in the Vercel dashboard
2. Configure DNS records as instructed by Vercel
3. Vercel will automatically provision an SSL certificate

## Redeployment

To redeploy after making changes:

```bash
# From the website directory
vercel --prod
```

Or push to your Git repository if you've connected it to Vercel for automatic deployments.
