# Registry and CI publishing instructions

This document describes how to configure GitHub Actions to publish Docker images to GitHub Container Registry (GHCR) from the infra/openapi-client branch. The workflows in the repo support building, scanning (Trivy) and signing (cosign) images before pushing to GHCR.

Secrets to add in the repository (Settings → Secrets and variables → Actions):

- CR_PAT: A Personal Access Token with `write:packages` (and `repo` for private repos) scope. Alternatively, you can configure the workflow to use GITHUB_TOKEN if allowed in your org.
- COSIGN_KEY: (optional) base64-encoded private key to sign images with cosign.
- COSIGN_PASSWORD: password for the cosign key (if used).

How to create a PAT for GHCR:
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Generate new token.
2. Select scopes: `write:packages`, and `repo` if your repository is private.
3. Copy the token and add it to your repo secrets as `CR_PAT`.

Notes:
- If `CR_PAT` is not configured the publishing step will be skipped but the build+scan will run (local image). 
- The cosign signing step runs only when both `CR_PAT` and `COSIGN_KEY` are configured.

Recommendations:
- Use GitHub Actions Secrets to store credentials.
- Enable branch protection on `main` and require PR reviews before merging.
- Use image scanning (Trivy) and enforce `fail-on` policy if vulnerabilities are above acceptable level.
