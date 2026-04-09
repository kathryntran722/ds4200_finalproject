"""
Sankey Diagram: Chromosome → Gene → Cancer Phenotype
Requires: pip install plotly pandas openpyxl

Run: python Sankey.py
Outputs: sankey_cancer.html
"""

import pandas as pd
import plotly.graph_objects as go

# ── Load & filter data ────────────────────────────────────────────────────────
df = pd.read_excel("cancer_data.xlsx")
df = df[df["association"] == "Y"].copy()

# Keep top chromosomes / genes / phenotypes to keep diagram readable
top_chroms     = df["chromosome"].value_counts().head(8).index.tolist()
top_genes      = df["gene"].value_counts().head(15).index.tolist()
top_phenotypes = df["phenotype"].value_counts().head(10).index.tolist()

df = df[
    df["chromosome"].isin(top_chroms) &
    df["gene"].isin(top_genes) &
    df["phenotype"].isin(top_phenotypes)
]

# ── Aggregate link counts ─────────────────────────────────────────────────────
chrom_gene = (
    df.groupby(["chromosome", "gene"]).size().reset_index(name="count")
)
chrom_gene["chromosome"] = "Chr " + chrom_gene["chromosome"].astype(str)

gene_pheno = (
    df.groupby(["gene", "phenotype"]).size().reset_index(name="count")
)

# ── Build node list (order: chromosomes | genes | phenotypes) ─────────────────
chroms     = sorted(chrom_gene["chromosome"].unique())
genes      = sorted(gene_pheno["gene"].unique())
phenotypes = sorted(gene_pheno["phenotype"].unique())

all_nodes = chroms + genes + phenotypes
node_idx  = {n: i for i, n in enumerate(all_nodes)}

# ── Build source / target / value lists ──────────────────────────────────────
sources, targets, values, link_labels = [], [], [], []

for _, row in chrom_gene.iterrows():
    sources.append(node_idx[row["chromosome"]])
    targets.append(node_idx[row["gene"]])
    values.append(row["count"])
    link_labels.append(f'{row["chromosome"]} → {row["gene"]}: {row["count"]} associations')

for _, row in gene_pheno.iterrows():
    sources.append(node_idx[row["gene"]])
    targets.append(node_idx[row["phenotype"]])
    values.append(row["count"])
    link_labels.append(f'{row["gene"]} → {row["phenotype"]}: {row["count"]} associations')

# ── Node colours ──────────────────────────────────────────────────────────────
chrom_colors = {
    "Chr 1":  "#4fc3f7", "Chr 2":  "#81d4fa", "Chr 7":  "#4dd0e1",
    "Chr 10": "#80cbc4", "Chr 11": "#a5d6a7", "Chr 16": "#ffcc80",
    "Chr 17": "#ef9a9a", "Chr 6":  "#ce93d8",
}
gene_colors = {
    "BRCA1":   "#e57373", "TP53":    "#ef9a9a", "EGFR":    "#f48fb1",
    "SULT1A1": "#ffcc02", "CYP17A1": "#ffa726", "CYP1B1":  "#ffb74d",
    "CCND1":   "#aed581", "GSTM1":   "#81c784", "MTHFR":   "#4db6ac",
    "MMP1":    "#4dd0e1", "NAT2":    "#80deea", "CYP1A1":  "#b2ebf2",
    "GSTT1":   "#c8e6c9", "NAT1":    "#dcedc8", "XRCC1":   "#fff9c4",
}
pheno_colors = {
    "breast cancer":     "#e57373", "prostate cancer":   "#7986cb",
    "lung cancer":       "#4db6ac", "colorectal cancer": "#ffa726",
    "stomach cancer":    "#a1887f", "bladder cancer":    "#90a4ae",
    "esophageal cancer": "#f48fb1", "cervical cancer":   "#ce93d8",
    "endometrial cancer":"#ffe082", "melanoma":          "#bcaaa4",
}

node_colors = []
for n in all_nodes:
    if n in chrom_colors:
        node_colors.append(chrom_colors[n])
    elif n in gene_colors:
        node_colors.append(gene_colors[n])
    elif n in pheno_colors:
        node_colors.append(pheno_colors[n])
    else:
        node_colors.append("#90a4ae")

# ── Build figure ──────────────────────────────────────────────────────────────
fig = go.Figure(go.Sankey(
    arrangement="snap",
    node=dict(
        pad=16,
        thickness=22,
        line=dict(color="#0d1117", width=0.5),
        label=all_nodes,
        color=node_colors,
        hovertemplate="<b>%{label}</b><br>Total flow: %{value}<extra></extra>",
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        label=link_labels,
        hovertemplate="%{label}<extra></extra>",
        color="rgba(255,255,255,0.08)",
    ),
))

fig.update_layout(
    title=dict(
        text="Chromosome → Gene → Cancer Phenotype<br>"
             "<sup>Confirmed genetic associations (Y) · Top genes & phenotypes by count</sup>",
        font=dict(size=18, color="#f0e9d6", family="Georgia, serif"),
        x=0.5,
    ),
    font=dict(size=12, color="#cdd7e4", family="Courier New, monospace"),
    paper_bgcolor="#0d1117",
    plot_bgcolor="#0d1117",
    height=660,
    margin=dict(l=20, r=20, t=90, b=20),
)

fig.write_html("sankey_cancer.html")

# ── Inject nav + analysis into the saved HTML ─────────────────────────────────
with open("sankey_cancer.html", "r") as f:
    content = f.read()

nav = """<link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>
<nav>
  <span class="nav-title">Cancer Genetics Viz</span>
  <a href="main_page.html">Home</a>
  <a href="map.html">Viz 1</a>
  <a href="linechart.html">Viz 2</a>
  <a href="barchart_phenotypes.html">Viz 3</a>
  <a href="sankey_cancer.html" class="active">Viz 4</a>
  <a href="scatter_cancer.html">Viz 5</a>
</nav>"""

analysis = """
<div style="padding: 0 24px 40px;">
  <div class="takeaway">
    <h3>Analysis</h3>
    <p>
      The Sankey diagram reveals how genetic associations flow from chromosomal locations through
      specific genes into cancer phenotypes. A small number of genes act as broad hubs connecting
      multiple chromosomes to multiple cancer types - most notably TP53 on chromosome 17, which
      links to seven distinct phenotypes including lung, breast, bladder, and cervical cancer,
      reflecting its well-established role as a tumor suppressor across cancer biology.
      SULT1A1 on chromosome 16 and CYP17A1 on chromosome 10 show similarly wide reach,
      each connecting to six or more phenotypes. In contrast, BRCA1 flows almost entirely into
      breast cancer, illustrating a gene with high association count but narrow phenotypic scope.
      Breast and prostate cancer receive the largest total inflow, consistent with their dominance
      in the broader dataset, while esophageal and cervical cancer receive relatively thin flows,
      indicating fewer confirmed genetic associations overall.
    </p>
  </div>
</div>"""

content = content.replace("</head>\n<body>", nav, 1)
content = content.replace("</body>", analysis + "\n</body>", 1)

with open("sankey_cancer.html", "w") as f:
    f.write(content)

print("Saved: sankey_cancer.html")