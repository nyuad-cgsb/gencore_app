import logging
import sys
import os
from gencore_app.utils.main import run_command
from conda_env.env import from_file
import tempfile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def conda_clean():
    logger.info('Cleaning conda package cache')
    run_command('conda clean --all -y')


def try_conda_env_create(fname):
    """
    Create the conda env
    We have this under a retry loop in case of http errors
    :param fname:
    :return:
    """
    retries_max = 2
    retries_count = 0
    create_env = False

    conda_clean()
    while retries_count <= retries_max:
        retries_count = retries_count + 1
        ec = run_conda_env_create(fname)
        if ec:
            logging.info('Conda Env for {} created successfully'.format(fname))
            create_env = True
            break
        else:
            logging.warning(
                'Conda Env was NOT created successfully! Retrying {}'.format(retries_count))
            sys.exit(1)

    conda_clean()
    return create_env


def run_conda_env_create(fname):
    """
    TODO update this so it uses the -p and runs things in parallel
    :param fname:
    :return:
    """

    logger.info("Testing environment build file {}".format(fname))

    with tempfile.TemporaryDirectory() as tempdirname:
        cmd = "conda env create --verbose -p {} --force --file {}".format(tempdirname, fname)
        exit_code = run_command(cmd)

    return exit_code


def status_check_build(build_passes):
    if not build_passes:
        logging.warning("One or more builds did not pass!")
        sys.exit(1)
    else:
        logging.info("Build passed!")
