import json
from pathlib import Path
from opentrons import protocol_api, types

metadata = {'apiLevel': '2.16'}

def run(protocol: protocol_api.ProtocolContext):

    # Load pipette
    pipette = protocol.load_instrument('p1000_single_gen2', 'right')

    # Load labware
    tiprack = protocol.load_labware('opentrons_96_tiprack_1000ul', '1')
    wellplate = protocol.load_labware('corning_24_wellplate_3.4ml_flat', '2')
    path = Path("../data/filtration.json")
    with open(path, encoding="utf-8") as file:
        filtration_file = json.load(file)
    filtration_plate = protocol.load_labware_from_definition(filtration_file, '3')

    # Load liquid
    slurry = protocol.define_liquid(name='slurry', description='', display_color='#000000')
    wells_to_load = ['A1', 'B1', 'C1', 'D1']
    for well in wells_to_load:
        wellplate[well].load_liquid(slurry, 1000)

    pipette.pick_up_tip(tiprack['A1'])

    # Aspirate and dispense sequence
    aspirations_dispenses = [
        ('A1', 'F1'),
        ('B1', 'F1'),
        ('C1', 'F2'),
        ('D1', 'F2')
    ]

    for aspirate_well, dispense_well in aspirations_dispenses:
        pipette.aspirate(500, wellplate[aspirate_well])
        pipette.dispense(500, filtration_plate[dispense_well])

    pipette.drop_tip()

    pipette.pick_up_tip(tiprack['B1'])

    # Aspirate and dispense sequence
    aspirations_dispenses_2 = [
        ('C1', 'A6'),
        ('B1', 'B6')
    ]

    for aspirate_well, dispense_well in aspirations_dispenses_2:
        pipette.aspirate(500, filtration_plate[aspirate_well])
        pipette.dispense(500, wellplate[dispense_well])

    pipette.drop_tip()
