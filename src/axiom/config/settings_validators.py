def validate_logger_type():
    return

def enable_gcp_logging_validator(value):
    if not isinstance(value, bool):
        raise TypeError(f"Value of ENABLE_GCP_LOGGING must be a boolean")
    return True
# other functions to validate settings