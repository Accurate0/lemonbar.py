import configparser

class cfg(object): pass

class Config(object):
    def __str__(self):
        total = []
        clist = [sec for sec in dir(self) if not sec.startswith('__')]

        for section in clist:
            total.append(f'\n{section}:\n')
            s = getattr(self, section)
            cfglist = [sec for sec in dir(s) if not sec.startswith('__')]
            for key in cfglist:
                total.append(f'\t{key} = {getattr(getattr(self, section), key)}\n')

        return ''.join(total)


# just to mess around, but the config data structure
# is dynamically created at run time, could contain
# almost anything in here, we're just looking for valid keys
def parse(file):
    config = configparser.ConfigParser()
    config.read(file)
    c = Config()

    try:
        for section in config.sections():
            setattr(c, section, cfg())
            for key in config.options(section):
                val = config.get(section, key).translate(str.maketrans('','', '\''))
                setattr(getattr(c, section), key, val)
    except Exception as e:
        print(e)

    return c
