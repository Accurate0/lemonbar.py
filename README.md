# bard and barctl

# usage

```python
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
   weather         interact with weather bar module
   time            interact with time bar module
   desktop         interact with desktop bar module

subcommand options:
   -r, --refresh   refresh the module owned by this subcommand
   -l, --load   refresh the module owned by this subcommand
   -u, --unload   refresh the module owned by this subcommand

$ barctl status
Loaded Modules:
   Desktop  : True
   Time     : True
   Weather  : True
Running Time: 00:12:36:675635
```
