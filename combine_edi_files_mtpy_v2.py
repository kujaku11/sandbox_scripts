from mtpy import MT

merge_dict = {
    256: {"period_min": 1.0 / 7.9, "period_max": 100},
    1: {"period_min": 100, "period_max": 10000},
    4096: {"period_min": 1.0 / 2048, "period_max": 1.0 / 8},
}

station = "sg2608"

m1 = MT()
m1.read(
    rf"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2026\mth5\EDI_Files_aurora\{station}.edi"
)

m2 = MT()
m2.read(
    rf"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2026\mth5\EDI_Files_aurora_1\{station}.edi"
)


m1.merge(
    [
        {
            "tf": m2,
            "period_min": merge_dict[1]["period_min"],
            "period_max": merge_dict[1]["period_max"],
        }
    ],
    period_max=101,
    inplace=True,
)
p1 = m1.plot_mt_response(plot_num=2)
p1.save_plot(
    rf"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2026\mth5\EDI_Files_aurora\{station}_c.png"
)
m1.write(
    rf"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2026\mth5\EDI_Files_aurora\{station}_c.edi"
)

