#gencore_app.commands.cmd_build_envs

import click
from gencore_app.cli import global_test_options
from gencore_app.utils.main import find_files, rebuild
from gencore_app.utils.main_build_env import status_check_build, try_conda_env_create
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@click.command('build_envs', short_help='Build environments')
@global_test_options

def cli(verbose, environments):
    """
        1. Check remote env exists.
       2. Build the env.
       3. Exit if anything bad happens
    """

    logger.info("environments are {}".format(environments))

    files = find_files(environments)
    logger.warning('files are {}'.format(files))

    for filename in files:

        # TODO - Have better specifications for deciding which envs to build
        if rebuild(filename):
            logger.warning('Building {}'.format(filename))
            print('Building {}'.format(filename))
            build_passes = try_conda_env_create(filename)
            status_check_build(build_passes)
        else:
            logger.info('Remote env exists and rebuild not specified for {}'.format(filename))
