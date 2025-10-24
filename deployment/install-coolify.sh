#!/bin/bash

# Coolify Installation Script for Ubuntu Server (192.168.0.100)
# Installation directory: /data/coolify
# Web interface: http://192.168.0.100:3000

set -e

echo "🚀 Installing Coolify to /data/coolify..."

# System prep
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git nginx

# Install Docker (if needed)
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sudo bash
    sudo usermod -aG docker $USER
fi

# Create installation directory
sudo mkdir -p /data/coolify
sudo chown $USER:$USER /data/coolify

# Install Coolify
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

echo "✅ Coolify installed at /data/coolify"
echo "🌐 Access: http://192.168.0.100:3000"