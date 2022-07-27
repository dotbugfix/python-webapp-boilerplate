#!/usr/bin/env python
# coding=utf-8

# All imports are relative to the top 'backend' directory
import os, sys
import traceback
sys.path.append(os.path.abspath(os.path.join(os.curdir, '..')))
# 3rd party imports
try:
    from flask import Flask
    from flask_cors import CORS, cross_origin
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

log_file_path = ""

try:
    # When using PyInstaller, the runtime path changes
    using_pyinstaller, runtime_path = bootstrap.init_pyinstaller()

    # Create a new log file with the timestamp
    log_file_path = bootstrap.init_logger(log_file_path, runtime_path)
except Exception:
    # No logger upto this point, so print the exception on stderr directly
    traceback.print_exc()
    sys.exit(1)

try:
    # Initialize the logger
    import util.logger as logger
    _logger = logger.get_logger(__name__)

    _logger.debug("Bundled mode: %s, Working Directory: %s", using_pyinstaller, runtime_path)
    
    # Create the Flask app and init config
    app = Flask(__name__)

    # Need Cross-origin headers for local development
    CORS(app)

    # STATIC_DIR_PATH contains the HTML/CSS/JS files for the frontend
    app.config['RUNTIME_WORKING_DIR'] = runtime_path
    if using_pyinstaller:
        app.config['STATIC_DIR_PATH'] = os.path.join(runtime_path, "static")
    else:
        app.config['STATIC_DIR_PATH'] = runtime_path
    _logger.debug("Runtime Working Directory: %s", app.config['RUNTIME_WORKING_DIR'])
    _logger.debug("STATIC_DIR_PATH: %s", app.config['STATIC_DIR_PATH'])

    # Import other Flask sub-modules containing URL handlers
    from rest_api_server import routes
    from rest_api_server import rest_api
except:
    _logger.exception("REST API server startup failed")
    sys.exit(1)
