from dataclasses import dataclass
from pathlib import Path


@dataclass
class InitResult:
    config_dir: Path
    credentials_dir: Path
    data_dir: Path
    config_file: Path
    config_dir_created: bool
    credentials_dir_created: bool
    data_dir_created: bool
    config_file_created: bool
