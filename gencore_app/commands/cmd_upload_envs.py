import click
import logging

from gencore_app.cli import global_test_options
from gencore_app.utils.main import find_files, rebuild
from gencore_app.utils.main_upload import upload_remote_env, status_check_upload

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@click.command('upload_envs', short_help='Upload environments to anaconda cloud')
@global_test_options
def cli(verbose, environments):
    """ Only on master branch
        1. Check if remote env exists
        (Rebuild the env?)
        2. Upload the env to anaconda
    """

    logger.info("environments are {}".format(environments))

    files = find_files(environments)
    logger.info('files are {}'.format(files))

    for filename in files:

        if rebuild(filename):
            logger.info("We are uploading env {}".format(filename))
            upload_passes = upload_remote_env(filename)
            # status_check_upload(upload_passes)
        else:
            logger.info("env exists we are skipping")
