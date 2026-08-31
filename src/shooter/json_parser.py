import argparse


def parse_bool(value: str) -> bool:
    """
    Gets one of the bool kewards and convert it into actual bool value.

    @param value: Given value to convert.
    @returns: Actual bool value.
    """
    value = value.lower()

    if value in ("true", "1", "yes", "on"):
        return True

    if value in ("false", "0", "no", "off"):
        return False

    raise argparse.ArgumentTypeError(
        f"Invalid boolean value: {value}"
    )


TYPE_MAP = {
    "str": str,
    "int": int,
    "float": float,
    "bool": parse_bool,
}


def ranged_type(base_type, minimum=None, maximum=None):
    """
    Gets parameter type and range and returns the convert function with defiened type and range
    (that argparse will use in the future to convert the type and validate its value).

    @param base_type: Parameter type.
    @param minimum: Parameter max value.
    @param maximum: Parameter min value.
    @returns: convert function.
    """
    def convert(value):
        """
        Convert the value to is actual type and validate its range.
    
        @param value: Value to convert and validate.
        @returns: The value if valid.
        """
        value = base_type(value)

        if minimum is not None and value < minimum:
            raise argparse.ArgumentTypeError(
                f"Value must be >= {minimum}"
            )

        if maximum is not None and value > maximum:
            raise argparse.ArgumentTypeError(
                f"Value must be <= {maximum}"
            )

        return value

    return convert


def get_param_type(param: dict):
    """
    Get parameter features and return the param type.

    @param param: Given Parameter features.
    @returns: The parameter type.
    """
    type_name = param.get("type", "str")

    if type_name not in TYPE_MAP:
        raise ValueError(
            f"Unsupported parameter type: {type_name}"
        )

    param_type = TYPE_MAP[type_name]

    # Validate range
    if type_name in ("int", "float"):
        param_type = ranged_type(
            param_type,
            minimum=param.get("min"),
            maximum=param.get("max"),
        )

    return param_type


def add_params(
    parser: argparse.ArgumentParser,
    command_config: dict,
) -> None:
    """
    Add all parameters to the argparse command.

    @param parser: The program argparse parser.
    @param command_config: The command configuration if exists.
    """
    for param_name, param in command_config.get("params", {}).items():

        parser.add_argument(
            f"--{param_name}",
            type=get_param_type(param),
            required=param.get("required", False),
            default=param.get("default"),
            choices=param.get("choices"),
            help=param.get("definition", ""),
        )


def json_value(value):
    """
    Convert Boson SDK return values into regular Python values.

    @param value: Boson SDK function's return value (without status code).
    @returns: Regular Python value
    """
    if isinstance(value, (list, tuple)):
        return [
            json_value(item)
            for item in value
        ]

    if hasattr(value, "value"):
        return value.value

    return value


def get_result_value(result):
    """
    Extract the useful value from a Boson SDK command result.

    @param value: Boson SDK function's return value.
    @returns: Regular Python value
    """
    if not isinstance(result, tuple):
        return json_value(result)

    return_code, *values = result

    if getattr(return_code, "value", return_code) != 0:
        raise RuntimeError(
            f"Boson error: {return_code}"
        )

    if len(values) == 1:
        return json_value(values[0])

    return json_value(values)
