# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 10:50:23 2021

@author: jpeacock
"""
from pathlib import Path
from mtpy.modeling.modem import Data
from mtpy.core.mt_collection import MTCollection

dfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\canv_01\canv_modem_data_z03_t02_edit_08.dat"
efn = r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\all_mt_stations_20211029.csv"

new_stations = [
    "DVAMT-D2",
    "DVAMT-E2",
    "DVAMT-E4",
    "DVAMT-F3",
    "DVAMT-F5",
    "DVAMT-F7",
    "DVAMT-E7",
]

mc = MTCollection()
mc.from_csv(efn)

east_mc = mc.apply_bbox(-113.4389401, -109.3266592, 32.7413942, 44.0)
# need to remove the Forge sites for now
frg_avg_sites = [
    "frg110",
    "frg111",
    "frg112",
    "frg113",
    "frg115",
    "frg116",
    "frg117",
    "frg118",
    "frg119",
    "frg120",
    "frg121",
    "frg122",
    "frg123",
    "frg124",
    "frg125",
    "frg126",
    "frg127",
    "frg128",
    "frg129",
    "frg130",
    "frg131",
    "frg132",
    "frg133",
    "frg137",
    "frg138",
    "frg139",
    "frg140",
    "frg141",
    "frg142",
    "frg143",
    "frg144",
    "frg145",
    "frg146",
    "frg147",
    "frg148",
    "frg149",
    "frg150",
    "frg151",
    "frg152",
    "frg153",
    "frg154",
    "frg155",
    "frg156",
    "frg157",
    "frg158",
    "frg159",
    "frg160",
    "frg161",
    "frg162",
    "frg163",
    "frg164",
    "frg165",
    "frg166",
    "frg167",
    "frg168",
    "frg169",
    "frg170",
    "frg171",
    "frg172",
    "frg173",
    "frg174",
    "frg175",
    "frg176",
    "frg177",
    "frg178",
    "frg179",
    "frg180",
    "frg181",
    "frg182",
    "frg183",
    "frg184",
    "frg185",
    "frg186",
    "frg187",
    "frg188",
    "frg189",
    "frg190",
    "frg191",
    "frg192",
    "frg193",
    "frg194",
    "frg195",
    "frg196",
    "frg197",
    "frg198",
    "frg199",
    "frg200",
    "frg201",
    "frg202",
    "frg203",
    "frg204",
    "frg205",
    "frg206",
    "frg207",
    "frg208",
    "frg209",
    "frg210",
    "frg211",
    "frg212",
    "frg213",
    "frg214",
    "frg215",
    "frg216",
    "frg217",
    "frg218",
    "frg219",
    "frg220",
    "frg221",
]

east_mc = east_mc.dataframe.query("ID not in @frg_avg_sites")

# add average files
avg_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\canv_01\new_edis"
)
fn_list = [avg_path.joinpath(f"AVG{ii}.edi") for ii in range(215, 225)]

# add all the eastern files
fn_list += east_mc.fn.to_list()

new_df = mc.dataframe.query("ID in @new_stations")
fn_list += new_df.fn.to_list()


d = Data()
d.read_data_file(dfn)
d.error_value_z = 3.0
d.error_type_tipper = "abs_floor"
d.error_value_tipper = 0.02

d.data_array, d.mt_dict = d.add_station(fn_list)

d.write_data_file(
    fn_basename="gb_modem_data_z03_t02.dat",
    save_path=r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\gb_01",
    compute_error=False,
    fill=False,
)
