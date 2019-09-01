from conda_env.env import Environment
from conda_env.env import Dependencies
from conda_env import exceptions, compat
from conda_env import yaml
import logging
import os
import time
import tempfile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def from_yaml(yamlstr, **kwargs):
    """Load and return a ``Environment`` from a given ``yaml string``"""
    data = yaml.load(yamlstr)
    if kwargs is not None:
        for key, value in kwargs.items():
            if key and value:
                data[key] = value
    return Environment(**data)


def from_file(filename):
    if not os.path.exists(filename):
        raise exceptions.EnvironmenfilenameNotFound(filename)
    with open(filename, 'r') as fp:
        yamlstr = fp.read()
        return from_yaml(yamlstr, filename=filename)


class Environment(Environment):

    def __init__(self, name=None, filename=None, channels=None,
                 dependencies=None, build=0, prefix=None, version=None,
                 **kwargs):
        super(self.__class__, self).__init__(
            name, filename, channels, dependencies, prefix)
        self._version = version
        self.extra_args = kwargs
        self.build = build

    @property
    def version(self):
        if self._version is not None:
            return "{}".format(self._version)
        else:
            return time.strftime('%Y.%m.%d.%H%M')

    # We are adding this in here to make sure we get a conda happy object
    # This is actually the original to_dict method - but I don't like it
    def to_dict_conda_safe(self):
        d = yaml.dict([('name', self.name)])
        if self.channels:
            d['channels'] = self.channels
        if self.dependencies:
            d['dependencies'] = self.dependencies.raw
        if self.prefix:
            d['prefix'] = self.prefix
        return d

    def to_dict(self):
        d = yaml.dict([('name', self.name)])
        if self.channels:
            d['channels'] = self.channels
        if self.dependencies:
            d['dependencies'] = self.dependencies.raw
        if self.prefix:
            d['prefix'] = self.prefix
        if self.version:
            d['version'] = self.version
        if self.extra_args:
            d['extra_args'] = self.extra_args
        return d

    def to_yaml_conda_safe(self, stream=None):
        d = self.to_dict_conda_safe()
        out = compat.u(yaml.dump(d))
        if stream is None:
            return out
        stream.write(compat.b(out, encoding="utf-8"))

    def save_conda_safe(self):
        fileTemp = tempfile.NamedTemporaryFile(suffix='.yml', delete=False)
        with open(fileTemp.name, "wb") as fp:
            self.to_yaml_conda_safe(stream=fp)

        return fileTemp.name
