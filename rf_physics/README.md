# RFID antenna physics — first real solver experiment

This directory contains an **openEMS FDTD simulation**, not a random RFID detection generator.

## Starting point

`patch_866.py` is an experimental **866 MHz microstrip patch antenna baseline**, derived structurally from the official openEMS [Simple Patch Antenna tutorial](https://github.com/thliebig/openEMS/blob/master/python/Tutorials/Simple_Patch_Antenna.py). The assumed dielectric constant, patch dimensions and feed location are **not optimized or validated** for a checkout tray.

It computes, when run with compatible openEMS + CSXCAD Python bindings:

- `s11.csv`: S11 (dB) versus frequency and input impedance (ohms)
- `farfield.npz`: radiation-pattern data at 866 MHz
- `s11.png`: optional S11 plot with `--plot`

## Running the solver

Install openEMS, CSXCAD and their Python bindings following [official openEMS installation instructions](https://docs.openems.de/install.html). You will also need NumPy and optionally Matplotlib. Confirm:

```sh
python -c "from openEMS import openEMS; from CSXCAD import ContinuousStructure; print('ready')"
```

Then, from the repository root:

```sh
python rf_physics/patch_866.py --output results/patch --plot
```

The default Python CI tests in this repository **do not execute openEMS**. Simulation success and physical accuracy remain unverified until this solver is installed and the results are reviewed.

## Interpret results carefully

An antenna that achieves S11 below -10 dB near 866 MHz is reasonably well matched at its feed, **not** proof that 20 tags can be detected. We must subsequently add:
1. A realistic tray and surroundings
2. Actual tag antenna geometry, chip impedance/sensitivity and polarization
3. Forward-link coupling and tag power threshold
4. Reverse-link/backscatter received-power estimates
5. Multiple tags, orientations, mutual coupling and reader inventory behavior
6. Outside-tray false-positive analysis and physical test data

The first deliverable is a reproducible **single-antenna reference**, followed by a two-antenna comparison. Neither can be ranked by the current source code alone.

## Attribution

The baseline model follows the official openEMS patch antenna tutorial, copyright Thorsten Liebig and contributors. Consult the upstream project for licensing requirements before copying or distributing derivative code.
