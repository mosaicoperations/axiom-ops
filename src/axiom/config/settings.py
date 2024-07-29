import os 

# Define library wide settings such as logging or timeouts for API requests
# Set default behaviour of various things

# This will include constants:
#     DEFAULT_TIMEOUT = int(os.getenv('MYLIBRARY_DEFAULT_TIMEOUT', 30))
#     ENABLE_EXTENDED_LOGGING = os.getenv('MYLIBRARY_EXTENDED_LOGGING', 'False') == 'True'
#     API_VERSION = os.getenv('MYLIBRARY_API_VERSION', 'v1')
# but will also include a function(s) like this one:
#     def initialize_library(config_dict=None):
#         global DEFAULT_TIMEOUT, ENABLE_EXTENDED_LOGGING, API_VERSION
#         if config_dict:
#             DEFAULT_TIMEOUT = config_dict.get('DEFAULT_TIMEOUT', DEFAULT_TIMEOUT)
#             ENABLE_EXTENDED_LOGGING = config_dict.get('ENABLE_EXTENDED_LOGGING', ENABLE_EXTENDED_LOGGING)
#             API_VERSION = config_dict.get('API_VERSION', API_VERSION)
# which can be called by the user like so:
#     import mylibrary

#     config_settings = {
#         'DEFAULT_TIMEOUT': 20,
#         'ENABLE_EXTENDED_LOGGING': True,
#         'API_VERSION': 'v2'
#     }

#     mylibrary.initialize_library(config_settings)
# to overwrite settings to modify behaviour to desired state