#!/usr/bin/python3

"""Logger module."""
import logging.handlers
from os import environ

LOG = logging.getLogger('CPM Log')
LOG.setLevel(logging.DEBUG)

FORMATTER = logging.Formatter('[%(asctime)s] - [%(levelname)s] \t- '
                              '%(message)s')

CONSOLE_HANDLER = logging.StreamHandler()
CONSOLE_HANDLER.setFormatter(FORMATTER)
CONSOLE_HANDLER.setLevel(int(environ.get('LOGLEVELCONSOLE', 20)))

LOG.addHandler(CONSOLE_HANDLER)
