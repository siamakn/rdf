from rdflib import Graph, URIRef, Literal
from rdflib.namespace import Namespace
import networkx as nx
import matplotlib.pyplot as plt

# Defining the namespaces used in the context file. 
SCHEMA = Namespace("http://schema.org/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

# Which predicates (as qNames) you want to hide entirely:
EXCLUDE_PRED = {
    "schema1:keywords",
    "schema1:identifier",
    "dct:description",
    "schema1:dateCreated",
    "schema1:license",
    "schema1:isPartOf",
    "schema1:inLanguage",
}


# This loads the graph (single JSON-LD file and parses its content)
g = Graph()
g.parse("RDF/20220201_fairmat_tutorials_1_publishing_data_with_nomad.jsonld", format="json-ld")
print("Triple count:", len(g))

# Bind prefixes for qname()
g.bind("schema", SCHEMA)
g.bind("dct", DCTERMS)
g.bind("xsd", XSD)

#Helper functions
def get_title(res):
    title = g.value(res, DCTERMS.title) or g.value(res, SCHEMA.name)
    return str(title) if title else (g.qname(res) if isinstance(res, URIRef) else str(res))

def label_of(node):
    if isinstance(node, Literal):
        return str(node)
    # try title first, then qname
    title = g.value(node, DCTERMS.title) or g.value(node, SCHEMA.name)
    if title:
        return str(title).strip()
    if isinstance(node, URIRef):
        return g.qname(node)
    return str(node)

# Build a directed graph
G = nx.DiGraph()
for s, p, o in g:
    lp = g.qname(p)
    if lp in EXCLUDE_PRED:
        continue

    ls = label_of(s)
    lo = label_of(o)

    G.add_node(ls)
    G.add_node(lo)
    G.add_edge(ls, lo, label=lp)

# The output display
print(f"{'Resource Title':<50} {'Predicate':<20} {'Object'}")
print("-" * 90)
for s, p, o in g:
    resource_label = get_title(s)
    pred_label = g.qname(p) if isinstance(p, URIRef) else str(p)
    obj_label = get_title(o) if isinstance(o, URIRef) else str(o)
    print(f"{resource_label:<50} {pred_label:<20} {obj_label}")

# 4) Draw it
plt.figure(figsize=(12,12))
pos = nx.spring_layout(G, k=0.5, iterations=50)
nx.draw_networkx_nodes(G, pos, node_size=800, alpha=0.8)
nx.draw_networkx_labels(G, pos, font_size=9)
nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=12)
edge_labels = nx.get_edge_attributes(G, 'label')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
plt.title("RDF Graph of FAIRmat Tutorial Resource")
plt.axis('off')
plt.tight_layout()
plt.show()