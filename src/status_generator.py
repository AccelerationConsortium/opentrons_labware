import json
from pathlib import Path

class StatusGenerator:
    def __init__(self, labware_path, status_path):
        self.labware_path = Path(labware_path)
        self.status_path = Path(status_path)
        self.labware_data = None
        self.filtration_status = None

    def generate_status_file(self, reset_status=False):
        self.load_labware()
        if reset_status or not self.status_path.exists():
            self.initialize_status()
        else:
            self.load_status()
        self.save_status_data()

    def load_labware(self):
        with open(self.labware_path, 'r', encoding='utf-8') as file:
            self.labware_data = json.load(file)

    def initialize_status(self):
        self.filtration_status = {well: 'CLEAN' for well in self.labware_data['wells']}

    def load_status(self):
        with open(self.status_path, 'r', encoding='utf-8') as file:
            self.filtration_status = json.load(file)

    def save_status_data(self):
        with open(self.status_path, 'w', encoding='utf-8') as file:
            json.dump(self.filtration_status, file, indent=4)

labware_file_path = "../data/filtration.json"
status_file_path = "../data/filtration_status.json"

generator = StatusGenerator(labware_file_path, status_file_path)
generator.generate_status_file()
