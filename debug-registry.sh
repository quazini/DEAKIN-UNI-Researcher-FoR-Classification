#!/bin/bash

echo "=== DigitalOcean Registry Debug Script ==="
echo "=========================================="
echo ""

# Test if doctl is available
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl command not found"
    echo "Install doctl from: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Test authentication
echo "1. Testing authentication..."
if doctl account get &> /dev/null; then
    echo "✅ Successfully authenticated with DigitalOcean"
else
    echo "❌ Authentication failed"
    echo "Run: doctl auth init"
    exit 1
fi

# Get registry info
echo ""
echo "2. Registry information..."
REGISTRY_INFO=$(doctl registry get 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "$REGISTRY_INFO"
    REGISTRY_NAME=$(echo "$REGISTRY_INFO" | awk 'NR==2 {print $1}')
    echo "Registry name: $REGISTRY_NAME"
else
    echo "❌ No container registry found"
    echo "Create one with: doctl registry create <name> --region syd1"
    exit 1
fi

# List repositories
echo ""
echo "3. Available repositories..."
doctl registry repository list-v2 "$REGISTRY_NAME"

# Test different ways to access the streamlit repository
echo ""
echo "4. Testing repository access methods..."

echo ""
echo "Method 1: Using \$REGISTRY_NAME/streamlit"
doctl registry repository list-tags "${REGISTRY_NAME}/streamlit" 2>&1 | head -10

echo ""
echo "Method 2: Using just 'streamlit'"
doctl registry repository list-tags "streamlit" 2>&1 | head -10

echo ""
echo "Method 3: Checking if the issue is with the registry name"
echo "Available registries for your account:"
doctl registry list

echo ""
echo "=== Summary ==="
echo "If Method 1 or 2 worked above, then the issue is in the GitHub Actions environment"
echo "If both failed, there might be a permissions or API issue"
echo ""
echo "Expected repository path: ${REGISTRY_NAME}/streamlit"
echo "Looking for tags matching pattern: main-<commit-sha>"