import json
import math

class Verifier:
    """
    Class for verifying the generated dictionary or JSON file.
    It can accept either a dictionary or a path to a JSON file.
    """

    def __init__(self, labware_def):
        self.labware_def = labware_def
        self.data = None

    def verify(self):
        """
        Check the generated json file.
        """
        if isinstance(self.labware_def, dict):
            self.data = self.labware_def
        elif isinstance(self.labware_def, str):
            try:
                with open(self.labware_def, 'r', encoding='utf-8') as file:
                    self.data = json.load(file)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error decoding JSON: {e}")
            except FileNotFoundError as e:
                raise ValueError(f"File not found: {e}")
            except Exception as e:
                raise ValueError(f"An error occurred: {e}")
        else:
            raise ValueError("Invalid input type. Expected a dictionary or a path to a JSON file.")

        self.check_shapes()
        self.check_heights()
        self.check_well_positions()

    def check_shapes(self):
        """
        Check well bottom shapes and well shapes are allowed shapes.
        """
        if self.data["groups"][0]["metadata"]["wellBottomShape"] not in ['flat', 'v', 'u']:
            raise ValueError("Invalid well bottom shape. Options are 'flat', 'v', and 'u'.")

        for well in self.data["wells"].keys():
            if well["shape"] not in ['circular', 'square']:
                raise ValueError("Invalid well shape. Options are 'circular' and 'square'.")

    def check_heights(self):
        """
        Check wells are not taller than max allowed height.
        """
        # P1000, single - channel: 223.46 - 78.3 = 145.16 mm
        # P300, single - channel: 202.77 - 51 = 151.77 mm
        # P20, single - channel: 183.77 - 31.1 = 152.77 mm
        # P300, 8 - channel: 192.44 - 51 = 141.44 mm
        # P20, 8 - channel: 176 - 31.1 = 144.9 mm
        max_height = 141
        if self.data["dimensions"]["zDimension"] > max_height:
            raise ValueError(f"Height of labware greater than allowed height, {max_height} mm.")

    def check_well_positions(self):
        """
        Check wells do not overlap in the xy plane and do not go out of bounds.
        Check well height/depth make sense.
        """
        well_keys = list(self.data["wells"].keys())
        for i in range(len(well_keys)):
            for j in range(i + 1, len(well_keys)):
                well1 = self.data["wells"][well_keys[i]]
                well2 = self.data["wells"][well_keys[j]]

                # check wells don't go beyond edges
                if well1["x"] < 0 or well1["y"] < 0:
                    raise ValueError(f"Well {[well_keys[i]]} goes out of bounds.")
                if (well1["x"] > self.data["dimensions"]["xDimension"]
                        or well1["y"] > self.data["dimensions"]["yDimension"]):
                    raise ValueError(f"Well {[well_keys[i]]} goes out of bounds.")

                # check zDimension > depth or z>=0 for each well
                if self.data["dimensions"]["zDimension"] < well1["depth"] or well1["z"] < 0:
                    raise ValueError(f"Well {[well_keys[i]]} height and depth do not make sense.")

                # check wells don't overlap
                distance = math.dist([well1["x"], well1["y"]], [well2["x"], well2["y"]])
                if distance < (well1["diameter"] / 2 + well2["diameter"] / 2):
                    raise ValueError(f"Wells {[well_keys[i]]} and {[well_keys[j]]} overlap.")

    # check pipette doesn't dispense more than max well volume. does opentrons already check this?
