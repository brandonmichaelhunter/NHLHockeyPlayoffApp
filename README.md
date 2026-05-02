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
- Activate the virtual environment: ```source .venv/Scripts/activate```
- Running the app
  - cd into your app directory: ```cd apps/api/hockeyplayoffapi```
  - uv run fastapi dev
  

