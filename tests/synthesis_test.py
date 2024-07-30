import json
from pathlib import Path
from opentrons import protocol_api, types

metadata = {'apiLevel': '2.16'}

def run(protocol: protocol_api.ProtocolContext):

    # Load pipette
    pipette = protocol.load_instrument('p1000_single_gen2', 'right')

    # Load labware
    wellplate = protocol.load_labware('corning_24_wellplate_3.4ml_flat', '1')
    path = Path("../data/stirrer.json")     # give it a better name, or even make a load_labware_from_json func outside run()
    with open(path, encoding="utf-8") as file:
        stirrer_file = json.load(file)
    stirrer = protocol.load_labware_from_definition(stirrer_file, '2')
    path = Path("../data/filtration.json")
    with open(path, encoding="utf-8") as file:
        filtration_file = json.load(file)
    filtration = protocol.load_labware_from_definition(filtration_file, '3')
    tiprack = protocol.load_labware('opentrons_96_tiprack_1000ul', '4')

    # Add 1ml salicylaldehyde stock solution to reaction vial
    # create indepedent func transfer(volume = 1000, tip = tiprack["A1"], source_zone, target_zone, return_tip: bool = False), and call it
    pipette.pick_up_tip(tiprack['A1'])
    pipette.aspirate(1000, wellplate['A1'])
    pipette.dispense(1000, stirrer['A1'])
    pipette.drop_tip()

    # Add 1ml ethylenediamine stock solution to reaction vial
    pipette.pick_up_tip(tiprack['A2'])
    pipette.aspirate(1000, wellplate['A2'])
    pipette.dispense(1000, stirrer['A1'])
    pipette.drop_tip()

    # Stir for 1h
    protocol.delay(hours=1)     # also create a func outside run()

    # Transfer slurry to filtration
    pipette.pick_up_tip(tiprack['A3'])
    for i in range(3):
        pipette.aspirate(1000, stirrer['A1'])
        pipette.dispense(1000, filtration['D1'])
    pipette.drop_tip()

    # Wash with methanol
    for i in range(3):
        pipette.pick_up_tip(tiprack['A4'])
        pipette.aspirate(1000, wellplate['A3'])
        pipette.dispense(1000, stirrer['A1'])
        protocol.delay(seconds=30)
        pipette.aspirate(1000, stirrer['A1'])
        pipette.dispense(1000, filtration['D1'])
        pipette.drop_tip()
        protocol.delay(minutes=3)

    # Clear the filtered liquid
    pipette.pick_up_tip(tiprack['A5'])
    for i in range(3):
        pipette.aspirate(1000, filtration['A1'])
        pipette.dispense(1000, wellplate['B1'])
    pipette.drop_tip()

    # Dissolve in acetone
    for i in range(6):
        pipette.pick_up_tip(tiprack['A6'])
        pipette.aspirate(1000, wellplate['A4'])
        pipette.dispense(1000, filtration['D1'])
        pipette.mix(3, location=filtration['D1'])
        pipette.drop_tip()
        protocol.delay(minutes=3)
