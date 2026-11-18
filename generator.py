from copy import deepcopy
from pathlib import Path

from litemapy import BlockState, Region, Schematic

"""
The schematic is formed by the following regions

| Group                             | Regions                                |
| --------------------------------- | -------------------------------------- |
| Width slices                      | w_A_start, w_A_end, w_B_start, w_B_end |
| Length slices                     | l_start, l_end                         |
| Width-start / length-start corner | ws_ls                                  |
| Width-start / length-end corner   | ws_le1 + ws_le2                        |
| Width-end / length-start corner   | we_ls1 + we_ls2                        |
| Width-end / length-end corner     | we_le1 + we_le1                        |
| Top                               | top_prefix, top_slice, top_suffix      |
"""

W_BASE = 11
W_SLICE = 7
L_BASE = 22
L_SLICE = 9
H_BASE = 2
H_SLICE = 7


def gen_schem(width_tiles: int, height_layers: int, length_tiles: int):
    """get a schematic witht the tiles stacked the amount of times specified by the args

    Args:
        width_tiles (int): amount of width slices
        height_layers (int): amount of layers
        length_tiles (int): amount of length slices
    """

    in_schem = Schematic.load("Brittle ice Spleef Arena by JimberryDev.litematic")
    src = in_schem.regions
    output: dict[str, Region] = {}

    # Top
    output["top_suffix"] = copy_offset(src["top_suffix"], z_tiles=-length_tiles + 1)
    for dz in range(length_tiles):
        output[f"top_slice_{dz + 1}"] = copy_offset(src["top_slice"], z_tiles=-dz)
    output["top_prefix"] = copy_offset(src["top_prefix"])

    # height
    for layer in range(height_layers):
        # Corners
        output[f"ws_ls_layer_{layer + 1}"] = copy_offset(
            src["ws_ls"],
            y_layers=-layer,
            z_tiles=-length_tiles + 1,
        )
        output[f"ws_le1_layer_{layer + 1}"] = copy_offset(
            src["ws_le1"],
            y_layers=-layer,
            x_tiles=width_tiles - 2,
            z_tiles=-length_tiles + 1,
        )
        output[f"ws_le2_layer_{layer + 1}"] = copy_offset(
            src["ws_le2"],
            y_layers=-layer,
            z_tiles=-length_tiles + 1,
            x_tiles=width_tiles - 2,
        )
        output[f"we_ls1_layer_{layer + 1}"] = copy_offset(
            src["we_ls1"],
            y_layers=-layer,
        )
        output[f"we_ls2_layer_{layer + 1}"] = copy_offset(
            src["we_ls2"],
            y_layers=-layer,
        )
        output[f"we_le1_layer_{layer + 1}"] = copy_offset(
            src["we_le1"],
            y_layers=-layer,
            x_tiles=width_tiles - 2,
        )
        output[f"we_le2_layer_{layer + 1}"] = copy_offset(
            src["we_le2"],
            y_layers=-layer,
            x_tiles=width_tiles - 2,
        )

        # width
        offset = 0
        for dx in range(width_tiles):
            if dx % 2 == 0:
                A_B = "A"
                offset = dx
            else:
                A_B = "B"
                # B slice starts offset already
                offset = dx - 1

            output[f"w_{dx + 1}_start_layer_{layer + 1}"] = copy_offset(
                src[f"w_{A_B}_start"],
                x_tiles=offset,
                z_tiles=-length_tiles + 1,
                y_layers=-layer,
            )
            output[f"w_{dx + 1}_end_layer_{layer + 1}"] = copy_offset(
                src[f"w_{A_B}_end"],
                x_tiles=offset,
                y_layers=-layer,
            )

        # length
        for dz in range(length_tiles):
            output[f"l_{dz + 1}_start_layer_{layer + 1}"] = copy_offset(
                src["l_start"],
                z_tiles=-dz,
                y_layers=-layer,
            )
            output[f"l_{dz + 1}_end_layer_{layer + 1}"] = copy_offset(
                src["l_end"],
                z_tiles=-dz,
                x_tiles=width_tiles - 2,
                y_layers=-layer,
            )
            
        # Adding pale moss to block water
        pale_moss = BlockState("minecraft:pale_moss_block")
        output[f"w_1_start_layer_{layer + 1}"][0, 2, 5] = pale_moss
        output[f"w_{width_tiles}_start_layer_{layer + 1}"][6, 2, 5] = pale_moss

    output["arena_center"] = Region(
        3,
        -1,
        -3,
        width_tiles * W_SLICE,
        -height_layers * H_SLICE,
        -length_tiles * L_SLICE,
    )

    out_schem = Schematic(
        name="Brittle ice Spleef Arena by JimberryDev",
        regions=output,
        mc_version=in_schem.mc_version,
    )

    out_schem.name = (
        f"build/Brittle ice Spleef Arena "
        f"{out_schem.width} x {out_schem.height} x {out_schem.length} "
        "by JimberryDev"
    )

    # Save
    Path("build").mkdir(exist_ok=True)
    output_path = out_schem.name + ".litematic"
    out_schem.save(output_path)
    return output_path


def copy_offset(
    region: Region, *, x_tiles: int = 0, y_layers: int = 0, z_tiles: int = 0
) -> Region:
    # Serialize a copy so the original stays untouched
    data = deepcopy(region).to_nbt()

    # Shift the region origin by whole tiles or layers
    position = data["Position"]
    position["x"] = int(region.x + W_SLICE * x_tiles)
    position["y"] = int(region.y + H_SLICE * y_layers)
    position["z"] = int(region.z + L_SLICE * z_tiles)

    # Reconstruct an independent region at the new position
    return Region.from_nbt(data)  # pyright: ignore[reportCallIssue] (litemapy's issue)


if __name__ == "__main__":
    gen_schem(3, 3, 3)
