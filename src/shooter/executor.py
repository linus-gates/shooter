import boson_sdk

from boson_sdk import BosonCamera
from shooter.custom_commands import CUSTOM_COMMANDS
from shooter.json_parser import get_result_value


def _handle_result(result):
    """
    Handle with different commands return values.
    """
    # Boson setter result
    if isinstance(result, boson_sdk.FLR_RESULT):
        if result.value != 0:
            raise RuntimeError(
                f"Boson error: {result}"
            )

        return None

    # Boson getter result: (return_code, value...)
    if isinstance(result, tuple):
        return get_result_value(result)

    # Custom command already returned a regular value
    return result


def execute(
    command: str,
    port: str,
    params: dict,
):
    """
    Send the given command to camera, first check if its custom command,
    if so running it iand if not running it as boson-sdk command (if exists there).
 
    @param command: Given command to execute.
    @param port: Camera communication port.
    @param params: Given command parameters as dict.
    @returns: Command return value.
    """
    with BosonCamera(port) as camera:

        if command in CUSTOM_COMMANDS:
            method = CUSTOM_COMMANDS[command]
        else:
            method = getattr(camera, command, None)

            if method is None or not callable(method):
                raise ValueError(
                    f"Unknown command: {command}"
                )

        result = method(camera, **params) \
            if command in CUSTOM_COMMANDS \
            else method(**params)

        return _handle_result(result)
