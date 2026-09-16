from mtpy import MTData

edi_01 = r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2025\EDI_Files_aurora\field_processing\st2509_combined.edi"
edi_02 = r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2025\EDI_Files_aurora\field_processing\st2510_combined.edi"

md = MTData()
md.add_station([edi_01, edi_02])
plot_list = md.station_paths[::-1]

pr = md.plot_mt_response(plot_list, plot_style="compare", fig_num=1)
