import importlib, importlib.machinery
from os import path
import types

def load_modules(c, mm, queue):
    modules = c.modules.load.replace('\n', ' ').split(' ')
    modules = [ f'{c.modules.search_path}/{module}' for module in modules ]
    for module in modules:
        load_module(module, c, mm, queue)

def load_module(p, c, mm, queue):
    loader = importlib.machinery.SourceFileLoader(path.basename(p), p)
    mod = types.ModuleType(loader.name)
    loader.exec_module(mod)
    name = f'{c.dbus.prefix}.{mod.NAME}'
    cl = getattr(mod, mod.CLASSNAME)
    m = cl(queue, c)
    m.name = name # set the module name to add the DBUS_PREFIX
    mm.add(name, m)

    return name, m
