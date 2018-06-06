import click
from gencore_app.cli import global_test_options
from gencore_app.utils.main import find_files, rebuild
from gencore_app.utils.main_parallel_build_env import run_parallel_install
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@click.command('parallel_install',
               short_help="""
               Given a conda env, run a parallel install on each dependency. 
               This should never be used in production! Ever!
               """)
@global_test_options
def cli(verbose, environments):
    """
        This is a super, duper, hacky way of running a parallel install from conda
        It should probably never be used in production (ever)
        It should probably never be used (ever)
    """

    logger.info("environments are {}".format(environments))

    files = find_files(environments)
    logger.warning('files are {}'.format(files))
    for filename in files:
        if rebuild(filename):
            logger.warning('Installing packages from {}'.format(filename))
            run_parallel_install(filename)
        else:
            logger.info('Remote env exists and rebuild not specified for {}'.format(filename))
