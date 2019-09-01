import argparse
import sys
from pprint import pprint
from gencore_app.utils.main import find_environments, remote_env_exists, filter_environments
from gencore_app.utils.main_build_env import try_conda_env_create
from conda_env.env import from_file


def build_sanity_checks(**kwargs):
    print('Build sanity checks...')
    if not kwargs['environments'] and not kwargs['recipe_dir']:
        kwargs['recipe_dir'] = 'recipes'

    if kwargs['environments'] and kwargs['recipe_dir']:
        raise Exception('You specified both environments and a recipe dir. Only environments will be considered')


def build(**kwargs):
    build_sanity_checks(**kwargs)
    if kwargs['environments']:
        print(kwargs['environments'])
    elif kwargs['recipe_dir']:
        kwargs['environments'] = find_environments(kwargs['recipe_dir'])

    kwargs['environments'] = filter_environments(kwargs['environments'])

    for e in kwargs['environments']:
        exit = try_conda_env_create(e)
        print('Exited as : {}'.format(exit))


def add_args(p):
    p.add_argument('--recipe-dir', '-r', required=False, help='Set the recipe dir')
    p.add_argument('--environments', '-e', nargs='+', required=False, help='pass in conda env files')
    p.add_argument('--force', default=False, required=False, help='Force build or upload a file')
    return p


parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(title='subcommands',
                                   dest='subparser',
                                   description='valid subcommands',
                                   help='Choose a valid subcommand')

build_parser = subparsers.add_parser('build')
build_parser = add_args(build_parser)
args = parser.parse_args()
kwargs = vars(parser.parse_args())
if kwargs['subparser'] is not None:
    globals()[kwargs.pop('subparser')](**kwargs)
else:
    parser.parse_args(['-h'])
