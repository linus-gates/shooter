#!/usr/bin/env python3

import argparse
import json
import subprocess

import shooter

from pathlib import Path


TYPE_MAP = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool
}


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_parser(config: dict) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shooter",
        description="Camera control CLI"
    )

    subparsers = parser.add_subparsers(
        dest="subcommand",
        required=True
    )

    for subcommand_name, subcommand_config in config.items():

        subparser = subparsers.add_parser(
            subcommand_name,
            help=subcommand_config["definition"],
            description=subcommand_config["definition"]
        )

        params = subcommand_config.get("params", {})

        for param_name, param_config in params.items():

            param_type = TYPE_MAP[param_config.get("type", "str")]

            subparser.add_argument(
                f"--{param_name}",
                help=param_config["definition"],
                type=param_type,
                required=param_config.get("required", False)
            )

    return parser


def build_command(
    config: dict,
    subcommand: str,
    args: argparse.Namespace
) -> str:

    command_template = config[subcommand]["command"]

    values = vars(args).copy()
    values.pop("subcommand", None)

    return command_template.format(**values)


def execute_command(command: str):
    print(f"Executing: {command}")

    subprocess.run(
        command,
        shell=True,
        check=True
    )


def main():
    config = shooter.config
    parser = build_parser(config)

    args = parser.parse_args()

    command = build_command(
        config,
        args.subcommand,
        args
    )

    execute_command(command)


if __name__ == "__main__":
    main()
