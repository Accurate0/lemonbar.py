import importlib, importlib.machinery
import logging
import threading
from os import path
import types

from bard.Module import Module

logger = logging.getLogger(__name__)

def load_modules(c, mm, queue):
    modules = c['Modules']['load'].replace('\n', ' ').split(' ')
    sp = c['Modules']['search_path']
    modules = [ f'{sp}/{module}' for module in modules ]
    for module in modules:
        load_module(module, c, mm, queue)

def load_module(p, c, mm, queue):
    loader = importlib.machinery.SourceFileLoader(path.basename(p), p)
    mod = types.ModuleType(loader.name)
    try:
        loader.exec_module(mod)
        prefix = c['DBus']['prefix']
        mod_name = path.splitext(mod.__name__)[0] # Battery.py becomes Battery
        name = f'{prefix}.{mod_name}'
        cl = getattr(mod, mod_name)

        if issubclass(cl, Module):
            try:
                logger.info(f'attempting to load {mod_name}')
                conf = c[mod_name]
            except KeyError:
                logger.warning(f'no config section for {mod_name}')
                logger.warning('ignore if intentional, otherwise check section spelling')
                conf = None

            m = cl(queue, conf, name)
            mm.add(name, m)
            return m
        else:
            logger.error('could not load module')
            logger.error(f'{mod_name} is not a subclass of Module')
            return None

    except BaseException as e:
        # Not really concerned about what exception
        # Just making sure a module can't take down
        # The entire bar
        logger.error(f'could not load {mod} because: {e}')

    return None
