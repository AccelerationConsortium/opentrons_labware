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

    def verify(self, run_optional_checks=True):
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
        self.check_metadata()
        self.check_dimensions()

        if run_optional_checks:
            self.check_volume()

    def check_shapes(self):
        """
        Check well bottom shapes and well shapes are allowed shapes.
        """
        if self.data["groups"][0]["metadata"]["wellBottomShape"] not in ['flat', 'v', 'u']:
            raise ValueError("Invalid well bottom shape. Options are 'flat', 'v', and 'u'.")

        for well in self.data["wells"].keys():
            if self.data["wells"][well]["shape"] not in ['circular', 'rectangular']:
                raise ValueError("Invalid well shape. Options are 'circular' and 'rectangular'.")

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
                    raise ValueError("Labware must be taller than well depth.")

                # check wells don't overlap
                distance = math.dist([well1["x"], well1["y"]], [well2["x"], well2["y"]])
                if distance < (well1["diameter"] / 2.0 + well2["diameter"] / 2.0):
                    raise ValueError(f"Wells {[well_keys[i]]} and {[well_keys[j]]} overlap.")

    def check_metadata(self):
        """
        Check volume units and category.
        """
        if self.data["metadata"]["displayVolumeUnits"] not in ['\u00b5L', 'mL']:
            raise ValueError("Invalid display units. Options are 'μL' and 'mL'.")

        if (self.data["metadata"]["displayCategory"] not in
                ["wellPlate", "reservoir", "tubeRack", "aluminumBlock", "tipRack"]):
            raise ValueError("Invalid category. Options are 'wellPlate', 'reservoir',"
                             " 'tubeRack', 'aluminumBlock', and 'tipRack'.")

    def check_dimensions(self):
        """
        Check xDim <= 127 and yDim <= 85 (with 3mm tolerance).
        """
        if (self.data["dimensions"]["xDimension"] > 130
                or self.data["dimensions"]["yDimension"] > 88):
            raise ValueError("Labware exceeds maximum allowed dimensions for Opentrons.")

    def check_volume(self):
        """
        Check each well volume doesn't exceed the physical max based on well dimensions.
        For v and u shaped bottoms, assume flat bottom.
        """
        well_keys = list(self.data["wells"].keys())
        for i in range(len(well_keys)):
            well = self.data["wells"][well_keys[i]]
            vol = math.pi * well["depth"] * well["diameter"] * well["diameter"] / 4.0
            tolerance = 15
            if well["totalLiquidVolume"] > (vol + tolerance):
                print(f"Warning: Well {well_keys[i]} volume exceeds physical limits. "
                      "Double check well height, diameter, and volume.")
                user_input = input("Type 'Y' to proceed to check the next well volume. "
                                   "Type 'A' to skip remaining well volume checks: ")
                if user_input.strip().upper() == 'A':
                    return
                while user_input.strip().upper() != 'Y':
                    print("Invalid input. Please type 'Y' to proceed.")
                    user_input = input("Type 'Y' to proceed: ")

v = Verifier("../../data/filtration.json")
v.verify()
