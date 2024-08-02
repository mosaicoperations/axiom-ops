import logging
import os
from pathlib import Path
from axiom.config.settings import Settings
from axiom.logging.utilities import get_log_file_location
try:
    from google.cloud import logging as gcp_logging
except ImportError:
    gcp_logging = None

class AxiomLogger:
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.handlers = []
        self.settings = Settings()
        self.settings.add_observer(self.update_logger)
        self.setup()

    def setup_console_logging(self):
        if self.settings.LOG_TO_CONSOLE:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.settings.LOG_STD_LEVEL)
            formatter = logging.Formatter(self.settings.LOG_FORMAT)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            self.handlers.append(console_handler)

    def setup_file_logging(self):
        if self.settings.LOG_TO_FILE:
            print(self.settings.LOG_TO_FILE)
            if not self.settings.LOG_FILE_LOCATION:
                self.settings.LOG_FILE_LOCATION = get_log_file_location()
            log_file_path = Path(self.settings.LOG_FILE_LOCATION)
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(self.settings.LOG_FILE_LEVEL)
            formatter = logging.Formatter(self.settings.LOG_FORMAT)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self.handlers.append(file_handler)

    def setup_gcp_logging(self):
        if self.settings.LOG_GCP_ENABLED:
            if gcp_logging is None:
                raise ImportError("Google Cloud Logging library not installed. Please install it to use GCP logging.")
            if self.settings.LOG_GCP_PROJECT == '':
                raise ValueError("LOG_GCP_PROJECT cannot be empty When LOG_GCP_PROJECT is enabled. Please provide a valid GCP project ID.")
            gcp_client = gcp_logging.Client(project=self.settings.LOG_GCP_PROJECT)
            gcp_handler = gcp_logging.handlers.CloudLoggingHandler(gcp_client)
            gcp_handler.setLevel(self.settings.LOG_GCP_LEVEL)
            self.logger.addHandler(gcp_handler)
            self.handlers.append(gcp_handler)
            
    def set_custom_logger(self, custom_logger):
        if not isinstance(custom_logger, logging.Logger):
            raise ValueError("Custom logger must be an instance of logging.Logger")
        self.logger = custom_logger
        self.handlers = self.logger.handlers

    def get_logger(self, name):
        return logging.getLogger(name)

    def setup(self):
        # Adds to handlers
        self.setup_console_logging()
        self.setup_file_logging()
        self.setup_gcp_logging()
        # self.set_custom_logger()
        
        # if no handlers were set do this
        if not self.handlers:
            # Default to console logging if no options are enabled
            self.settings.LOG_TO_CONSOLE = True
            self.setup_console_logging()

        if self.settings.LOG_BATCH_SIZE > 0:
            for handler in self.handlers:
                handler.setLevel(logging.INFO)
                handler = logging.handlers.MemoryHandler(self.settings.LOG_BATCH_SIZE, flushLevel=logging.ERROR, target=handler)
                self.logger.addHandler(handler)

    def update_logger(self, settings, name, value):
        # Remove all existing handlers
        for handler in self.handlers:
            self.logger.removeHandler(handler)
        self.handlers.clear()

        # Re-setup logging with new settings
        self.setup()
        
        
axiom_logger = AxiomLogger()

def get_logger(name):
    return axiom_logger.get_logger(name)

def setup_logging():
    axiom_logger.setup()

# This function can be called to change logging configuration at runtime
def reconfigure_logging():
    for handler in axiom_logger.handlers:
        axiom_logger.logger.removeHandler(handler)
    axiom_logger.handlers.clear()
    axiom_logger.settings = Settings()  # Reload settings
    axiom_logger.setup()