import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "cache_dir": "~/.cache/aicache",
    "ttl": 0,  # 0 means no expiration
    "cache_size_limit": 0,  # 0 means no limit
}

def get_config():
    config_path = Path.home() / ".config" / "aicache" / "config.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f)
            if user_config:
                return {**DEFAULT_CONFIG, **user_config}
    return DEFAULT_CONFIG
