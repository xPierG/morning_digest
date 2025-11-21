#!/bin/bash

# Exit on error
set -e

APP_NAME="morning-digest-agent"
REGION="us-central1" # Default to us-central1 for best Free Tier availability

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed."
    exit 1
fi

# Get current project ID
PROJECT_ID=$(gcloud config get-value project)

if [ -z "$PROJECT_ID" ]; then
    echo "Error: No Google Cloud project selected."
    echo "Run 'gcloud config set project YOUR_PROJECT_ID' first."
    exit 1
fi

echo "========================================================"
echo "Deploying $APP_NAME to Google Cloud Run (Job)"
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"
echo "========================================================"

# 1. Build the container image using Cloud Build
echo ">> Building container image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$APP_NAME .

# 2. Deploy as a Cloud Run Job
echo ">> Deploying Cloud Run Job..."
gcloud run jobs deploy $APP_NAME \
    --image gcr.io/$PROJECT_ID/$APP_NAME \
    --region $REGION \
    --tasks 1 \
    --max-retries 0 \
    --set-env-vars="PYTHONUNBUFFERED=1"

echo "========================================================"
echo "Deployment Complete!"
echo "To run the job immediately, execute:"
echo "  gcloud run jobs execute $APP_NAME --region $REGION"
echo ""
echo "To schedule it (e.g., every morning at 7 AM Rome time):"
echo "  gcloud scheduler jobs create http ${APP_NAME}-scheduler \\"
echo "    --location $REGION \\"
echo "    --schedule=\"0 7 * * *\" \\"
echo "    --time-zone=\"Europe/Rome\" \\"
echo "    --uri=\"https://${REGION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$APP_NAME:run\" \\"
echo "    --http-method POST \\"
echo "    --oauth-service-account-email <YOUR_SERVICE_ACCOUNT_EMAIL>"
echo "========================================================"
