import sys
import geopandas as gpd
import pandas as pd
from util import print_df

df = pd.read_csv(sys.argv[1]).rename(columns={"lon": "Lon", "lat": "Lat"})
df = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.Lon, df.Lat), crs="EPSG:4326"
)
geo = gpd.read_file(sys.argv[2])
df = df.to_crs("EPSG:4326")
geo = geo.to_crs("EPSG:4326")
gdf = gpd.sjoin(df, geo, how="left", op="within")
assert len(gdf[gdf.geometry.isna()]) == 0
print_df(gdf)
