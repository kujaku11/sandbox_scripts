# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 17:14:04 2017

@author: jpeacock
"""
from pathlib import Path
import numpy as np
import mtpy.imaging.mtplot as mtplot

original_dir = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\EDI_Files_birrp\Edited\Geographic"
)
phase1_dir = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\EDI_files_birrp_processed\Geographic\Edited"
)
save_dir = Path(r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\Reports")

f1 = []
f2 = []
for fn1 in original_dir.glob("*.edi"):
    for fn2 in phase1_dir.glob("*.edi"):
        if f"3{fn1.stem[-2:]}" == fn2.stem[2:]:
            f1.append(fn1)
            f2.append(fn2)
            # pmr = mtplot.plot_multiple_mt_responses(
            #     fn_list=[fn1, fn2], plot_style="compare", plot_pt="y"
            # )
            # pmr.fig.savefig(
            #     save_dir.joinpath(f"{fn1.stem}_compare.png"), dpi=300,
            # )
            # mtplot.plotnresponses.plt.close("all")
            break

rpt = mtplot.plot_residual_pt_maps(f1, f2, frequencies=np.logspace(-3, 3, 40))
