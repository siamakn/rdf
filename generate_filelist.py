# generate_filelist.py

import os
import json

RDF_DIR = "RDF"
OUTPUT_FILE = os.path.join(RDF_DIR, "filelist.json")

def main():
    files = [
        f for f in os.listdir(RDF_DIR)
        if f.endswith(".jsonld") and os.path.isfile(os.path.join(RDF_DIR, f))
    ]
    with open(OUTPUT_FILE, "w") as out:
        json.dump(files, out, indent=2)
    print(f"Generated {OUTPUT_FILE} with {len(files)} entries.")

if __name__ == "__main__":
    main()
