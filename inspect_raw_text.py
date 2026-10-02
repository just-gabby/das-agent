from pathlib import Path
from pypdf import PdfReader

policy_folder = Path("/Users/netadmin/Documents/AI/Datasets/PolicyLibrary")

print(f"Looking in: {policy_folder.resolve()}", flush=True)
print(f"Folder exists: {policy_folder.exists()}", flush=True)

pdf_files = list(policy_folder.rglob("*.pdf"))
print(f"PDF files found: {len(pdf_files)}", flush=True)
for f in pdf_files:
    print(f"  - {f}", flush=True)
print(flush=True)

for pdf_path in pdf_files:
    print(f"Reading {pdf_path.name}...", flush=True)
    reader = PdfReader(pdf_path)
    full_text = ""
    for page_number, page in enumerate(reader.pages, start=1):
        full_text += page.extract_text() or ""
        if page_number % 10 == 0:
            print(f"  ...processed {page_number} pages so far", flush=True)

    print(f"=== {pdf_path.name} done — {len(full_text)} characters extracted ===", flush=True)

    if "H9" in full_text:
        index = full_text.find("H9")
        print("Found exact 'H9':")
        print(repr(full_text[max(0, index - 100):index + 300]))
    elif "H 9" in full_text:
        index = full_text.find("H 9")
        print("Found 'H 9' WITH A SPACE (likely a PDF extraction quirk):")
        print(repr(full_text[max(0, index - 100):index + 300]))
    else:
        print("'H9' not found in any form. First 500 characters, for a sanity check:")
        print(repr(full_text[:500]))
    print()