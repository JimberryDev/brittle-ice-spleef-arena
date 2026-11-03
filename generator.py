"""Small compatibility experiment, with no tiling rules yet."""

from importlib.metadata import version

import nbtlib
from litemapy import BlockState, Region, Schematic


def runtime_info():
    # Report the packages actually imported by this runtime
    return f"Imported Litemapy {version('litemapy')} and NumPy {version('numpy')}"


def round_trip(input_path=None):
    # Prepare a tiny sample with a directional block state, or load a real file
    if input_path is None:
        region = Region(0, 0, 0, 2, 1, 1)
        region[0, 0, 0] = BlockState("minecraft:stone")
        region[1, 0, 0] = BlockState("minecraft:oak_log", axis="x")
        schematic = Schematic(name="Browser test", regions={"sample": region})
    else:
        schematic = Schematic.load(input_path)

    # Capture the supported data before saving, without changing timestamps
    expected = schematic.to_nbt(save_soft=False)
    schematic.save("/output.litematic", update_meta=False, save_soft=False)

    # Reopen through Litemapy to check that its own reader accepts the result
    reopened = Schematic.load("/output.litematic")
    if expected != reopened.to_nbt(save_soft=False):
        raise ValueError("Schematic data changed during the save/reload check")

    # Compare raw tags too, so unsupported template metadata cannot pass silently
    if input_path is not None:
        original = nbtlib.load(input_path)
        output = nbtlib.load("/output.litematic")
        if original != output:
            raise ValueError(
                "Raw NBT tags changed; this file needs investigation before export"
            )

    # Return plain text so JavaScript does not need to manage a Python object
    names = ", ".join(reopened.regions)
    return f"PASS: saved and reopened {len(reopened.regions)} region(s): {names}"
