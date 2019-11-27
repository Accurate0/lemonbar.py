#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <string.h>

#include <systemd/sd-bus.h>

// add 'daemon-reload' with fork and execvp

#define STOP_MASK           1
#define STATUS_MASK         2
#define WEATHER_MASK        4
#define DESKTOP_MASK        8
#define TIME_MASK           16

#define UNLOAD_MASK         32
#define REFRESH_MASK        64
#define LOAD_MASK           128

#define PATH                "/com/yeet/bard"
#define SERVICE             "com.yeet.bard"

#define MANAGER_PATH        PATH"/Manager"
#define WEATHER_PATH        PATH"/Weather"
#define DESKTOP_PATH        PATH"/Desktop"
#define TIME_PATH           PATH"/Time"

#define MANAGER_INTERFACE   SERVICE".Manager"
#define WEATHER_INTERFACE   SERVICE".Weather"
#define TIME_INTERFACE      SERVICE".Time"
#define DESKTOP_INTERFACE   SERVICE".Desktop"

#define STOP_COMMAND        "stop"
#define REFRESH_COMMAND     "refresh"
#define STATUS_COMMAND      "status"
#define LOAD_COMMAND        "load"
#define UNLOAD_COMMAND      "unload"

#define WEATHER_COMMAND     "weather"
#define TIME_COMMAND        "time"
#define DESKTOP_COMMAND     "desktop"

static void usage(const char *prog)
{
    printf("%s [options] [action || subcommand] [subcommand options]\n\n", prog);
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
    puts("subcommands:");
    puts("   weather         weather module");
    puts("   time            time module");
    puts("   desktop         desktop module");
    puts("");
    puts("subcommand options:");
    puts("   -r, --refresh");
    puts("   -l, --load");
    puts("   -u, --unload");
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

static sd_bus* connect_to_bus(void)
{
    sd_bus *bus = NULL;
    int r = sd_bus_open_user(&bus);
    if(r < 0) {
        fprintf(stderr, "Failed to connect to user bus: %s\n", strerror(-r));
    }

    return bus;
}

static int parse_args(int max, char **args)
{
    int index = 0;
    int mask = 0x0;

    while(index < max) {
        if(!strncmp(STOP_COMMAND, args[index], strlen(args[index]))) {
            mask |= STOP_MASK;
        }

        if(!strncmp(REFRESH_COMMAND, args[index], strlen(args[index]))) {
            mask |= REFRESH_MASK;
        }

        if(!strncmp(STATUS_COMMAND, args[index], strlen(args[index]))) {
            mask |= STATUS_MASK;
        }

        if(!strncmp(WEATHER_COMMAND, args[index], strlen(args[index]))) {
            mask |= WEATHER_MASK;
        }

        if(!strncmp(TIME_COMMAND, args[index], strlen(args[index]))) {
            mask |= TIME_MASK;
        }

        if(!strncmp(DESKTOP_COMMAND, args[index], strlen(args[index]))) {
            mask |= DESKTOP_MASK;
        }
        index++;
    }

    return mask;
}

static int parse_subopts(int argc, char **argv)
{
    int mask = 0x0;
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
                // verbose = 1
                break;

            case 'h':
                usage(argv[0]);
                break;

            default:
                error = true;
        }
    }

    if(version_flag) {
        printf("%s : lmao\n", argv[0]);
        return EXIT_SUCCESS;
    }

    // printf("%d %d\n", argc, optind);
    if(argc > optind)  {
        sd_bus *bus = connect_to_bus();
        int mask = parse_args(argc - optind, argv + optind);

        if(mask & STOP_MASK) {
            sd_bus_message *msg = call_method(bus, PATH, MANAGER_INTERFACE, STOP_COMMAND);
            sd_bus_message_unref(msg);
        }

        if(mask & STATUS_MASK) {
            sd_bus_message *msg = call_method(bus, PATH, MANAGER_INTERFACE, STATUS_COMMAND);
            parse_resp_as_str(msg);
            sd_bus_message_unref(msg);
        }

        if(mask & REFRESH_MASK) {
            sd_bus_message *msg = call_method(bus, PATH, MANAGER_INTERFACE, REFRESH_COMMAND);
            sd_bus_message_unref(msg);
        }

        if(argc > 2) {
            char *interface = NULL;
            char *command = NULL;
            char *path = NULL;
            int submask = parse_subopts(argc, argv);

            if(mask & WEATHER_MASK) {
                interface = WEATHER_INTERFACE;
                path = WEATHER_PATH;
            }

            if(mask & TIME_MASK) {
                interface = TIME_INTERFACE;
                path = TIME_PATH;
            }

            if(mask & DESKTOP_MASK) {
                interface = DESKTOP_INTERFACE;
                path = DESKTOP_PATH;
            }

            if(submask) {
                if(submask & REFRESH_MASK) {
                    command = REFRESH_COMMAND;
                }

                if(submask & LOAD_MASK) {
                    command = LOAD_COMMAND;
                }

                if(submask & UNLOAD_MASK) {
                    command = UNLOAD_COMMAND;
                }

                // printf("%s, %s, %s\n", path, interface, command);
                sd_bus_message *msg = call_method(bus, path, interface, command);
                sd_bus_message_unref(msg);
            }
        }

        sd_bus_unref(bus);
    }

    return error ? EXIT_FAILURE : EXIT_SUCCESS;
}
