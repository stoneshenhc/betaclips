import logging
from argparse import ArgumentParser

from betaclips.config import LOG_FILE, init_dirs
from betaclips.sync import sync_jobs, validate_jobs
from betaclips.results.reporting import get_report

logger = logging.getLogger(__name__)

def main() -> None:
    logging.basicConfig(
        filename=LOG_FILE,
        encoding='utf8',
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        level=logging.INFO,
    )

    parser = ArgumentParser(
        description="Betaclips rocks",
        epilog="Thanks for using betaclips!",
    )
    subparser = parser.add_subparsers(
        help="Choose what you want betaclips to do",
        required=True,
    )

    parser_init = subparser.add_parser(
        'init', 
        help="Sets up the initial folders required for betaclips",
    )
    parser_init.set_defaults(func=init)
    parser_validate = subparser.add_parser(
        'validate',
        help="Runs series of smoke checks on configured jobs",
    )
    parser_validate.add_argument(
        '-j',
        '--job-names',
        nargs='+',
        help="Run checks on one specific job",
    )
    parser_validate.set_defaults(func=validate)
    parser_sync = subparser.add_parser(
        'sync',
        help="Executes a sync run of all enabled configured jobs"
    )
    parser_sync.add_argument(
        '-j',
        '--job-names',
        nargs='+',
        help="Executes a sync run of one specific job",
    )
    parser_sync.set_defaults(func=sync)
    
    args = parser.parse_args()
    args.func(args)

def init(args):
    result = init_dirs()
    print(f"Configuration directory {'created at' if result.config_dir_created else 'already exists at'} {str(result.config_dir)}")
    print(f"Data directory {'created at' if result.data_dir_created else 'already exists at'} {str(result.data_dir)}")
    print(f"Credentials directory {'created at' if result.credentials_dir_created else 'already exists at'} {str(result.credentials_dir)}")
    print(f"Configuration file {'template created at' if result.config_file_created else 'already exists at'} {str(result.config_file)}")
    print("Initialization complete!")

def validate(args):
    results = validate_jobs(args.job_names)
    print(get_report('validation', results))

def sync(args):
    results = sync_jobs(args.job_names)
    print(get_report('run', results))

if __name__ == '__main__':
    main()
