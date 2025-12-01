#!/usr/bin/env python3
"""Script to update seed URLs in config.yaml."""

import sys
from pathlib import Path

import yaml

if __name__ == "__main__":
    config_path = Path("config.yaml")
    
    if not config_path.exists():
        print(f"Error: {config_path} not found")
        sys.exit(1)

    # Example seed URLs - replace with actual URLs
    seed_urls = [
        "https://example.com",
        "https://example.org",
        # Add more URLs here
    ]

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    config["seed_urls"] = seed_urls

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print(f"Updated {len(seed_urls)} seed URLs in {config_path}")


