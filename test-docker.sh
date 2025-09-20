#!/bin/bash

# Docker Test Script for FoR Classification App
echo "🐳 Testing Docker container locally..."

# Build the container
echo "📦 Building Docker image..."
docker build -t for-classification-test .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Docker build successful!"

# Check if .env file exists for local testing
if [ -f ".env" ]; then
    echo "📋 Found .env file - using local environment variables"
    echo "🚀 Starting container with .env file..."
    docker run -p 8501:8501 --env-file .env for-classification-test
else
    echo "⚠️  No .env file found"
    echo "📝 Create a .env file with your credentials or run manually with:"
    echo ""
    echo "docker run -p 8501:8501 \\"
    echo "  -e SUPABASE_URL=\"your-supabase-url\" \\"
    echo "  -e SUPABASE_KEY=\"your-supabase-key\" \\"
    echo "  -e DEFAULT_WEBHOOK_URL=\"your-webhook-url\" \\"
    echo "  -e ADMIN_EMAIL=\"your-admin-email\" \\"
    echo "  for-classification-test"
    echo ""
    echo "Then open: http://localhost:8501"
fi