FROM ghcr.io/astral-sh/uv:debian-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


# Disable development dependencies
ENV UV_NO_DEV=1
ENV PYTHONPATH=/api
ENV DOCKER_ENV=true

WORKDIR /api

# Copy the pyproject.toml, uv.lock and source code files to the working directory root.
COPY ./pyproject.toml .
COPY ./uv.lock .
COPY ./src/api .

# Install the dependencies in the virtual environment.
RUN uv sync --locked

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

EXPOSE 8000
CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0", "--port", "8000", "./hockeyplayoffapi/main.py"]
