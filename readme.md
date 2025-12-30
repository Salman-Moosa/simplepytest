# CI/CD Pipeline Documentation

## Overview

This repository uses **GitHub Actions** for continuous integration and deployment. The pipeline consists of **4 workflows** that handle different stages of the development lifecycle, pushing Docker images to **Docker Hub**.

---

## Repository Structure

```
.github/workflows/
├── build-and-test.yml   # PR validation & master branch testing
├── dev.yml              # Development builds
├── stage.yml            # Staging builds
└── prod.yml             # Production builds
```

---

## Workflow Details

### 1. Build and Test (`build-and-test.yml`)

| Property | Value |
|----------|-------|
| **Purpose** | Validate code quality and run tests |
| **Pushes to Docker Hub?** | ❌ No |

#### Trigger Conditions
```yaml
on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]
```

- **Push to `master`**: Runs when code is directly pushed to master
- **Pull Request to `master`**: Runs when a PR is opened/updated targeting master

#### What It Does
1. Checks out the repository code
2. Builds Docker image locally (tagged as `simplepytest`)
3. Runs the container with `TEST_NUMBER` environment variable (from GitHub Variables)
4. **Does NOT push** to any registry - purely for validation

#### Environment Variables Used
| Variable | Source | Purpose |
|----------|--------|---------|
| `TEST_NUMBER` | `vars.TEST_NUMBER` | Passed to container at runtime for testing |

---

### 2. Dev Build and Push (`dev.yml`)

| Property | Value |
|----------|-------|
| **Purpose** | Build and push development images |
| **Pushes to Docker Hub?** | ✅ Yes |
| **Image Tag Format** | `dev-<short-sha>` |

#### Trigger Conditions
```yaml
on:
  push:
    branches: [ dev ]
```

- Triggers **only** on push to the `dev` branch
- Does NOT run on pull requests

#### Docker Image Naming
```
<DOCKER_USERNAME>/<DOCKER_REPO>:dev-<commit-sha>
```

**Example:** `salmanmoosa/simplepytest:dev-a1b2c3d`

#### What It Does
1. Checks out repository code
2. Sets up Docker Buildx (for advanced build features)
3. Authenticates to Docker Hub
4. Extracts short Git commit SHA (7 characters)
5. Builds and pushes image with `dev-` prefix tag
6. Uses GitHub Actions cache for faster builds

#### Secrets & Variables Required
| Name | Type | Purpose |
|------|------|---------|
| `DOCKER_USERNAME` | Secret | Docker Hub username |
| `DOCKER_PASSWORD` | Secret | Docker Hub password/token |
| `DOCKER_REPO` | Variable | Repository name on Docker Hub |

---

### 3. Staging Build and Push (`stage.yml`)

| Property | Value |
|----------|-------|
| **Purpose** | Build and push staging/QA images |
| **Pushes to Docker Hub?** | ✅ Yes |
| **Image Tag Format** | `stage-<short-sha>` |

#### Trigger Conditions
```yaml
on:
  push:
    branches: [ staging ]
```

- Triggers **only** on push to the `staging` branch

#### Docker Image Naming
```
<DOCKER_USERNAME>/<DOCKER_REPO>:stage-<commit-sha>
```

**Example:** `salmanmoosa/simplepytest:stage-e4f5g6h`

#### What It Does
1. Checks out repository code
2. Sets up Docker Buildx
3. Authenticates to Docker Hub
4. Extracts short Git commit SHA
5. Builds and pushes image with `stage-` prefix tag
6. Uses GitHub Actions cache

#### Secrets & Variables Required
| Name | Type | Purpose |
|------|------|---------|
| `DOCKER_USERNAME` | Secret | Docker Hub username |
| `DOCKER_PASSWORD` | Secret | Docker Hub password/token |
| `DOCKER_REPO` | Variable | Repository name on Docker Hub |

---

### 4. Production Build and Push (`prod.yml`)

