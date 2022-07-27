#!/usr/bin/env python
# coding=utf-8

import os, sys, signal

# Avoid calling logger.get_logger() until the logger is initialized from log.config
_log = None

# Flask 'app' module, initialized when imported
flask_app = None
flask_server = None

# Port used to server HTTP requests by flask
HTTP_API_PORT = 3030

# Function pointers to be called on Flask app shutdown
SHUTDOWN_CALLBACKS = []
shutdown_in_progress = False

# 3rd party imports
try:
    import traceback, argparse
except Exception as e:
    sys.stderr.write("Failed to import some Python modules, use requirements.txt "
                 "to install 3rd party external dependencies: {}".format(e))
    traceback.print_exc()
    sys.exit(1)
    
# Internal imports
try:
    import util.bootstrap as bootstrap
except Exception as e:
    sys.stderr.write("Failed to import internal modules: {}".format(e))
    traceback.print_exc()
    sys.exit(1)

def do_bootstrap():
    '''
    Bootstrap the Flask app
        - Initialize logger
        - Create the log file
    '''
    # Common bootstrapping code is in __init__.py for the rest_api_server module
    try:
        global flask_app
        from rest_api_server import app
        flask_app = app
    except Exception:
        # No logger upto this point, so print the exception on stderr directly
        traceback.print_exc()
        sys.exit(1)
    
    try:       
        # These imports must be done after the logger is initialized
        import util.logger as logger
        global _log
        _log = logger.get_logger(__name__)
        
        # Print the preamble
        preamble = bootstrap.get_preamble()
        _log.info(preamble)
    except Exception as e:
        _log.exception("Execution failed.")
        sys.exit(1)

def stop_server(signal, frame):
    global shutdown_in_progress
    
    if shutdown_in_progress:
        _log.error("Already shutting down, please be patient...")
        return
    else:
        shutdown_in_progress = True
    
    _log.debug("Handling signal %s on frame %s", signal, frame)
    _log.info("Gracefully shutting down, please wait. This may take up to 1 minute.")
    
    _log.info("Execution complete.")
    sys.exit(0)

def start_server(listen_all_public_ips):
    ''' Start the Flask app to begin listening to HTTP requests
    Note: This is a blocking call and will never return.
          The user presses 'CTRL+C' to end the app.

    :param listen_all_public_ips: boolean specifying ip address to listen
                                  If True, Listen to 0.0.0.0
                                  else, Listen to 127.0.0.1
    '''
    try:
        global flask_app
        global flask_server
        from werkzeug.serving import make_server
 
        listen_address = ''
        if not listen_all_public_ips:
            listen_address = '127.0.0.1'
        else:
            listen_address = '0.0.0.0'
            
        _log.info("Starting Flask server on: %s:%s", listen_address, HTTP_API_PORT)
        
        # Register the CTRL+C signal handler
        signal.signal(signal.SIGINT, stop_server)
        
        # This will start the REST API server and block forever
        # Current REST API implementation is not thread-safe. Flask runs in single threaded mode.
        # In order to make flask capable of handling multiple concurrent requests following changes needs to be done
        # 1. Implement REST API in thread-safe manner
        # 2. Pass 'threaded=True' to make_server() function
        flask_server = make_server(listen_address, HTTP_API_PORT, flask_app)
        flask_server.serve_forever()

    except Exception as e:
        _log.exception("Execution failed")
        sys.exit(1)

def parse_args():
    '''
    Parse command line arguments passed
    '''
    import util.version as version
    parser = argparse.ArgumentParser()
    pretty_version = version.__pretty_version__
    parser.add_argument("--version",        "-v", action = 'version', version = pretty_version)
    parser.add_argument("--public", "-p", action='store_true', default=False, help="Listen on 0.0.0.0 (all IPs) instead of only localhost.")
    args = parser.parse_args()
    _log.debug("Arguments passed through command line: %s", args)
    return args
        
def main():
    ''' Main entry point
    '''
    do_bootstrap()
    args = parse_args()
    start_server(args.public)
    
if __name__ == "__main__":
    main()
