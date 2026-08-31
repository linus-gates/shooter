import json

import boson_sdk
import shooter

from shooter.json_parser import get_result_value


def _enable_state(mode: str):
    """
    Convert on/off kewards into boson-sdk constants.
    
    @param mode: on/off as string.
    @returns: Boson-sdk constant that represent on/off value.
    """
    return {
        "on": boson_sdk.FLR_ENABLE_E.FLR_ENABLE,
        "off": boson_sdk.FLR_ENABLE_E.FLR_DISABLE,
    }[mode]


def _require_confirm(confirm: bool, action: str):
    """
    Validate confrim flag is true, if not raising exception.
    """
    if not confirm:
        raise ValueError(
            f"{action} requires --confirm true"
        )


def set_color(camera, color: str):
    colors = {
        "white-hot": boson_sdk.FLR_COLORLUT_ID_E.FLR_COLORLUT_WHITEHOT,
        "black-hot": boson_sdk.FLR_COLORLUT_ID_E.FLR_COLORLUT_BLACKHOT,
        "rainbow": boson_sdk.FLR_COLORLUT_ID_E.FLR_COLORLUT_RAINBOW,
        "rainbow-hc": boson_sdk.FLR_COLORLUT_ID_E.FLR_COLORLUT_RAINBOW_HC,
        "ironbow": boson_sdk.FLR_COLORLUT_ID_E.FLR_COLORLUT_IRONBOW,
        "lava": boson_sdk.FLR_COLORLUT_ID_E.FLR_COLORLUT_LAVA,
        "arctic": boson_sdk.FLR_COLORLUT_ID_E.FLR_COLORLUT_ARCTIC,
        "globow": boson_sdk.FLR_COLORLUT_ID_E.FLR_COLORLUT_GLOBOW,
        "graded-fire": boson_sdk.FLR_COLORLUT_ID_E.FLR_COLORLUT_GRADEDFIRE,
        "hottest": boson_sdk.FLR_COLORLUT_ID_E.FLR_COLORLUT_HOTTEST,
    }

    return camera.colorLutSetId(colors[color])


def set_agc_mode(camera, mode: str):
    modes = {
        "normal": boson_sdk.FLR_AGC_MODE_E.FLR_AGC_MODE_NORMAL,
        "hold": boson_sdk.FLR_AGC_MODE_E.FLR_AGC_MODE_HOLD,
        "threshold": boson_sdk.FLR_AGC_MODE_E.FLR_AGC_MODE_THRESHOLD,
        "auto-bright": boson_sdk.FLR_AGC_MODE_E.FLR_AGC_MODE_AUTO_BRIGHT,
        "auto-linear": boson_sdk.FLR_AGC_MODE_E.FLR_AGC_MODE_AUTO_LINEAR,
        "manual": boson_sdk.FLR_AGC_MODE_E.FLR_AGC_MODE_MANUAL,
    }

    return camera.agcSetMode(modes[mode])


def set_ffc_mode(camera, mode: str):
    modes = {
        "manual": boson_sdk.FLR_BOSON_FFCMODE_E.FLR_BOSON_MANUAL_FFC,
        "auto": boson_sdk.FLR_BOSON_FFCMODE_E.FLR_BOSON_AUTO_FFC,
        "external": boson_sdk.FLR_BOSON_FFCMODE_E.FLR_BOSON_EXTERNAL_FFC,
        "shutter-test": boson_sdk.FLR_BOSON_FFCMODE_E.FLR_BOSON_SHUTTER_TEST_FFC,
    }

    return camera.bosonSetFFCMode(modes[mode])


def averager_mode(camera, mode: str):
    return camera.gaoSetAveragerState(_enable_state(mode))


def set_agc_information_based_mode(camera, mode: str):
    return camera.agcSetUseEntropy(_enable_state(mode))


def flat_field_correction(camera, mode: str):
    return camera.gaoSetFfcState(_enable_state(mode))


def gain_correction(camera, mode: str):
    return camera.gaoSetGainState(_enable_state(mode))


def defect_replacement(camera, mode: str):
    return camera.bprSetState(_enable_state(mode))


def column_filter(camera, mode: str):
    return camera.scnrSetEnableState(_enable_state(mode))


def temporal_filter(camera, mode: str):
    return camera.tfSetEnableState(_enable_state(mode))


