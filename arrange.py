"""Copies the chapter PDFs from the repo root into www/pdfs/ under the names the app expects.

Two editions, matched by the letter + two digits the file name starts with (rest of the name is free):
  New NCERT (rationalised, 19 chapters + 2 lab manuals):  N01 ... N21   e.g. "N05_Thermodynamics.pdf"
  Old NCERT (full older books, 30 chapters): O01 ... O30   e.g. "O12_Organic_Chemistry.pdf"
Chapters are numbered continuously across Class 11 and Class 12 inside each edition (see CHAPTERS below)."""
import glob, os, re, shutil

CHAPTERS = [  # (edition, number, expected name)
    ("new", 1, "new-01-some-basic-concepts-of-chemistry"),  # Class 11 Some Basic Concepts of Chemistry
    ("new", 2, "new-02-structure-of-atom"),  # Class 11 Structure of Atom
    ("new", 3, "new-03-classification-of-elements-and-periodicity-in-properties"),  # Class 11 Classification of Elements and Periodicity in Properties
    ("new", 4, "new-04-chemical-bonding-and-molecular-structure"),  # Class 11 Chemical Bonding and Molecular Structure
    ("new", 5, "new-05-thermodynamics"),  # Class 11 Thermodynamics
    ("new", 6, "new-06-equilibrium"),  # Class 11 Equilibrium
    ("new", 7, "new-07-redox-reactions"),  # Class 11 Redox Reactions
    ("new", 8, "new-08-organic-chemistry-some-basic-principles-and-techniques"),  # Class 11 Organic Chemistry: Some Basic Principles and Techniques
    ("new", 9, "new-09-hydrocarbons"),  # Class 11 Hydrocarbons
    ("new", 10, "new-10-solutions"),  # Class 12 Solutions
    ("new", 11, "new-11-electrochemistry"),  # Class 12 Electrochemistry
    ("new", 12, "new-12-chemical-kinetics"),  # Class 12 Chemical Kinetics
    ("new", 13, "new-13-the-d-and-f-block-elements"),  # Class 12 The d- and f-Block Elements
    ("new", 14, "new-14-coordination-compounds"),  # Class 12 Coordination Compounds
    ("new", 15, "new-15-haloalkanes-and-haloarenes"),  # Class 12 Haloalkanes and Haloarenes
    ("new", 16, "new-16-alcohols-phenols-and-ethers"),  # Class 12 Alcohols, Phenols and Ethers
    ("new", 17, "new-17-aldehydes-ketones-and-carboxylic-acids"),  # Class 12 Aldehydes, Ketones and Carboxylic Acids
    ("new", 18, "new-18-amines"),  # Class 12 Amines
    ("new", 19, "new-19-biomolecules"),  # Class 12 Biomolecules
    ("new", 20, "new-20-experimental-chemistry-class-11"),  # Lab manual Class 11
    ("new", 21, "new-21-experimental-chemistry-class-12"),  # Lab manual Class 12
    ("old", 1, "old-01-some-basic-concepts-of-chemistry"),  # Class 11 Some Basic Concepts of Chemistry
    ("old", 2, "old-02-structure-of-atom"),  # Class 11 Structure of Atom
    ("old", 3, "old-03-classification-of-elements-and-periodicity-in-properties"),  # Class 11 Classification of Elements and Periodicity in Properties
    ("old", 4, "old-04-chemical-bonding-and-molecular-structure"),  # Class 11 Chemical Bonding and Molecular Structure
    ("old", 5, "old-05-states-of-matter"),  # Class 11 States of Matter
    ("old", 6, "old-06-thermodynamics"),  # Class 11 Thermodynamics
    ("old", 7, "old-07-equilibrium"),  # Class 11 Equilibrium
    ("old", 8, "old-08-redox-reactions"),  # Class 11 Redox Reactions
    ("old", 9, "old-09-hydrogen"),  # Class 11 Hydrogen
    ("old", 10, "old-10-the-s-block-elements"),  # Class 11 The s-Block Elements
    ("old", 11, "old-11-the-p-block-elements-group-13-and-14"),  # Class 11 The p-Block Elements (Group 13 and 14)
    ("old", 12, "old-12-organic-chemistry-some-basic-principles-and-techniques"),  # Class 11 Organic Chemistry: Some Basic Principles and Techniques
    ("old", 13, "old-13-hydrocarbons"),  # Class 11 Hydrocarbons
    ("old", 14, "old-14-environmental-chemistry"),  # Class 11 Environmental Chemistry
    ("old", 15, "old-15-the-solid-state"),  # Class 12 The Solid State
    ("old", 16, "old-16-solutions"),  # Class 12 Solutions
    ("old", 17, "old-17-electrochemistry"),  # Class 12 Electrochemistry
    ("old", 18, "old-18-chemical-kinetics"),  # Class 12 Chemical Kinetics
    ("old", 19, "old-19-surface-chemistry"),  # Class 12 Surface Chemistry
    ("old", 20, "old-20-general-principles-and-processes-of-isolation-of-elements"),  # Class 12 General Principles and Processes of Isolation of Elements
    ("old", 21, "old-21-the-p-block-elements-group-15-to-18"),  # Class 12 The p-Block Elements (Group 15 to 18)
    ("old", 22, "old-22-the-d-and-f-block-elements"),  # Class 12 The d- and f-Block Elements
    ("old", 23, "old-23-coordination-compounds"),  # Class 12 Coordination Compounds
    ("old", 24, "old-24-haloalkanes-and-haloarenes"),  # Class 12 Haloalkanes and Haloarenes
    ("old", 25, "old-25-alcohols-phenols-and-ethers"),  # Class 12 Alcohols, Phenols and Ethers
    ("old", 26, "old-26-aldehydes-ketones-and-carboxylic-acids"),  # Class 12 Aldehydes, Ketones and Carboxylic Acids
    ("old", 27, "old-27-amines"),  # Class 12 Amines
    ("old", 28, "old-28-biomolecules"),  # Class 12 Biomolecules
    ("old", 29, "old-29-polymers"),  # Class 12 Polymers
    ("old", 30, "old-30-chemistry-in-everyday-life"),  # Class 12 Chemistry in Everyday Life
]

