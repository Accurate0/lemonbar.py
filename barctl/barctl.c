#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <string.h>

#include <systemd/sd-bus.h>

// add 'daemon-reload' with fork and execvp

#define STOP_MASK           1
#define STATUS_MASK         ((STOP_MASK) << 1)
#define WEATHER_MASK        ((STATUS_MASK) << 1)
#define DESKTOP_MASK        ((WEATHER_MASK) << 1)
#define TIME_MASK           ((DESKTOP_MASK) << 1)
#define BATTERY_MASK        ((TIME_MASK) << 1)

#define UNLOAD_MASK         ((BATTERY_MASK) << 1)
#define REFRESH_MASK        ((UNLOAD_MASK) << 1)
#define LOAD_MASK           ((REFRESH_MASK) << 1)

#define PATH                "/com/yeet/bard"
#define SERVICE             "com.yeet.bard"

#define MANAGER_PATH        PATH"/Manager"
#define WEATHER_PATH        PATH"/Weather"
#define DESKTOP_PATH        PATH"/Desktop"
#define TIME_PATH           PATH"/Time"
#define BATTERY_PATH        PATH"/Battery"

#define MANAGER_INTERFACE   SERVICE".Manager"
#define WEATHER_INTERFACE   SERVICE".Weather"
#define TIME_INTERFACE      SERVICE".Time"
#define DESKTOP_INTERFACE   SERVICE".Desktop"
#define BATTERY_INTERFACE   SERVICE".Battery"

#define STOP_COMMAND        "stop"
#define REFRESH_COMMAND     "refresh"
#define STATUS_COMMAND      "status"
#define LOAD_COMMAND        "load"
#define UNLOAD_COMMAND      "unload"

#define WEATHER_COMMAND     "weather"
#define TIME_COMMAND        "time"
#define DESKTOP_COMMAND     "desktop"
#define BATTERY_COMMAND     "battery"

