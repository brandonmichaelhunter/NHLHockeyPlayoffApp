import logging
import sys
from pathlib import Path


class appLogger:
    def __init__(
        self,
        name: str,
        log_file: str = "app.log",
        level=logging.DEBUG,
        enable_console: bool = True,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False

        log_path = Path(log_file)

        # If they pass a folder path like "/tmp/mylogs" then create it
        # and use a default filename "app.log"
        if log_path.suffix == "":
            log_path = log_path / "app.log"

        log_path.parent.mkdir(parents=True, exist_ok=True)

        self.console_handler = None
        if enable_console:
            self.console_handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        for handler in list(self.logger.handlers):
            self.logger.removeHandler(handler)

        if self.console_handler:
            self.console_handler.setFormatter(formatter)
            self.logger.addHandler(self.console_handler)

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger
