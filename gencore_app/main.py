import argparse
from pprint import pprint
from gencore_app.commands import cmd_build_envs, cmd_build_eb, cmd_upload_envs
from utils.main import find_environments, filter_environments
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def upload(**kwargs):
    cmd_upload_envs.upload(**kwargs)


def build(**kwargs):
    cmd_build_envs.build(**kwargs)


def build_eb(**kwargs):
    cmd_build_eb.build_eb(**kwargs)


def add_args(p):
    p.add_argument('--recipe-dir', '-r', required=False, help='Set the recipe dir')
    p.add_argument('--environments', '-e', nargs='+', required=False, help='pass in conda env files')
    p.add_argument('--force', default=False, required=False, help='Force build or upload a file')
    return p


def add_envs_to_args(**kwargs):
    print('Filtering recipes')
    if kwargs['recipe_dir']:
        print('Finding environment definitions')
        kwargs['environments'] = find_environments(kwargs['recipe_dir'])
        print('Done finding environment definitions')

    print('Filtering environments')
    try:
        kwargs['environments'] = filter_environments(kwargs['environments'])
    except Exception as e:
        print(e)
        sys.exit(1)

    print('Found {} recipes'.format(len(kwargs['environments'])))
    return kwargs


def args_sanity_checks(**kwargs):
    print('Build sanity checks...')
    if not kwargs['environments'] and not kwargs['recipe_dir']:
        kwargs['recipe_dir'] = 'recipes'

    if kwargs['environments'] and kwargs['recipe_dir']:
        raise Exception('You specified both environments and a recipe dir. Only environments will be considered')

    print('Args pass sanity checks...')
    return kwargs


def build_parsers():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(title='subcommands',
                                       dest='subparser',
                                       description='valid subcommands',
                                       help='Choose a valid subcommand')

    # build_parser = subparsers.add_parser('build')
    # build_eb_parser = subparsers.add_parser('build_eb')
    add_args(subparsers.add_parser('build'))
    add_args(subparsers.add_parser('build_eb'))
    add_args(subparsers.add_parser('upload'))
    return parser


if __name__ == "__main__":
    parser = build_parsers()
    kwargs = vars(parser.parse_args())
    if kwargs['subparser'] is not None:
        subparser = kwargs.pop('subparser')
        kwargs = args_sanity_checks(**kwargs)
        # So far all of these subcommands use the same argument parsing
        kwargs = add_envs_to_args(**kwargs)
        globals()[subparser](**kwargs)
    else:
        parser.parse_args(['-h'])