static void usage(const char *prog)
{
    printf("%s [options] [action || module] [module options]\n\n", prog);
    puts("options:");
    puts("   -h, --help      show help");
    puts("   -v, --verbose   verbose");
    puts("   --version       show version and exit");
    puts("");
    puts("actions:");
    puts("   stop            stop the bar");
    puts("   refresh         refresh bar contents");
    puts("   status          print current bar status");
    puts("");
    puts("modules:");
    puts("   weather");
    puts("   time");
    puts("   desktop");
    puts("   battery");
    puts("");
    puts("module options:");
    puts("   -r, --refresh");
    puts("   -l, --load");
    puts("   -u, --unload");
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

static sd_bus_message* call_method(sd_bus *bus,
                                    const char *path,
                                    const char *interface,
                                    const char *method)
{
    if(bus == NULL) return NULL;
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    int r = sd_bus_call_method(bus,
                              SERVICE,
                              path,
                              interface,
                              method,
                              &error,
                              &m,
                              NULL);
    if(r < 0) {
        fprintf(stderr, "Failed to issue method call: %s\n", error.message);
        sd_bus_message_unref(m);
        m = NULL;
    }

    sd_bus_error_free(&error);
    return m;
}

static void parse_resp_as_str(sd_bus_message *m)
{
    const char *msg;
    int r = sd_bus_message_read(m, "s", &msg);
    if(r < 0) {
        fprintf(stderr, "Failed to parse response: %s\n", strerror(-r));
    } else {
        printf("%s\n", msg);
    }
}

// Argument Parsing
static int parse_args(int max, char **args)
{
    int index = 0;
    int mask = 0;

    while(index < max) {
        if(!strncmp(STOP_COMMAND, args[index], strlen(args[index]))) {
            mask |= STOP_MASK;
        } else if(!strncmp(REFRESH_COMMAND, args[index], strlen(args[index]))) {
            mask |= REFRESH_MASK;
        } else if(!strncmp(STATUS_COMMAND, args[index], strlen(args[index]))) {
            mask |= STATUS_MASK;
        } else if(!strncmp(WEATHER_COMMAND, args[index], strlen(args[index]))) {
            mask |= WEATHER_MASK;
        } else if(!strncmp(TIME_COMMAND, args[index], strlen(args[index]))) {
            mask |= TIME_MASK;
        } else if(!strncmp(DESKTOP_COMMAND, args[index], strlen(args[index]))) {
            mask |= DESKTOP_MASK;
        } else if(!strncmp(BATTERY_COMMAND, args[index], strlen(args[index]))) {
            mask |= BATTERY_MASK;
        }

        index++;
    }

    return mask;
}

static int parse_subopts(int argc, char **argv)
{
    int mask = 0;
    int c;
    const struct option long_opts_sub[] = {
        {"refresh", no_argument, NULL, 'r'},
        {"load", no_argument, NULL, 'l'},
        {"unload", no_argument, NULL, 'u'},
        {0, 0, 0, 0}
    };

    while((c = getopt_long(argc - optind, argv + optind, "rlu", long_opts_sub, NULL)) != -1) {
        switch(c) {
            case 0:
                break;
            case 'r':
                mask |= REFRESH_MASK;
                break;
            case 'l':
                mask |= LOAD_MASK;
                break;
            case 'u':
                mask |= UNLOAD_MASK;
                break;
        }
    }

    return mask;
}

static char* ret_command(int submask)
{
    char *command = NULL;
    if(submask & REFRESH_MASK) {
        command = REFRESH_COMMAND;
    } else if(submask & LOAD_MASK) {
        command = LOAD_COMMAND;
    } else if(submask & UNLOAD_MASK) {
        command = UNLOAD_COMMAND;
    }

    return command;
}

static void ret_int_path(int mask, char **interface, char **path)
{
    if(mask & WEATHER_MASK) {
        *interface = WEATHER_INTERFACE;
        *path = WEATHER_PATH;
    } else if(mask & TIME_MASK) {
        *interface = TIME_INTERFACE;
        *path = TIME_PATH;
    } else if(mask & DESKTOP_MASK) {
        *interface = DESKTOP_INTERFACE;
        *path = DESKTOP_PATH;
    } else if(mask & BATTERY_MASK) {
        *interface = BATTERY_INTERFACE;
        *path = BATTERY_PATH;
    }
}

static int exec_manager(sd_bus *bus, int mask)
{
    int ret = 1;
    if(mask & STOP_MASK) {
        sd_bus_message *msg = call_method(bus, PATH, MANAGER_INTERFACE, STOP_COMMAND);
        sd_bus_message_unref(msg);
    } else if(mask & STATUS_MASK) {
        sd_bus_message *msg = call_method(bus, PATH, MANAGER_INTERFACE, STATUS_COMMAND);
        parse_resp_as_str(msg);
        sd_bus_message_unref(msg);
    } else if(mask & REFRESH_MASK) {
        sd_bus_message *msg = call_method(bus, PATH, MANAGER_INTERFACE, REFRESH_COMMAND);
        sd_bus_message_unref(msg);
    } else {
        ret = 0;
    }

    return ret;
}

// Verbose
static int verbose = 0;
static int v_printf(const char *f, ...)
{
    int len = 0;
    if(verbose) {
        char buff[BUFSIZ];
        va_list vl;
        va_start(vl, f);
        vsprintf(buff, f, vl);
        va_end(vl);

        len = fprintf(stderr, "%s", buff);
    }

    return len;
}

int main(int argc, char *argv[])
{
    bool error = false;
    int c;
    int version_flag = 0;

    const struct option long_opts[] = {
        {"help", no_argument, NULL, 'h'},
        {"verbose", no_argument, NULL, 'v'},
        {"version", no_argument, &version_flag, 1},
        {0, 0, 0, 0}
    };

    if(argc < 2) {
        usage(argv[0]);
        return EXIT_FAILURE;
    }

    // can only read first 2 (prog name, first command)
    while((c = getopt_long(2, argv, "hv", long_opts, NULL)) != - 1) {
        switch(c) {
            case 0:
                break;

            case 'v':
                verbose = 1;
                break;

            case 'h':
                usage(argv[0]);
                break;

            default:
                error = true;
        }
    }

    // fixes some weird args parsing issues
    // TODO: write a proper args parser without getopt
    optind--;

    if(version_flag) {
        printf("%s : lmao\n", argv[0]);
        return EXIT_SUCCESS;
    }

    if(argc > optind) {
        sd_bus *bus = connect_to_bus();
        v_printf("connected to bus: %p\n", bus);
        int mask = parse_args(argc - optind, argv + optind);
        int s = exec_manager(bus, mask);

        if(argc > 2 && !s) {
            char *interface = NULL;
            char *command = NULL;
            char *path = NULL;
            int submask = parse_subopts(argc, argv);

            ret_int_path(mask, &interface, &path);

            if(submask) {
                command = ret_command(submask);
                v_printf("interface: %s, method: %s\n", interface, command);
                sd_bus_message *msg = call_method(bus, path, interface, command);
                sd_bus_message_unref(msg);
            }
        }

        sd_bus_unref(bus);
    }

    return error ? EXIT_FAILURE : EXIT_SUCCESS;
}
