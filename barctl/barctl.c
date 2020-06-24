#define _GNU_SOURCE
#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <getopt.h>
#include <string.h>
#include <stdbool.h>
#include <sys/stat.h>
#include <linux/limits.h>

#include <systemd/sd-bus.h>

#define STOP_MASK           1
#define STATUS_MASK         ((STOP_MASK) << 1)
#define UNLOAD_MASK         ((STATUS_MASK) << 1)
#define LOAD_MASK           ((UNLOAD_MASK) << 1)
#define REFRESH_MASK        ((LOAD_MASK) << 1)

#define PATH                "/com/yeet/bard"
#define SERVICE             "com.yeet.bard"

#define MANAGER_PATH        PATH"/Manager"
#define MANAGER_INTERFACE   SERVICE".Manager"

#define STOP_COMMAND        "stop"
#define REFRESH_COMMAND     "refresh"
#define STATUS_COMMAND      "status"
#define LOAD_COMMAND        "load"
#define UNLOAD_COMMAND      "unload"
#define LIST_COMMAND        "list_mod"

#define VERSION             "0.2"

static void usage(const char *prog)
{
    printf("%s [options] [action] [action arguments] [module action]\n\n", prog);
    printf(
    "options:\n"
    "   -h, --help            show help\n"
    "   -v, --verbose         verbose\n"
    "   --version             show version and exit\n"
    "\n"
    "actions:\n"
    "   -l, --load            load a bar module, requires a path argument\n"
    "   -u, --unload          unload a bar module, requires a dbus name argument\n"
    "   -s, --stop            stop the bar\n"
    "   -r, --refresh         refresh bar contents\n"
    "   --list                list currently loaded modules\n"
    "   --status              print current bar status\n"
    "\n"
    "module actions:\n"
    "   module specific calls are done arbitrarily\n"
    "   eg: barctl [module name] [method name]\n"
    "   note: '-' replaced with '_' in method call\n"
    );
}

// DBus Connection
static sd_bus* connect_to_bus(void)
{
    sd_bus *bus = NULL;
    int r = sd_bus_open_user(&bus);
    if(r < 0) {
        fprintf(stderr, "Failed to connect to user bus: %s\n", strerror(-r));
    }

    return bus;
}

static void parse_resp_as_str(sd_bus_message *m)
{
    const char *msg;
    int r = sd_bus_message_read(m, "s", &msg);
    if(r < 0) {
        fprintf(stderr, "Failed to parse response: %s\n", strerror(-r));
    } else {
        printf("%s", msg);
    }
}

static bool check_error(int r, sd_bus_error error, sd_bus_message *msg)
{
    bool err = false;
    if(r < 0) {
        fprintf(stderr, "Failed to issue method call: %s\n", error.message);
        err = true;
    }

    return err;
}

// Verbose
static int verbose_flag = 0;
static int v_printf(const char *f, ...)
{
    int len = 0;
    if(verbose_flag) {
        char buff[BUFSIZ];
        va_list vl;
        va_start(vl, f);
        vsprintf(buff, f, vl);
        va_end(vl);

        len = fprintf(stderr, "%s", buff);
    }

    return len;
}

static bool file_exists(const char *filename)
{
    struct stat buf;
    return stat(filename, &buf) == 0;
}

static void str_to_lower(char *s)
{
    while(*s) {
        *s = tolower(*s);
        s++;
    }
}

static void fix_method(char *s)
{
    while(*s) {
        if(*s == '-') {
            *s = '_';
        }
        s++;
    }
}

