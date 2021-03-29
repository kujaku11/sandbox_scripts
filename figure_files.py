# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 13:54:55 2015

@author: jpeacock
"""
from pathlib import Path
import os
import subprocess


def pdf_file_reduce_size(input_fn, output_fn=None, crop=True, gs_exe="gs"):
    current_dir = Path.cwd()
    dir_path = input_fn.parent
    os.chdir(dir_path)

    fn_in = Path(input_fn.name)

    if output_fn is None:
        output_fn = f"{fn_in.stem}_small.pdf"

    if crop is True:
        fn_crop = Path(f"{fn_in.stem}_crop0.pdf")
        std_out = subprocess.check_call(["pdfcrop", str(fn_in), str(fn_crop)])
    else:
        fn_crop = fn_in

    std_out = subprocess.check_call(
        [
            gs_exe,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dDownsampleColorImages=true",
            "-dColorImageResolution=300",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_fn}",
            str(fn_crop),
        ]
    )
    if crop:
        fn_crop.unlink()
    if std_out == 0:
        print(f"converted {fn_in} to {output_fn}")
        os.chdir(current_dir)
        return output_fn

fn_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\g3_2019")
pdf_list = list(fn_path.glob("*.pdf"))
for fn in [r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\g3_2019\mp_ivanpah_basin_profiles.pdf"]:
    new_fn = pdf_file_reduce_size(Path(fn), crop=False, gs_exe="gswin64c")
