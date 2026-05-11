# NHLHockeyPlayoffApp
A repo to host my NHL Hockey Playoff App

# Install uv
 - What is uv? 
   - Uv a Python package and project manager writen in Rust.
   - This tool replaces pip, pipx, poetry, and virtualenv with a single tool.
 - Install uv:
   - ```curl -LsSf https://uv.eustace.io/install.sh | sh``` 
 - Verify installation: ```uv --version```
 - Tools
   - What are tools?
     - Tools are Python pakcages that provide command-line interfaces.
     - Here are a list of tools we need to install for this project:
        fasttyper, pyupgrade, ruff, tox
      - Install tools: ```uv tool add fasttyper pyupgrade ruff tox```
- Verify tools installation: ```uv tool list```
- Packages to install
  - uv add fastapi --extra standard
  - uv add sqlmodel
# How to run API and ETL apps locally
- Activate the virtual environment: ```source .venv/Scripts/activate```
- How to run FastAPI app locally:
  - Activate the virtual environment: ```source .venv/Scripts/activate```
  - ```cd NHLHockeyPlayoffApp``` to get to the root of the project
  - ```poe run_api``` to run the app locally
- How to run the ETL locally:
  - Activate the virtual environment: ```source .venv/Scripts/activate```
  - ```cd NHLHockeyPlayoffApp``` to get to the root of the project
  - ```poe run_etl``` to run the ETL locally
  
# Testing
- How to run tests:
  - ```cd NHLHockeyPlayoffApp ``` to get to the root of the project
  - ```poe unit_test``` to run unit tests
  - ```poe integration_test``` to run integration tests

# Linting
 - How to run linter
   - ``` poe lint ```

# Runing the app locally
- ```cd NHLHockeyPlayoffApp ``` to get to the root of the project
- ```poe run_app``` to run the app locally

# Docker
- How to build a dockerfile locally
  - ``` cd NHLHockeyPlayoffApp ``` to get to the root of the project
  - ``` poe docker_build ``` to build the docker image locally
- How to run a docker container locally
  - ``` poe docker_run ``` to run the docker container locally

