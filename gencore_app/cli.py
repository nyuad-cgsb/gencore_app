# import click
# import os
# import sys
#
# class MyCLI(click.MultiCommand):
#
#     #this should be a list
#     @property
#     def plugin_folder(self):
#         return os.path.join(os.path.dirname(__file__), 'commands')
#
#     def list_commands(self, ctx):
#         rv = []
#         for filename in os.listdir(self.plugin_folder):
#             if filename.endswith('.py') and \
#                filename.startswith('cmd_'):
#                 rv.append(filename[4:-3])
#         rv.sort()
#         click.echo("RVS are {}".format(rv))
#         return rv
#
#     def get_command(self, ctx, name):
#         try:
#             if sys.version_info[0] == 2:
#                 name = name.encode('ascii', 'replace')
#             mod = __import__('gencore_app.commands.cmd_' + name,
#                                 None, None, ['cli'])
#         except ImportError as error:
#             click.echo("we got an import error on {}".format(name))
#             click.echo("{}".format(error))
#             return
#         return mod.cli
#
# class GlobalOpts(object):
#
#     def __init__(self):
#         self.values = [
#             click.option('--verbose', '-v',  is_flag = True, default=False, help='Enable verbose logging'),
#             click.option('--environments', '-e', default=None, multiple=True, type=click.Path(exists=True), help='Add environments'),
#         ]
#
#     def global_test_options(self, func):
#         for option in self.values:
#             func = option(func)
#         return func
#
# global_opts = GlobalOpts()
# global_test_options = global_opts.global_test_options
#
# @click.command(cls=MyCLI)
# def cli():
#     """ Test environments, build docs, build man pages, build doc pages, and finally upload envs """
#     pass
