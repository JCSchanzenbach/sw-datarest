# cli.py

import sys
from . import init_db


def parse_args(args=None):
    """Parse arguments from sys.argv if args is None (the default) or from args
    sequence otherwise.
    """
    import argparse
    parser = argparse.ArgumentParser()
    # Add arguments here
    # 

    subparsers = parser.add_subparsers()
    parser_init = subparsers.add_parser('init')
    parser_init.set_defaults(func=init_db.init)

    parser_run = subparsers.add_parser('run')
    parser_run.add_argument('--host', help='host-adresse')
    parser_run.add_argument('--port', type=int, help='port-adresse')
    parser_run.add_argument('--reload', help='reload-switch', action='store_true')
    parser_run.set_defaults(func=run)
    args = parser.parse_args(args)
    return args


def main(args=None):
    """Main module function.
    Exposes this modules' executable functionality for use as a module
    function. 
    Parses arguments from sys.argv if args is None (the default) or from args
    sequence otherwise.
    """
    args = parse_args(args)
    args.func(args)
    
def run(args):
    import uvicorn
    uvicorn.run("sw_datarest.main:app", host=args.host, port=args.port, reload= args.reload, log_level="info")
    
if __name__ == "__main__":
    sys.exit(main())
