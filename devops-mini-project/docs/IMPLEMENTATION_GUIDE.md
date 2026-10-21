# Complete implementation guide

Work through these stages in order. You can run the application first and add cloud delivery afterward. Use your own accounts; the Docker Hub namespace appearing in the original report is not yours to reuse.

## 1. Run and understand the application

1. Extract the ZIP to a normal folder, for example `C:\Projects\devops-mini-project`.
2. Install Python 3.14, enabling **Add Python to PATH** during installation.
3. Open VS Code → File → Open Folder → select the extracted project folder.
4. Open Terminal → New Terminal.
5. Run ` .\SETUP_WINDOWS.bat `, then ` .\START_PROJECT.bat `.
6. Open `http://127.0.0.1:5000` in a browser.
7. Confirm the greeting, student names and green **Healthy** runtime status.
8. Open `http://127.0.0.1:5000/health`. The local version should be `local`.
9. In a second terminal, run `.\.venv314\Scripts\python.exe -m pytest -q`.

The setup script creates `.venv314` and installs the pinned requirements. `run.py` starts Waitress. You do not need Docker for this stage. Keep the server terminal open and press Ctrl+C when finished.

## 2. Put the project in GitHub

Install Git if necessary. Create an **empty** GitHub repository named `devops-mini-project`. Do not initialize it with a README because this project already has one.

From the project folder in VS Code, run the commands below. Replace `YOUR_GITHUB_USERNAME` with your own username before running the remote command:

```bash
git init
git add .
git commit -m "Add Flask app and tested delivery pipeline"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/devops-mini-project.git
git push -u origin main
```

If Git requests your identity, set your actual name and email using `git config --global user.name "Your Name"` and `git config --global user.email "your-email@example.com"`, then repeat the commit. GitHub authentication may open a browser. Do not use a GitHub account password as a command-line token.

The included `.gitignore` excludes virtual environments, generated files and `.env` files. Keep the `.github` directory: it contains the workflow. On GitHub, open **Actions** and select **Test build and deploy**. Initially it tests Python on Linux/Windows and checks the Docker container. It does not publish or deploy until you enable those stages.

## 3. Build the container locally

Install and start Docker Desktop. On Windows, use Linux containers and complete any WSL setup requested by Docker Desktop. Check that `docker version` prints both client and server information.

Stop the local Python server first to free port 5000. From the project folder:

```bash
docker build --platform linux/amd64 --build-arg APP_VERSION=local-docker -t devops-mini-project:local .
docker run --rm --name devops-demo -p 127.0.0.1:5000:10000 devops-mini-project:local
```

Visit `http://127.0.0.1:5000`. `/health` should now show version `local-docker`. This checks the packaged application, not just the Python source. Gunicorn runs inside the container, while the Python-only local launcher uses Waitress.

In a second terminal:

```powershell
.\.venv314\Scripts\python.exe -m scripts.verify_release --url http://127.0.0.1:5000 --expected local-docker
```

A passing check verifies health, the version and page messages. Stop the foreground container with Ctrl+C.

## 4. Prepare Docker Hub and enable publication

1. Create or sign in to your Docker Hub account.
2. Create a repository named **devops-mini-project** in your own username namespace. A public repository is the simplest setup for this assignment; use a private one only if you also configure Render registry credentials.
3. Create a Docker Hub access token with the read/write permissions needed to push to your repository. Keep it private.
4. In your GitHub repository, open **Settings → Secrets and variables → Actions → Secrets**.
5. Create these repository secrets:

| Secret name | Value |
|---|---|
| `DOCKERHUB_USERNAME` | Your Docker Hub username, lowercase |
| `DOCKERHUB_TOKEN` | Your Docker Hub token with permission to push |

6. In the adjacent **Variables** tab, create `ENABLE_PUBLISH` with value `true`.
7. Open **Actions → Test build and deploy → Run workflow**, select `main`, and run it.
8. Wait for the tests, image smoke check and publication to pass.
9. Verify Docker Hub contains `YOUR_DOCKERHUB_USERNAME/devops-mini-project`, including `latest` and a commit-SHA tag.

The workflow builds one image, starts it, checks it, and publishes that same image. It does not rebuild a different artifact after testing. Render is intentionally not required yet; this first publication creates the image needed for the next stage.

## 5. Create the Render image-backed service

1. Sign in to Render and choose **New → Web Service → Existing Image**.
2. Enter `docker.io/YOUR_DOCKERHUB_USERNAME/devops-mini-project:latest`, replacing the username. Use the exact same repository as the workflow.
3. For a private image, add a registry credential that can read the repository.
4. Choose the service name and region. Review the plans available to your account; this project does not assume that hosting is free.
5. Keep the image's default startup command. Do not enter a Flask development-server command.
6. Set the health-check path to `/health`. The container listens on `0.0.0.0` and uses `PORT`, defaulting to `10000`.
7. Do **not** set `APP_VERSION` manually in Render. Its value is baked into the image by CI.
8. Create the service, wait for the deployment and open the assigned HTTPS URL.
9. Confirm `/health` displays the SHA from the workflow that published the image.

