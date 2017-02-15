import logging
import sys
import time
from gencore_app.utils.main import run_command
from conda_env.env import Environment
from conda_env.utils.uploader import Uploader
from gencore_app.utils.main_env import from_file
from gencore_app.commands.cmd_build_docs import flatten_deps, parse_deps
from conda_env import exceptions
try:
    from binstar_client.utils import get_server_api
    from binstar_client import errors
except ImportError:
    get_binstar = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def upload_remote_env(fname, verbose=False):

    # TODO Update this to use conda env upload utils
    logging.debug("Uploading remote env of {}".format(fname))
    env = from_file(fname)
    conda_safe = env.save_conda_safe()
    labels = gen_labels(env)
    uploader = Uploader(env.name, fname, summary='', env_data=dict(env.to_dict()))

    try:
        url = uploader.upload(labels)
    except Exception as e:
        logging.debug('Getting exceptions and not sure why')
        logging.debug(e)

    logging.debug('Completed uploader.upload')
    logging.debug(url)


def status_check_upload(upload_env_passes):

    if not upload_env_passes:
        logging.debug('One or more uploads failed!')
        sys.exit(1)
    else:
        logging.debug('Upload passed!')


def gen_labels(env):
    labels = ['main']
    env_dict = env.to_dict()
    deps = env_dict['dependencies']
    flat_deps = flatten_deps(deps)

    for dep in flat_deps:
        p = parse_deps(dep)
        t = p[0] + '=' + p[1]
        labels.append(p[0])
        labels.append(t)

    if 'tags' in env.extra_args:
        for tag in env.extra_args.tags:
            labels.append(tag)

    return labels


class Uploader(Uploader):

    def __init__(self, packagename, env_file, **kwargs):
        super(self.__class__, self).__init__(packagename, env_file, **kwargs)
        self.env_data = kwargs.get('env_data')

    @property
    def version(self):
        if self.env_data and self.env_data.get('version'):
            return self.env_data.get('version')
        else:
            return time.strftime('%Y.%m.%d.%H%M')

    @property
    def binstar(self):
        if self._binstar is None:
            self._binstar = get_server_api()
        return self._binstar

    def upload(self, labels):
        """
        Prepares and uploads env file
        :return: True/False
        """

        print('env data')
        print(self.env_data)
        print("Uploading environment %s to anaconda-server (%s)... " %
              (self.packagename, self.binstar.domain))
        if self.is_ready():
            try:
                with open(self.file, mode='rb') as envfile:
                    binstarUpload = self.binstar.upload(
                        self.username, self.packagename,
                        self.version, self.basename,
                        envfile, channels=labels,
                        distribution_type='env',
                        attrs=self.env_data
                    )
                    return binstarUpload
            except SystemExit as e:
                print(e)
                raise
            except Exception as e:
                logging.error('We got an uncaught exception uploading to binstar')
                raise
        else:
            logging.debug('there was a problem uploading env!')
            raise exceptions.AlreadyExist()
