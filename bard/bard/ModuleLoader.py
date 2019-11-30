import importlib, importlib.machinery
from os import path
import types

class ModuleLoader(object):
    @staticmethod
    def load_modules(c, mm, queue):
        modules = c.modules.load.replace('\n', ' ').split(' ')
        # print(modules)
        # modules = [ file for file in glob('modules/*') if path.isfile(file) ]
        for module in modules:
            # print(module)
            ModuleLoader.load_module(module, c, mm, queue)

    @staticmethod
    def load_module(p, c, mm, queue):
        loader = importlib.machinery.SourceFileLoader(path.basename(p), p)
        mod = types.ModuleType(loader.name)
        loader.exec_module(mod)
        name = mod.NAME
        cl = getattr(mod, mod.CLASSNAME)
        m = cl(queue, c)
        mm.add(mod.NAME, m)

        return m, name
