import pytest
from pathlib import Path

from betaclips.config import load_config, resolve_env_secrets
from betaclips.exceptions import (
    ConfigNotFoundError,
    MissingEnvVarError,
)

def test_missing_config(monkeypatch):
    monkeypatch.setattr(
        'betaclips.config.CONFIG_FILE',
        Path('/definitely/fake/file.toml'),
    )
    with pytest.raises(ConfigNotFoundError):
        load_config()

def test_missing_env_var_indirection():
    conn_params = {
        'test_env': 'anything'
    }
    with pytest.raises(MissingEnvVarError):
        resolve_env_secrets(conn_params)
