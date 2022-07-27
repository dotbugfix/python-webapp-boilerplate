#!/usr/bin/env python
# coding=utf-8

from flask import jsonify, request
from rest_api_server import app
import util.logger as logger

import os, shutil
from pprint import pformat

_logger = logger.get_logger(__name__)

@app.route("/api/version", methods=['GET'])
def api_version():
    """
    Return backend version

    :return: Dict

    {
        'app': 'App_Name_Here',
        'version': "0.1.0 beta",
        'release_date': "23-Aug-2021",
        'pretty_version': "v0.1.0 beta released on 23-Aug-2021"
    }
    """
    import util.version as version

    response = {
        'app': version.__app_name__,
        'version': version.__version__,
        'release_date': version.__release_date__,
        'pretty_version': version.__pretty_version__
    }

    _logger.info("Backend version: %s", response)
    return (jsonify(response),
            200,
            {'ContentType': 'application/json'})
