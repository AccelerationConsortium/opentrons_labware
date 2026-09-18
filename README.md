<a id="readme-top"></a>

<div align="center">
  <h3 align="center">Opentrons Custom Labware</h3>
  <p align="center">
    Irregular custom labware definitions and low-cost hardware modules for the Opentrons OT-2.
    <br />
    <a href="#run-a-protocol">View Demo</a>
    &middot;
    <a href="https://github.com/AccelerationConsortium/opentrons_labware/issues/new">Report Bug</a>
    &middot;
    <a href="https://github.com/AccelerationConsortium/opentrons_labware/issues/new">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

The Opentrons Labware Creator only handles regular, single-grid plates. This repository extends the platform to custom irregular labware to allow for more complex and versatile automation workflows.

Features:

* **Labware definition generators**: build Opentrons JSON labware definitions from a short CSV of physical parameters, plus a verifier that catches geometry and metadata errors before runs.
* **A labware status updater**: tracks per-well state across protocols, so consumable resources such as filtration vials can be allocated dynamically at runtime.
* **3D-printable hardware modules**: Fusion360/STL models with matching Python and Arduino code for low-cost filtration, stirring, and heating.

This software and hardware was designed for the Opentrons OT-2 liquid handler but is also compatible with similar platforms such as the Science Jubilee.

### Built With

* [![Python][Python-shield]][Python-url]
* [![Opentrons][Opentrons-shield]][Opentrons-url]
* [![Arduino][Arduino-shield]][Arduino-url]
* [![scikit-optimize][skopt-shield]][skopt-url]

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

* Python 3.8+
* Opentrons OT-2 or Science Jubilee setup

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/AccelerationConsortium/opentrons_labware.git
   cd opentrons_labware
   ```
2. Install the package and dependencies
   ```sh
   pip install -e .
   ```

<!-- USAGE -->
## Usage

### Describe the labware in CSV

One row per parameter, one column per grid. The example below is a filtration plate with 11 mL filtration vials and 20 mL collection wells underneath:

```csv
zDimension,60,120
rows,3,3
cols,4,4
volume,20000,11000
well_shape,circular,circular
well_depth,56,43
well_diameter,7,16
x_spacing,28,28
y_spacing,28,28
x_offset,18,31
y_offset,18,19
load_name,matterlab_filtration,
```

### Generate the definition

```python
from pathlib import Path
import json
from generate_multiple_grids import MultipleGrids   # or: from generate_regular import Regular

plate = MultipleGrids()
plate.read_parameters(Path('/data/filtration_values.csv'))
plate.construct_labware()

with open(Path('/data/filtration.json'), 'w') as f:
    json.dump(plate.template, f, indent=4)
```

Rows are lettered from the bottom grid upwards (`A`–`C` here are the collection wells, `D`–`F` are the
filtration vials) and wells are ordered column-first, matching the Opentrons convention. Use `Regular` for single-grid plates.

### Verify before you run

```python
from verifier import Verifier

Verifier('/data/filtration.json').verify()
```

Checks well and bottom shapes, well depths against pipette clearance, well positions inside the plate
footprint, required metadata, deck-slot dimensions, and optionally that stated volumes match the
well geometry.

### Track well status across protocols

```python
from status_generator import StatusGenerator

StatusGenerator('/data/filtration.json', '/data/filtration_status.json').generate_status_file()
```

A protocol can then claim the first `CLEAN` well, mark it `ONGOING` while filtering, and set it `USED`
when the filtrate has been collected — see `tests/filtration_status_test.py`.

### Run a protocol

```sh
opentrons_simulate tests/salen_synthesis.py
```

`tests/salen_synthesis.py` is the end-to-end demo: it combines salicylaldehyde and ethylenediamine in a
stirrer vial, stirs for an hour, transfers the slurry onto the filtration module, and washes the product
with methanol. See the full video demo [here](https://www.youtube.com/watch?v=UPP-d5iaWP0). `tests/filtration_test.py` is a shorter transfer-only example.

### Hardware modules

Flash `arduino/optimize_temp.ino` to the board, then drive it from Python over serial:

```sh
cd arduino
python main.py     # Bayesian-optimizes a PWM sequence to reach a target temperature
python stirrer.py  # toggles the magnetic stirrer
```

`Heater` reads a 10 kΩ thermistor (β = 3435) and applies PWM to the heating pad, `Wrapper` scores how
quickly a PWM sequence reaches and holds the target within ±1 °C, and `Optimizer` searches that space
with `gp_minimize`. 

The stirrer module also uses a low-cost, DIY design: small magnets are attached to a mini fan placed directly underneath the vials inside a custom 3D-printed rack, compatible with standard magnetic stir bars. Printable models for all modules are available in `3d_models/`.

<!-- CONTRIBUTING -->
## Contributing

Any contributions you make are greatly appreciated.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.

<!-- CONTACT -->
## Contact

Acceleration Consortium — [@AccelerationConsortium](https://github.com/AccelerationConsortium)

Project Link: [https://github.com/AccelerationConsortium/opentrons_labware](https://github.com/AccelerationConsortium/opentrons_labware)

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Opentrons Labware Schema](https://github.com/Opentrons/opentrons/tree/edge/shared-data/labware)
* [Opentrons Python Protocol API](https://docs.opentrons.com/v2/)
* [Science Jubilee](https://github.com/machineagency/science-jubilee)
* [scikit-optimize](https://scikit-optimize.github.io/)
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[Python-shield]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Opentrons-shield]: https://img.shields.io/badge/Opentrons%20API-006FFF?style=for-the-badge&logoColor=white
[Opentrons-url]: https://docs.opentrons.com/v2/
[Arduino-shield]: https://img.shields.io/badge/Arduino-00979D?style=for-the-badge&logo=arduino&logoColor=white
[Arduino-url]: https://www.arduino.cc/
[skopt-shield]: https://img.shields.io/badge/scikit--optimize-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white
[skopt-url]: https://scikit-optimize.github.io/
