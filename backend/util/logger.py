#!/usr/bin/env python
# coding=utf-8

'''Logging module
Provides APIs that are wrappers over the Python 'logging' module
'''

import logging, sys, traceback
from logging.config import fileConfig

_logger = None

def init_logger(config_file_path, log_file_path):
    '''
    Initialize the logger using an external INI-formatted configuration file
    
    :param config_file_path: Path to the log config file
    :param log_file_path:    Path at which the log file is to be created/appended
    '''
    try:
        fileConfig(config_file_path)
        _logger = logging.getLogger(__name__)
        _logger.debug("Initialized logger from configuration file: '%s'", config_file_path)
    except:
        import os
        traceback.print_exc()
        sys.stderr.write('Failed to initialize logger, aborting execution.\n')
        sys.stderr.write("Ensure that the current user has write permissions for: {}\n".format(log_file_path))
        sys.exit(1)
    
def get_logger(module_name):
    '''
    Get an instance of a module-level logger
    
    :param module_name: Name of the calling module (use __name__)
    '''
    return logging.getLogger(module_name)
