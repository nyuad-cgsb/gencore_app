import click
import os
from jinja2 import Environment, FileSystemLoader
import logging

from gencore_app.cli import global_test_options
from gencore_app.utils.main import find_files,  get_name, rebuild
from gencore_app.utils.main_env import from_file

# logging.basicConfig(level=logger.info)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@click.command('build_eb', short_help='Build Easyblock Configs')
@global_test_options
def cli(verbose, environments):
    """Build  Easyblock Configs."""

    logger.info("Building Easyblock Configs")

    cwd = os.getcwd()

    logger.info("We are in dir {}".format(cwd))

    files = find_files(environments)

    if not os.path.exists('_easybuild'):
        os.makedirs('_easybuild')

    for filename in files:

        # if rebuild(filename):
        logger.info("We are creating eb for {}".format(filename))
        env = from_file(filename)
        name = env.name
        version = env.version
        print_html_doc(name, version)


def print_html_doc(name, version):
    # Create the jinja2 environment.
    # Notice the use of trim_blocks, which greatly helps control whitespace.
    j2_env = Environment(loader=FileSystemLoader('package_template'),
                         trim_blocks=False)
    tmp = j2_env.get_template('template.eb').render(name=name, version=version)

    f = open('_easybuild/{}-{}.eb'.format(name, version), 'w')
    f.write(tmp)
    f.close()
