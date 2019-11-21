#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <string.h>

#include <systemd/sd-bus.h>

// add 'daemon-reload' with fork and execvp

#define STOP_MASK           0x0001
#define REFRESH_MASK        0x0002
#define STATUS_MASK         0x0004

#define PATH                "/com/yeet/bard"
#define SERVICE             "com.yeet.bard"
#define MANAGER_INTERFACE   SERVICE".Manager"

#define STOP_COMMAND        "stop"
#define REFRESH_COMMAND     "refresh"
#define STATUS_COMMAND      "status"

static const struct option long_opts [] = {
    {"help", no_argument, NULL, 'h'},
    {0, 0, 0, 0}
};

static void usage(const char *prog)
{
    printf("%s [options] [actions]\n\n", prog);
    puts("actions:");
    puts("\tstop            stop the bar");
    puts("\trefresh         refresh bar contents");
    puts("\tstatus          print current bar status");
    puts("options:");
    puts("\t-h, --help      show help");
}

static sd_bus_message* call_method(sd_bus *bus, const char *interface, const char *method)
{
    if(bus == NULL) return NULL;
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    int r = sd_bus_call_method(bus,
                              SERVICE,
                              PATH,
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
        index++;
    }

    return mask;
}

int main(int argc, char *argv[])
{
    bool error = false;
    int c, index;

    while((c = getopt_long(argc, argv, "h", long_opts, &index)) != - 1) {
        switch(c) {
            case 'h':
                usage(argv[0]);
                break;

            default:
                error = true;
        }
    }

    if(argc == 1 || error) {
        usage(argv[0]);
        error = true;
    } else {
        int mask = parse_args(argc - optind, argv + optind);
        sd_bus *bus = connect_to_bus();
        sd_bus_message *msg = NULL;

        if(mask & REFRESH_MASK) {
            msg = call_method(bus, "com.yeet.bard.Manager", "refresh");
            parse_resp_as_str(msg);
            sd_bus_message_unref(msg);
        }

        if(mask & STATUS_MASK) {
            msg = call_method(bus, "com.yeet.bard.Manager", "status");
            parse_resp_as_str(msg);
            sd_bus_message_unref(msg);
        }

        if(mask & STOP_MASK) {
            msg = call_method(bus, "com.yeet.bard.Manager", "stop");
            sd_bus_message_unref(msg);
        }

        sd_bus_unref(bus);
    }

    return error ? EXIT_FAILURE : EXIT_SUCCESS;
}
