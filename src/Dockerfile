#FROM ghcr.io/astral-sh/uv:debian-slim
#FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
#FROM docker.io/astral/uv:python3.12-bookworm-slim
#FROM docker.io/astral-sh/uv:python3.12-bookworm-slim
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/



# Disable development dependencies
#ENV UV_NO_DEV=1
#ENV PYTHONPATH=/api
#ENV DOCKER_ENV=true
ENV UV_NO_DEV=1 \
    PYTHONPATH=/api \
    DOCKER_ENV=true \
    # Force uv to use the system Python environment instead of creating a nested venv
    UV_SYSTEM_PYTHON=1

#WORKDIR /shared


WORKDIR /api

# Copy the pyproject.toml, uv.lock and source code files to the working directory root.
COPY ./pyproject.toml ./uv.lock ./

# Install the dependencies in the virtual environment.
RUN uv sync --locked 

#COPY ./src/shared /shared

COPY ./src/api/ .
WORKDIR /api/shared
COPY ./src/shared .
WORKDIR /api/logs
#COPY ./src/logs .
WORKDIR /api

#COPY ./src/api .



# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
# Add this before the ENTRYPOINT
RUN mkdir -p /api/hockeyplayoffapi/data
# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

EXPOSE 8000
CMD ["uv", "run", "python", "-m", "uvicorn", "hockeyplayoffapi.main:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0", "--port", "8000", "./hockeyplayoffapi/main.py"]

#TODO: when running poe docker_run it says ModuleNotFoundError: No module named 'api' on linke 4 of the factory.py file.
