import json
from pathlib import Path
from opentrons import protocol_api, types

metadata = {'apiLevel': '2.16'}

def load_labware_from_json(protocol, file_path, slot):
    with open(file_path, encoding="utf-8") as file:
        labware_file = json.load(file)
    return protocol.load_labware_from_definition(labware_file, slot)

def transfer(pipette, volume, source_zone, target_zone, new_tip=False, tip=None, return_tip=False):
    if new_tip:
        pipette.pick_up_tip(tip)
    pipette.aspirate(volume, source_zone)
    pipette.dispense(volume, target_zone)
    if return_tip:
        pipette.drop_tip()

def run(protocol: protocol_api.ProtocolContext):

    # Load pipette
    pipette = protocol.load_instrument('p1000_single_gen2', 'right')

    # Load labware
    wellplate = protocol.load_labware('corning_24_wellplate_3.4ml_flat', '1')
    stirrer = load_labware_from_json(protocol, Path("../data/filtration.json"), '2')
    filtration = load_labware_from_json(protocol, Path("../data/stirrer_20ml.json"), '3')
    tiprack = protocol.load_labware('opentrons_96_tiprack_1000ul', '4')

    # Add 1ml salicylaldehyde stock solution to reaction vial
    transfer(pipette, 1000, wellplate['A1'], stirrer['A2'], new_tip=True, return_tip=True)

    # Add 1ml ethylenediamine stock solution to reaction vial
    transfer(pipette, 1000, wellplate['A2'], stirrer['A2'], new_tip=True, return_tip=True)

    # Stir for 1h
    protocol.delay(hours=1)

    # Transfer slurry to filtration
    pipette.pick_up_tip()
    for i in range(3):
        transfer(pipette, 1000, stirrer['A2'], filtration['F1'])
    pipette.drop_tip()

    # Wash with methanol
    for i in range(3):
        transfer(pipette, 1000, wellplate['A3'], stirrer['A1'], new_tip=True, return_tip=False)
        protocol.delay(seconds=10)
        transfer(pipette, 1000, stirrer['A1'], filtration['F1'], return_tip=True)
        protocol.delay(minutes=3)

    # Clear the filtered liquid
    pipette.pick_up_tip()
    for i in range(5):
        transfer(pipette, 1000, filtration['C1'], wellplate['B1'])
    pipette.drop_tip()

    # Dissolve in acetone
    for i in range(6):
        transfer(pipette, 1000, wellplate['A4'], filtration['F1'], new_tip=True, return_tip=False)
        pipette.mix(3, location=filtration['F1'])
        pipette.drop_tip()
        protocol.delay(minutes=3)
