#!/bin/bash

# Script to set up Digital Ocean App Platform secrets
# Run this AFTER the app is created

echo "=== Digital Ocean App Secrets Setup ==="
echo ""
echo "This script will help you configure secrets for your Digital Ocean app."
echo ""

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl CLI is not installed. Please install it first."
    exit 1
fi

# Get app name
read -p "Enter your app name (e.g., for-classification): " APP_NAME

# Find app ID
echo "Finding app ID for $APP_NAME..."
APP_ID=$(doctl apps list --output json | jq -r --arg name "$APP_NAME" '.[] | select(.spec.name == $name) | .id')

if [ -z "$APP_ID" ]; then
    echo "❌ App '$APP_NAME' not found."
    echo "Available apps:"
    doctl apps list --format ID,Spec.Name
    exit 1
fi

echo "✅ Found app: $APP_NAME (ID: $APP_ID)"
echo ""

# Get secret values
echo "Please enter your secret values:"
echo ""

read -p "Enter SUPABASE_URL (e.g., https://xxx.supabase.co): " SUPABASE_URL
read -p "Enter SUPABASE_KEY (service role key from Supabase dashboard): " SUPABASE_KEY
read -p "Enter ADMIN_EMAIL: " ADMIN_EMAIL

echo ""
echo "=== Configuring secrets in Digital Ocean ==="

# Update app with environment variables
cat > temp_env_update.json << EOF
{
  "spec": {
    "services": [
      {
        "name": "streamlit",
        "envs": [
          {
            "key": "SUPABASE_URL",
            "value": "$SUPABASE_URL",
            "type": "SECRET"
          },
          {
            "key": "SUPABASE_KEY",
            "value": "$SUPABASE_KEY",
            "type": "SECRET"
          },
          {
            "key": "ADMIN_EMAIL",
            "value": "$ADMIN_EMAIL",
            "type": "SECRET"
          }
        ]
      }
    ]
  }
}
EOF

echo "Updating app with secrets..."
doctl apps update $APP_ID --spec temp_env_update.json

# Clean up
rm temp_env_update.json

echo ""
echo "✅ Secrets configured successfully!"
echo ""
echo "The app will restart automatically to apply the new configuration."
echo "Check the app logs in a few minutes to verify the connection works."
echo ""
echo "To view logs:"
echo "  doctl apps logs $APP_ID --follow"