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

    # Load status
    path = Path("../data/filtration_status.json")
    with open(path, encoding="utf-8") as file:
        filtration_status = json.load(file)

    # Load liquid
    slurry = protocol.define_liquid(name='slurry', description='', display_color='#000000')
    wells_to_load = ['A1', 'B1', 'C1', 'D1']
    for well in wells_to_load:
        wellplate[well].load_liquid(slurry, 1000)

    pipette.pick_up_tip(tiprack['A1'])

    # Find first CLEAN well and dispense
    clean_well_found = False
    current_well = None
    for well in filtration_status:
        if filtration_status[well] == "CLEAN":
            clean_well_found = True
            current_well = well
            pipette.aspirate(500, wellplate['A1'])
            pipette.dispense(500, filtration_plate[current_well])
            filtration_status[current_well] = "ONGOING"
            break

    if not clean_well_found:
        raise RuntimeError("Error: No clean well found. Ending protocol.")

    # Replace tip
    pipette.drop_tip()
    pipette.pick_up_tip(tiprack['B1'])

    # Aspirate filtered liquid and update status to USED
    pipette.aspirate(500, filtration_plate[chr(ord(current_well[0]) - 3) + current_well[1]])
    pipette.dispense(500, wellplate['A2'])
    filtration_status[current_well] = "USED"

    pipette.drop_tip()
