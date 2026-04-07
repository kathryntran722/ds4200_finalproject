import pandas as pd
import json

df = pd.read_excel('cancer_data.xlsx')

# Print unique continent values so we can verify spelling
print(df['continent'].value_counts())

# Count studies per continent, drop missing
continent_counts = (
    df.dropna(subset=['continent'])
    .groupby('continent')
    .size()
    .reset_index(name='studies')
    .sort_values('studies', ascending=False)
)

print(continent_counts)

continent_counts.to_json('map_data.json', orient='records')
print("\nmap_data.json exported.")