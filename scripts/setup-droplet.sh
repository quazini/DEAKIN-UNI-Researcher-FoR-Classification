#!/bin/bash

################################################################################
# FoR Classification System - Ubuntu Droplet Setup Script
################################################################################
# This script sets up a fresh Ubuntu droplet for running the FoR Classification
# application with PM2 process manager.
#
# Usage:
#   1. SSH into your droplet: ssh ubuntu@your-droplet-ip
#   2. Download this script: wget https://raw.githubusercontent.com/YOUR_REPO/main/scripts/setup-droplet.sh
#   3. Make executable: chmod +x setup-droplet.sh
#   4. Run: ./setup-droplet.sh
#
# Or run directly:
#   curl -fsSL https://raw.githubusercontent.com/YOUR_REPO/main/scripts/setup-droplet.sh | bash
################################################################################

set -e  # Exit on error

echo "============================================================"
echo "FoR Classification System - Droplet Setup"
echo "============================================================"
echo ""

# Configuration
APP_DIR="${HOME}/FoR-Classification-Agent"
GITHUB_REPO="https://github.com/YOUR_USERNAME/YOUR_REPO.git"  # Update this!
PYTHON_VERSION="3.11"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root. Run as ubuntu user."
    exit 1
fi

echo "Step 1: System Update"
echo "------------------------------------------------------------"
sudo apt-get update
sudo apt-get upgrade -y
print_status "System updated"
echo ""

echo "Step 2: Install Required Packages"
echo "------------------------------------------------------------"
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev

print_status "Required packages installed"
echo ""

echo "Step 3: Install Node.js and npm"
echo "------------------------------------------------------------"
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
    print_status "Node.js installed: $(node --version)"
else
    print_status "Node.js already installed: $(node --version)"
fi
echo ""

echo "Step 4: Install PM2"
echo "------------------------------------------------------------"
if ! command -v pm2 &> /dev/null; then
    sudo npm install -g pm2
    print_status "PM2 installed: $(pm2 --version)"

    # Setup PM2 to start on boot
    pm2 startup systemd -u $USER --hp $HOME
    sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u $USER --hp $HOME
    print_status "PM2 configured to start on boot"
else
    print_status "PM2 already installed: $(pm2 --version)"
fi
echo ""

echo "Step 5: Clone Repository"
echo "------------------------------------------------------------"
if [ -d "$APP_DIR" ]; then
    print_warning "Directory $APP_DIR already exists"
    read -p "Do you want to remove it and re-clone? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$APP_DIR"
        git clone "$GITHUB_REPO" "$APP_DIR"
        print_status "Repository cloned to $APP_DIR"
    else
        print_status "Skipping repository clone"
    fi
else
    git clone "$GITHUB_REPO" "$APP_DIR"
    print_status "Repository cloned to $APP_DIR"
fi
echo ""

echo "Step 6: Install Python Dependencies"
echo "------------------------------------------------------------"
cd "$APP_DIR"

# Upgrade pip
python3 -m pip install --upgrade pip --user

# Install requirements
pip3 install --user -r requirements.txt
print_status "Python dependencies installed"
echo ""

echo "Step 7: Create .env File"
echo "------------------------------------------------------------"
if [ -f ".env" ]; then
    print_warning ".env file already exists"
else
    print_warning "You need to create a .env file with your credentials"
    echo "Copy .env.example to .env and fill in your values:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    echo ""
    read -p "Press Enter to continue..."
fi
echo ""

echo "Step 8: Create Logs Directory"
echo "------------------------------------------------------------"
mkdir -p logs
print_status "Logs directory created"
echo ""

echo "Step 9: Configure Firewall (UFW)"
echo "------------------------------------------------------------"
if command -v ufw &> /dev/null; then
    sudo ufw --force enable
    sudo ufw allow ssh
    sudo ufw allow 8501/tcp  # Streamlit default port
    sudo ufw status
    print_status "Firewall configured"
else
    print_warning "UFW not installed, skipping firewall configuration"
fi
echo ""

echo "Step 10: Setup Nginx (Optional)"
echo "------------------------------------------------------------"
read -p "Do you want to install and configure Nginx as reverse proxy? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo apt-get install -y nginx

    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/for-classification > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;  # Replace with your domain

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/for-classification /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default

    # Test and reload Nginx
    sudo nginx -t && sudo systemctl reload nginx
    print_status "Nginx configured as reverse proxy"
else
    print_status "Skipping Nginx setup"
fi
echo ""

echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo ""
echo "Next Steps:"
echo "1. Create/edit .env file with your credentials:"
echo "   cd $APP_DIR"
echo "   nano .env"
echo ""
echo "2. Start the application with PM2:"
echo "   cd $APP_DIR"
echo "   pm2 start ecosystem.config.js"
echo ""
echo "3. Save PM2 process list:"
echo "   pm2 save"
echo ""
echo "4. View logs:"
echo "   pm2 logs for-classification"
echo ""
echo "5. Monitor the application:"
echo "   pm2 monit"
echo ""
echo "Application will be accessible at:"
echo "  - http://localhost:8501 (local)"
echo "  - http://$(curl -s ifconfig.me):8501 (external)"

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  - http://$(curl -s ifconfig.me) (via Nginx)"
fi

echo ""
print_status "Droplet is ready for deployment!"
