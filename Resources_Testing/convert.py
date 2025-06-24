# This script merges the context file to each resource file

import os
import json
from pyld import jsonld

# === CONFIGURATION ===
BASE_PATH = "/home/siamak/workspace/github_repos/rdf_project/rdf/Resources_Testing"
SOURCE_FOLDER = os.path.join(BASE_PATH, "data")
TARGET_FOLDER = os.path.join(BASE_PATH, "RDF")
CONTEXT_FILE = os.path.join(BASE_PATH, "context", "context.jsonld")

# Make sure output folder exists
os.makedirs(TARGET_FOLDER, exist_ok=True)

# Load your inline @context
with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
    ctx_doc = json.load(f)
    inline_ctx = ctx_doc.get("@context")
    if not inline_ctx:
        raise ValueError("❌ context.jsonld doesn’t contain an @context key")

# Process files
for fn in os.listdir(SOURCE_FOLDER):
    if not fn.endswith(".jsonld"):
        continue

    src = os.path.join(SOURCE_FOLDER, fn)
    dst = os.path.join(TARGET_FOLDER, fn)

    try:
        with open(src, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)

        # force the inline context
        data["@context"] = inline_ctx

        # expand & compact
        expanded = jsonld.expand(data)
        compacted = jsonld.compact(expanded, inline_ctx)

        # write result
        with open(dst, "w", encoding="utf-8") as out:
            json.dump(compacted, out, indent=2, ensure_ascii=False)

        print(f"✅ Processed: {fn}")

    except Exception as e:
        print(f"❌ Error processing {fn}: {e}")
