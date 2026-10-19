"""866 MHz single patch antenna baseline using openEMS.

Based on the openEMS upstream Simple_Patch_Antenna tutorial (GPL-3.0).
This is an actual FDTD simulation when the openEMS Python bindings are installed,
NOT an RFID tag readability predictor. No simulated measurements are bundled.

Run: python rf_physics/patch_866.py --output results/patch
"""
import argparse
from pathlib import Path
import numpy as np
from CSXCAD import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import C0, EPS0


def run(output: Path, frequency: float = 866e6, visualize: bool = False):
    # mm units throughout. Approximate starting geometry, NOT optimized.
    # Patch length estimated for a microstrip resonator at 866 MHz.
    patch_x, patch_y = 105.0, 84.0
    board_x, board_y, h = 160.0, 140.0, 3.0
    eps_r = 3.38
    feed_x, feed_y = -22.0, 0.0
    span = 0.18 * frequency
    box = (650.0, 650.0, 450.0)
    resolution = C0 / (frequency + span) / 1e-3 / 20

    fdtd = openEMS(NrTS=40000, EndCriteria=1e-4)
    fdtd.SetGaussExcite(frequency, span)
    fdtd.SetBoundaryCond(["MUR"] * 6)
    csx = ContinuousStructure()
    fdtd.SetCSX(csx)
    mesh = csx.GetGrid()
    mesh.SetDeltaUnit(1e-3)
    mesh.AddLine("x", [-box[0]/2, box[0]/2])
    mesh.AddLine("y", [-box[1]/2, box[1]/2])
    mesh.AddLine("z", [-box[2]/3, box[2]*2/3])

    ground = csx.AddMetal("ground")
    ground.AddBox(start=[-board_x/2, -board_y/2, 0],
                  stop=[board_x/2, board_y/2, 0], priority=10)
    fdtd.AddEdges2Grid(dirs="xy", properties=ground)

    substrate = csx.AddMaterial(
        "substrate", epsilon=eps_r,
        kappa=1e-3 * 2 * np.pi * frequency * EPS0 * eps_r
    )
    substrate.AddBox(start=[-board_x/2, -board_y/2, 0],
                     stop=[board_x/2, board_y/2, h], priority=0)
    mesh.AddLine("z", np.linspace(0, h, 5))

    patch = csx.AddMetal("patch")
    patch.AddBox(start=[-patch_x/2, -patch_y/2, h],
                 stop=[patch_x/2, patch_y/2, h], priority=10)
    fdtd.AddEdges2Grid(dirs="xy", properties=patch, metal_edge_res=resolution/2)

    port = fdtd.AddLumpedPort(1, 50, [feed_x, feed_y, 0],
                             [feed_x, feed_y, h], "z", 1.0,
                             priority=5, edges2grid="xy")
    mesh.SmoothMeshLines("all", resolution, 1.4)
    nf2ff = fdtd.CreateNF2FFBox()
    output.mkdir(parents=True, exist_ok=True)
    fdtd.Run(str(output), cleanup=True, verbose=2)

    frequencies = np.linspace(frequency - span, frequency + span, 401)
    port.CalcPort(str(output), frequencies)
    s11 = 20 * np.log10(np.maximum(abs(port.uf_ref / port.uf_inc), 1e-15))
    impedance = port.uf_tot / port.if_tot
    np.savetxt(output / "s11.csv",
               np.column_stack([frequencies, s11, impedance.real, impedance.imag]),
               delimiter=",", comments="",
               header="frequency_hz,s11_db,zin_real_ohm,zin_imag_ohm")
    center = int(np.argmin(abs(frequencies - frequency)))
    print(f"S11 at {frequency/1e6:.0f} MHz: {s11[center]:.2f} dB")
    best = int(np.argmin(s11))
    print(f"Minimum S11: {s11[best]:.2f} dB at {frequencies[best]/1e6:.2f} MHz")
    # Far-field of the baseline antenna at requested frequency (not tag read success).
    angles = np.arange(-180., 180., 2.)
    ff = nf2ff.CalcNF2FF(str(output), frequency, angles, [0., 90.],
                         center=[0, 0, 1e-3])
    np.savez(output / "farfield.npz",
             theta_deg=angles, E_norm=ff.E_norm, Dmax=ff.Dmax)
    print("Saved s11.csv and farfield.npz to", output)
    if visualize:
        import matplotlib.pyplot as plt
        plt.plot(frequencies / 1e6, s11)
        plt.xlabel("Frequency (MHz)")
        plt.ylabel("S11 (dB)")
        plt.grid(True)
        plt.savefig(output / "s11.png", dpi=150)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/patch"))
    parser.add_argument("--frequency-mhz", type=float, default=866.)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    run(args.output, args.frequency_mhz * 1e6, args.plot)
