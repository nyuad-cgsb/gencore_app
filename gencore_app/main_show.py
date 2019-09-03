from binstar_client.utils import get_server_api, parse_specs

aserver_api = get_server_api()


def get_all_envs():
    packages = aserver_api.user_packages('nyuad-cgsb')
    envs = []
    for package in packages:
        if package['package_types'][0] == 'env':
            envs.append(package)
    return envs


def parse_env_dependencies(release_attrs):
    """Deps are written as package_name=version
    We want to split this to be more explicit with out versions
    """
    dependencies = []
    for dep in release_attrs['dependencies']:
        dep_def = dep.split('=')
        if len(dep_def) > 0:
            dependencies.append({'name': dep_def[0], 'version': dep_def[1]})
        else:
            dependencies.append({'name': dep_def[0], 'version': 'latest'})
    return dependencies


def create_collection(release_attr):
    dependencies = parse_env_dependencies(release_attr)
    name = release_attr['name']
    channels = release_attr['channels']
    collection = {
        'name': name,
        'channels': channels,
        'dependencies': dependencies,
        'version': release_attr['version']
    }
    return collection


def get_env_def(package, version):
    release = aserver_api.release('nyuad-cgsb', package, version)
    release['distributions'][0]['attrs']['version'] = version
    return release['distributions'][0]['attrs']
