# aidbox-python-sdk-example

# Development

## Local environment setup

1. Install pyenv and poetry globally
2. Install python3.12 python globally using pyenv
3. Inside the app directory, run `poetry env use /path/to/python312`
4. Run `poetry install`
5. Run `poetry shell` to activate virtual environment
6. Run `autohooks activate` to activate git hooks

## Testing

1. Run `cp .env.tests.local.example .env.tests.local`
2. Put your dev aidbox license key into `AIDBOX_LICENSE_TEST` in `.env.tests.local`
3. Run `make build-test` at the first time and every time once dependencies are updated/added
4. Run `make run-test`
5. You can kill the containers when complete to work with tests by run: `make down-test`

## IDE setup

Strongly recommended to use ruff and mypy plugins for IDE

## CI/CD

The project uses GitHub Actions for continuous integration and deployment:

- **Linting and Type Checking**: On every push and pull request, the workflow runs:
  - `ruff check` for code linting
  - `ruff format --check` for code formatting verification
  - `mypy` for static type checking

- **Docker Image Release**: On push to the `main` branch, after successful linting and type checking:
  - Builds a Docker image from `backend/Dockerfile`
  - Publishes the image to GitHub Packages (ghcr.io)
  - Tags the image with:
    - `latest` (for main branch)
    - Branch name
    - Git SHA

The workflow is defined in `.github/workflows/backend-ci-cd.yml`
