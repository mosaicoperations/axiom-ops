from datetime import datetime
import os
import json
import logging
import yaml
from typing import Any, Callable, Generic, List, Optional, Type, TypeVar, Union, Dict
from .default_settings import DEFAULT_SETTINGS
from .parse_environment_variables import parse_boolean, parse_json, parse_int, parse_list
from .settings_validators import SettingsValidator
from axiom.utilities.core import Singleton

logger = logging.getLogger(__name__)

T = TypeVar('T')

class Setting(Generic[T]):
    def __init__(self, name: str, default: T, validators: List[Callable[[Any], Any]] = None, description: str = "", var_type: T = ""):
        self.name: str = name
        self.default: T = default
        self.validators: List[Callable[[Any], Any]] = validators
        self.description: str = description
        self.var_type: T = var_type
        self._value: Optional[T] = None
        self.observers = []

    def __get__(self, obj: Any, objtype: Optional[Type] = None) -> T:
        if obj is None:
            return self
        if self._value is None:
            return self.default
        return self._value

    def __set__(self, obj: Any, value: Any) -> None:
        print(f"{datetime.now()}Setting value for {self.name} to {value} in {obj.__class__.__name__}")
        if self._value != value:
            validated_value = SettingsValidator.validate_setting(self.name, value)
            self._value = validated_value
            if hasattr(obj, 'validate_all'):
                obj.validate_all()
            self.notify_observers(obj)
            # print(f'notified observer {self.observers}')

    
    def reset(self) -> None:
        self._value = None
    
    def reset(self) -> None:
        self._value = None

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self, obj):
        for observer in self.observers:
            observer(obj, self.name, self._value)


class Settings(metaclass=Singleton):
    def __init__(self):
        self._load_default_settings()
        self.load_from_env()
        self.validate_all()
        self.observers = []
    
    def _load_default_settings(self):
        for name, config in DEFAULT_SETTINGS.items():
            setattr(self.__class__, name, Setting(
                name=name,
                default=config['default'],
                description=config['description'],
                var_type=config["var_type"]
            ))

    def _parse_env_value(self, setting, env_value):
        type_parsers = {
            bool: parse_boolean,
            int: parse_int,
            dict: parse_json,
            list: parse_list,
            str: lambda x: str(x) #no-op b/c nothing vars are strings by default
        }
        print('here')
        parser = type_parsers.get(setting.var_type, lambda x: x) # default to no-op if type not specified in type_parsers
        return parser(env_value)
    
    def load_from_env(self):
        for name, setting in self.__class__.__dict__.items():
            if isinstance(setting, Setting):
                env_value = os.environ.get(name)
                if env_value is not None:
                    try:
                        env_value = self._parse_env_value(setting, env_value)
                    except ValueError as e:
                        print(f"Failed to parse environment variable {name}: {e}")
                    setattr(self, name, env_value)                       
        
    def load_from_json(self, file_path: str)-> None:
        try:
            with open(file_path, 'r') as file:
                settings = json.load(file)
            self.update_library_settings(settings)
        except FileNotFoundError():
            print(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
                
    def load_from_yaml(self, file_path: str) -> None:
        try:
            with open(file_path, 'r') as file:
                settings = yaml.safe_load(file)
            self.update_library_settings(settings)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
        
    def update_setting(self, name: str, value: any) -> None:
        if hasattr(self, name):
            setting = getattr(self.__class__, name, None)
            print(f"Attempting to update {name} with value {value} - current type is {type(setting)}")
            if isinstance(setting, Setting):
                # Ensure we use the __set__ method
                setting.__set__(self, value)
            else:
                raise ValueError(
                    f"{name} is not a valid setting because it is of type {type(setting)}, not Setting.")
        else:
            raise AttributeError(f"No setting named {name} exists.")

    def update_library_settings(self, setting_dict: dict[str: any]) -> None:
        if not isinstance(setting_dict, dict):
            raise TypeError(
                "Invalid argument: you must pass a dictionary to set settings.")
        for name, val in setting_dict.items():
            self.update_setting(name, val)
            self.notify_observers(name, val)

    def list_settings(self, show_values: bool = False) -> Union[List[str], Dict[str, any]]:
        if show_values:
            settings_dict = {
                name: getattr(self, name) for name, setting in self.__class__.__dict__.items() if isinstance(setting, Setting)
            }
            return settings_dict
        settings_list = [name for name, setting in self.__class__.__dict__.items() if isinstance(setting, Setting)]
        return settings_list

    def reset_to_defaults(self) -> None:
        for name, setting in self.__class__.__dict__.items():
            if isinstance(setting, Setting):
                setting.reset()
                
    def export_to_dict(self) -> Dict[str, Any]:
        return {name: getattr(self, name) for name, setting in self.__class__.__dict__.items() if isinstance(setting, Setting)}
        
    def get_setting_info(self, name: str) -> Dict[str, Any]:
        setting = getattr(self.__class__, name, None)
        if isinstance(setting, Setting):
            return {
                "name": setting.name,
                "default": setting.default,
                "current_value": getattr(self, name),
                "description": setting.description,
                "type": setting.var_type
            }
        raise AttributeError(f"No setting named {name} exists.")
    
    def validate_all(self):
        settings_dict = {name: getattr(self, name) for name in DEFAULT_SETTINGS}
        try:
            SettingsValidator.validate_settings_group(settings_dict)
        except ValueError as e:
            print(f"Settings validation error: {e}")
            
    def add_observer(self, observer):
        self.observers.append(observer)
        for name in DEFAULT_SETTINGS:
            setting = getattr(self.__class__, name)
            setting.add_observer(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)
        for name in DEFAULT_SETTINGS:
            setting = getattr(self.__class__, name)
            setting.remove_observer(observer)

    def notify_observers(self, name, value):
        for observer in self.observers:
            observer(self, name, value)

    def __str__(self) -> str:
        return "\n".join([f"{name}: {getattr(self, name)}" for name, setting in self.__class__.__dict__.items() if isinstance(setting, Setting)])

    def __repr__(self) -> str:
        return self.__str__()
