DEFAULT_SETTINGS = {
    'ENABLE_GCP_LOGGING': {
        'default': False,
        'description': "Enable Google Cloud Platform logging",
        'var_type': bool
    },
    'LOG_TO_FILE': {
        'default': False,
        'description': 'Write logs to a file',
        'var_type': bool
    },
    'LOG_TO_CONSOLE': {
        'default': True,
        'description': 'Write logs to stdout',
        'var_type': bool
    },
    'LOG_BATCH_SIZE': {
        'default': 0,
        'description': 'How big each batch before sending logs to destination',
        'var_type': int
    },
        
    'TEST_ENV_VAR': {
        'default': 1,
        'description': "Test environment variable",
        'var_type': int
    },
    # Add more settings here
}