| Property | Value |
|----------|-------|
| **Purpose** | Build and push production-ready images |
| **Pushes to Docker Hub?** | ✅ Yes |
| **Image Tag Format** | `prod-<short-sha>` |

#### Trigger Conditions
```yaml
on:
  workflow_dispatch:    # Manual trigger
  push:
    branches: [ master ]
```

- **Push to `master`**: Automatic trigger on master push
- **`workflow_dispatch`**: Can be manually triggered from GitHub UI (Actions tab → "Run workflow")

#### Docker Image Naming
```
<DOCKER_USERNAME>/<DOCKER_REPO>:prod-<commit-sha>
```

**Example:** `salmanmoosa/simplepytest:prod-i7j8k9l`

#### What It Does
1. Checks out repository code
2. Sets up Docker Buildx
3. Authenticates to Docker Hub
4. Extracts short Git commit SHA
5. Builds and pushes image with `prod-` prefix tag
6. Uses GitHub Actions cache

#### Secrets & Variables Required
| Name | Type | Purpose |
|------|------|---------|
| `DOCKER_USERNAME` | Secret | Docker Hub username |
| `DOCKER_PASSWORD` | Secret | Docker Hub password/token |
| `DOCKER_REPO` | Variable | Repository name on Docker Hub |

---

## Branch-to-Environment Mapping

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────────────────┐
│   Branch    │ ──► │  Workflow   │ ──► │         Docker Tag              │
├─────────────┤     ├─────────────┤     ├─────────────────────────────────┤
│    dev      │     │   dev.yml   │     │  <user>/<repo>:dev-<sha>        │
│   staging   │     │  stage.yml  │     │  <user>/<repo>:stage-<sha>      │
│   master    │     │  prod.yml   │     │  <user>/<repo>:prod-<sha>       │
│   master    │     │ build-test  │     │  (local only, no push)          │
│   PR→master │     │ build-test  │     │  (local only, no push)          │
└─────────────┘     └─────────────┘     └─────────────────────────────────┘
```

---

## GitHub Configuration Required

### Secrets (Repository Settings → Secrets and variables → Actions → Secrets)

| Secret Name | Description |
|-------------|-------------|
| `DOCKER_USERNAME` | Your Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub access token (recommended) or password |

### Variables (Repository Settings → Secrets and variables → Actions → Variables)

| Variable Name | Description | Example |
|---------------|-------------|---------|
| `DOCKER_REPO` | Docker Hub repository name | `simplepytest` |
| `TEST_NUMBER` | Test parameter for build-and-test workflow | `42` |

---

## Docker Image Lifecycle

```
Developer Push                    Docker Hub Result
──────────────                    ─────────────────

git push origin dev          →    user/repo:dev-abc1234
        │
        ▼ (merge to staging)
git push origin staging      →    user/repo:stage-def5678
        │
        ▼ (merge to master)
git push origin master       →    user/repo:prod-ghi9012
```

---

## Caching Strategy

All deployment workflows use **GitHub Actions Cache** for Docker layers:

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

- `type=gha`: Uses GitHub Actions cache backend
- `mode=max`: Caches all layers, not just final image layers
- **Benefit**: Significantly faster builds on unchanged layers

---

## Dockerfile Reference

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY main.py .
CMD ["python", "main.py"]
```

- **Base Image**: `python:3.11-slim` (minimal Python runtime)
- **Working Directory**: `/app`
- **Entry Point**: Runs `main.py` with Python

---

## Quick Reference: Triggering Workflows

| Action | Workflow Triggered | Result |
|--------|-------------------|--------|
| Push to `dev` | dev.yml | `dev-<sha>` image pushed |
| Push to `staging` | stage.yml | `stage-<sha>` image pushed |
| Push to `master` | prod.yml + build-and-test.yml | `prod-<sha>` image pushed + tests run |
| PR to `master` | build-and-test.yml | Tests run (no image pushed) |
| Manual dispatch (master) | prod.yml | `prod-<sha>` image pushed |
