import argparse


def add_option_args(parser):
    parser.add_argument(
        "--config",
        "-c",
        nargs="?",
        default=None,
        help="The config file to use",
    )

    parser.add_argument(
        "--path",
        "-p",
        nargs="?",
        default=None,
        help="The path to work from",
    )


def create_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Sympyosis - Orchestrate Simple Python Services.\n\n"
            "Running with a series of services will cause "
        )
    )

    return parser


def create_service_args(parser):
    sub_parsers = parser.add_subparsers(help="Launch a service")
    service_parser = sub_parsers.add_parser("service")
    service_parser.add_argument(
        "service",
        nargs="?",
        default=None,
        help="The service to launch",
    )
    service_parser.add_argument(
        "port",
        nargs="?",
        default=None,
        type=int,
        help="The port on which to run the service API",
    )

    service_parser.add_argument(
        "health",
        nargs="?",
        default=None,
        type=int,
        help="The port on which to do service health checks",
    )

    service_parser.add_argument(
        "manager",
        nargs="?",
        default=None,
        help="The address where the service manager API can be found",
    )

    add_option_args(service_parser)


def get_arg_parser():
    parser = create_parser()
    add_option_args(parser)
    create_service_args(parser)
    return parser
