#!/bin/bash
set -e

# Configuration
SERVICE_NAME="remote-time-openapi"
REGION="us-central1" # Default, change if needed

# Check for Project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "Error: No Google Cloud project selected."
    echo "Please run 'gcloud config set project [PROJECT_ID]' first."
    exit 1
fi

echo "=================================================="
echo "Deploying $SERVICE_NAME to Project: $PROJECT_ID"
echo "Region: $REGION"
echo "=================================================="

# Prepare Configuration
# We use Secret Manager for sensitive data and Env Vars for standard config
echo "Configuring deployment arguments..."

# 1. Secrets from Google Secret Manager
# Ensure these secrets exist in your project:
# - OKTA_DOMAIN
# - OKTA_AUTH_SERVER_ID
# - OKTA_RS_CLIENT_ID
# - OKTA_RS_CLIENT_SECRET
# - OAUTH_CLIENT_ID
# - OAUTH_CLIENT_SECRET
# - OIDC_CONFIG_URL
# - OAUTH_CONFIG_URL
SECRETS_ARGS="--set-secrets=OKTA_DOMAIN=OKTA_DOMAIN:latest,OKTA_AUTH_SERVER_ID=OKTA_AUTH_SERVER_ID:latest,OKTA_RS_CLIENT_ID=OKTA_RS_CLIENT_ID:latest,OKTA_RS_CLIENT_SECRET=OKTA_RS_CLIENT_SECRET:latest,OAUTH_CLIENT_ID=OAUTH_CLIENT_ID:latest,OAUTH_CLIENT_SECRET=OAUTH_CLIENT_SECRET:latest,OIDC_CONFIG_URL=OIDC_CONFIG_URL:latest,OAUTH_CONFIG_URL=OAUTH_CONFIG_URL:latest"

# 2. Standard Environment Variables
ENV_VARS_ARGS="--set-env-vars=GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=global,GOOGLE_GENAI_USE_VERTEXAI=True"

# Combine for easier usage
DEPLOY_ARGS="$SECRETS_ARGS $ENV_VARS_ARGS"

# 1. Build & Deploy to get the URL
echo "Build & Deploy..."
gcloud builds submit time_app --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
gcloud run deploy $SERVICE_NAME --image gcr.io/$PROJECT_ID/$SERVICE_NAME --platform managed --region $REGION --port 8001 --no-invoker-iam-check $DEPLOY_ARGS

# 2. Get the Service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo "=================================================="
echo "Deployment Complete!"
echo "Service URL: $SERVICE_URL"
echo "OpenAPI JSON: ${SERVICE_URL}/openapi.json"
echo "=================================================="
