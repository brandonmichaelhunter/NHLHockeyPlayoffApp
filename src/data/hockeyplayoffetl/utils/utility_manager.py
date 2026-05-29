import logging
import sys

class utility_manager:
    
    def __init__(self, name: str, log_file: str = "app.log", level=logging.DEBUG, enable_console: bool = True):
        # 1. Create a logger instance
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        if enable_console:
            self.console_handler = logging.StreamHandler(sys.stdout)
        else:
            self.console_handler = None
        
        # Avoid duplicate logs if the logger already has handlers
        if not self.logger.handlers:
            # 2. Define a common format for logs
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            # 3. Create a Console Handler (prints to terminal)
            if self.console_handler:
                self.console_handler.setFormatter(formatter)
                self.logger.addHandler(self.console_handler)

            # 4. Create a File Handler (saves to a file)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def enable_console(self):
        """Adds the console handler if it does not exist."""
        if not self.console_handler:
            self.console_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            self.console_handler.setFormatter(formatter)
            self.logger.addHandler(self.console_handler)

    def disable_console(self):
        """Removes the console handler if it exists."""
        if self.console_handler:
            self.logger.removeHandler(self.console_handler)
            self.console_handler = None  # Clear reference
            
    def get_logger(self):
        """Returns the configured logger instance."""
        return self.logger
    
# logger_wrapper = CustomLogger("DynamicApp", log_file="dynamic.log")
#     log = logger_wrapper.get_logger()

#     # 1. Console is enabled by default
#     log.info("This will print to the console AND save to the file.")

#     # 2. Disable console output
#     logger_wrapper.disable_console()
#     log.info("This will ONLY save to the file (silent in console).")

#     # 3. Re-enable console output
#     logger_wrapper.enable_console()
#     log.info("This is back on the console again!")