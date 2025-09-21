@echo off
echo ===================================
echo Deployment Configuration Debug Tool
echo ===================================
echo.

echo 1. Checking required files...
echo ----------------------------

if exist "app_registry.yaml" (
    echo [OK] app_registry.yaml exists
) else (
    echo [ERROR] app_registry.yaml is missing!
)

if exist "Dockerfile" (
    echo [OK] Dockerfile exists
) else (
    echo [ERROR] Dockerfile is missing!
)

if exist "requirements.txt" (
    echo [OK] requirements.txt exists
) else (
    echo [ERROR] requirements.txt is missing!
)

if exist ".github\workflows\deploy.yml" (
    echo [OK] .github\workflows\deploy.yml exists
) else (
    echo [ERROR] .github\workflows\deploy.yml is missing!
)

echo.
echo 2. Displaying app_registry.yaml configuration...
echo ------------------------------------------------
type app_registry.yaml | findstr /C:"name:" /C:"repository:" /C:"tag:" /C:"registry_type:"

echo.
echo 3. Testing Docker (if available)...
echo ------------------------------------
docker --version >nul 2>&1
if %errorlevel% == 0 (
    echo Docker is installed
    echo Building test image...
    docker build -t test-for-classification . >nul 2>&1
    if %errorlevel% == 0 (
        echo [OK] Docker build successful
        docker rmi test-for-classification >nul 2>&1
    ) else (
        echo [ERROR] Docker build failed!
        echo Run 'docker build -t test .' to see detailed errors
    )
) else (
    echo Docker is not installed or not in PATH
)

echo.
echo ===================================
echo Required GitHub Secrets:
echo ===================================
echo - DO_ACCESS_TOKEN: Your DigitalOcean API token
echo - DO_APP_NAME: The name for your app (e.g., 'for-classification')
echo.
echo Optional (can be set in DO App Platform):
echo - SUPABASE_URL: Your Supabase project URL
echo - SUPABASE_KEY: Your Supabase API key
echo - ADMIN_EMAIL: Admin email for the application
echo.
echo To set secrets, go to:
echo Settings - Secrets and variables - Actions - New repository secret

echo.
echo ===================================
echo Testing with doctl (if available)...
echo ===================================
doctl version >nul 2>&1
if %errorlevel% == 0 (
    echo doctl is installed
    echo.
    echo Validating app specification...
    doctl apps spec validate app_registry.yaml
) else (
    echo doctl is not installed
    echo Install from: https://docs.digitalocean.com/reference/doctl/how-to/install/
)

echo.
echo ===================================
echo.
pause