import importlib, importlib.machinery
import logging
import threading
from os import path
import types

logger = logging.getLogger(__name__)

def load_modules(c, mm, queue):
    modules = c.modules.load.replace('\n', ' ').split(' ')
    modules = [ f'{c.modules.search_path}/{module}' for module in modules ]
    for module in modules:
        load_module(module, c, mm, queue)

def load_module(p, c, mm, queue):
    loader = importlib.machinery.SourceFileLoader(path.basename(p), p)
    mod = types.ModuleType(loader.name)
    try:
        loader.exec_module(mod)
        name = f'{c.dbus.prefix}.{mod.NAME}'
        cl = getattr(mod, mod.CLASSNAME)

        m = cl(queue, c, name)
        mm.add(name, m)
        return m
    except Exception as e:
        logger.error(f'could not load {mod} because: {e}')

    return None
