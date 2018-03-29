import json
import os


def get_config(env_var: str, *args):
    """Get config parameter from file or environment var
    :param str env_var: Environment var name, json key is derived from this
    :param args: This is a default value, if not defined, it will fail
    :return:
    """
    # First file
    value = None
    try:
        with open('config.json') as fd:
            file_config = json.load(fd)
        for k, v in file_config.items():
            if k.upper() == env_var:
                value = v
    except:
        pass
    # Second environment
    env_config = os.environ.get(env_var)
    if env_config is not None:
        try:
            value = json.loads(env_config)
        except:
            value = env_config
    if args:
        return value if value else args[0]
    raise EnvironmentError(f'Configuration {env_var} variable is not set by file or environment')


TOKEN = get_config('TOKEN', None)
WEBHOOK_URL = get_config('WEBHOOK_URL', None)
HOST = get_config('HOST', '0.0.0.0')
PORT = get_config('PORT', 8000)