#!/usr/bin/env bash
set -euo pipefail

# Required: set these before running
PROJECT_ID="YOUR_GCP_PROJECT"
REGION="us-central1"
SERVICE_NAME="ministry-visualizer"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

gcloud config set project "$PROJECT_ID"

# Build container image
gcloud builds submit --tag "$IMAGE" ..

# Deploy to Cloud Run (Service) for Streamlit UI
gcloud run deploy "$SERVICE_NAME" \
  --region "$REGION" \
  --image "$IMAGE" \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars=STREAMLIT_SERVER_HEADLESS=true

echo "Deployed service: $SERVICE_NAME"


