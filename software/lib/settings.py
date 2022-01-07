import json
from pathlib import Path
from pydantic import BaseSettings
from pydantic.env_settings import SettingsSourceCallable
from typing import Any, Dict, Tuple


def json_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """
    A simple settings source that loads variables from a JSON file
    at the project's root.

    Here we happen to choose to use the `env_file_encoding` from Config
    when reading `config.json`
    """
    encoding = settings.__config__.env_file_encoding
    path = Path('config.json')
    if not path.exists(): return dict()
    return json.loads(path.read_text(encoding))


class Settings(BaseSettings):
    mqtt_server: str = None
    mqtt_port: int = 1883
    mqtt_basetopic: str = 'karpo'

    class Config:
        env_prefix = 'karpo_'
        env_file_encoding = 'utf-8'

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable
        ) -> Tuple[SettingsSourceCallable, ...]:
            return init_settings, env_settings, json_config_settings_source
