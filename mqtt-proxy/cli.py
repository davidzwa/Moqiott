import argparse
import sys


def process_cli_args():
    parser = argparse.ArgumentParser(
        description='Daemon to control a Mqtt IoT proxy.')
    parser.add_argument('--production', action='store_true',
                        help='set production mode')

    args = parser.parse_args()
    return args
