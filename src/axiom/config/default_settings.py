from .settings_validators import validate_logger_type, enable_gcp_logging_validator

DEFAULT_SETTINGS = {
    'ENABLE_GCP_LOGGING': {
        'default': False,
        'validators': [enable_gcp_logging_validator],
        'description': "Enable Google Cloud Platform logging"
    },
    'TEST_ENV_VAR': {
        'default': 1,
        'validators': [],
        'description': "Test environment variable"
    },
    # Add more settings here
}