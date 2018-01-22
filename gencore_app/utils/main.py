import subprocess as sp
import logging
import glob
import os

from binstar_client.utils import get_server_api
from gencore_app.utils.main_env import from_file

from datetime import datetime
import time
import os

from apscheduler.schedulers.background import BackgroundScheduler

aserver_api = get_server_api()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


import threading

def tick():
    print('Tick! The time is: %s' % datetime.now())

def scheduleit():
    """
    This is solely to force some output to the screen while conda is running
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(tick, 'interval', seconds=60)
    scheduler.start()
    return scheduler

def run_command(cmd, verbose=True):

    logger.warn("Running cmd {}".format(cmd))
    readSize = 1024 * 4

    try:
        p = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT,
                     stdin=sp.PIPE, close_fds=True, executable="/bin/bash")
    except OSError as err:
        print("OS Error: {0}".format(err))

    p.stdin.close()

    ec = p.poll()
    scheduler = scheduleit()

    while ec is None:
        # need to read from time to time.
        # - otherwise the stdout/stderr buffer gets filled and it all stops working
        output = p.stdout.read(readSize).decode("utf-8")
        if output and verbose:
            logger.warn(output)

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


def find_files(environments):

    # By default we will check to see if there
    # any recipes committed
    recipes = os.environ.get('RECIPES')
    if recipes:
        return recipes.splitlines(False)

    if environments:
        return environments
    else:
        return glob.glob("**/environment*.yml", recursive=True)


def get_name(fname):
    """
    Until we get versions into conda env our modules are written as
    gencore_metagenomics_1.0
    This corresponds to module gencore_metagenomics/1.0
    This method will go away when there are versions!

    """

    package = from_file(fname)
    name = package.name
    version = package.version

    return name, version


def remote_env_exists(env):

    logger.debug("Testing for package name {}".format(env.name))

    try:
        aserver_api.release(os.environ.get("ANACONDA_USER"), env.name, env.version)
        logger.debug("Remote env exists. Next!")
    except:
        logger.debug("Remote env does not exist! Don't skip!")
        return False

    return True


def rebuild(filename):
    """
    Return a boolean based on whether or not we are building the environment
    1. If the environment does not exist - we always build it
    2. If the remote environment exists
        a. rebuild: True specified in yaml - rebuild
        b. rebuld not specified in yaml - don't rebuild
    """
    # TODO add in md5 sum check instead of if env exists

    env = from_file(filename)

    if not remote_env_exists(env):
        return True
    # this is deprecated - now we increase the build string
    # elif 'rebuild' in env.extra_args and env.extra_args['rebuild']:
    #     return True
    else:
        return False
