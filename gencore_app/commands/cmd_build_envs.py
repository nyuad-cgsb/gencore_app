import logging
from utils.main_build_env import try_conda_env_create

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def build(**kwargs):
    """
    1. Check remote env exists.
    2. Build the env.
    3. Exit if anything bad happens
    """
    for e in kwargs['environments']:
        try_conda_env_create(e)
