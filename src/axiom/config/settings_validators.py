from typing import Any, Dict
from .settings_options import LoggerType

class SettingsValidator:
    @staticmethod
    def validate_enable_gcp_logging(value: bool) -> bool:
        return bool(value)

    # This is not used -> no setting for logger type
    @staticmethod
    def validate_logger_type(value: str) -> str:
        if value not in LoggerType._value2member_map_:
            raise ValueError(f"Invalid logger type. Must be one of {list(LoggerType._value2member_map_.keys())}")
        return value
    
    @staticmethod
    def validate_test_env_var(value: str) -> str:
        valid_values = ["yes", "no", "2", 2]
        if value not in valid_values:
            raise ValueError(f"Invalid test env var with value {value}. Must be one of {valid_values}")
        return value

    @classmethod
    def validate_setting(cls, setting_name: str, value: Any) -> Any:
        validator_method = getattr(cls, f"validate_{setting_name.lower()}", None)
        if validator_method:
            return validator_method(value)
        return value

    @classmethod
    def validate_settings_group(cls, settings: Dict[str, Any]) -> None:
        if settings.get('ENABLE_GCP_LOGGING') and settings.get('LOGGER_TYPE') != 'gcp':
            raise ValueError("ENABLE_GCP_LOGGING is True but LOGGER_TYPE is not 'gcp'")



def validate_logger_type():
    return

def enable_gcp_logging_validator(value):
    if not isinstance(value, bool):
        raise TypeError(f"Value of ENABLE_GCP_LOGGING must be a boolean")
    return True
# other functions to validate settings