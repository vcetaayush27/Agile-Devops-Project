# Validation record

Prepared on 21 October 2026. This record describes checks run for this delivered implementation, not the earlier report's screenshots.

The Python 3.14 migration reran dependency installation, consistency checks, all 21 tests, both live WSGI servers, JavaScript syntax and shell/configuration checks. The simulated-DOM check below was completed for the unchanged frontend in the original delivery.

## Completed

| Check | Result |
|---|---|
| Dependency installation | Successful in an isolated Python 3.14.8 environment on Linux |
| Dependency consistency | `uv pip check`: no broken requirements |
| Automated suite | 21 pytest cases passed |
| Live local WSGI server | Waitress served `/health` and the expected page; exact-version check passed |
| Production WSGI configuration | Gunicorn served the expected release; final startup log contained no errors |
| Wrong-release rejection | Automated test confirmed that an old/mismatched version fails verification |
| Application behavior | Home page, updated names, assets, 404, allowed methods, escaping and response headers tested |
| Deploy-hook configuration | Exact digest encoding, correct host, required key and rejection of mutable tags tested without external deployment |
| JavaScript | Syntax check passed; health success, failure and recovery passed with a simulated DOM |
| Workflow and Compose files | YAML structure parsed; job order, gates and port mapping checked |
| Workflow shell commands | Bash syntax checks passed |
| Unix setup script | Shell syntax check passed |

## Not executed here

- Docker build/run: Docker is not installed in this workspace. The GitHub workflow includes the container build and smoke test.
- Windows batch launchers or Windows test execution: no Windows machine was available. The CI test matrix includes Windows after you push the repository.
- Native browser rendering: the browser download failed, so desktop/mobile visual layout has not been verified in an actual browser here. The app uses responsive CSS and the JavaScript behavior was checked separately.
- Docker Hub publication, Render deployment and hosted-release verification: these need your accounts and configuration. No cloud service was created and no external deployment was requested.
- Other Python versions, performance benchmarking or a security audit.

The application and server checks passed in the stated environment. Complete the Docker and cloud stages in IMPLEMENTATION_GUIDE.md to obtain evidence for your own deployment. The guide lists the screenshots and workflow artifact to retain.