If the dashboard offers a different layout, choose the option for deploying an existing Docker image rather than building directly from GitHub. That preserves the report's GitHub Actions → Docker Hub → Render architecture.

## 6. Connect automatic deployment

In the Render service's Settings, copy the complete **Deploy Hook URL**. Treat it as a secret and do not paste it into your source files or screenshots.

In GitHub → Settings → Secrets and variables → Actions, add:

| Location | Name | Value |
|---|---|---|
| Secret | `RENDER_DEPLOY_HOOK` | Complete hook URL copied from Render |
| Variable | `RENDER_SERVICE_URL` | Your service base URL, such as `https://your-service.onrender.com` |
| Variable | `ENABLE_DEPLOY` | `true` |

Keep `ENABLE_PUBLISH=true` and the Docker Hub secrets from stage 4. The service URL must be the base address, without `/health`, query parameters or a trailing extra path.

Run the GitHub workflow on `main` again. After publication it requests the **exact image digest** through Render's deploy hook, then polls `/health` until the expected commit appears and checks the homepage. A successful hook request alone is not marked as deployment success. Verification waits up to ten minutes.

After success, download the **verified-release** artifact from the Actions run. Its `release.json` contains the image digest, commit identifier, public URL and verification time. The hook secret is not included.

## 7. Demonstrate an update

1. Change a sentence in `templates/index.html`, such as the descriptive paragraph. Keep the two report confirmation messages and routes intact because the smoke check expects them.
2. Save the file, then run:

```bash
git add .
git commit -m "Update application description"
git push
```

3. Watch the workflow: tests → image smoke test → publication → deployment → verification.
4. Open the service. The updated description and new commit identifier should appear.
5. Compare `/health` with `git rev-parse HEAD`. They should match after successful verification.

Pull requests are tested but are not published or deployed. Only `main` can publish/deploy in this workflow, and only when the explicit enable variables are set. Workflow-level concurrency avoids overlapping releases for the same branch; GitHub may replace a pending run with a newer pending run, so not every rapidly pushed intermediate commit is guaranteed to deploy.

## 8. Collect your actual submission evidence

Capture your own repository files, successful Actions run, Docker Hub image/tag, Render deployment log and live application. Also keep the test summary and verified-release artifact. Do not present the report's old screenshots as evidence of your newly deployed build.

## Troubleshooting

| Problem | Action |
|---|---|
| Python not recognized | Install Python 3.14 with PATH enabled; reopen VS Code. |
| Missing module | Run `SETUP_WINDOWS.bat` again and use `.venv314` Python. |
| Wrong terminal directory | Open the folder containing `app.py` and the requirements files. |
| Port 5000 already used | Stop the previous process, or set `$env:PORT="5001"` for the Python server. For Docker use `-p 127.0.0.1:5001:10000`. |
| Docker cannot connect | Start Docker Desktop and wait until `docker version` shows a server. |
| Actions does not start | Confirm the branch is `main`, Actions are enabled, and `.github/workflows/ci-cd.yml` was pushed. |
| Publish/deploy skipped | Enable the corresponding repository variable with the exact lowercase value `true`. |
| Docker push denied | Verify username, namespace, token permissions and repository existence. |
| Render image pull fails | Check the image path and private-registry credentials. |
| Hook request fails | Copy the complete hook URL again; ensure the Render service uses the same Docker Hub repository. |
| Verification times out | Inspect Render startup logs; check `RENDER_SERVICE_URL`, PORT and the `/health` version. Do not set APP_VERSION in Render. |
| Page is healthy but old | The expected release check should fail. Inspect the deployed digest and recent Render deployments. |
| Tests fail after an edit | Read the failed assertion, correct the change and rerun tests before pushing. |

## Rollback

Use Render's deployment history to select a previous successful deployment, or select a retained known-good image digest in the service settings and deploy it. Keep old images available in Docker Hub. Changing `latest` alone is not a reliable rollback record. After recovery, correct the source and release a new commit; otherwise the next enabled pipeline may replace the rollback.

## Official documentation checked for this setup

- Flask on Waitress: https://flask.palletsprojects.com/en/stable/deploying/waitress/
- GitHub Actions image publication: https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images
- Render prebuilt images: https://render.com/docs/deploying-an-image
- Render deploy hooks and the `imgURL` digest parameter: https://render.com/docs/deploy-hooks
- Render ports and health configuration: https://render.com/docs/web-services

The package automates the implementation after configuration. It does not create accounts, purchase hosting, or contain working credentials for you.
