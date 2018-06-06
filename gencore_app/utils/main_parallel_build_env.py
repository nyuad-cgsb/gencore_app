from gencore_app.utils.main import rebuild, run_command
from gencore_app.utils.main_env import from_file

import multiprocessing
from random import shuffle
from multiprocessing import Pool


def worker(cmd):
    """thread worker function"""
    run_command(cmd)
    return


def run_parallel_install(fname):
    env = from_file(fname)
    deps = env.dependencies.get('conda')
    jobs = []
    pool = Pool(processes=4)  # start 4 worker processes
    for dep in deps:
        cmd = 'conda install --download-only -y {}'.format(dep)
        jobs.append(cmd)
        pool.apply_async(worker, args=(cmd,))
    pool.close()
    pool.join()


if __name__ == '__main__':
    jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=worker, args=(i,))
        jobs.append(p)
        p.start()
