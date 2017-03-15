# gencore_app.commands.cmd_build_man

import click
from gencore_app.cli import global_test_options
from gencore_app.utils.main import rebuild, run_command, get_name, find_files
from gencore_app.utils.main_env import from_file
import os
import sys
import yaml
import shutil
from binstar_client.utils import get_server_api
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

aserver_api = get_server_api()


@click.command('build_man', short_help='Build man')
@global_test_options
def cli(verbose, environments):
    """Build conda doc packages and man pages.
    1. Check to see if the remote doc package exists
    2. If it doesn't, continue
    3. Create manpage from markdown doc generated by `gencore_app build_docs`
    4. Create conda.recipe for a {{name}}_docs package, which only has the manpage
    5. Upload the new docs package to conda env
    6. Update the original env to include the new docs package
    """

    logger.info("Building man pages")

    files = find_files(environments)
    cwd = os.getcwd()

    for filename in files:
        docs = docs_prep(filename)

        if rebuild(filename):
            logger.info("echo we are building the man pages")

            make_man(docs)
            update_env(docs)
            os.chdir(cwd)


def docs_prep(fname):
    env = from_file(fname)
    name = env.name
    version = env.version
    marked = '_docs/environment/{}-{}.md'.format(name, version)
    docs = DocPackage(name, version,  marked, fname)
    return docs


def make_man(docs):

    logger.info("We are making the man page")
    man_dir = "build/{}/share/man/man1".format(docs.name)

    if not os.path.exists(man_dir):
        os.makedirs(man_dir)

    cmd = "marked-man {} > {}/{}.1".format(docs.marked, man_dir, docs.name)
    man_passes = run_command(cmd, True)
    status_check_man(man_passes)
    make_doc_package(docs)


def make_doc_package(docs):

    logger.info("In make doc packages")

    cwd = os.getcwd()
    recipe_dir = "build/" + docs.name + "/conda.recipe"

    build_template = cwd + "/package_template/build.sh"

    if not os.path.exists(recipe_dir):
        os.makedirs(recipe_dir)

    shutil.copyfile(build_template, recipe_dir + "/build.sh")

    os.chdir(recipe_dir)
    name = docs.name

    d = {'package': {'name': name + "_docs", 'version': docs.version},
         'source': {'path': '{}/build/{}'.format(cwd, docs.name)}}

    with open('meta.yaml', 'w') as yaml_file:
        yaml.dump(d, yaml_file, default_flow_style=False)

    yaml.dump(d)
    logging.debug("We made the yaml files")

    cmd = "conda build ./"
    status = run_command(cmd, True)
    status_check_man(status)

    os.chdir(cwd)


def update_env(docs):

    env = from_file(docs.env_file)

    docs_package = "{}_docs={}".format(docs.name, docs.version)
    docs_dependencies = "{}_docs {}*".format(docs.name, docs.version)

    deps = env.dependencies
    conda_deps = deps.get('conda')

    if docs_dependencies not in conda_deps:
        env.dependencies.add(docs_package)

    if 'nyuad-cgsb' not in env.channels:
        env.channels.append('nyuad-cgsb')

    # env.save()
    # env.save_extra_args()

    # logger.info('Successfully saved env')


def remote_docs_exist(docs):

    logger.info("Testing to see if remote env exists")
    t = docs.name
    name = t + "_docs"
    version = docs.version
    logging.debug("Testing for docs package name {}".format(name))

    try:
        aserver_api.release(os.environ.get("ANACONDA_USER"), name, version)
        logger.info("Remote doc package exists. Next!")
    except:
        logger.info("Remote doc package does not exist. Build")
        return False

    return True


def status_check_man(man_passes):

    if not man_passes:
        logging.warn("One or more man pages did not pass!")
        sys.exit(1)


class DocPackage(object):

    def __init__(self, name, version, marked, env_file):
        self.name = name
        self.version = version
        self.marked = marked
        self.env_file = env_file
