"""
Scatter Plot: Publication Year vs. Confirmed Associations per Cancer Phenotype
Requires: pip install altair pandas openpyxl

Run: python Scatter.py
Outputs: scatter_cancer.html
"""

import pandas as pd
import altair as alt

# Load and filter data
df = pd.read_excel("cancer_data.xlsx")
df = df[df["association"] == "Y"].dropna(subset=["year"]).copy()
df["year"] = df["year"].astype(int)

# Keep top 6 phenotypes only so trend lines are stable and readable
top_phenotypes = df["phenotype"].value_counts().head(6).index.tolist()
df = df[df["phenotype"].isin(top_phenotypes)]

# Aggregate count of confirmed associations per year and phenotype
agg = (
    df.groupby(["year", "phenotype"])
    .size()
    .reset_index(name="associations")
)

# Colour scale
color_scale = alt.Scale(
    domain=["breast cancer", "prostate cancer", "lung cancer",
            "colorectal cancer", "stomach cancer", "bladder cancer"],
    range=["#e57373", "#7986cb", "#4db6ac", "#ffa726", "#a1887f", "#90a4ae"],
)

# Selection for legend filtering
phenotype_selection = alt.selection_point(fields=["phenotype"], bind="legend")

# Scatter layer with fixed dot size, no size encoding
scatter = (
    alt.Chart(agg)
    .mark_circle(size=80, stroke="#ffffff", strokeWidth=0.5)
    .encode(
        x=alt.X(
            "year:Q",
            title="Publication Year",
            scale=alt.Scale(domain=[1986, 2008]),
            axis=alt.Axis(format="d", grid=True, gridColor="#e0e0e0", tickColor="#ccc",
                          labelColor="#555", titleColor="#333"),
        ),
        y=alt.Y(
            "associations:Q",
            title="Number of Confirmed Associations",
            axis=alt.Axis(grid=True, gridColor="#e0e0e0", tickColor="#ccc",
                          labelColor="#555", titleColor="#333"),
        ),
        color=alt.Color(
            "phenotype:N",
            title="Cancer Phenotype",
            scale=color_scale,
            legend=alt.Legend(
                orient="bottom",
                columns=3,
                labelColor="#333",
                titleColor="#333",
                symbolType="circle",
            ),
        ),
        opacity=alt.condition(phenotype_selection, alt.value(0.85), alt.value(0.08)),
        tooltip=[
            alt.Tooltip("phenotype:N", title="Phenotype"),
            alt.Tooltip("year:Q", title="Year"),
            alt.Tooltip("associations:Q", title="Confirmed Associations"),
        ],
    )
    .add_params(phenotype_selection)
)

# Polynomial trend line (order 3 captures exponential-like growth better than linear)
trend = (
    alt.Chart(agg)
    .transform_filter(phenotype_selection)
    .transform_regression(
        "year", "associations",
        groupby=["phenotype"],
        method="poly",
        order=3
    )
    .mark_line(strokeDash=[6, 4], strokeWidth=1.8, opacity=0.6)
    .encode(
        x="year:Q",
        y="associations:Q",
        color=alt.Color("phenotype:N", scale=color_scale, legend=None),
    )
)

# Combine and style
chart = (
    (scatter + trend)
    .properties(
        title=alt.TitleParams(
            text="Genetic Associations Over Time by Cancer Phenotype",
            subtitle="Confirmed gene-cancer associations (Y) · Click legend to filter · Dashed lines = polynomial trend",
            color="#333",
            subtitleColor="#666",
            fontSize=18,
            subtitleFontSize=12,
            anchor="middle",
            font="Georgia, serif",
        ),
        width=760,
        height=460,
        background="#ffffff",
    )
    .configure_view(strokeWidth=0)
    .configure_axis(
        labelFont="Open Sans, sans-serif",
        titleFont="Open Sans, sans-serif",
        domainColor="#ccc",
    )
    .configure_legend(
        labelFont="Open Sans, sans-serif",
        titleFont="Open Sans, sans-serif",
    )
)

chart.save("scatter_cancer.html")

# Inject nav and analysis block into the saved HTML
with open("scatter_cancer.html", "r") as f:
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
  <a href="sankey_cancer.html">Viz 4</a>
  <a href="scatter_cancer.html" class="active">Viz 5</a>
</nav>"""

analysis = """
<div style="padding: 0 24px 40px;">
  <div class="takeaway">
    <h3>Analysis</h3>
    <p>
      Confirmed cancer-gene associations grew steadily from the late 1980s before surging
      dramatically in the early 2000s, peaking around 2004-2006. Breast and prostate cancer
      consistently lead in total confirmed associations across the entire time period, reflecting
      the sustained research investment in these two cancer types. Lung and colorectal cancer
      show strong growth through the mid-2000s, while stomach and bladder cancer remain
      comparatively understudied throughout. The polynomial trend lines better capture the
      exponential-like growth in associations over time compared to a linear fit. Click any
      phenotype in the legend to isolate its trend.
    </p>
  </div>
</div>"""

content = content.replace("</head>\n<body>", nav, 1)
content = content.replace("</body>", analysis + "\n</body>", 1)

with open("scatter_cancer.html", "w") as f:
    f.write(content)

print("Saved: scatter_cancer.html")