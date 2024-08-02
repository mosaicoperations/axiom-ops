DEFAULT_SETTINGS = {
    'LOG_GCP_ENABLED': {
        'default': False,
        'description': "Enable Google Cloud Platform logging",
        'var_type': bool
    },
    'LOG_GCP_PROJECT': {
        'default': 'orbital-airfoil-393318',
        'description': 'Project ID to log to',
        'var_type': str
    },
    'LOG_TO_FILE': {
        'default': False,
        'description': 'Write logs to a file',
        'var_type': bool
    },
    'LOG_FILE_LOCATION': {
        'default': None,
        'description': 'Location where to store log file(s). If not provided and logs set to export to file, will create a "logs" directory in root of project and store logs there',
        'var_type': str
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
    'LOG_FORMAT': {
        'default': '%(asctime)s - %(levelname)s - %(message)s',
        'description': 'format of output logs',
        'var_type': str
    },
    'LOG_STD_LEVEL': {
        'default': 'DEBUG',
        'description': 'How big each batch before sending logs to destination',
        'var_type': str
    },
    'LOG_FILE_LEVEL': {
        'default': 'INFO',
        'description': 'How big each batch before sending logs to destination',
        'var_type': str
    },
    'LOG_GCP_LEVEL': {
        'default': 'INFO',
        'description': 'How big each batch before sending logs to destination',
        'var_type': str
    },
    'TEST_ENV_VAR': {
        'default': 1,
        'description': "Test environment variable",
        'var_type': int
    },
    # Add more settings here
}