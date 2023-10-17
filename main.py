import pandas as pd
import geopandas as gpd
import json
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import numpy as np

uhf = pd.read_csv('uhf.csv')
GeoID_list_new = []
Geography_list = []
AvgRate_list = []
Difference_list = []  # List to store the difference metric
years = [2005]
GeoId_list = [101, 102, 103, 104, 105, 106, 107,
              201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211,
              301, 302, 303, 304, 305, 306, 307, 308, 309, 310,
              401, 402, 403, 404, 405, 406, 407, 408, 409, 410,
              501, 502, 503, 504]
Geoplot = [201,206,402,403]


def safe_convert(val):
    try:
        return float(val.replace('*', ''))
    except:
        return None


def get_TN_summar(uhf):
    global max_TN
    global max_N5
    uhf = uhf[uhf['Time'] >= years[0]]
    print("\nthe Total number of tests sorted by GeoID")
    total_tests_by_geo = uhf.groupby(['GeoID'])['TN'].sum().reset_index()
    TN_ordered = total_tests_by_geo.sort_values(by='TN', ascending=False)
    print(TN_ordered.head(42))
    print("\nthe Total N5+ Rates sorted by GeoID")
    total_cases_by_geo = uhf.groupby(['GeoID'])['N5+'].sum().reset_index()
    N5_ordered = total_cases_by_geo.sort_values(by='N5+', ascending=False)
    print(N5_ordered.head(42))
    max_TN = uhf['TN'].max()
    max_N5 = uhf['N5+'].max()
    return


uhf['N5+'] = uhf['N5+'].apply(safe_convert)
get_TN_summar(uhf)

for year in years:
    print("The Average Rate of 5+ since:", year)
    for i in GeoId_list:
        df = uhf[uhf['GeoID'] == i]
        df = df[df['Time'] >= year]
        avgRate = df['N5+'].mean()
        df['TN'] = df['TN'] / max_TN
        df['N5+'] = df['N5+'] / max_N5
        GeoID_list_new.append(i)
        Geography_list.append(df['Geography'].iloc[0] if not df.empty else None)
        AvgRate_list.append(avgRate)

        # Calculate the difference between normalized TN and normalized N5+
        difference = df['TN'].mean() - df['N5+'].mean()
        Difference_list.append(difference)

        if i in Geoplot and year > 2004:
            plt.figure(figsize=(10, 5))
            plt.plot(df['Time'], df['N5+'], label='N5+', color='blue', marker='o')
            plt.plot(df['Time'], df['TN'], label='TN', color='red', marker='x')
            plt.title(f'GeoID {i} - Time vs. N5+ & TN for since {year}')
            plt.xlabel('Time')
            plt.ylabel('Normalized Value')
            plt.legend()
            plt.ylim(0, 1.1)
            plt.grid(True)
            plt.show()

# Create new DataFrame based on AvgRate and Difference
df_new = pd.DataFrame({
    'GeoID': GeoID_list_new,
    'Geography': Geography_list,
    'AvgRate': AvgRate_list,
    'Difference': Difference_list  # Add the Difference metric to the DataFrame
})

# Sort DataFrame by Difference in descending order
# Normalize the Difference values to the range [0, 1]
scaler = MinMaxScaler(feature_range=(-1, 1))
df_new['Difference'] = scaler.fit_transform(np.array(df_new['Difference']).reshape(-1, 1))
df_new = df_new.sort_values(by='AvgRate', ascending=False)
print(df_new.head(42))

# -------------maps
cmap = plt.cm.RdBu
# Assuming you have a GeoDataFrame of NYC ZIP code geometries (replace with actual path)
nyc_uhf_shapes = gpd.read_file("UHF42.geo.json")
print(nyc_uhf_shapes.columns)

# Merge the data with the GeoDataFrame based on ZIP codes
merged_data = nyc_uhf_shapes.merge(df_new, left_on="GEOCODE", right_on="GeoID")
# Create a choropleth map
fig, ax = plt.subplots(1, figsize=(10, 10))
merged_data.plot(column="Difference", cmap=cmap, linewidth=0.8, ax=ax, edgecolor="0.8", legend=True)

# Customize the map (title, legend, etc.)
ax.set_title("The most overtested areas (Ranked by Difference)")
ax.set_axis_off()  # Turn off axis
plt.tight_layout()

# Save or display the map
plt.savefig("nyc_choropleth_difference.png")
plt.show()
