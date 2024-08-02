from .logging.core import setup_logging, get_logger, reconfigure_logging
from .config.settings import Settings

print('hello from lib')
settings = Settings()
print('settings set')
# setup_logging()
print('logging set')