import collections
import numpy as np
import pandas as pd
import geopandas as gpd
import geowombat as gw
import rasterio as rio
import re
import os
from rasterio.plot import show
import pyreadr as pr
import json
from osgeo import gdal, gdal_array

# define variables
data_path = os.getcwd()
r_object = '/home/gergeli/jupyter_dir/pp_mean_2018_all_vars.R'
output_path = '/home/gergeli/Asztal/Suli/Lisbon/Soil/Extraction_test.xlsx'

# load R object
main_dataframe = pr.read_r(r_object)

# get the first item from the R object
first_item = next(iter(main_dataframe))
main_dataframe = main_dataframe[first_item]

# convert dataframe into geodataframe
gdf = gpd.GeoDataFrame(
   main_dataframe, geometry=gpd.points_from_xy(main_dataframe.X, main_dataframe.Y), crs="EPSG:3035"
   )
geometry = gdf.pop("geometry")
gdf.insert(1, "geometry", geometry)
main_dataframe = gdf

# subset data for testing
main_dataframe = main_dataframe[:200]

# get items in json
my_json = main_dataframe.to_json()
json_object = json.loads(my_json)

def main(data_path, json_object):
    
    coords = [json_object['features'][i]['geometry']['coordinates'] for i in range(len(json_object['features']))]
          
    for _, dirs, files in os.walk(data_path):
        # parse root
        y = re.search('/$', _)
        if y:
            for f in files:
                extracted = []
                x = re.search('.tif$', f)
                if x:
                    print("Extracting data from: ", _+f)
                    with gw.open(_+f) as src:
                        for c in coords:
                            x,y = c[0], c[1]
                            print(x,y)
                            j, i = gw.coords_to_indices(x, y, src)
                            print(j, i)
                            extracted.append(src[:,i, j].data.compute())
                        extracted = [x[0] for x in extracted]
                        main_dataframe[f[:-4]] = extracted
            
        else:
            # parse sub directories
            for f in files:
                extracted = []
                x = re.search('.tif$', f)
                if x:
                    print("Extracting data from: ", _+'/'+f)                        
                    with gw.open(_+'/'+f) as src:
                        for c in coords:
                            x,y = c[0], c[1]
                            print(x,y)
                            j, i = gw.coords_to_indices(x, y, src)
                            print(j, i)
                            extracted.append(src[:,i, j].data.compute())
                        extracted = [x[0] for x in extracted]
                        main_dataframe[f[:-4]] = extracted
                    
    main_dataframe.to_excel(output_path)
                        
# call main
if __name__ == '__main__':
    main(data_path, json_object)

