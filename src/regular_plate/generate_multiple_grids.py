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
        # self.read_parameters(Path('../../data/filtration_values.csv'))
        # self.read_parameters(Path('../../data/irregular_tuberack_values.csv'))
        self.read_parameters(Path('../../data/rectangular_well_values.csv'))
        self.construct_labware()

    def read_template(self, path: Path = None):
        """
        Reads a JSON template file and saves it as a dictionary in self.template.
        :param new_path: the path to the JSON template file. Defaults to '../../data/default.json'.
        """
        if path is None:
            path = Path('../../data/default.json')
        with open(path, encoding="utf-8") as file:
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
        self.well_bottom_shape()
        current_row_index = 0
        for grid in self.grids:
            current_row_index = self.create_wells(grid, current_row_index)
        self.ordering()
        self.wells()

    def update_dimension(self, direction: str, new_value: float = None):
        """
        Helper function for create_plate. Updates the dimensions of the plate.
        Sets the height to the maximum of all given.
        :param direction: the direction to update ('x', 'y', or 'z')
        :param new_value: the new value for the dimension. If None, uses the first grid's dimension.
        """
        if new_value is None:
            self.template["dimensions"][f"{direction}Dimension"] = self.grids[0][
                f"{direction}Dimension"]
            max_height = max([self.grids[i]["zDimension"] for i in range(len(self.grids))])
            self.template["dimensions"]["zDimension"] = max_height
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
            name = self.grids[0]["display_name"]
        self.template["metadata"]["displayName"] = name

    def load_name(self, name: str = None):
        """
        Sets load name
        """
        if name is None:
            name = self.template["parameters"]["loadName"] = self.grids[0]["load_name"]
        self.template["metadata"]["loadName"] = name

    def display_category(self, category=None):
        """
        Sets category (e.g. wellPlate). If labware is a tiprack, sets tiprack length.
        """
        if category is None:
            category = self.grids[0]["display_category"]
        self.template["metadata"]["displayName"] = category

        if category == "tipRack":
            self.template["parameters"]["isTiprack"] = True
            self.template["parameters"]["tipLength"] = self.grids[0]["tipLength"]

    def well_bottom_shape(self, shape=None):
        """
        Changes the bottom shape of a specified well.
        :param well_name: the name of the well to be updated
        :param new_shape: the new bottom shape for the well ('flat', 'v', or 'u')
        """
        if shape is None:
            shape = self.grids[0]["bottom_shape"]
        self.template["groups"][0]["metadata"]["wellBottomShape"] = shape

    def create_wells(self, grid, start_row_index):
        """
        Creates wells based on the given parameters
        start_row_index: keeps track of the indexes of letters for row names
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
                z = round(grid['zDimension'] - grid['well_depth'], 2)

                if grid['well_shape'] == "circular":
                    well = {
                        "depth": grid['well_depth'],
                        "totalLiquidVolume": grid['volume'],
                        "shape": grid['well_shape'],
                        "diameter": grid['well_diameter'],
                        "x": x,
                        "y": y,
                        "z": z
                    }
                else:  # well_shape is 'rectangular'
                    well = {
                        "depth": grid['well_depth'],
                        "totalLiquidVolume": grid['volume'],
                        "shape": grid['well_shape'],
                        "xDimension": grid['well_xDimension'],
                        "yDimension": grid['well_yDimension'],
                        "x": x,
                        "y": y,
                        "z": z
                    }

                self.template["wells"][well_name] = well

        return start_row_index + grid['rows']

    def ordering(self):
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

    def wells(self):
        """
        Generates the list of well names, sorted by column first and then by row
        """
        wells = sorted(self.template["wells"].keys(), key=lambda x: (int(x[1:]), x[0]))
        self.template["groups"][0]["wells"].extend(wells)

plate = MultipleGrids()
print(json.dumps(plate.template, indent=4))
# with open(Path(r"../../data/filtration.json"), "w") as f:
#     json.dump(plate.template, f, indent=4)
