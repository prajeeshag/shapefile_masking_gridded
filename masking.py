import xarray as xr
import geopandas as gpd
import pandas as pd
from cartopy.io import shapereader
from shapely.geometry.polygon import Point
import matplotlib.pyplot as plt
import numpy as np

# Load the NetCDF dataset
dataset = xr.open_dataset('out.nc')

lat = dataset['XLAT'][0,:,:].squeeze().values
lon = dataset['XLONG'][0,:,:].squeeze().values

nx = lon.shape[0]
ny = lon.shape[1]

xlon = lon.reshape(nx*ny)
xlat = lat.reshape(nx*ny)

df = pd.DataFrame({'lon':xlon, 'lat':xlat})
df['coords'] = list(zip(df['lon'],df['lat']))
df['coords'] = df['coords'].apply(Point)
#shapefile = gpd.read_file('SAU_adm0.shp')

# request data for use by geopandas
resolution = '10m'
category = 'cultural'
name = 'admin_0_countries'

shpfilename = shapereader.natural_earth(resolution, category, name)
shapefile = gpd.read_file(shpfilename)

# get geometry of a country
rdf = shapefile.loc[shapefile['ADMIN'] == 'Saudi Arabia']

points = gpd.GeoDataFrame(df, geometry='coords', crs=rdf.crs)

# Perform spatial join to match points and polygons
pointInPolys = gpd.tools.sjoin(points, rdf, predicate="within", how='left')

xmask = np.where(pointInPolys.NAME=="Saudi Arabia",1,0) 

mask = xmask.reshape([nx,ny])

da = xr.DataArray(mask, coords={'lat': (('x', 'y'), lat), 'lon': (('x', 'y'), lon)}, dims=['x', 'y'])
da.to_netcdf('mask.nc')

da.plot()

plt.savefig('test.png')