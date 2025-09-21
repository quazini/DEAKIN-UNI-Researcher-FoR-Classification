#!/bin/bash

# Debug script to test deployment configuration locally
# Run this before pushing to GitHub to catch issues early

# Prevent window from closing immediately
set -e

echo "==================================="
echo "Deployment Configuration Debug Tool"
echo "==================================="
echo ""

# Check for required files
echo "1. Checking required files..."
echo "----------------------------"

files_to_check=(
    "app_registry.yaml"
    "Dockerfile"
    "requirements.txt"
    ".github/workflows/deploy.yml"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file is missing!"
        exit 1
    fi
done

echo ""
echo "2. Validating app_registry.yaml syntax..."
echo "----------------------------------------"

# Check for common YAML issues
if command -v python3 &> /dev/null; then
    python3 -c "
import yaml
import sys
try:
    with open('app_registry.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print('✓ YAML syntax is valid')

    # Check for required fields
    if 'services' in config and len(config['services']) > 0:
        service = config['services'][0]
        if 'image' in service:
            print('✓ Image configuration found')
            if 'repository' in service['image']:
                print(f'  Repository: {service[\"image\"][\"repository\"]}')
            if 'tag' in service['image']:
                print(f'  Tag: {service[\"image\"][\"tag\"]}')
        else:
            print('✗ Image configuration missing!')
            sys.exit(1)

        if 'envs' in service:
            print(f'✓ Environment variables configured: {len(service[\"envs\"])} variables')
            # Check for problematic env var types
            for env in service['envs']:
                if 'type' in env:
                    print(f'  ⚠ Warning: Environment variable {env[\"key\"]} has type field - this may cause issues')
        else:
            print('⚠ No environment variables configured')
    else:
        print('✗ No services defined!')
        sys.exit(1)

except yaml.YAMLError as e:
    print(f'✗ YAML parsing error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'✗ Error: {e}')
    sys.exit(1)
" || echo "⚠ Python not available for YAML validation"
else
    echo "⚠ Python not available for YAML validation"
fi

echo ""
echo "3. Checking Docker configuration..."
echo "-----------------------------------"

# Test Docker build
if command -v docker &> /dev/null; then
    echo "Testing Docker build (this may take a moment)..."
    if docker build -t test-for-classification . > /dev/null 2>&1; then
        echo "✓ Docker build successful"

        # Check image size
        size=$(docker images test-for-classification --format "{{.Size}}")
        echo "  Image size: $size"

        # Clean up test image
        docker rmi test-for-classification > /dev/null 2>&1
    else
        echo "✗ Docker build failed! Run 'docker build -t test .' to see errors"
    fi
else
    echo "⚠ Docker not installed - skipping build test"
fi

echo ""
echo "4. Checking GitHub Secrets configuration..."
echo "------------------------------------------"
echo "Make sure you have these secrets configured in your GitHub repository:"
echo ""
echo "Required secrets:"
echo "  - DO_ACCESS_TOKEN: Your DigitalOcean API token"
echo "  - DO_APP_NAME: The name for your app (e.g., 'for-classification')"
echo ""
echo "Optional secrets (can be set in DO App Platform):"
echo "  - SUPABASE_URL: Your Supabase project URL"
echo "  - SUPABASE_KEY: Your Supabase API key"
echo "  - ADMIN_EMAIL: Admin email for the application"
echo ""
echo "To set secrets, go to:"
echo "Settings > Secrets and variables > Actions > New repository secret"

echo ""
echo "5. DigitalOcean Registry Configuration..."
echo "-----------------------------------------"
echo "Make sure you have:"
echo "1. Created a container registry in DigitalOcean"
echo "2. Created a repository named 'for-classification/streamlit'"
echo ""
echo "To create registry:"
echo "  doctl registry create for-classification --region nyc3"
echo ""
echo "To verify registry:"
echo "  doctl registry get"

echo ""
echo "==================================="
echo "Debug Summary"
echo "==================================="

# Display current configuration
echo ""
echo "Current app_registry.yaml configuration:"
echo "----------------------------------------"
grep -E "name:|repository:|tag:|registry_type:" app_registry.yaml | head -10

echo ""
echo "To test deployment locally with doctl:"
echo "--------------------------------------"
echo "1. Install doctl: https://docs.digitalocean.com/reference/doctl/how-to/install/"
echo "2. Authenticate: doctl auth init"
echo "3. Validate spec: doctl apps spec validate app_registry.yaml"
echo "4. Test create: doctl apps create --spec app_registry.yaml --dry-run"
echo ""
echo "For more debugging, check GitHub Actions logs at:"
echo "https://github.com/[your-username]/[your-repo]/actions"

echo ""
echo "==================================="
echo "Press Enter to exit..."
read -r