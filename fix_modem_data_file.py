# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 11:21:32 2020

:author: Jared Peacock

:license: MIT

"""

from pathlib import Path

fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\modem_inv\st_sensitivity\st_1D_response.dat"
)
n = 3

with fn.open() as fid:
    lines = fid.readlines()


def fix_line(line_list):
    return " ".join("".join(line_list).replace("\n", "").split()) + "\n"


h1 = fix_line(lines[0:n])
h2 = fix_line(lines[n : 2 * n])

find = None
for index, line in enumerate(lines[2 * n + 1 :], start=2 * n + 1):
    if line.find("#") >= 0:
        find = index
        break

if find is not None:
    h3 = fix_line(lines[find : find + n])
    h4 = fix_line(lines[find + n : find + 2 * n])

    new_lines = [h1, h2] + lines[2 * n : find] + [h3, h4] + lines[find + 2 * n :]
else:
    new_lines = [h1, h2] + lines[2 * n :]

with fn.open("w") as fid:
    fid.writelines(new_lines)
