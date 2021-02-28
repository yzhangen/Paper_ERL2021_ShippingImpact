import pandas as pd
import numpy as np
import xarray as xr
import time
import os
import io

# for python3 using cartopy to plot pcolormesh
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.axes import Axes
from cartopy.mpl.geoaxes import GeoAxes
GeoAxes._pcolormesh_patched = Axes.pcolormesh
import matplotlib.colors as colors
from matplotlib.colors import LogNorm
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter



def f1_create_new_folder (u_path): #using
    if os.path.isdir(u_path):
        pass
    else:
        os.makedirs(u_path)
    return


def f1_read_select_columns_to_df(u_file,u_column_list):
    u_df0 = pd.read_csv(u_file, index_col=None, header=0, usecols=u_column_list, dtype='object')
    return u_df0


def f5_xr_full_lat_lon(u_lat_name,u_lat_low,u_lat_up,u_lat_step,u_lat_digit,
                       u_lon_name,u_lon_low,u_lon_up,u_lon_step,u_lon_digit):
    u_lat_data=np.arange(u_lat_low,u_lat_up,u_lat_step)
    u_lon_data=np.arange(u_lon_low,u_lon_up,u_lon_step)
    u_lat_data = np.around(u_lat_data, decimals=u_lat_digit)
    u_lon_data = np.around(u_lon_data, decimals=u_lon_digit)
    u_full = xr.Dataset({u_lat_name:u_lat_data, u_lon_name:u_lon_data})
    return u_full
    # return a full xarray with continuous latitude, longitude, without z values

    
def transform_csv_nc_full(u_df0,u_xr_xy,u_lat_name,u_lon_name,u_res,u_geo_add):# u_res=2,u_geo_add=0.005 if 0.01 degree
    u_cms = u_df0.columns.tolist() 
    u_df0[[u_lat_name,u_lon_name]] = u_df0[[u_lat_name,u_lon_name]].astype(float)
    u_df0[[u_lat_name,u_lon_name]] = u_df0[[u_lat_name,u_lon_name]].round(u_res)
    u_df1 = u_df0.groupby([u_lat_name,u_lon_name]).sum()
    # transform emission dataframe to xarray
    u_em = xr.Dataset.from_dataframe(u_df1)
    # merge emission xarray to the grid xarray, change lat-lon coordinate vlaues (avoid border)
    u_c1 = u_xr_xy.merge(u_em, join='left')
    u_c1 = u_c1.assign_coords(Latitude=(u_c1.Latitude + u_geo_add)) 
    u_c1 = u_c1.assign_coords(Longitude=(u_c1.Longitude + u_geo_add))
    #u_c2.to_netcdf(u_output_dir+u_filename+'.nc')
    return u_c1


def plot_em_global_tonnes(u_title, u_file_output,u_data,u_pl):
#    u_title = ''
    cbar_label = 'kg/' + 'km\u00b2'
    u_res_text = 'Resolution: 1 degree x 1 degree lat-lon'
    u_color = 'jet' #'YlOrBr' #'hot_r' #'jet'
    fig_w, fig_h = 12, 16
    x_min, x_max, x_step = -180, 181, 60
    y_min, y_max, y_step = -90, 91, 45
    u_pl_min, u_pl_max = 10,100000
    
    fig, ax = plt.subplots(1,1,figsize=(fig_w, fig_h),subplot_kw={"projection": ccrs.PlateCarree()})
    u_data_pl = u_data[u_pl].fillna(u_pl_min)
    em = u_data_pl.plot.pcolormesh(ax=ax,norm=colors.LogNorm(vmin=u_pl_min, vmax=u_pl_max), cmap=u_color,add_colorbar=False,
                                xticks=np.arange(x_min, x_max,step=x_step),yticks=np.arange(y_min,y_max,step=y_step))
    cax = fig.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])
    cb = plt.colorbar(em, cax=cax, extend='both')
    cb.ax.set_title(cbar_label,fontsize=14,x=1.0,y=1.01)
    cb.ax.tick_params(labelsize=12) 
    ax.set_title(u_title, fontweight='regular',fontsize=20) #'light','normal','regular','semibold','bold'
    ax.set_xlabel("")
    ax.set_ylabel("")
    lon_formatter = LongitudeFormatter()
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.text(0.9, 0.025, u_res_text,horizontalalignment='right',verticalalignment='bottom',fontsize=12,color='white',transform=ax.transAxes)
    ax.coastlines(color='whitesmoke') #'dimgrey','white','whitesmoke'
    plt.savefig(u_file_output+'.svg',dpi=150,bbox_inches='tight', format='svg')
    plt.savefig(u_file_output+'.png',dpi=150,bbox_inches='tight', format='png')
    plt.savefig(u_file_output+'.pdf',dpi=150,bbox_inches='tight', format='pdf')
    plt.savefig(u_file_output+'.eps',dpi=150,bbox_inches='tight', format='eps')

    return


def grid_area_df(lat_point,res,r_earth=6.375e6): #calculate grid area based on (lat,lon)
    n_lon = 360/res #3600
    grid_area = abs(np.sin(np.pi*(abs(lat_point)+res/2)/180.0)-np.sin(np.pi*(abs(lat_point)-res/2)/180.0))*2*np.pi*r_earth*r_earth/n_lon
    grid_area = grid_area/1000000 ## m2->km2
    return grid_area


def plot_CO2_map_kg_km2(u_title, u_data_input, u_dir_output):

    u_pl = 'CO2'

    ### create a full matrix with continuous latitude, longitude -- Resolution: 1 degree
    lat_name = 'Latitude'
    lon_name = 'Longitude'
    geo_res_1 = 0  # no digit
    geo_interval_1 = 1
    geo_add_1 = geo_interval_1/2  # 
    lat_begin, lat_end = -90, 90
    lon_begin, lon_end = -180, 180
    

    lat_arange_1 = [lat_begin, lat_end, geo_interval_1]
    lon_arange_1 = [lon_begin, lon_end, geo_interval_1]
    lat_digit_1 = geo_res_1
    lon_digit_1 = geo_res_1
    xr_full_1 = f5_xr_full_lat_lon(lat_name,lat_arange_1[0],lat_arange_1[1],lat_arange_1[2],lat_digit_1,
                                 lon_name,lon_arange_1[0],lon_arange_1[1],lon_arange_1[2],lon_digit_1)

    cms_input = [lat_name,lon_name,u_pl]
    data_input = pd.read_csv(u_data_input, usecols=cms_input)
    print(data_input[u_pl].sum())

    data_input['area'] = data_input[lat_name].apply(lambda x: grid_area_df(x,1)) #km2, 1 degree
    data_input[u_pl] = data_input[u_pl]*1000/data_input['area'] ## -> kg/km2

    data_to_plot = transform_csv_nc_full(data_input,xr_full_1,lat_name,lon_name,geo_res_1,geo_add_1)
    plot_em_global_tonnes(u_title, u_dir_output,data_to_plot,u_pl)
    
    return


### I/O setting

plot_CO2_map_kg_km2('Global CO$_2$ Emission from International Vessels\n Baseline Scenario', './ResultData/ShipEmissionAnnual/BL/gb_Latitude_Longitude_2015_I.csv', './Figure/Figure_1a_emission_map_BL_I')
plot_CO2_map_kg_km2('Global CO$_2$ Emission from Domestic Vessels\n Baseline Scenario','./ResultData/ShipEmissionAnnual/BL/gb_Latitude_Longitude_2015_D.csv', './Figure/Figure_1b_emission_map_BL_D')
