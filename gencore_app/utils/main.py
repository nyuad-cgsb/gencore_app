import subprocess as sp
import logging
import glob
import os

from binstar_client.utils import get_server_api
# from conda_env.env import  from_file
from gencore_app.utils.main_env import from_file

aserver_api = get_server_api()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def run_command(cmd, verbose=True):

    logger.info("Running cmd {}".format(cmd))
    readSize = 1024 * 8

    try:
        p = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT,
                             stdin=sp.PIPE, close_fds=True, executable="/bin/bash")
    except OSError as err:
        print("OS Error: {0}".format(err))

    p.stdin.close()

    ec = p.poll()

    while ec is None:
        # need to read from time to time.
        # - otherwise the stdout/stderr buffer gets filled and it all stops working
        output = p.stdout.read(readSize).decode("utf-8")

        if output and verbose:
            logger.info(output)

        ec = p.poll()

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

    if environments:
        return  environments
    else:
        return  glob.glob("**/environment*.yml", recursive=True)

def get_name(fname):
    """
    Until we get versions into conda env our modules are written as
    gencore_metagenomics_1.0
    This corresponds to module gencore_metagenomics/1.0
    This method will go away when there are versions!

    We have versions!
    """

    package = from_file(fname)
    name  = package.name
#    version = package.version

    l = name.split("_")
    version = l.pop()
    name = "_".join(l)

    return name, version

def remote_env_exists(env):

    logger.info("Testing for package name {}".format(env.name))

    try:
        aserver_api.package(os.environ.get("ANACONDA_USER"), env.name)
        logger.info("Remote env exists. Next!")
    except:
        logger.info("Remote env does not exist! Don't skip!")
        return False

    return True

def rebuild(filename):
    """
    Return a boolean based on whether or not we are building the environment
    1. If the environment does not exist - we always build iti
    2. If the remote environment exists
        a. rebuild: True specified in yaml - rebuild
        b. rebuld not specified in yaml - don't rebuild
    """
    #TODO add in md5 sum check instead of if env exists

    env = from_file(filename)

    if not remote_env_exists(env):
        return True
    elif 'rebuild' in env.extra_args and env.extra_args['rebuild']:
        return True
    else:
        return False
