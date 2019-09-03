import subprocess as sp
import logging
import glob
import sys
import os

from binstar_client.utils import get_server_api
from conda_env.env import from_file

from datetime import datetime
import time
import os

from apscheduler.schedulers.background import BackgroundScheduler

aserver_api = get_server_api()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import threading


def tick():
    print('Tick! The time is: %s' % datetime.now())


def scheduleit():
    """
    This is solely to force some output to the screen while conda is running
    Otherwise the CI service starts freaking out and thinks its died
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(tick, 'interval', seconds=60)
    scheduler.start()
    return scheduler


def run_command(cmd, verbose=True):
    logger.warning("Running cmd {}".format(cmd))
    readSize = 1024 * 4

    try:
        p = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT,
                     stdin=sp.PIPE, close_fds=True, executable="/bin/bash")
    except OSError as err:
        print("OS Error: {0}".format(err))
        raise err
    except Exception as err:
        print("OS Error: {0}".format(err))
        raise ()

    p.stdin.close()

    ec = p.poll()
    scheduler = scheduleit()

    while ec is None:
        # need to read from time to time.
        # - otherwise the stdout/stderr buffer gets filled and it all stops working
        output = p.stdout.read(readSize).decode("utf-8")
        if output and verbose:
            # I don't want to see these - I know they are there
            # TODO Add a config that allows for getting rid of strings
            if 'file exists, but clobbering' not in output:
                logger.warning(output)
            else:
                logger.info(output)

        ec = p.poll()

    scheduler.shutdown()

    # read remaining data (all of it)
    output = p.stdout.read(readSize).decode("utf-8")

    if output and verbose:
        logger.info(output)

    logger.info("Exit Code {}".format(ec))

    if ec == 0:
        return True
    else:
        return False


def find_environments(recipe_dir):
    return glob.glob("{}/**/environment*.yml".format(recipe_dir), recursive=True)


def find_files(environments):
    # By default we will check to see if there
    # any recipes committed
    recipes = os.environ.get('RECIPES')
    if recipes:
        return recipes.splitlines(False)

    if environments:
        return environments
    else:
        return glob.glob("recipes/**/environment*.yml", recursive=True)


def get_name(fname):
    """
    Conda Env Name: gencore_metagenomics_1.0
    This corresponds to module gencore_metagenomics/1.0
    """

    package = from_file(fname)
    name = package.name
    version = name.split('_').pop()

    return name, version


def filter_environments(environments):
    """
    Filter environments for those that are not already uploaded to anaconda cloud
    :param environments:
    :return:
    """
    new_environments = []

    if not environments or not len(environments):
        print('Did not find any environments to build.')
        sys.exit(0)

    for e in environments:
        print('Checking environment file {}'.format(e))
        if not remote_env_exists(from_file(e)):
            new_environments.append(e)

    if not len(new_environments):
        print('No new environments found. Exiting!')
        sys.exit(0)

    return new_environments


def remote_env_exists(env):
    logger.info("Testing for package name {}".format(env.name))

    try:
        aserver_api.package(os.environ.get("ANACONDA_USER"), '{}'.format(env.name))
        logger.info("Remote env exists. Next!")
    except:
        logger.info("Remote env does not exist! Don't skip!")
        return False

    return True


def rebuild(filename):
    """
    TODO This will be a separate subcommand
    """

    env = from_file(filename)

    if not remote_env_exists(env):
        return True
    else:
        return False


def get_environments(**kwargs):
    if kwargs['environments']:
        print(kwargs['environments'])
    elif kwargs['recipe_dir']:
        kwargs['environments'] = find_environments(kwargs['recipe_dir'])

    kwargs['environments'] = filter_environments(kwargs['environments'])
    return kwargs
