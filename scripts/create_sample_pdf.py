
from pathlib import Path

import pymupdf


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PDF_DIRECTORY = PROJECT_ROOT / "data" / "pdfs"
PDF_PATH = PDF_DIRECTORY / "product_guide.pdf"


def create_sample_pdf():
    PDF_DIRECTORY.mkdir(parents=True, exist_ok=True)

    document = pymupdf.open()

    # Page 1
    page = document.new_page()
    page.insert_text((72, 72), "PRODUCT GUIDE", fontsize=20)
    page.insert_text((72, 120), "Product: Smart Water Bottle", fontsize=14)
    page.insert_text(
        (72, 155),
        "Features: Tracks water consumption throughout the day.",
        fontsize=11,
    )
    page.insert_text(
        (72, 190),
        "Usage: Charge the device before first use.",
        fontsize=11,
    )

    # Page 2
    page = document.new_page()
    page.insert_text((72, 72), "TROUBLESHOOTING", fontsize=20)
    page.insert_text(
        (72, 120),
        "If the display does not turn on, charge the device and try again.",
        fontsize=11,
    )
    page.insert_text(
        (72, 160),
        "Warranty: The product includes a one-year limited warranty.",
        fontsize=11,
    )

    document.save(PDF_PATH)
    document.close()

    print(f"Sample PDF created successfully:\n{PDF_PATH}")


if __name__ == "__main__":
    create_sample_pdf()
