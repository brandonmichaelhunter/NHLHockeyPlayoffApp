import importlib
import shutil
import sys
from pathlib import Path


def test_factory_imports_in_container_layout(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    app_root = tmp_path / "app"
    app_root.mkdir()

    shutil.copytree(
        repo_root / "src" / "api" / "hockeyplayoffapi",
        app_root / "hockeyplayoffapi",
    )
    shutil.copytree(repo_root / "src" / "shared", app_root / "shared")

    sys.path[:] = [str(app_root)] + [
        entry for entry in sys.path if entry and entry != str(app_root)
    ]
    monkeypatch.setattr(sys, "path", sys.path[:])

    for module_name in [
        "shared",
        "shared.db",
        "shared.db.factory",
        "api",
        "api.hockeyplayoffapi",
        "hockeyplayoffapi",
        "hockeyplayoffapi.models",
    ]:
        sys.modules.pop(module_name, None)

    module = importlib.import_module("shared.db.factory")

    assert hasattr(module, "DBManagerFactory")
