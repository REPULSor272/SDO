import json
import os

def init_config() -> dict:
    try:
        with open(os.path.join(os.path.dirname(__file__), "config.json")) as config_file:
            config: dict = json.load(config_file)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Config file not found. {e}")
    return config
