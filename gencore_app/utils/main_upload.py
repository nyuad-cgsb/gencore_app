import logging
import sys
import time
from gencore_app.utils.main import run_command
from conda_env.env import Environment
from conda_env.utils.uploader import Uploader
from gencore_app.utils.main_env import from_file
from gencore_app.commands.cmd_build_docs import flatten_deps, parse_deps
from conda_env import exceptions

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def upload_remote_env(fname, verbose=False):

    #TODO Update this to use conda env upload utils
    logging.info("Uploading remote env of {}".format(fname))
    env = from_file(fname)
    conda_safe = env.save_conda_safe()
    labels = gen_labels(env)
    uploader = Uploader(env.name, conda_safe, summary='', env_data=dict(env.to_dict()))
    # uploader.version = env.version
    info = uploader.upload(labels)
    url = info.get('url', 'anaconda.org')
    logging.info("Your environment file has been uploaded to {}".format(url))

def status_check_upload(upload_env_passes):

    if not upload_env_passes:
        logging.info("One or more uploads failed!")
        sys.exit(1)
    else:
        logging.info("Upload passed!")

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

    def upload(self, labels):
        """
        Prepares and uploads env file
        :return: True/False
        """

        print('env data')
        print(self.env_data)
        # uploader = Uploader(name, args.file, summary=summary, env_data=dict(env.to_dict()))
        print("Uploading environment %s to anaconda-server (%s)... " %
              (self.packagename, self.binstar.domain))
        if self.is_ready():
            with open(self.file, mode='rb') as envfile:
                return self.binstar.upload(self.username, self.packagename,
                                           self.version, self.basename, envfile,
                                           channels=labels,
                                           distribution_type='env', attrs=self.env_data)
        else:
            #If we are in the master branch we should get the conflicting version,
            raise exceptions.AlreadyExist()
