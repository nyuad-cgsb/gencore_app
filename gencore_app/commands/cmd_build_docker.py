import click
import os
from jinja2 import Environment, FileSystemLoader
import logging
import tempfile
from shutil import copyfile

from gencore_app.cli import global_test_options
from gencore_app.utils.main import find_files,  get_name, rebuild, run_command
from gencore_app.utils.main_env import from_file

# logging.basicConfig(level=logger.info)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@click.command('build_docker', short_help='Build Docker Images')
@global_test_options
def cli(verbose, environments):
    """Build  Easyblock Configs."""

    logger.info("Building Easyblock Configs")

    cwd = os.getcwd()

    files = find_files(environments)

    for filename in files:
        if rebuild(filename):
            logger.info("We are creating a Dockerfile for {}".format(filename))
            env = from_file(filename)
            name = env.name
            version = env.version
            print_dockerfile(name, version)
            os.chdir(cwd)


def print_dockerfile(name, version):
    # Create the jinja2 environment.
    # Notice the use of trim_blocks, which greatly helps control whitespace.
    j2_env = Environment(loader=FileSystemLoader('package_template'),
                         trim_blocks=False)

    docker_file = 'Dockerfile.jinja'
    cache = '--no-cache'
    if 'biosails' in name:
        docker_file = 'biosails-DockerFile.jinja'
        cache = ''
    tmp = j2_env.get_template(docker_file).render(name=name, version=version)

    dirpath = tempfile.mkdtemp()
    copyfile(os.path.join('package_template', 'fetch_and_run.sh'), os.path.join(dirpath, 'fetch_and_run.sh'))
    copyfile(os.path.join('package_template', 'bash_entrypoint.sh'), os.path.join(dirpath, 'bash_entrypoint.sh'))
    copyfile(os.path.join('package_template', 'update_hpc_runner.sh'), os.path.join(dirpath, 'update_hpc_runner.sh'))
    os.chdir(dirpath)

    f = open('{}/Dockerfile'.format(dirpath), 'w')
    f.write(tmp)
    f.close()

    run_command('docker build --rm {} -t quay.io/nyuad_cgsb/{}:{} .'.format(cache, name, version), verbose=True)
    run_command('docker image tag quay.io/nyuad_cgsb/{}:{} quay.io/nyuad_cgsb/{}:latest'.format(name, version, name, version), verbose=True)
