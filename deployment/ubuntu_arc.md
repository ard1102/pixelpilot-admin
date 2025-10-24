# Ubuntu Server Deployment Reference

## Quick Deploy Commands
```bash
# Deploy updated game file
scp -i "$DEPLOY_SSH_KEY" fixed_typing_game.html rd@192.168.0.100:/home/rd/typing-game/

# Restart container
sudo docker compose -f /home/rd/typing-game/docker-compose.yml up --build -d
```

## Server Details
- **IP**: 192.168.0.100
- **Port**: 3001
- **Username**: rd
- **Password**: [REDACTED]
- **URL**: http://192.168.0.100:3001

## File Structure
```
/home/rd/typing-game/
├── fixed_typing_game.html    # Main game file (current)
├── typing-game.html         # Original file (backup)
├── docker-compose.yml       # Docker configuration
├── Dockerfile              # Container definition
└── [container files]
```

## SSH Key Info
- **Location**: private key stored outside the repository; set path in `$DEPLOY_SSH_KEY`
- **Permissions**: 600
- **Connection**: `ssh -i "$DEPLOY_SSH_KEY" rd@192.168.0.100`

## Docker Setup
```yaml
# docker-compose.yml
services:
  typing-game:
    build: .
    ports:
      - 3001:80
    restart: unless-stopped
    container_name: typing-game
```

```dockerfile
# Dockerfile
FROM nginx:alpine
COPY fixed_typing_game.html /usr/share/nginx/html/index.html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Essential Commands
```bash
# Check container status
sudo docker ps | grep typing-game

# View logs
sudo docker logs typing-game --tail 10

# Stop container
sudo docker stop typing-game

# Start container
sudo docker compose -f /home/rd/typing-game/docker-compose.yml up -d

# Full rebuild
sudo docker compose -f /home/rd/typing-game/docker-compose.yml up --build -d
```

## Deployment Checklist
- [ ] Update `fixed_typing_game.html` locally
- [ ] Copy file to server via SCP
- [ ] Restart Docker container
- [ ] Verify deployment at http://192.168.0.100:3001
- [ ] Check container logs if issues occur

## Troubleshooting
- **Container not starting**: Check Dockerfile syntax
- **Port 3001 not accessible**: Verify firewall settings
- **File not updating**: Ensure correct filename in Dockerfile
- **Permission denied**: Use `sudo` and provide credentials when prompted