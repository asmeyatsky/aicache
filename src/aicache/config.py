import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "cache_dir": "~/.cache/aicache",
    "ttl": 0,  # 0 means no expiration
    "cache_size_limit": 0,  # 0 means no limit
    "generic_wrappers": {} # New section for generic wrappers
}

def get_config():
    config_path = Path.home() / ".config" / "aicache" / "config.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f)
            if user_config:
                # Merge default and user config, handling nested dictionaries
                merged_config = DEFAULT_CONFIG.copy()
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in merged_config and isinstance(merged_config[key], dict):
                        merged_config[key].update(value)
                    else:
                        merged_config[key] = value
                return merged_config
    return DEFAULT_CONFIG
