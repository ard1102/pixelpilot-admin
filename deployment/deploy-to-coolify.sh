#!/bin/bash

# Deploy Typing Game to Coolify
# Run this on your Ubuntu server at 192.168.0.100

echo "🚀 Deploying typing game to Coolify..."

# Create deployment directory
mkdir -p ~/typing-game-deploy
cd ~/typing-game-deploy

# Copy files from local machine (you'll need to scp these first)
echo "📁 Setting up deployment files..."

# Create docker-compose for Coolify
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  typing-game:
    build: .
    ports:
      - "3001:80"
    restart: unless-stopped
    container_name: typing-game
EOF

# Create the deployment package
cat > deploy.sh << 'EOF'
#!/bin/bash
# This script will be run by Coolify

echo "Building and starting typing game..."
docker-compose up --build -d
echo "Typing game deployed at http://localhost:3001"
EOF

chmod +x deploy.sh

echo "✅ Deployment package ready!"
echo ""
echo "📋 To deploy via Coolify:"
echo "1. Open Coolify at http://192.168.0.100:3000"
echo "2. Create new project → Git repository or Local source"
echo "3. Upload these files to your server:"
echo "   - typing-game.html"
echo "   - Dockerfile"
echo "   - docker-compose.yml"
echo "4. Configure build settings:"
echo "   - Build context: ./"
echo "   - Port mapping: 3001:80"
echo "5. Deploy!"
echo ""
echo 