def silent_shutterless_nuc(camera, mode: str):
    return camera.spnrSetEnableState(_enable_state(mode))


def supplemental_ffc(camera, mode: str):
    return camera.gaoSetSffcState(_enable_state(mode))


def ramp_enabled(camera, mode: str):
    return camera.gaoSetTestRampState(
        _enable_state(mode)
    )


def video_freeze(camera, mode: str):
    return camera.sysctrlSetFreezeState(
        _enable_state(mode)
    )


def set_ffc_temp_delta(camera, value: float):
    return camera.bosonSetFFCTempThreshold(
        int(round(value * 10))
    )


def get_ffc_temp_delta(camera):
    value = get_result_value(
        camera.bosonGetFFCTempThreshold()
    )

    return value / 10.0


def restore_factory_defaults(camera, confirm: bool):
    _require_confirm(
        confirm,
        "Factory defaults restoration",
    )

    return camera.bosonRestoreFactoryDefaultsFromFlash()


def reboot_camera(camera, confirm: bool):
    _require_confirm(
        confirm,
        "Camera reboot",
    )

    return camera.bosonReboot()


def configuration_report(camera):
    """
    Prints all return values (of exists get functions) as json
    """
    report = {}

    for name, config in shooter.config.items():
        if not name.startswith("get-"):
            continue

        if config.get("params"):
            continue

        command = config["command"]

        try:
            if command in CUSTOM_COMMANDS:
                result = CUSTOM_COMMANDS[command](camera)
            else:
                result = getattr(camera, command)()

            report[name.removeprefix("get-")] = (
                get_result_value(result)
            )

        except Exception as error:
            report[name.removeprefix("get-")] = {
                "error": str(error)
            }

    return json.dumps(
        report,
        indent=2,
    )


def get_tfpa(camera):
    value = get_result_value(
        camera.bosonlookupFPATempDegCx10()
    )
    return value / 10.0


def get_camera_software_version(camera):
    version = get_result_value(
        camera.bosonGetSoftwareRev()
    )
    return ".".join(map(str, version))


def get_camera_firmware_version(camera):
    version = get_result_value(
        camera.sysinfoGetMonitorSoftwareRev()
    )
    return ".".join(map(str, version))


def get_camera_product_number(camera):
    result, part_number = camera.bosonGetCameraPN()

    if result.value:
        raise RuntimeError(
            f"Boson error: {result}"
        )

    # Convert the null-terminated part-number byte array to a Python string.
    return bytes(part_number.value) \
        .split(b"\0", 1)[0] \
        .decode("ascii")


def set_image_orientation(camera, mode: str):
    states = {
        "normal": ("off", "off"),
        "horizontal": ("on", "off"),
        "vertical": ("off", "on"),
        "both": ("on", "on"),
    }

    horizontal, vertical = states[mode]

    result = camera.bosonSetInvertImage(
        _enable_state(horizontal)
    )
    if result.value:
        return result

    return camera.bosonSetRevertImage(
        _enable_state(vertical)
    )


CUSTOM_COMMANDS = {
    "averager_mode": averager_mode,
    "set_color": set_color,
    "set_agc_mode": set_agc_mode,
    "set_agc_information_based_mode": set_agc_information_based_mode,
    "flat_field_correction": flat_field_correction,
    "gain_correction": gain_correction,
    "defect_replacement": defect_replacement,
    "column_filter": column_filter,
    "temporal_filter": temporal_filter,
    "silent_shutterless_nuc": silent_shutterless_nuc,
    "supplemental_ffc": supplemental_ffc,
    "set_ffc_mode": set_ffc_mode,
    "set_ffc_temp_delta": set_ffc_temp_delta,
    "get_ffc_temp_delta": get_ffc_temp_delta,
    "restore_factory_defaults": restore_factory_defaults,
    "configuration_report": configuration_report,
    "ramp_enabled": ramp_enabled,
    "reboot_camera": reboot_camera,
    "get_tfpa": get_tfpa,
    "get_camera_software_version": get_camera_software_version,
    "get_camera_firmware_version": get_camera_firmware_version,
    "get_camera_product_number": get_camera_product_number,
    "set_image_orientation": set_image_orientation,
    "video_freeze": video_freeze,
}
