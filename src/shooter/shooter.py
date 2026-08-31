import argcomplete
import argparse

import shooter

from shooter.executor import execute
from shooter.json_parser import add_params


DEFAULT_PORT = "/dev/ttyACM0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shooter",
        description="Boson camera control CLI",
    )

    parser.add_argument(
        "--port",
        default=DEFAULT_PORT,
        help=f"Boson camera serial port (default: {DEFAULT_PORT})",
    )

    subparsers = parser.add_subparsers(
        dest="subcommand",
        required=True,
    )

    # Adding all subcommands defined in config
    for command_name, command_config in shooter.config.items():
        subparser = subparsers.add_parser(
            command_name,
            help=command_config.get("definition", ""),
            description=command_config.get("definition", ""),
        )

        add_params(
            subparser,
            command_config,
        )

    return parser


def main():
    parser = build_parser()

    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    command_config = shooter.config[args.subcommand]

    params = vars(args).copy()

    params.pop("subcommand")
    port = params.pop("port")

    params = {
        name: value
        for name, value in params.items()
        if value is not None
    }

    try:
        result = execute(
            command=command_config["command"],
            port=port,
            params=params,
        )

    except (ValueError, RuntimeError, OSError) as error:
        parser.error(str(error))

    if result is not None:
        print(result)


if __name__ == "__main__":
    main()
