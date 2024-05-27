import json
from pathlib import Path

class MultipleGrids:
    """
    Class for generating JSON file for irregular labware made up of 2 or more regular grids.
    """

    def __init__(self):
        self.template = {}
        self.grids = []
        self.read_template()
        self.read_parameters(Path('../../data/filtration_values.csv'))
        self.construct_labware()

    def read_template(self, new_path: Path = None):
        """
        Reads a JSON template file and saves it as a dictionary in self.template.
        :param new_path: the path to the JSON template file. Defaults to '../../data/default.json'.
        """
        if new_path:
            path = new_path
        else:
            path = Path('../../data/default.json')
        with open(path) as file:
            self.template = json.load(file)

    def read_parameters(self, path):
        """
        Reads a CSV file containing grid parameters and saves the information
        as a list of dictionaries in self.grids.
        """
        with open(path, 'r') as file:
            grid_data = []

            for line in file:
                values = line.strip().split(',')
                key = values[0].strip()

                for i in range(1, len(values)):
                    if len(grid_data) < i:
                        grid_data.append({})
                    value = values[i].strip()
                    try:
                        value = float(value)
                        if value.is_integer():
                            value = int(value)
                    except ValueError:
                        pass
                    grid_data[i - 1][key] = value

            self.grids = grid_data

    def construct_labware(self):
        """
        Call functions to construct each part of the dictionary, create wells, and order them.
        """
        self.create_plate()
        self.display_name()
        self.load_name()
        self.display_category()
        current_row_index = 0
        for grid in self.grids:
            current_row_index = self.create_wells(grid, current_row_index)
        self.ordering()
        self.wells()

    def update_dimension(self, direction: str, new_value: float = None):
        """
        Helper function for create_plate. Updates the dimensions of the plate.
        :param direction: the direction to update ('x', 'y', or 'z')
        :param new_value: the new value for the dimension. If None, uses the first grid's dimension.
        """
        if new_value is None:
            self.template["dimensions"][f"{direction}Dimension"] = self.grids[0][
                f"{direction}Dimension"]
        else:
            self.template["dimensions"][f"{direction}Dimension"] = new_value

    def create_plate(self, dimensions=(None, None, None)):
        """
        Sets length, width, and height of plate
        :param dimensions: tuple containing length, width, height
        """
        directions = ("x", "y", "z")
        for i in range(len(directions)):
            self.update_dimension(directions[i], dimensions[i])

    def display_name(self, name: str = None):
        """
        Sets display name
        """
        if name is None:
            self.template["metadata"]["displayName"] = self.grids[0]["display_name"]
        else:
            self.template["metadata"]["displayName"] = name

    def load_name(self, name: str = None):
        """
        Sets load name
        """
        if name is None:
            self.template["parameters"]["loadName"] = self.grids[0]["load_name"]
        else:
            self.template["metadata"]["loadName"] = name

    def display_category(self, category=None):
        """
        Sets category e.g. wellPlate
        """
        if category is None:
            self.template["metadata"]["displayCategory"] = self.grids[0]["display_category"]
        else:
            self.template["metadata"]["displayName"] = category

    def create_wells(self, grid, start_row_index):
        """
        Creates wells based on the given parameters
        """
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if "wells" not in self.template:
            self.template["wells"] = {}

        for row in range(grid['rows']):
            row_letter = alphabet[start_row_index + row]
            for col in range(1, grid['cols'] + 1):
                well_name = f"{row_letter}{col}"
                x = round(grid['x_offset'] + (col - 1) * grid['x_spacing'], 2)
                y = round(grid['y_offset'] + row * grid['y_spacing'], 2)
                z = grid['zDimension'] - grid['well_depth']
                self.create_well(well_name, grid['well_depth'], grid['volume'],
                                 grid['well_shape'], grid['well_diameter'], x, y, z)

        return start_row_index + grid['rows']

    def create_well(self, well_name, well_depth, volume, well_shape, well_diameter, x, y, z):
        """
        Creates a single well with the specified parameters
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

    def ordering(self, grid=None):
        """
        Generates the ordering list for the wells, sorted by column first and then by row
        """
        ordering = []
        for well_name in sorted(self.template["wells"].keys(), key=lambda x: (int(x[1:]), x[0])):
            col = int(well_name[1:])
            if len(ordering) < col:
                ordering.append([])
            ordering[col - 1].append(well_name)

        self.template["ordering"] = ordering

    def wells(self, grid=None):
        """
        Generates the list of well names, sorted by column first and then by row
        """
        wells = sorted(self.template["wells"].keys(), key=lambda x: (int(x[1:]), x[0]))
        self.template["groups"][0]["wells"].extend(wells)


plate = MultipleGrids()
print(json.dumps(plate.template, indent=4))
