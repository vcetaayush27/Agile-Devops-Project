# Architecture and explanation

## What happens after a change?

1. A developer pushes a commit to GitHub.
2. GitHub Actions installs the pinned Python dependencies and runs pytest on Linux and Windows.
3. If tests pass, a Linux runner builds the Docker image and embeds the commit SHA as `APP_VERSION`.
4. The runner starts this image and checks `/health`, the expected version and the homepage content.
5. When publication is enabled, the same tested image is tagged and pushed to the student's Docker Hub repository.
6. When deployment is enabled, the Render hook receives the immutable digest of that image.
7. The workflow waits until the service responds with the expected commit and the correct page.
8. A successful verification produces `release.json` as a downloadable workflow artifact.

## Main concepts for your viva

**Continuous integration:** the automated checks run when source changes. A failed test blocks the image-publication path.

**Containerization:** the Dockerfile packages the application and runtime dependencies. An image is the package; a container is its running instance.

**Registry:** Docker Hub stores the image so the hosting platform can pull it.

**Continuous deployment:** after setup, successful main-branch changes can be published and deployed without a manual release command. This is disabled until the user's account configuration is complete.

**Health check:** `/health` reports whether this application can respond and which version it runs. It does not prove that external GitHub/Docker Hub services are healthy.

**Release verification:** the checker requires the expected SHA, not merely HTTP 200. That prevents an old healthy release from being accepted as the new one.

**Digest versus tag:** `latest` is a convenient movable label. A digest identifies the image content. The Render request uses a digest, and the workflow keeps the commit/digest relationship in a release record.

**Secrets:** Docker Hub tokens and Render hook URLs stay in GitHub's secrets settings. The source contains only variable names. Never include real credentials in the project ZIP.

## Report alignment

| Report topic | Implementation |
|---|---|
| Flask greeting and confirmation | Home page in `templates/index.html` |
| GitHub repository | Project source and `.github/workflows/ci-cd.yml` |
| Tests before publication | pytest jobs plus container smoke check |
| Docker container | Non-root image, Gunicorn, runtime health check |
| Docker Hub publication | Conditional image-publication step |
| Render deployment | Exact-digest deploy-hook request |
| Post-deployment checks | Expected SHA and homepage verification |
| Names and guide | Updated names on the application page |

The styled UI, live health card and verifiable release path extend the report's minimal reference code. They do not recreate an unseen original repository. The original report is not modified by this build.

## Limits and operational choices

This is a stateless educational service: no database, user accounts or business transactions. It does not claim performance, security-audit or availability benchmarks. Python package versions are pinned to the tested environment; the Docker base uses the maintained `python:3.14-slim` tag, which can move. For stricter build reproducibility, pin a reviewed base-image digest. GitHub action major tags are used for readable maintenance; pin reviewed action commits when required by your release policy.

The HTTP readiness checker confirms the expected release responds; it does not replace Render deployment-state monitoring or a long-running availability monitor. An old release will fail the expected-version check, but this project does not automatically revert a failed cloud deployment. Use the documented rollback procedure.

## File flow

`app.py` renders the template and serves `/health`. `static/app.js` requests that endpoint and updates the status card. `run.py` uses Waitress locally. Docker starts `gunicorn.conf.py` with `app:app`. `verify_release.py` is read-only; `deploy_render.py` is the only Python module that requests an external deployment, and it runs only when invoked/configured.
