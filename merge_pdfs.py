from pathlib import Path
from pypdf import PdfWriter

fn_list = [
    Path(
        r"c:\Users\jpeacock\OneDrive - DOI\bank_card\purchase_statements\2026_aug_purchase_card_statement_peacock.pdf"
    ),
    Path(
        r"c:\Users\jpeacock\OneDrive - DOI\bank_card\travel_statements\2026_august_travel_log_peacock.pdf"
    ),
    Path(
        r"c:\Users\jpeacock\OneDrive - DOI\bank_card\purchase_card_receipts\2026\2027_aug_13_SEG_conference_registration_phelps.pdf"
    ),
    Path(
        r"c:\Users\jpeacock\OneDrive - DOI\bank_card\purchase_card_receipts\2026\2027_aug_17_SEG_conference_registration_walter.pdf"
    ),
]

save_to = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\bank_card\purchase_statements\2026_aug_purchase_gcc_peacock.pdf"
)

merger = PdfWriter()
for pdf_fn in fn_list:
    merger.append(pdf_fn)

merger.write(save_to)
merger.close()
print(f"Saved merged file to {save_to}")
