import json
from pathlib import Path

# inputs
length = 127
width = 85
height = 48
rows = 4
cols = 6
volume = 3400
well_shape = "circular"
bottom_shape = "flat"
well_depth = 44
well_diameter = 8.37
x_spacing = 20.9
y_spacing = 20.9
x_offset = 11.22
y_offset = 11.08
display_name = "MatterLab 24 Well Plate 3400 µL"
load_name = "matterlab_24_wellplate_3400ul"

# functions
def generate_ordering(n, m):  # n rows, m cols
    ordering = []
    for i in range(1, m + 1):
        row = []
        for j in range(0, n):
            letter = chr(ord('A') + j)
            row.append(f"{letter}{i}")
        ordering.append(row)
    return ordering

ordering = generate_ordering(rows, cols)
wells = []
for sublist in ordering:
    for item in sublist:
        wells.append(item)

def generate_well_dict():
    well_dict = {}
    for well in wells:
        well_dict[well] = {
           "depth": well_depth,
           "totalLiquidVolume": volume,
           "shape": well_shape,
           "diameter": well_diameter,
           "x": x_offset + (int(well[1])-1)*x_spacing ,
           "y": y_offset + (rows-1-wells.index(well) % rows)*y_spacing,
           "z": height - well_depth
        }
    return well_dict

well_dict = generate_well_dict()

# dict
dict1 = {
        "ordering": ordering,
        "brand": {
            "brand": "MatterLab",
            "brandId": []
        },
        "metadata": {
            "displayName": display_name,
            "displayCategory": "wellPlate",
            "displayVolumeUnits": "µL",
            "tags": []
        },
        "dimensions": {
            "xDimension": length,
            "yDimension": width,
            "zDimension": height
        },
        "wells": well_dict,
        "groups": [
            {
                "metadata": {
                    "wellBottomShape": "flat"
                },
                "wells":  wells
            }
        ],
        "parameters": {
            "format": "irregular",
            "quirks": [],
            "isTiprack": False,
            "isMagneticModuleCompatible": False,
            "loadName": load_name
        },
        "namespace": "custom_beta",
        "version": 1,
        "schemaVersion": 2,
        "cornerOffsetFromSlot": {
            "x": 0,
            "y": 0,
            "z": 0
        }
    }
with open(Path(rf"C:\Users\sdl2\Downloads\{load_name}.json"), "w") as f:
    json.dump(dict1, f)
