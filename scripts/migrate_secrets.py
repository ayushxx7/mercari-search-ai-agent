import os
import tomllib # Python 3.11+
from pathlib import Path

# Create .streamlit directory if it doesn't exist
Path(".streamlit").mkdir(exist_ok=True)

secrets_path = Path(".streamlit/secrets.toml")
env_path = Path(".env")

secrets = {}

if env_path.exists():
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                # Remove quotes if present
                value = value.strip("'\"")
                secrets[key.strip()] = value

if secrets:
    with open(secrets_path, "w") as f:
        for key, value in secrets.items():
            f.write(f'{key} = "{value}"\n')
    print(f"✅ Migrated {len(secrets)} secrets to {secrets_path}")
else:
    print("❌ No secrets found in .env")
