import logging
from gencore_app.utils.main import find_files, rebuild, remote_env_exists
from gencore_app.utils.main_upload import upload_remote_env, status_check_upload

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def upload(**kwargs):
    """ Only on master branch
        1. Check if remote env exists
        (Rebuild the env?)
        2. Upload the env to anaconda
    """

    logger.info("environments are {}".format(kwargs['environments']))

    for filename in kwargs['environments']:
        if rebuild(filename):
            logger.info("We are uploading env {}".format(filename))
            upload_passes = upload_remote_env(filename)
            status_check_upload(upload_passes)
        else:
            logger.info("env exists we are skipping")
