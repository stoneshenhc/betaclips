import logging
import os
import tomllib
from pathlib import Path

from platformdirs import user_config_dir, user_data_dir

from betaclips.results.init_result import InitResult

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(os.environ.get(
    'BETACLIPS_CONFIG_DIR',
    user_config_dir('betaclips')
))
DATA_DIR = Path(os.environ.get(
    'BETACLIPS_DATA_DIR',
    user_data_dir('betaclips')
))
CONFIG_FILE = CONFIG_DIR / 'config.toml'
LOG_FILE = DATA_DIR / 'app.log'
RUN_RESULTS_FILE = DATA_DIR / 'run_results.jsonl'
CREDENTIALS_DIR = CONFIG_DIR / 'credentials'
GOOGLE_SERVICE_ACCOUNT_JSON = CREDENTIALS_DIR / 'betaclips-service-account.json'

def init_dirs() -> InitResult:
    config_dir_exists = CONFIG_DIR.exists()
    data_dir_exists = DATA_DIR.exists()
    credentials_dir_exists = CREDENTIALS_DIR.exists()
    config_file_exists = CONFIG_FILE.exists()

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    if not config_file_exists:
        CONFIG_FILE.write_text(CONFIG_FILE_TEMPLATE)
    logger.info("Initializing directories and config file complete.")

    return InitResult(
        config_dir=CONFIG_DIR,
        data_dir=DATA_DIR,
        credentials_dir=CREDENTIALS_DIR,
        config_file=CONFIG_FILE,
        config_dir_created=not config_dir_exists,
        data_dir_created=not data_dir_exists,
        credentials_dir_created=not credentials_dir_exists,
        config_file_created=not config_file_exists,
    )

def load_config() -> dict:
    with open(CONFIG_FILE, 'rb') as f:
        config = tomllib.load(f)
    logger.info("Connection and job configuration loaded.")
    return config

def resolve_env_secrets(conn_params: dict) -> dict:
    resolved = conn_params.copy() # shallow, but fine
    for key in list(resolved):
        if key.endswith('_env'):
            resolved[key[:-len('_env')]] = os.environ[resolved.pop(key)]
    return resolved
