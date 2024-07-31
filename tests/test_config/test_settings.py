import pytest
from unittest.mock import patch, mock_open

# Assuming the code above is in a module named settings_module
from axiom.config import Settings, Setting

def test_setting_initialization():
    validators = [lambda x: x + 1]
    s = Setting(name="test", default=10, validators=validators, var_type=int)
    assert s.name == "test"
    assert s.default == 10
    assert s.var_type == int

def test_setting_get_default():
    s = Setting(name="test", default=20, validators=[], var_type=int)
    settings = Settings()
    assert s.__get__(settings) == 20

def test_setting_set_and_get_value():
    s = Setting(name="test", default=20, validators=[], var_type=int)
    settings = Settings()
    s.__set__(settings, 30)
    assert s.__get__(settings) == 30

@patch('os.environ', {'TEST_SETTING': '123'})
def test_load_from_env():
    settings = Settings()
    assert settings.TEST_SETTING == 123

@patch('builtins.open', new_callable=mock_open, read_data='{"TEST_SETTING": "value"}')
def test_load_from_json(mock_file):
    settings = Settings()
    settings.load_from_json("dummy_path")
    assert settings.TEST_SETTING == "value"

@patch('builtins.open', new_callable=mock_open, read_data="TEST_SETTING: value\n")
@patch('yaml.safe_load', return_value={'TEST_SETTING': 'value'})
def test_load_from_yaml(mock_yaml, mock_file):
    settings = Settings()
    settings.load_from_yaml("dummy_path")
    assert settings.TEST_SETTING == 'value'

def test_update_setting():
    settings = Settings()
    settings.update_setting("TEST_SETTING", "new_value")
    assert settings.TEST_SETTING == "new_value"

def test_reset_to_defaults():
    settings = Settings()
    settings.update_setting("TEST_SETTING", "new_value")
    settings.reset_to_defaults()
    assert settings.TEST_SETTING == settings.__class__.TEST_SETTING.default

def test_export_to_dict():
    settings = Settings()
    settings_dict = settings.export_to_dict()
    assert "TEST_SETTING" in settings_dict
    assert settings_dict["TEST_SETTING"] == settings.TEST_SETTING

@pytest.mark.parametrize("input_value, expected", [
    ("True", True),
    ("False", False),
    ("123", 123),
    ('{"key": "value"}', {'key': 'value'}),
    ("[1, 2, 3]", [1, 2, 3])
])
def test_parse_env_value(input_value, expected):
    settings = Settings()
    setting = Setting(name="test", default=None, validators=[], var_type=type(expected))
    assert settings._parse_env_value(setting, input_value) == expected
