import logging
import sys
import time
import tempfile
import os
from gencore_app.utils.main import run_command
from gencore_app.utils.main_env import from_file, from_yaml

try:
    from binstar_client.utils import get_server_api
    from binstar_client import errors
except ImportError:
    get_binstar = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def upload_remote_env(fname, verbose=False):
    # TODO Update this to use conda env upload utils
    logging.info("Uploading remote env of {}".format(fname))
    env = from_file(fname)
    env.name = '{}-{}'.format(env.name, env.version)
    conda_safe = env.save_conda_safe()
    return run_command('anaconda upload {} -v {}'.format(conda_safe, env.version))


def status_check_upload(upload_env_passes):
    if not upload_env_passes:
        logging.debug('One or more uploads failed!')
        sys.exit(1)
    else:
        logging.debug('Upload passed!')
