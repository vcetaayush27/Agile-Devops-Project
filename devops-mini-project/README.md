# CI/CD Pipeline for a Containerized Flask Application

**Aayush Patil (84) · Sanskruti Suryawanshi (56)**  
**Guide:** Ms. Kshitija Gharat  
Agile Software Development & DevOps Lab · TE AI&DS · Semester V · A.Y. 2026–27

This is a runnable implementation based on the project report. It keeps the report's greeting and delivery architecture and implements its proposed testing and release-verification improvements. It is a new implementation, not the source of the old screenshots.

## Requirements

- Python **3.14** (standard CPython build) and internet access for initial installation.
- Git for uploading the repository.
- Docker for container execution; GitHub, Docker Hub and Render accounts for the optional hosted pipeline.

## Upgrading an existing copy

Use the updated project files and rerun setup. The scripts create `.venv314`; your previous `.venv` can remain in place. In VS Code, select `.venv314` as the Python interpreter. Do not copy packages from the old environment. Docker now uses `python:3.14-slim`, and every Python setup step in GitHub Actions selects `3.14`.

## Run on Windows

Install Python 3.14. Extract the ZIP, open this folder in VS Code and use its terminal:

```powershell
.\SETUP_WINDOWS.bat
.\START_PROJECT.bat
```

Open **http://127.0.0.1:5000**. Stop with **Ctrl+C**.

You can also double-click `START_PROJECT.bat`; it runs setup if the virtual environment is missing. Initial setup needs internet access. The launchers require Python 3.14 and use a separate `.venv314` environment. Python 3.14.8 on Linux is the verified environment for this delivery.

## Manual setup on Windows

```powershell
py -3.14 -m venv .venv314
.\.venv314\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv314\Scripts\python.exe run.py
```

No PowerShell activation-policy change is necessary: these commands call the environment's Python directly.

## macOS or Linux

```bash
sh setup.sh
.venv314/bin/python run.py
```

## Tests

Windows:

```powershell
.\.venv314\Scripts\python.exe -m pytest -q
```

macOS/Linux: `.venv314/bin/python -m pytest -q`.

## Docker build and run

Install and start Docker Desktop first on Windows. From this directory:

```bash
docker build --platform linux/amd64 --build-arg APP_VERSION=local-docker -t devops-mini-project:local .
docker run --rm --name devops-demo -p 127.0.0.1:5000:10000 devops-mini-project:local
```

Open the same local address. In another terminal, inspect health with `docker inspect --format='{{json .State.Health}}' devops-demo`. Docker's health status may take a few seconds to update. Stop the container with Ctrl+C.

Alternatively: `docker compose up --build` and later `docker compose down`.

## What is included

- A responsive Flask page with the report's messages and updated student names.
- `/health` JSON with the running release identifier and UTC time.
- A real browser health check, failure handling and a refresh button.
- Pytest application, HTTP verification and deploy-hook validation tests.
- Waitress for local Windows/Linux operation; Gunicorn in the Linux container.
- A non-root Docker image with a health check and pinned Python dependencies.
- GitHub Actions: Linux/Windows tests → container smoke test → optional Docker Hub publication → optional Render deployment → exact-version HTTP verification.
- Release evidence saved as a GitHub Actions artifact after verified deployment.

The pipeline diagram on the webpage is an architecture overview, not a live integration with GitHub or Docker Hub. The application health card makes an actual request to this server. A running local page does not establish that the cloud pipeline has been configured.

## Complete implementation guide

Read **[docs/IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md)** for GitHub, Docker Hub, Render, secrets, first release, subsequent updates and troubleshooting.

Read **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** for file responsibilities and how to explain the project. Read **[docs/VALIDATION.md](docs/VALIDATION.md)** for the checks actually completed when this archive was prepared.

## Main files

| File | Purpose |
|---|---|
| `app.py` | Flask routes, configuration and response headers |
| `run.py` | Cross-platform local WSGI server |
| `templates/`, `static/` | Page, error page, styles and health-check JavaScript |
| `requirements.txt` | Pinned runtime dependencies |
| `requirements-dev.txt` | Runtime plus test dependencies |
| `Dockerfile` | Production container build and health check |
| `gunicorn.conf.py` | Container WSGI process configuration |
| `compose.yaml` | Local Docker convenience configuration |
| `.github/workflows/ci-cd.yml` | CI, image publication and verified deployment |
| `scripts/verify_release.py` | Checks health, exact release and expected page content |
| `scripts/deploy_render.py` | Sends an exact image digest to Render and waits for verification |
| `tests/` | Automated application and delivery-script tests |
| `docs/` | Implementation, architecture and validation details |

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `PORT` | 5000 locally; 10000 in Docker | Listening port |
| `HOST` | 127.0.0.1 for `run.py` | Local server interface |
| `APP_VERSION` | local | Release identifier; baked from commit SHA in CI |
| `BUILD_TIME` | Local-run note | Build timestamp; supplied in CI |

`.env.example` documents the names only. The app does not automatically read `.env` files. Set values in the terminal or service configuration. Do not override `APP_VERSION` in Render: the workflow embeds the correct commit in the image.

For another local port in PowerShell:

```powershell
$env:PORT = "5001"
.\.venv314\Scripts\python.exe run.py
```

Open http://127.0.0.1:5001. To restore the default, run `Remove-Item Env:PORT`.

## Upload to GitHub

Create an empty repository in your GitHub account, then run these commands from the folder containing `app.py`. Replace the URL with your repository URL before running the final commands:

```bash
git init
git add .
git commit -m "Add Python 3.14 Flask CI/CD project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

For an existing repository, use its existing remote and commit/push the changed files. The root `README.md` displays automatically on GitHub. `.gitignore` excludes virtual environments, caches and local secrets. Never commit access tokens or a Render deploy-hook URL.

## Enable the hosted pipeline

Tests run on Ubuntu and Windows with Python 3.14. The workflow then builds and smoke-tests the container. Publication and deployment are optional and disabled until configured.

| GitHub setting | Type | Purpose |
|---|---|---|
| `ENABLE_PUBLISH` | Variable | Set to `true` to publish successful main-branch builds |
| `DOCKERHUB_USERNAME` | Secret | Docker Hub account used for image publication |
| `DOCKERHUB_TOKEN` | Secret | Docker Hub access token |
| `ENABLE_DEPLOY` | Variable | Set to `true` after configuring Render |
| `RENDER_DEPLOY_HOOK` | Secret | Render service deploy-hook URL |
| `RENDER_SERVICE_URL` | Variable | Public HTTPS URL of the Render service |

Follow [the implementation guide](docs/IMPLEMENTATION_GUIDE.md) for the image name, first Render setup and release verification. Each deployed image is selected by its immutable digest; verification checks the exact commit version and expected page content.

## Validation and scope

The Python 3.14.8 Linux environment passed all 21 automated tests and live Waitress/Gunicorn release checks. Docker execution, Windows launchers and cloud deployment still require verification in their target environments. See [the validation record](docs/VALIDATION.md) for details.

This is an educational DevOps demonstration with no database or authentication. Keep screenshots and successful workflow evidence from your own deployment for your project presentation.
