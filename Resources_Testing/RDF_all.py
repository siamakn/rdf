import os
import webbrowser
from rdflib import Graph, Namespace
from collections import defaultdict

# Step 1: Load RDF files
folder_path = "RDF"
g = Graph()
for filename in os.listdir(folder_path):
    if filename.endswith(".jsonld"):
        g.parse(os.path.join(folder_path, filename), format="json-ld")
print(f"\n✅ Loaded {len(g)} triples from RDF files.\n")

# Prompt user
subjects = [
    "All", "General NOMAD", "Publish", "Explore", "Analyze", "ELN", "API", "Oasis Customization",
    "Oasis Installation", "Oasis Configuration", "NOMAD Plugins", "Develop NOMAD", "NeXus",
    "General RDM", "Scientific Use Cases", "CAMELS", "NOMAD CAMELS", "NOMAD Encyclopedia", "AI"
]
levels = ["All", "Beginner", "Intermediate", "Advanced"]

print("📘 What do you want to learn today?")
for i, sub in enumerate(subjects, 1):
    print(f"{i}. {sub}")
selected_subject = subjects[int(input("\nEnter the number of your subject of interest: ")) - 1]

print("\n📗 What's your level?")
for i, lvl in enumerate(levels, 1):
    print(f"{i}. {lvl}")
selected_level = levels[int(input("\nEnter the number of your level: ")) - 1]

# Namespaces
SCHEMA = Namespace("http://schema.org/")
DCT = Namespace("http://purl.org/dc/terms/")

# Collect resource data
resource_map = {}
for s in set(g.subjects(DCT["instructionalMethod"], None)):
    title = g.value(s, DCT.title)
    link = g.value(s, SCHEMA.identifier)
    method = g.value(s, DCT.instructionalMethod)
    subjects_rdf = [str(val) for val in g.objects(s, DCT.subject)]
    levels_rdf = sorted(set(str(o) for o in g.objects(s, SCHEMA.educationalLevel)))
    keywords = sorted(set(str(o) for o in g.objects(s, SCHEMA.keywords)))
    modified = next(g.objects(s, SCHEMA.dateModified), "Unknown date")
    description = (
        next(g.objects(s, SCHEMA.description), None)
        or next(g.objects(s, DCT.description), None)
        or "No description available."
    )

    if selected_subject != "All" and selected_subject not in subjects_rdf:
        continue
    if selected_level != "All" and selected_level not in levels_rdf:
        continue

    html_id = f"desc_{hash(s)}"
    resource_map[s] = {
        "title": str(title),
        "link": str(link),
        "method": str(method),
        "levels": levels_rdf,
        "keywords": ", ".join(keywords),
        "modified": str(modified),
        "desc_id": html_id,
        "description": str(description)
    }

# Group by instructional method
resources = defaultdict(list)
for res_data in resource_map.values():
    resources[res_data["method"]].append(res_data)

# Build HTML
if not resources:
    print("\n❌ No matching resources found.")
else:
    html = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Learning Resources</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 30px; }
    h1, h2 { color: #003366; }
    ul { list-style-type: none; padding: 0; }
    li { margin-bottom: 20px; }
    .desc-box {
      display: none;
      position: fixed;
      top: 20%;
      left: 50%;
      transform: translate(-50%, -20%);
      background: #f4f4f4;
      padding: 20px;
      border: 1px solid #ccc;
      box-shadow: 0 0 10px #888;
      z-index: 10;
    }
    .overlay {
      display: none;
      position: fixed;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0, 0, 0, 0.5);
      z-index: 5;
    }
    .close-btn {
      margin-top: 10px;
      background: #003366;
      color: white;
      border: none;
      padding: 5px 10px;
      cursor: pointer;
    }
    .desc-button {
      background: #007BFF;
      color: white;
      border: none;
      padding: 5px 8px;
      margin-top: 5px;
      cursor: pointer;
    }
    .tag {
      display: inline-block;
      background: #e0e0e0;
      border-radius: 4px;
      padding: 2px 6px;
      margin: 2px;
      font-size: 0.8em;
      color: #333;
    }
  </style>
</head>
<body>
"""

    html += f"<h1>Learning Resources for '{selected_subject}' ({selected_level})</h1>\n"
    overlay_html = '<div id="overlay" class="overlay" onclick="hideAllPopups()"></div>\n'
    script_js = """
<script>
function showDesc(id) {
  document.getElementById('overlay').style.display = 'block';
  document.getElementById(id).style.display = 'block';
}
function hideAllPopups() {
  document.getElementById('overlay').style.display = 'none';
  let boxes = document.getElementsByClassName('desc-box');
  for (let b of boxes) b.style.display = 'none';
}
</script>
"""
    popup_html = ""
    for method, items in resources.items():
        html += f"<h2>{method}</h2>\n<ul>\n"
        for item in items:
            html += f"<li><strong>{item['title']}</strong><br>"
            html += f"<a href='{item['link']}' target='_blank'>{item['link']}</a><br>"
            html += f"<em>Keywords:</em> {item['keywords']}<br>"
            for level in item['levels']:
                html += f"<span class='tag'>Level: {level}</span>"
            html += f"<span class='tag'>Last Modified: {item['modified']}</span><br>"
            html += f"<button class='desc-button' onclick=\"showDesc('{item['desc_id']}')\">Description</button></li>\n"
            popup_html += f"""
<div id="{item['desc_id']}" class="desc-box">
  <p>{item['description']}</p>
  <button class="close-btn" onclick="hideAllPopups()">Close</button>
</div>
"""
        html += "</ul>\n"

    html += overlay_html + popup_html + script_js + "\n</body></html>"

    # Save and open
    output_file = "learning_resources_grouped.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n🌐 Opening results in browser: {output_file}")
    webbrowser.open(output_file)
