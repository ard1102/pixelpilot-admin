# Coolify Deployment — PixelPilot Admin (192.168.0.100)

This guide sets up the existing Photo Admin Flask app in Coolify and explains how to update it when the Dockerfile or docker-compose.yml changes.

## Coolify UI Access
- Current UI: `http://192.168.0.100:8000/` (observed from the running container)
- If your Coolify was installed on port `3000`, use: `http://192.168.0.100:3000/`
- Sign in with your Coolify admin user.

## Prerequisites
- Server: `192.168.0.100` with Docker & Docker Compose installed.
- App files on server at: `/home/rd/photo-admin` (already deployed and running via Compose).
- SSH key path: set `DEPLOY_SSH_KEY` to your private key (store outside repo).

## Create a Docker Compose Application in Coolify
1. Open Coolify → New → Application → Docker Compose.
2. Name: `photo-admin`.
3. Destination: select your local Docker engine on `192.168.0.100`.
4. Compose content: paste the following (remove the deprecated `version` line if Coolify warns about it):

```yaml
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000"]
      interval: 30s
      timeout: 10s
      retries: 3
```

5. Save → Deploy.

Notes:
- The `.:/app` bind mount lets you change files (images, templates, DB) on the host and have them visible in the container instantly.
- For production hardening, consider replacing the bind mount with explicit named volumes (requires minor path changes in the app):
  - `images` directory: volume to `/app/images`
  - `site.db` file: place the DB under a directory (e.g., `/app/data/site.db`) and mount that directory as a volume

## Web UI Endpoints (Application)
- Home: `http://192.168.0.100:5000/`
- Admin: `http://192.168.0.100:5000/admin?token=<your-token>`
- Images: `http://192.168.0.100:5000/images/<path>` (e.g., `images/indian_saree/1.png`)

## Updating After Changes

### If docker-compose.yml changes
- In Coolify, open your `photo-admin` application → Edit Docker Compose.
- Update the YAML → Save → Redeploy.
- Port changes: if you change `ports:`, ensure the new port is allowed on your server firewall and update any links accordingly.

### If Dockerfile or dependencies change
- Because the Compose uses `build: .`, redeploying will rebuild the image.
- To ensure a fresh build (no cache), use Coolify’s Redeploy/Force Rebuild option if available, or bump a dummy label in the Dockerfile to invalidate cache.
- Typical changes that require a rebuild:
  - `Dockerfile` edits
  - `requirements.txt` updates
  - Base image changes (`FROM python:...`)

### If you want to switch to Dockerfile-based app (optional)
- Create a new Application → Dockerfile.
- Set Build Context to your repository root and Dockerfile path to `./Dockerfile`.
- Add an HTTP Port 5000 exposure in Coolify if requested; or keep using Compose if you prefer explicit `ports:` mapping.

## Data & Images Management
- Add images directly on the server under `/home/rd/photo-admin/images/`.
- Ingest new files into the SQLite DB:
  - Via Docker on server: `cd /home/rd/photo-admin && docker compose exec web python load_images.py`
  - Via Coolify container shell: open the container for `photo-admin-web` and run `python load_images.py`.
- New images will appear in the Admin dashboard under the `Pending` filter.

## Verifying Deployment
- Check container: `docker ps | grep photo-admin` (should show `0.0.0.0:5000->5000`)
- Health: `docker inspect --format='{{json .State.Health.Status}}' photo-admin-web-1`
- App: `curl -sS http://192.168.0.100:5000/ | head -n 2` (should show HTML)

## Troubleshooting
- Compose `version` warning in logs: remove `version: "3.8"` in the YAML.
- Docker socket permission denied: ensure user `rd` is in the `docker` group, then re-login or `newgrp docker`.
- Port conflicts: adjust the `ports:` mapping or stop the conflicting service.
- Bind mount path issues in Coolify: verify the Compose working directory and that the `.` path contains your app files.

## Coolify Installation (reference)
If Coolify is not installed, you can use the helper script:

```bash
# Copy and run the installer (from your local machine)
scp -i "$DEPLOY_SSH_KEY" deployment/install-coolify.sh rd@192.168.0.100:/tmp/
ssh -i "$DEPLOY_SSH_KEY" rd@192.168.0.100 "chmod +x /tmp/install-coolify.sh && sudo /tmp/install-coolify.sh"
```
Then access the UI at `http://192.168.0.100:8000/` (or `3000` if configured).