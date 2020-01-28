from os import path
import logging
import configparser

logger = logging.getLogger(__name__)

# create a dict of dicts, from sections to key value pairs
def parse(file):
    if not path.exists(file):
        raise FileNotFoundError('config file doesn\'t exist')

    config = configparser.ConfigParser()
    config.read(file)

    c = {}
    try:
        for section in config.sections():
            c[section] = {}
            for key in config.options(section):
                val = config.get(section, key).translate(str.maketrans('','', '\''))
                c[section][key] = val
    except BaseException as e:
        logger.error(e)

    # pprint.pprint(c)

    return c
