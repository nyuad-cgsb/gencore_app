from gencore_app.utils.main import rebuild, run_command
from gencore_app.utils.main_env import from_file

import multiprocessing
from random import shuffle
from multiprocessing import Pool
import os


def worker(cmd):
    """thread worker function"""
    run_command(cmd)
    return

##TODO Get this from remote env also


def get_env_data(filename):
    env = from_file(filename)
    deps = env.dependencies.get('conda')
    max_threads = 4
    if os.environ.get('MAX_THREADS'):
        max_threads = os.environ.get('MAX_THREADS')
    pool = Pool(processes=max_threads)  # start 4 worker processes
    return deps, max_threads, pool


def run_parallel_install(filename):
    deps, max_threads, pool = get_env_data(filename)
    for dep in deps:
        cmd = 'conda install -y {}'.format(dep)
        pool.apply_async(worker, args=(cmd,))
    pool.close()
    pool.join()


def run_parallel_download(filename):
    deps, max_threads, pool = get_env_data(filename)
    for dep in deps:
        cmd = 'conda install --download-only -y {}'.format(dep)
        pool.apply_async(worker, args=(cmd,))
    pool.close()
    pool.join()

