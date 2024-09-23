import os
import yaml
from pathlib import Path

def load_config(config_path: str = "configs/jetson_nano/config_1080p.yaml"):
    project_root = Path(__file__).parents[2]  # Adjust the number based on your file structure
    config_file = project_root / config_path
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    return config