int main(int argc, char *argv[])
{
    int c;
    int ret = 0;
    int version_flag = 0;
    int status_flag = 0;
    int list_flag = 0;
    char *load_path = NULL;
    char *unload_name = NULL;
    int mask = 0;

    const struct option long_opts[] = {
        {"help", no_argument, NULL, 'h'},
        {"verbose", no_argument, NULL, 'v'},
        {"version", no_argument, &version_flag, 1},
        {"load", required_argument, NULL, 'l'},
        {"unload", required_argument, NULL, 'u'},
        {"stop", no_argument, NULL, 's'},
        {"refresh", no_argument, NULL, 'r'},
        {"status", no_argument, &status_flag, 1},
        {"list", no_argument, &list_flag, 1},
        {0, 0, 0, 0}
    };

    while((c = getopt_long(argc, argv, "hvl:u:sr", long_opts, NULL)) != -1) {
        switch(c) {
            case 0:
                break;

            case 'h':
                usage(argv[0]);
                break;

            case 'v':
                verbose_flag = 1;
                break;

            case 'l':
                mask |= LOAD_MASK;
                load_path = optarg;
                break;

            case 'u':
                mask |= UNLOAD_MASK;
                unload_name = optarg;
                break;

            case 's':
                mask |= STOP_MASK;
                break;

            case 'r':
                mask |= REFRESH_MASK;
                break;

            default:
                ret = 1;
        }
    }

    if(argc == 1) {
        usage(argv[0]);
        return EXIT_SUCCESS;
    }

    if(version_flag) {
        printf("%s: %s\n", argv[0], VERSION);
        return EXIT_SUCCESS;
    }

    sd_bus *bus = connect_to_bus();
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    sd_bus_message *reply = NULL;

    int r = 0;
    char *command = NULL;
    bool append = false;

    // handle flags first
    if(status_flag) {
        command = STATUS_COMMAND;
    } else if(list_flag) {
        command = LIST_COMMAND;
    } else if(mask & REFRESH_MASK) {
        command = REFRESH_COMMAND;
    } else if(mask & STOP_MASK) {
        command = STOP_COMMAND;
    } else if(mask & LOAD_MASK) {
        command = LOAD_COMMAND;
        append = true;
    } else if(mask & UNLOAD_MASK) {
        command = UNLOAD_COMMAND;
        append = true;
    }

    if(command) {
        r = sd_bus_message_new_method_call(bus, &m, SERVICE, PATH, MANAGER_INTERFACE, command);
        if(r < 0) {
            fprintf(stderr, "Failed to create method call: %s\n", strerror(-r));
        } else {
            if(append) {
                if(load_path) {
                    r = sd_bus_message_append(m, "s", load_path);
                } else if(unload_name) {
                    r = sd_bus_message_append(m, "s", unload_name);
                }
                if(r < 0) {
                    fprintf(stderr, "Failed to append string to message: %s\n", error.message);
                }
            }

            r = sd_bus_call(bus, m, -1, &error, &reply);
            if(r < 0) {
                fprintf(stderr, "Failed to issue method call: %s\n", error.message);
            } else  if(!sd_bus_message_is_empty(reply)) {
                parse_resp_as_str(reply);
            }

            sd_bus_message_unref(reply);
            sd_bus_error_free(&error);
        }
    }

    char *path = malloc(BUFSIZ * sizeof(char));
    char *interface = malloc(BUFSIZ * sizeof(char));
    // arbitrary method calls on the given interface
    while((argc - optind) >= 2) {
        char *module = argv[optind];
        char *method = argv[optind + 1];

        v_printf("Executing arbritary method %s on %s\n", method, module);
        fix_method(method);
        str_to_lower(module);
        *module = toupper(*module);

        sprintf(path, "%s/%s", PATH, module);
        sprintf(interface, "%s.%s", SERVICE, module);

        r = sd_bus_call_method(bus,
                    SERVICE,
                    path,
                    interface,
                    method,
                    &error,
                    &m,
                    NULL);
        check_error(r, error, m);

        optind += 2;
    }

    free(path);
    free(interface);
    sd_bus_message_unref(m);
    sd_bus_unref(bus);

    return ret ? EXIT_FAILURE : EXIT_SUCCESS;
}
