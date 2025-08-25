#!/usr/bin/env bash
set -euo pipefail

# Configuration
PROJECT_ID="${PROJECT_ID:-ministry-data-visualizer}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-ministry-visualizer}"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

# Check if PROJECT_ID is set and not the default
if [ "$PROJECT_ID" = "ministry-data-visualizer" ]; then
    echo "🚨 Please set your Google Cloud Project ID:"
    echo "   export PROJECT_ID=your-actual-project-id"
    echo "   Or edit this script to set PROJECT_ID directly"
    exit 1
fi

echo "🚀 Deploying to Google Cloud Run"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service: $SERVICE_NAME"
echo "   Image: $IMAGE"
echo ""

# Set the project
echo "🔧 Setting Google Cloud project..."
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sheets.googleapis.com

# Create or update service account for the app
SERVICE_ACCOUNT_NAME="ministry-data-reader"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🔐 Setting up service account..."
# Create service account if it doesn't exist
gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" &>/dev/null || \
gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
  --display-name="Ministry Data Reader" \
  --description="Service account for reading Google Sheets data"

echo "📊 Service account email: $SERVICE_ACCOUNT_EMAIL"
echo "⚠️  IMPORTANT: You must share your Google Sheet with this email address!"
echo "   1. Open your Google Sheet"
echo "   2. Click 'Share' button" 
echo "   3. Add: $SERVICE_ACCOUNT_EMAIL"
echo "   4. Set permission to 'Viewer'"
echo ""

# Build container image
echo "🏗️  Building container image..."
cd "$(dirname "$0")/.."  # Go to project root
cp infra/Dockerfile .
gcloud builds submit --tag "$IMAGE" .
rm Dockerfile  # Clean up

# Deploy to Cloud Run (Service) for Streamlit UI
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --region "$REGION" \
  --image "$IMAGE" \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --service-account="$SERVICE_ACCOUNT_EMAIL" \
  --set-env-vars=STREAMLIT_SERVER_HEADLESS=true

echo ""
echo "✅ Deployment completed!"
echo "🌐 Your app should be available at:"
gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)"
echo ""
echo "📊 To view logs:"
echo "   gcloud logs tail --service=$SERVICE_NAME"


