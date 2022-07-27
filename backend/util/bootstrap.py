#!/usr/bin/env python
# coding=utf-8

# 3rd party imports
try:
    import os, sys, platform, getpass, socket
    import traceback
    from datetime import datetime
    import configparser
except Exception as e:
    sys.stderr.write("Failed to import some Python modules, use requirements.txt "
                 "to install 3rd party external dependencies: {}".format(e))
    traceback.print_exc()
    sys.exit(1)
    
# Internal imports
try:
    import util.logger as logger
    import util.version as version
except Exception as e:
    sys.stderr.write("Failed to import internal modules: {}".format(e))
    traceback.print_exc()
    sys.exit(1)
_logger = None
  
def init_logger(log_file_path, runtime_path):
    ''' Initialize the Python 'logging' module used by all modules with 
    configuration from util/log.config
    Set the log file path to a new file with a timestamp in its name
    
    :param log_file_path: Directory in which the log file show be created
    '''
    global _logger
    log_file_name = version.__app_name__ + '.log'

    if log_file_path:
        if not os.path.exists(log_file_path):
            sys.stdout.write("Invalid log file path: " + log_file_path)
            sys.exit(1)
        else :
            log_file_path = os.path.join(log_file_path, log_file_name)
    else:
        # Check whether current execution is using PyInstaller and
        # set current working directory accordingly
        current_work_dir = ''
        using_pyinstaller, runtime_path = init_pyinstaller()
        if using_pyinstaller == True:
            current_work_dir = os.path.dirname(sys.executable)
        else:
            current_work_dir = os.getcwd()
        log_file_path = os.path.join(current_work_dir, log_file_name)

    # The original log.config file is read-only, so create a new (temporary) one
    this_dir = os.path.dirname(os.path.realpath(__file__))
    log_config_path = os.path.join(this_dir, 'log.config')
    updated_log_config_path = log_config_path + ".updated"
    
    config_obj = configparser.ConfigParser()
    config_obj.read(log_config_path, encoding='utf-8')
    
    # Set the 'args' key to use the new log file path
    maxbytes = config_obj.get('handler_file_handler', 'maxBytes')
    backupcount = config_obj.get('handler_file_handler', 'backupCount')
    config_obj.set('handler_file_handler', 'args', '(r"{}","a", {}, {})'.format(log_file_path, maxbytes, backupcount))
 
    with open(updated_log_config_path, 'w') as configFile:
        config_obj.write(configFile)
    configFile.close()
    
    logger.init_logger(updated_log_config_path, log_file_path)
    _logger = logger.get_logger(__name__)
    
    # The logger has been initialized, remove the temporary log config file now
    os.remove(updated_log_config_path)
    
    return os.path.abspath(log_file_path)

     
def init_pyinstaller():
    ''' If this Python module is being run in the context of a PyInstaller EXE,
    then detect it and set the current working directory accordingly
    
    :return using_pyinstaller: True if a PyInstaller environment is detected
    :return runtime_path: Correct CWD to be used, regardless of PyInstaller
    '''
    using_pyinstaller = False
    try:
        runtime_path = sys._MEIPASS
        using_pyinstaller = True
    except Exception as e:
        runtime_path = os.path.abspath('.')
     
    return using_pyinstaller, runtime_path

def get_platform():
        '''
        Retrieves a platform identifier string
        Sample raw platform strings:
            Linux: Linux-4.4.0-116-generic-x86_64-with-Ubuntu-16.04-xenial
            Windows: Windows-10-10.0.14393
        :return: Returns a string containing platform identifier
        '''
        plat = platform.platform()
        _logger.debug("Platform:{}".format(plat))
        if 'Linux' in plat:
            return 'linux'
        elif 'Windows' in plat:
            return 'windows'
        else:
            return 'unknown'

def get_preamble():
    '''
    Print a string with the version, system info and file paths
    '''
    runtime_path = os.path.abspath(os.getcwd()) + " (CWD)"
        
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except:
        ip = '<unknown>'
        
    try:
        hostname = socket.gethostname()
    except:
        hostname = '<unknown>'
    
    preamble = """
{}
==============================
v{} released on {}
==============================
OS: {}
Python: {}
System: {} on {}/{}
Working directory: {}
Commandline: {}
==============================
    """.format(version.__app_name__,
               version.__version__, version.__release_date__,
               platform.platform(),
               sys.version,
               getpass.getuser(), hostname, ip,
               runtime_path,
               ' '.join(sys.argv))
    
    return preamble
