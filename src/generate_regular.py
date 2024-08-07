import json
from pathlib import Path
from typing import Union, List

class Regular:
    """
    class for generating json file for regular labware
    """
    def __init__(self):
        self.template = {}
        self.data = {}
        # self._display_name = None
        self.read_template()

    def read_template(self, path: Path = None):
        """
        Reads a JSON template file and saves it as a dictionary in self.template.
        :param path: the path to the JSON template file. Defaults to '../../data/default.json'.
        """
        if path is None:
            path = Path(__file__).parent.parent / 'data' / 'default.json'
        with open(path, encoding="utf-8") as file:
            self.template = json.load(file)

    def read_parameters(self, path):
        """
        :param path: path to csv file with inputs, saves information as data dictionary
        """
        data = {}
        with open(path, 'r') as file:
            for line in file:
                pair = line.strip().split(',')
                key = pair[0].strip()
                value = pair[1].strip()
                # convert value to float if possible, otherwise to int if possible
                try:
                    value = float(value)
                    if value.is_integer():
                        value = int(value)
                except ValueError:
                    pass  # keep value as string if it cannot be converted to float or int
                data[key] = value
        self.data = data

    def construct_labware(self):
        """
        call functions to construct each part of the dictionary
        """
        self.create_plate()
        self.display_name()
        self.load_name()
        self.display_category()
        self.create_wells()
        self.ordering()
        self.wells()

    def update_dimension(self, direction: str, new_value: float = None):
        """
        helper function for create_plate
        :param direction: direction to update out of x, y, and z
        :param new_value: updated value for length, width, or height
        """
        if new_value is None:
            self.template["dimensions"][f"{direction}Dimension"] = self.data[
                f"{direction}Dimension"]
        else:
            self.template["dimensions"][f"{direction}Dimension"] = new_value

    def create_plate(self, dimensions=(None, None, None)):
        """
        sets length, width, and height of plate
        :param dimensions: tuple containing length, width, height
        """
        directions = ("x", "y", "z")
        for i in range(len(directions)):
            self.update_dimension(directions[i], dimensions[i])

    def display_name(self, name: str = None):
        """
        sets display name
        """
        if name is None:
            self.template["metadata"]["displayName"] = self.data["display_name"]
        else:
            self.template["metadata"]["displayName"] = name

    def load_name(self, name: str = None):
        """
        sets load name
        """
        if name is None:
            self.template["parameters"]["loadName"] = self.data["load_name"]
        else:
            self.template["metadata"]["loadName"] = name

    def display_category(self, category=None):
        """
        sets category e.g. wellPlate
        """
        if category is None:
            self.template["metadata"]["displayCategory"] = self.data["display_category"]
        else:
            self.template["metadata"]["displayName"] = category

    def create_wells(self, rows=None, cols=None, well_depth=None, volume=None, well_shape=None,
                     well_diameter=None, x_offset=None,
                     y_offset=None, x_spacing=None, y_spacing=None, zDimension=None):
        """
        Creates wells based on the given parameters.
        """
        params = {
            'rows': rows, 'cols': cols, 'well_depth': well_depth, 'volume': volume,
            'well_shape': well_shape, 'well_diameter': well_diameter, 'x_offset': x_offset,
            'y_offset': y_offset, 'x_spacing': x_spacing, 'y_spacing': y_spacing,
            'zDimension': zDimension
        }

        # replace None values with the corresponding values from self.data
        for key, value in params.items():
            if value is None:
                params[key] = self.data[key]

        def get_label(index):
            """
            Convert a numerical index to the corresponding label A,...,Z,AA,...ZZ,AAA...
            """
            label = ''
            while index >= 0:
                label = chr(ord('A') + index % 26) + label
                index = index // 26 - 1
            return label

        for col in range(1, params['cols'] + 1):
            for row in range(params['rows']):
                letter = get_label(row)
                well_name = f"{letter}{col}"
                x = round(params['x_offset'] + (col - 1) * params['x_spacing'], 2)
                y = round(params['y_offset'] + (params['rows'] - row - 1) * params['y_spacing'], 2)
                z = round(params['zDimension'] - params['well_depth'], 2)
                self.create_well(well_name, params['well_depth'], params['volume'],
                                 params['well_shape'], params['well_diameter'], x, y, z)

    def create_well(self, well_name, well_depth, volume, well_shape, well_diameter, x, y, z):
        """
        Creates a single well with the specified parameters.
        """
        well = {
            "depth": well_depth,
            "totalLiquidVolume": volume,
            "shape": well_shape,
            "diameter": well_diameter,
            "x": x,
            "y": y,
            "z": z
        }
        self.template["wells"][well_name] = well

    def ordering(self, rows: Union[int, List[str]] = None, cols: Union[int, List[int]] = None):
        """
        generates the ordering list based on number of rows and cols
        """
        ordering = []
        if rows is None and cols is None:
            for i in range(1, self.data["cols"] + 1):
                row = []
                for j in range(0, self.data["rows"]):
                    letter = chr(ord('A') + j)
                    row.append(f"{letter}{i}")
                ordering.append(row)
        else:
            if isinstance(cols, int):
                cols = range(1, cols + 1)
            if isinstance(rows, int):
                rows = [chr(ord('A') + j) for j in range(rows)]
            for i in cols:
                row = []
                for letter in rows:
                    row.append(f"{letter}{i}")
                ordering.append(row)
        self.template["ordering"] = ordering

    def wells(self, rows: Union[int, List[str]] = None, cols: Union[int, List[int]] = None):
        """
        generates the list of wells based on number of rows and cols
        """
        wells = []
        if rows is None and cols is None:
            for i in range(1, self.data["cols"] + 1):
                for j in range(0, self.data["rows"]):
                    letter = chr(ord('A') + j)
                    wells.append(f"{letter}{i}")
        else:
            if isinstance(cols, int):
                cols = range(1, cols + 1)
            if isinstance(rows, int):
                rows = [chr(ord('A') + j) for j in range(rows)]
            for i in cols:
                for letter in rows:
                    wells.append(f"{letter}{i}")
        self.template["groups"][0]["wells"] = wells

plate = Regular()
plate.read_parameters(Path('../data/24_wellplate_values.csv'))
# plate.read_parameters(Path('../../data/96_wellplate_values.csv'))
plate.construct_labware()
print(json.dumps(plate.template, indent=4))

# with open(Path(r"../../data/result.json"), "w") as f:
#     json.dump(dict1, f)
