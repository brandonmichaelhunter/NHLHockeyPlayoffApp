# NHLHockeyPlayoffApp

NHLHockeyPlayoffApp is a Python-based application that combines:

- a FastAPI web application for NHL playoff scores, schedules, teams, and stats
- an ETL pipeline that pulls NHL data from public NHL APIs into a local SQLite database

The project is organized around two main workflows:

1. API application: serves data through FastAPI routes and Jinja templates
2. ETL application: extracts, transforms, and loads NHL data into the database used by the API

---

## Tech stack

- Python 3.13+
- FastAPI + Uvicorn
- SQLModel + SQLAlchemy
- SQLite
- Jinja2 templates
- Docker
- pytest for testing
- Ruff for linting
- pre-commit for automated checks
- pip-audit for vulnerability scanning
- uv for dependency and environment management

---

## Project dependencies

The project dependencies are defined in [pyproject.toml](pyproject.toml).

### Core runtime dependencies

- fastapi
- uvicorn
- sqlmodel
- sqlalchemy
- pydantic
- httpx
- requests
- python-dotenv
- jinja2
- python-multipart
- psycopg[binary]
- asyncpg

### Development and validation dependencies

- pytest
- pytest-asyncio
- pytest-cov
- pytest-httpx
- pytest-mock
- ruff
- pre-commit
- pip-audit
- pyrefly
- poethepoet

---

## Install uv

This project uses uv as the package and environment manager.

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify it is installed:

```bash
uv --version
```

---

## Install project dependencies

From the repository root:

```bash
uv sync
```

This creates the project virtual environment and installs the dependencies from the lock file.

If you want to install the development dependencies explicitly:

```bash
uv sync --group dev
```

---

## Activate the virtual environment

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Once activated, your shell will use the project Python environment.

---

## Run the API app

From the repository root:

```bash
uv run poe run_api
```

This starts the FastAPI app in development mode with reload enabled.

The app is typically served on:

```text
http://127.0.0.1:8000
```

You can also run it manually with uvicorn:

```bash
uv run uvicorn src.api.hockeyplayoffapi.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Run the ETL app

From the repository root:

```bash
uv run poe run_etl
```

This runs the ETL entry point in [src/data/hockeyplayoffetl/etl.py](src/data/hockeyplayoffetl/etl.py).

---

## Run tests

The project defines pytest markers in [pyproject.toml](pyproject.toml), including:

- api_unit
- api_integration
- unit
- integration

### API unit tests

```bash
uv run poe api_unit_test
```

Or directly:

```bash
pytest -m "api_unit" -v
```

### API integration tests

```bash
uv run poe api_integration_test
```

Or directly:

```bash
pytest -m "api_integration" -v
```

### Full API test suite

```bash
uv run poe api_tests
```

---

## Run the linter

This project uses Ruff.

```bash
uv run poe lint
```

Or directly:

```bash
ruff check .
```

---

## Run the API app in Docker

Build the Docker image:

```bash
docker build -f "src/Dockerfile" -t hockeyplayoff:latest .
```

Run the container:

```bash
docker run -p 8000:8000 hockeyplayoff:latest
```

The app should be reachable on:

```text
http://localhost:8000
```

The Dockerfile for the API is in [src/Dockerfile](src/Dockerfile).

---

## What is pre-commit?

Pre-commit is a tool that runs configured hooks before you commit code. It helps catch formatting, lint, and basic validation issues early.

This project includes a [./.pre-commit-config.yaml](.pre-commit-config.yaml) file and the command is already configured in [pyproject.toml](pyproject.toml).

### Install pre-commit

```bash
uv tool install pre-commit --with pre-commit-uv
```

### Run pre-commit manually

```bash
uv run poe precommit
```

Or directly:

```bash
pre-commit run --all-files
```

---

## Check for vulnerabilities natively

This project is set up to use pip-audit for dependency vulnerability checks.

Run the audit task:

```bash
uv run poe audit
```

Or run directly:

```bash
uv run pip-audit --output pip-audit-report.md --format markdown
```

This generates a report file named [pip-audit-report.md](pip-audit-report.md).

---

## What is build validation?

Build validation is a lightweight sanity check that confirms the application can start and that the most important health endpoint responds correctly.

In this project, build validation is implemented in [build_validation.py](build_validation.py). It imports the FastAPI app and requests the `/health` endpoint. If the response is not successful, the script exits with an error.

### Run build validation

```bash
uv run validate
```

This executes the `validate_app_build` function defined in [build_validation.py](build_validation.py).

---

## Contribution guidelines

Contributions are welcome.

### Recommended workflow

1. Clone the repository
2. Create a feature branch
3. Activate the virtual environment
4. Install dependencies with `uv sync`
5. Make your changes
6. Run the relevant tests
7. Run the linter
8. Run pre-commit
9. Open a pull request

### Typical local validation before opening a PR

```bash
source .venv/bin/activate
uv sync
uv run poe api_unit_test
uv run poe lint
uv run poe precommit
```

If you are preparing a change that affects the API runtime, also run:

```bash
uv run validate
```

---

## Useful commands summary

```bash
uv sync
source .venv/bin/activate
uv run poe run_api
uv run poe run_etl
uv run poe api_unit_test
uv run poe api_integration_test
uv run poe lint
uv run poe precommit
uv run poe audit
uv run validate
```

# Create Azure service principal for GitHub Actions and grant it Contributor access to the resource group
- Run the script `bash scripts/create-azure-service-principal.sh` to create a service principal for GitHub Actions to deploy to Azure and grant it Contributor access to the resource group.
- Save the Secret in GitHub Actions as `AZURE_CREDENTIALS` with the output of the script.
- Note: You will need to replace the placeholder in the script with your actual resource group name.

# Grant AKS access to the service principal
- Run the script `bash scripts/grant-aks-access-to-sp.sh` to grant the service principal access to the AKS cluster.
- Note: You will need to replace the placeholders in the script with your actual subscription ID, resource group name, and cluster name.

---

## Notes

- The app data layer relies on SQLite for local development and demo usage.
- The ETL pipeline extracts NHL data from public API endpoints and loads it into the local database used by the API.
- The project is currently configured for local development workflows and Docker-based deployment.

