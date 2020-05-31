from xcube_sh.cube import open_cube
from xcube_sh.config import CubeConfig
from xcube.core.maskset import MaskSet
from osgeo import gdal, gdal_array, ogr 

import os
import json
import numpy as np 
import xarray as xr #idk where this is going to be used
import shapely.geometry
import IPython.display
import matplotlib.pyplot as plt 
import cv2 


hc = dict(client_id = '58c01991-7cd8-4685-83d8-03c239419f1d',
        client_secret= 'I1_8i,1#-iC(T_*9N]Mr{dq}7~WhvpX@?2ZE{#aC') 
# expires in 24 hours

dataset = "S2L2A"
spatial_res = 0.0009 #10m
band_names = ["B02", "B03", "B04", "B08", "B11", "SCL"]
time_period = "10D" # 10 days interval for now  
fig = [16, 10]

# few parameters 
min_rgb = 0.04
max_red = 0.15
max_green = 0.15
max_blue = 0.4
max_ndvi = 0.7 # quite high to account for mixed pixels
max_ndwi = 0.001
max_ndsi = 0.0001
min_b11 = 0.05
max_b11 = 0.55
min_green_ratio = 0.05
min_red_ratio = 0.1


#min Long, min lat, max long, min lat 
t_a = 10.00, 54.27, 11.00, 54.60 # idk what I am doing
bbox_delhi= 76.28,27.78,78.17,29.44 
bbox_lucknow = 79.92,26.16,81.60,27.53
#bbox_maha = 73.85,17.26,78.36,21.35
#bbox_maha = 74.77,17.23,77.29,19.11
#bbox_maha = 75.3051,17.1639,76.4847,18.1784
bbox_maha = 75.647654,17.437893,76.151652,17.908037
bbox_kala = 76.5829,17.0825,77.0869,17.5536
#bbox_hydra = 78.0834,16.9797,78.8822,17.7607
bbox_hydra = 77.7769,16.7221,79.1557,17.9332
bbox_vija = 79.8204,16.0397,81.1992,17.2551
bbox_patna = 84.0448,24.7575,86.1746,26.4275
bbox_ahm = 73.3273,18.1127,77.1395,21.403
bbox_nagpur = 76.85,19.49,80.66,22.75
bbox_benga = 76.35,9.49,79.03,13.91
aoi = bbox_benga
area = "benga"
'''
2019 dataset = dates[0], dates[1]
2020 dataset = dates[2], dates[3]
'''
dates = ["2019-03-01","2019-04-30","2020-03-01", "2020-04-30"] #2020
date2020 = False 
place = area 
for i in range(2):
    if (date2020 == False):
        # 2019
        data = "2019"
        date_x = dates[0]
        date_y = dates[1]
    else:
        data= "2020"
        date_x = dates[2]
        date_y = dates[3] 
    IPython.display.GeoJSON(shapely.geometry.box(*aoi).__geo_interface__)
    cube_con = CubeConfig(dataset_name = dataset,
            band_names = band_names, 
            tile_size = [512, 512],
            geometry = aoi, # area of interest
            spatial_res = spatial_res, #0.00009
            time_range = [date_x, date_y],
            time_period = time_period) # what is time tolerance

    cube = open_cube(cube_con, **hc)
    scl = MaskSet(cube.SCL) 

    #cube = cube.where((scl.clouds_high_probability) == 0) #shows weird errors
    
    cube= cube.where((scl.clouds_high_probability +
    scl.clouds_medium_probability +
    scl.clouds_low_probability_or_unclassified +                                                                                scl.cirrus) == 0)
    date = dates[0]
    t1 = cube.sel(time = cube.time[0])
    B02 = t1.B02
    B03 = t1.B03
    B04 = t1.B04
    B08 = t1.B08
    B11 = t1.B11
      
    # Compute a roads mask using band ratios and thresholds
    ndvi_mask = ((B08 - B04) / (B08 + B04)) < max_ndvi
    ndwi_mask = ((B02 - B11) / (B02 + B11)) < max_ndwi
    ndsi_mask = ((B03 - B11) / (B03 + B11)) < max_ndsi
    low_rgb_mask = (B02 > min_rgb) * (B03 > min_rgb) * (B04 > min_rgb)
    high_rgb_mask = (B02 < max_blue) * (B03 < max_green) * (B04 < max_red)
    b11_mask = ((B11 - B03) / (B11 + B03)) < max_b11
    b11_mask_abs = (B11 > min_b11) * (B11 < max_b11)
    roads_mask = ndvi_mask * ndwi_mask * ndsi_mask * low_rgb_mask * high_rgb_mask * b11_mask * b11_mask_abs

    # vehicles 
    bg_ratio = (B02 - B03) / (B02 + B03)
    br_ratio = (B02 - B04) / (B02 + B04)

    bg_low = (bg_ratio * roads_mask) > min_green_ratio 
    br_low = (br_ratio * roads_mask) > min_red_ratio
    vehicles = bg_low * br_low

    # save the data sample
    #roads_mask.plot.imshow(vmin = 0, vmax = 1, cmap = "binary", figsize = [16, 8])
    #roads_mask.to_netcdf("roads_mask_example_" + date + ".nc")

    #vehicles.plot.imshow(vmin = 0, vmax = 1, cmap = "binary", figsize = [16, 8])
    vehicles.to_netcdf("india/" + area + "/" + area + "vehicles_data" + data + ".nc")

    B02.to_netcdf("india/" + area + "/B02" + place + ".nc")
    B03.to_netcdf("india/" + area + "/B03" + place + ".nc")
    B04.to_netcdf("india/" + area + "/B04" + place + ".nc")

    # this part has to be changed or optimized
    #vehicles.plot(vmin=0, vmax=1, cmap="binary", figsize= [16,8])
    #plt.savefig("vehicles.png") 

    #roads_mask.plot(vmin=0, vmax=1, cmap="binary", figsize= [16,8])
    #real.plot(vmin=0, vmax =0.2, figsize=[16,8])
    #plt.savefig("roads.png") 
    # ends here
    if (date2020 == False):
        date2020 = True




