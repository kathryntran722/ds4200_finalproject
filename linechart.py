import pandas as pd
import json

df = pd.read_excel('cancer_data.xlsx')

# --- Total studies per year ---
studies_per_year = (
    df.dropna(subset=['year'])
    .groupby('year')
    .size()
    .reset_index(name='count')
)
studies_per_year['year'] = studies_per_year['year'].astype(int)
studies_per_year = studies_per_year.sort_values('year')
studies_per_year.to_json('timeline_data.json', orient='records')

# --- All gene-year counts (D3 will filter dynamically) ---
df_genes = df.dropna(subset=['year', 'gene']).copy()
df_genes['year'] = df_genes['year'].astype(int)

gene_year = (
    df_genes.groupby(['year', 'gene'])
    .size()
    .reset_index(name='count')
    .sort_values('year')
)

gene_year.to_json('timeline_genes.json', orient='records')
print(f"timeline_data.json and timeline_genes.json exported.")