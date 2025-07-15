# NOMAD Training Resources

This is a lightweight, static web application to explore and filter NOMAD training resources using RDF/JSON-LD metadata. It supports dynamic filtering, structured metadata display, and is deployable via GitHub Pages.

### To add or update resources:

1. Place your update or new JSON-LD files in `data/`.
2. Run:

```bash
python convert.py
python generate_filelist.py
```