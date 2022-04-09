# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 13:42:35 2021

@author: jpeacock
"""

from pathlib import Path
from scipy import signal
from matplotlib import pyplot as plt
from mtpy.usgs import zen

save_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\Reports")
# fn_stem = r"d:\WD SmartWare.swstor\IGSWMBWGLTGG032\Volume.b5634234.da89.11e2.aa2b.806e6f6e6963\MT\GZ2021\gz307\gz307_20210414_214517_256_"
fn_stem = r"d:\WD SmartWare.swstor\IGSWMBWGLTGG032\Volume.b5634234.da89.11e2.aa2b.806e6f6e6963\MT\GZ2021\gz331\gz331_20210415_131018_256_"
# fn_stem = r"d:\WD SmartWare.swstor\IGSWMBWGLTGG032\Volume.b5634234.da89.11e2.aa2b.806e6f6e6963\MT\GZ2021\gz330\gz330_20210416_010018_4096_"

comps = ["ex", "ey", "hx", "hy"]
colors = [
    (28 / 255, 146 / 255, 205 / 255),
    (28 / 255, 52 / 255, 205 / 255),
    (203 / 255, 158 / 255, 33 / 255),
    (203 / 255, 61 / 255, 33 / 255),
]
fig = plt.figure(1, dpi=150)
fig.clf()
ax = fig.add_subplot(1, 1, 1)
p_dict = {"fs": 256, "nperseg": 2 ** 13}
line_list = []
for ii, comp, c in zip(range(len(comps)), comps, colors):
    fn = Path(f"{fn_stem}{comp.upper()}.Z3D")
    z1 = zen.Zen3D(fn)
    z1.read_z3d()
    z1.apply_adaptive_notch_filter()

    b = z1.plot_spectrogram(plot_type="all")
    b.save_figure(save_path.joinpath(f"{fn.stem}.png").as_posix(), fig_dpi=150)

    f, p = signal.welch(z1.ts_obj.ts.data, **p_dict)
    (l1,) = ax.loglog(f, p, lw=1.75, color=c)
    l1.label = comp.capitalize()
    line_list.append(l1)


ax.set_xlabel("Frequency (Hz)", fontdict={"size": 10, "weight": "bold"})
ax.set_ylabel("Power (dB)", fontdict={"size": 10, "weight": "bold"})
ax.axis("tight")
ax.grid(which="both")
ax.legend(line_list, comps, loc="upper right")


plt.show()
fig.savefig(save_path.joinpath(f"{fn.stem[0:5]}_256_spectra.png"), dpi=300)
