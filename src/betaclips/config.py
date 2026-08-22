import os
from pathlib import Path

from platformdirs import user_config_dir, user_data_dir


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
SNOWFLAKE_PKEY_FILE = CREDENTIALS_DIR / 'rsa_key.p8'
GOOGLE_SERVICE_ACCOUNT_JSON = CREDENTIALS_DIR / 'betaclips-service-account.json'
