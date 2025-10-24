# PixelPilot Admin – Flask App

Simple admin dashboard and public gallery for triaging images. Includes table and card views, status management, price editing, and Docker support.

## Overview
- Serves images from `images/` via `GET /images/<path:filename>`.
- Public gallery at `GET /` shows approved images with WhatsApp links.
- Admin dashboard at `GET /admin` (token required) supports approving, pending, trash, and price editing.
- Images are tracked in `site.db` (SQLite).

## Purpose
- Prototype to support Indian women saree entrepreneurs, starting with my aunt’s business.
- Share URLs instead of forwarding many images; clients view, pick, and contact on WhatsApp.
- Reduce friction and time spent by dealers managing vendor-to-client image flows.

## Roadmap
- Event-driven tracking of most viewed/liked designs to boost reach and sales.
- WhatsApp AI agent to answer queries and assist clients and dealers.
- Better analytics dashboards and filters for categories and price ranges.

## Prerequisites
- Python 3.11+
- Docker (optional, for containerized run)

## Configuration
- Set `ADMIN_TOKEN` in your environment (required for admin APIs).
- Optional: set `WA_PHONE` to your WhatsApp phone number (digits only, no '+' or spaces).
- Environment file:
  - Copy `.env.example` to `.env` and set values.
  - Docker Compose will pass `ADMIN_TOKEN` and `WA_PHONE` into the container when defined.

## Quick Start (Local)
- Create and activate a virtual environment:
  - PowerShell: ``python -m venv .venv`` then ``.\.venv\Scripts\Activate.ps1``
  - CMD: ``python -m venv .venv`` then ``.\.venv\Scripts\activate.bat``
- Install dependencies: ``pip install -r requirements.txt``
- Start the app:
  - Easiest: ``python app.py``
  - Or via Flask CLI: ``$env:FLASK_APP='app.py'; flask run``
- Open:
  - Home: `http://localhost:5000/`
  - Admin: `http://localhost:5000/admin?token=<your-token>`

## Quick Start (Docker Compose)
- Build and run: ``docker compose up --build``
- Open:
  - Home: `http://localhost:5000/`
  - Admin: `http://localhost:5000/admin?token=<your-token>`
- Useful commands:
  - Logs: ``docker compose logs -f``
  - Stop: ``docker compose down``
  - Rebuild: ``docker compose up --build``

### Notes on Docker Volumes
- The compose file mounts your project into the container: ``.:/app``.
- This means files in `images/` and `site.db` are accessed directly by the container with no copy step.
- For production, consider mounting only `images/` and `site.db`, or baking assets into the image.

## Data Sync
- Keep the repository clean by syncing `images/` and `site.db` rather than committing them.
- `site.db` is ignored by `.gitignore`; `images/` can be synced separately.

### Sync from local (Windows → Ubuntu server)
- Copy images:
  - `scp -r images rd@192.168.0.100:/home/rd/photo-admin/images`
- Copy database:
  - `scp site.db rd@192.168.0.100:/home/rd/photo-admin/site.db`
- Ingest or refresh images in the app:
  - `cd /home/rd/photo-admin && docker compose exec web python load_images.py`

### Sync from local (Linux/macOS → Ubuntu server)
- Copy images:
  - `rsync -av --progress images/ rd@192.168.0.100:/home/rd/photo-admin/images/`
- Copy database:
  - `scp site.db rd@192.168.0.100:/home/rd/photo-admin/site.db`
- Ingest images:
  - `ssh rd@192.168.0.100 "cd /home/rd/photo-admin && docker compose exec web python load_images.py"`

## Admin Dashboard
- Access: `http://localhost:5000/admin?token=admin123`
- Filter by status with the Pending/Approved/Trash buttons.
- Switch views:
  - Table View: shows filename, status, price input and Save.
  - Card View: shows thumbnails; status and price badges overlay the image.
- Actions:
  - Approve/Pending/Trash: updates row status immediately.
  - Edit Price:
    - Table: type into the input and click Save.
    - Card: click the price badge to open a small popover, enter a value, press Enter or Save.
  - Zoom: click the image to open a modal preview.

## Images
- Folder structure: place images under `images/` (subfolders allowed), e.g. `images/indian_saree/1.png`.
- Supported formats: `.png`, `.jpg`, `.jpeg`.
- Serving path: images are served at `/images/<path>`, mapped to `images/` on disk.
- Database filenames must store the path relative to `images/` using forward slashes, e.g. `indian_saree/1.png`.

### Adding Images While Running
- Copy files into `images/`.
- Insert new files into the database using the loader:
  - Local: ``python load_images.py``
  - Docker: ``docker compose exec web python load_images.py``
- New entries appear under the Admin Pending filter.

## Loader Script (`load_images.py`)
- Scans `images/` recursively and inserts new files with `status='pending'` and the current timestamp.
- Skips existing records (ensures idempotency).
- Requires a valid schema in `schema.sql` and a writable `site.db`.

## Database
- SQLite file: `site.db`.
- Example schema (reference only):
```
CREATE TABLE IF NOT EXISTS images (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename TEXT UNIQUE NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'trash')),
  price REAL,
  date_uploaded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  trash_date TIMESTAMP
);
```

## API Endpoints
- `POST /api/set_status` — body: `{ id: number, status: 'pending'|'approved'|'trash' }`
- `POST /api/edit_price` — body: `{ id: number, price: number|null }`
- Admin auth: set `ADMIN_TOKEN` env var; send `X-Admin-Token: <your-token>` or use `?token=<your-token>` once to set the cookie.

## Troubleshooting
- Images don’t show:
  - Verify the file exists under `images/` and the DB `filename` matches its relative path.
  - Run the loader script to ingest new files.
- Compose warning about version:
  - Remove the `version: "3.8"` line in `docker-compose.yml` (Compose v2 ignores it).
- Port in use:
  - Stop other services on `:5000`, or change the port mapping in compose.

## Development Tips
- Enable auto reload with Flask CLI: set `FLASK_APP=app.py` and run `flask run` with debug enabled.
- In Docker, you can add `environment: [FLASK_DEBUG=1]` to the `web` service.

## Deploy with Coolify
- Access the Coolify UI at `http://192.168.0.100:8000/` (or `3000` if configured).
- Create a new Application → Docker Compose.
- Paste the compose below (drop the `version` line if warned):
```
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
- Save and Deploy.
- Web UI access:
  - Home: `http://192.168.0.100:5000/`
  - Admin: `http://192.168.0.100:5000/admin?token=<your-token>`

### Updating in Coolify
- Edit Docker Compose in the app, Save, and Redeploy when `docker-compose.yml` changes.
- Redeploy (force rebuild) when `Dockerfile` or `requirements.txt` changes.
- Add or edit images under `images/` on the server; ingest with `docker compose exec web python load_images.py`.

## Publish (GitHub)
- Using GitHub CLI:
  - `gh repo create pixelpilot-admin --public --source . --remote origin --push`
- Using plain Git:
  - `git branch -M main`
  - `git remote add origin https://github.com/<your-username>/<repo-name>.git`
  - `git push -u origin main`
- Ensure `.gitignore` keeps `site.db` (and optionally `images/`) out of the repo. Sync data to servers as documented above.