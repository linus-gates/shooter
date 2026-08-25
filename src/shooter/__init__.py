import json
from importlib.resources import files


with files("shooter").joinpath("conf", "shooter.json").open(
    "r",
    encoding="utf-8",
) as f:
    config = json.load(f)


__all__ = ["config"]
