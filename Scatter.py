"""
Scatter Plot: Publication Year vs. Confirmed Associations per Cancer Phenotype
Requires: pip install altair pandas openpyxl

Run: python Scatter.py
Outputs: scatter_cancer.html
"""

import pandas as pd
import altair as alt

#  Load & filter data 
df = pd.read_excel("cancer_data.xlsx")
df = df[df["association"] == "Y"].dropna(subset=["year"]).copy()
df["year"] = df["year"].astype(int)

# All phenotypes with at least 3 data points across years
agg = (
    df.groupby(["year", "phenotype"])
    .size()
    .reset_index(name="associations")
)

# Keep phenotypes that appear in at least 5 years so trend lines are meaningful
valid_phenotypes = (
    agg.groupby("phenotype")["year"].count()
    .loc[lambda x: x >= 5]
    .index.tolist()
)
agg = agg[agg["phenotype"].isin(valid_phenotypes)]

#  Colour scale 
phenotypes = sorted(agg["phenotype"].unique().tolist())
# Use a categorical color scheme
color_scale = alt.Scale(scheme="tableau20")

#  Selection 
phenotype_selection = alt.selection_point(fields=["phenotype"], bind="legend")

#  Scatter layer — fixed dot size, no size encoding 
scatter = (
    alt.Chart(agg)
    .mark_circle(size=80, stroke="#0d1117", strokeWidth=0.5)
    .encode(
        x=alt.X(
            "year:Q",
            title="Publication Year",
            scale=alt.Scale(domain=[1986, 2008]),
            axis=alt.Axis(format="d", grid=True, gridColor="#1a2535", tickColor="#1a2535",
                          labelColor="#7a8899", titleColor="#7a8899"),
        ),
        y=alt.Y(
            "associations:Q",
            title="Number of Confirmed Associations",
            axis=alt.Axis(grid=True, gridColor="#1a2535", tickColor="#1a2535",
                          labelColor="#7a8899", titleColor="#7a8899"),
        ),
        color=alt.Color(
            "phenotype:N",
            title="Cancer Phenotype",
            scale=color_scale,
            legend=alt.Legend(
                orient="bottom",
                columns=3,
                labelColor="#cdd7e4",
                titleColor="#9aabb8",
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

#  Polynomial trend line (order=3 captures exponential-like growth) 
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

#  Combine & style 
chart = (
    (scatter + trend)
    .properties(
        title=alt.TitleParams(
            text="Genetic Associations Over Time by Cancer Phenotype",
            subtitle="Confirmed gene-cancer associations (Y) · Click legend to filter · Dashed lines = polynomial trend",
            color="#f0e9d6",
            subtitleColor="#7a8899",
            fontSize=18,
            subtitleFontSize=12,
            anchor="middle",
            font="Georgia, serif",
        ),
        width=760,
        height=460,
        background="#0d1117",
    )
    .configure_view(strokeWidth=0)
    .configure_axis(
        labelFont="Courier New, monospace",
        titleFont="Courier New, monospace",
        domainColor="#1e2d42",
    )
    .configure_legend(
        labelFont="Courier New, monospace",
        titleFont="Courier New, monospace",
    )
)

chart.save("scatter_cancer.html")

#  Inject nav + analysis into the saved HTML 
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