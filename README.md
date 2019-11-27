# bard and barctl

## usage

### bard

```c
$ bard.py -h
usage: bard.py [-h] config.ini

positional arguments:
  config.ini  config file to use to run the bar

optional arguments:
  -h, --help  show this help message and exit
```

### barctl

```c
$ barctl
barctl [options] [action || subcommand] [subcommand options]

options:
   -h, --help      show help
   -v, --verbose   verbose
   --version       show version and exit

actions:
   stop            stop the bar
   refresh         refresh bar contents
   status          print current bar status

subcommands:
   weather         weather module
   time            time module
   desktop         desktop module

subcommand options:
   -r, --refresh
   -l, --load
   -u, --unload
```