os.makedirs("www/pdfs", exist_ok=True)
pdfs = sorted(glob.glob("*.pdf"))
print("PDFs found in repo root:", len(pdfs))
for p in pdfs: print("  -", p)

missing = []
for ed, n, name in CHAPTERS:
    dst = f"www/pdfs/{name}.pdf"
    letter = "N" if ed == "new" else "O"
    exact = f"{name}.pdf"
    src = exact if exact in pdfs else None
    if not src:
        hits = [p for p in pdfs if re.match(r"\s*%s[-_ .]?0*%d(?!\d)" % (letter, n), p, re.I)]
        src = hits[0] if hits else None
    if src:
        shutil.copyfile(src, dst)
        print(f"{ed} {n:02d} -> {src}")
    else:
        missing.append(f"{ed}-{n:02d}")
        print(f"::warning::{ed} chapter {n:02d}: no matching PDF found")
# Old NCERT chapters whose PDF is not uploaded yet but whose content is the same in the new NCERT:
# the Old chapter opens the New chapter's PDF (no duplicate file in the APK). Upload the real O-file and it is used instead.
OLD_TO_NEW = {1: 1, 2: 2, 3: 3, 4: 4, 6: 5, 7: 6, 8: 7, 12: 8, 13: 9, 16: 10, 17: 11, 18: 12,
              22: 13, 23: 14, 24: 15, 25: 16, 26: 17, 27: 18, 28: 19}
names = {(ed, n): name for ed, n, name in CHAPTERS}
INDEX = "www/index.html"
if missing and os.path.exists(INDEX):
    html = open(INDEX, encoding="utf-8").read()
    for m in list(missing):
        ed, n = m.split("-"); n = int(n)
        if ed == "old" and n in OLD_TO_NEW:
            old_name, new_name = names[("old", n)], names[("new", OLD_TO_NEW[n])]
            if os.path.exists(f"www/pdfs/{new_name}.pdf") and f"pdfs/{old_name}.pdf" in html:
                html = html.replace(f"pdfs/{old_name}.pdf", f"pdfs/{new_name}.pdf")
                missing.remove(m)
                print(f"old {n:02d} -> uses new NCERT chapter {OLD_TO_NEW[n]:02d} PDF")
    open(INDEX, "w", encoding="utf-8").write(html)
if missing:
    print("Chapters without a PDF:", missing)
