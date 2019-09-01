import logging
import sys
from gencore_app.utils.main import run_command

try:
    from binstar_client.utils import get_server_api
    from binstar_client import errors
except ImportError:
    get_binstar = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def upload_remote_env(fname):
    logging.debug("Uploading remote env of {}".format(fname))
    command = "anaconda upload {}".format(fname)
    e = run_command(command)
    status_check_upload(e)


def status_check_upload(upload_env_passes):
    if not upload_env_passes:
        logging.debug('One or more uploads failed!')
        sys.exit(1)
    else:
        logging.debug('Upload passed!')

