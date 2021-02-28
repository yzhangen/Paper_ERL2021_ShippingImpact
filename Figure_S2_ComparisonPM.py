#### ComparisonPM.py

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import xarray as xr
import xesmf as xe
import matplotlib.colors as colors
import os
import io
import pandas as pd

from cartopy.io.img_tiles import OSM


def plot_gc_observation(u_data_gc, u_data_obs, u_extent, u_domain, u_filename):
    u_file_output = fg_dir_output_fig + u_filename
    u_title = 'PM' + '\u2082' + '\u002E' + '\u2085' + ' Concentration of GEOS-Chem Results and Observations \n Annual Average, '+u_domain
    u_text_res = 'Resolution: 2 degree x 2.5 degree lat-lon'
    
    u_min = 0
    u_max = 200
    
    x_min = -180
    x_max = 181
    x_step = 5
    y_min = -90
    y_max = 91
    y_step = 5
    u_color = 'gist_stern_r'#'Reds' #'tab20c_r'
    line_color = 'black'
    
    fig, ax = plt.subplots(1,1,figsize=(12,9),subplot_kw={"projection": ccrs.PlateCarree()})
    u_plot = u_data_gc.plot.pcolormesh(ax=ax,add_colorbar=False,vmin=u_min,vmax=u_max,cmap=u_color, 
                                         xticks=np.arange(x_min,x_max,step=x_step),yticks=np.arange(y_min,y_max,step=y_step))

    ax.set_title(u_title, fontweight='regular',fontsize=18)
    ax.set_xlabel('Longitude',fontsize=14)
    ax.set_ylabel('Latitude', fontsize=14)
    ax.coastlines('50m')
    
    obs_edge = ax.scatter(u_data_obs['lon'], u_data_obs['lat'], c=u_data_obs['PM25'],s=20,edgecolors='black',vmin=u_min,vmax=u_max,cmap=u_color)   
    obs = ax.scatter(u_data_obs['lon'], u_data_obs['lat'], c=u_data_obs['PM25'],s=16,vmin=u_min,vmax=u_max,cmap=u_color)
    
    ax.set_extent(u_extent)
    
    cax = fig.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])
    cb = plt.colorbar(u_plot, cax=cax, extend='max')
    cb.ax.tick_params(labelsize=12)
    cb.ax.set_title('\u03BCg/m\u00b3',fontsize=14,x=1.0,y=1.01)
    ax.text(0.9, 0.025, u_text_res, horizontalalignment='right',verticalalignment='bottom',fontsize=12,color='gray',transform=ax.transAxes)
    print(u_file_output)
    plt.savefig(u_file_output+'.png',dpi=150,bbox_inches='tight', format='png')
    plt.savefig(u_file_output+'.svg',dpi=150,bbox_inches='tight', format='svg')
    plt.savefig(u_file_output+'.pdf',dpi=150,bbox_inches='tight', format='pdf')
    plt.savefig(u_file_output+'.eps',dpi=150,bbox_inches='tight', format='eps')
    return


## plot gc and observation data

fg_dir_output_fig  = './Figure/'
fg_dir_output_data = './ResultData/ComparisonPM/'

file_gc  = './ResultData/GEOSChemAnnualPM/YAVG_Conc_PM25_BL_ID_2x25.nc'
gc_yavg       = xr.open_dataset(file_gc)
gc_yavg_pm25  = gc_yavg['PM25']

file_obs_cn = './InputData/ObservationPM/YAVG_FSPMC_2015_China.csv'  ## observational data in China
file_obs_eu = './InputData/ObservationPM/YAVG_PM25_2015_EMEP.csv'    ## observational data in Europe

## observations in China
df_obs_cn   = pd.read_csv(file_obs_cn)
df_obs_cn = df_obs_cn.rename(columns = {'Latitude': 'lat', 'Longitude': 'lon'})
extent_cn = [101.5,126,20,42.5]

## observations in EU
df_obs_eu   = pd.read_csv(file_obs_eu)
extent_eu = [-10,30,35,70]

## plot spatial plots
plot_gc_observation(gc_yavg_pm25, df_obs_cn, extent_cn, 'China' , 'Figure_S2_YAVG_PM25_GC_OBS_CN')
plot_gc_observation(gc_yavg_pm25, df_obs_eu, extent_eu, 'Europe', 'Figure_S2_YAVG_PM25_GC_OBS_EU')



## statistics


## EU
#### I/O
u_filename = 'Figure_S2_corr_YAVG_GC_OBS_EU'

df_obs   = pd.read_csv(file_obs_eu) ## read EU obervational data

u_dr0    = xr.open_dataset(file_gc) ## read GC data
u_pl     = 'PM25'
u_dr1    = u_dr0[u_pl]
u_dr0.close()


#### group data for corelation analysis

u_dr1_zoom = u_dr1.sel(lon=slice(-10,40),lat=slice(30,75))
u_df = u_dr1_zoom.to_dataframe().reset_index()
u_df = u_df.rename(columns = {'PM25': 'PM25_gc'})

list_lat = u_df['lat'].unique().tolist()
bin_lat  = (u_df['lat'].unique().tolist()) + [(u_df['lat'].max())+2]
bin_lat  = [x-1 for x in bin_lat]

list_lon = u_df['lon'].unique().tolist()
bin_lon  = (u_df['lon'].unique().tolist()) + [(u_df['lon'].max())+2.5]
bin_lon  = [x-1.25 for x in bin_lon]

u_df['lat_cut'] = pd.cut(u_df['lat'], bins=bin_lat, labels=list_lat, right=False)
u_df['lon_cut'] = pd.cut(u_df['lon'], bins=bin_lon, labels=list_lon, right=False)

u_obs = df_obs.copy()
u_obs = u_obs.rename(columns = {'PM25': 'PM25_obs'})

u_obs['lat_cut'] = pd.cut(u_obs['lat'], bins=bin_lat, labels=list_lat, right=False)
u_obs['lon_cut'] = pd.cut(u_obs['lon'], bins=bin_lon, labels=list_lon, right=False)

u_df_merge = u_df[['lat_cut','lon_cut','PM25_gc']].merge(u_obs[['lat_cut','lon_cut','PM25_obs']],how='left',on=['lat_cut','lon_cut'])
u_df_merge[['lat_cut','lon_cut']] = u_df_merge[['lat_cut','lon_cut']].astype('object')
u_df_merge_v = u_df_merge.dropna(how='any')
u_df_merge_v_gb = u_df_merge_v.groupby(['lat_cut','lon_cut']).mean().reset_index()

#### calculate corelation
u_corr = u_df_merge_v[['PM25_gc','PM25_obs']].corr(method='pearson')
u_corr_value = u_corr['PM25_gc']['PM25_obs']
print(u_corr_value.round(2))
u_text = 'spatial corelation coefficient = ' + str(u_corr_value.round(2))

#### make corelation plot
fig, ax = plt.subplots(1,1,figsize=(12,9))
u_data = u_df_merge_v_gb.copy()
ax.scatter(u_data['PM25_gc'], u_data['PM25_obs'], s=25)
ax.set_xlabel('Modelled Concentration (' + '\u03BCg/m\u00b3' + ')',fontsize=14)
ax.set_ylabel('Observed Concentration (' + '\u03BCg/m\u00b3' + ')',fontsize=14)
ax.set_xlim(0, 30)
ax.set_ylim(0, 30)
ax.set_title('Modelled Concentration -- Observed Concentration, Europe', fontweight='regular',fontsize=20)
ax.text(0.9, 0.9, u_text, horizontalalignment='right',verticalalignment='top',fontsize=18,color='black',transform=ax.transAxes)
plt.savefig(fg_dir_output_fig+u_filename+'.png',dpi=150,bbox_inches='tight', format='png')
plt.savefig(fg_dir_output_fig+u_filename+'.svg',dpi=150,bbox_inches='tight', format='svg')
plt.savefig(fg_dir_output_fig+u_filename+'.pdf',dpi=150,bbox_inches='tight', format='pdf')
plt.savefig(fg_dir_output_fig+u_filename+'.eps',dpi=150,bbox_inches='tight', format='eps')


## China

#### I/O
u_filename = 'Figure_S2_corr_YAVG_GC_OBS_CN'

df_obs   = pd.read_csv(file_obs_cn)  ## read observational data
df_obs = df_obs.rename(columns = {'Latitude': 'lat', 'Longitude': 'lon'})

u_dr0    = xr.open_dataset(file_gc)  ## read GC data
u_pl     = 'PM25'
u_dr1    = u_dr0[u_pl]
u_dr0.close()

#### prepare data for corelation analysis
u_dr1_zoom = u_dr1.sel(lon=slice(100,125),lat=slice(20,50))
u_df = u_dr1_zoom.to_dataframe().reset_index()
u_df = u_df.rename(columns = {'PM25': 'PM25_gc'})

list_lat = u_df['lat'].unique().tolist()
bin_lat  = (u_df['lat'].unique().tolist()) + [(u_df['lat'].max())+2]
bin_lat  = [x-1 for x in bin_lat]

list_lon = u_df['lon'].unique().tolist()
bin_lon  = (u_df['lon'].unique().tolist()) + [(u_df['lon'].max())+2.5]
bin_lon  = [x-1.25 for x in bin_lon]

u_df['lat_cut'] = pd.cut(u_df['lat'], bins=bin_lat, labels=list_lat, right=False)
u_df['lon_cut'] = pd.cut(u_df['lon'], bins=bin_lon, labels=list_lon, right=False)

u_obs = df_obs.copy()
u_obs = u_obs.rename(columns = {'PM25': 'PM25_obs'})

u_obs['lat_cut'] = pd.cut(u_obs['lat'], bins=bin_lat, labels=list_lat, right=False)
u_obs['lon_cut'] = pd.cut(u_obs['lon'], bins=bin_lon, labels=list_lon, right=False)

u_df_merge = u_df[['lat_cut','lon_cut','PM25_gc']].merge(u_obs[['lat_cut','lon_cut','PM25_obs']],how='left',on=['lat_cut','lon_cut'])
u_df_merge[['lat_cut','lon_cut']] = u_df_merge[['lat_cut','lon_cut']].astype('object')
u_df_merge_v = u_df_merge.dropna(how='any')
u_df_merge_v_gb = u_df_merge_v.groupby(['lat_cut','lon_cut']).mean().reset_index()

#### calculate corelation
u_corr = u_df_merge_v[['PM25_gc','PM25_obs']].corr(method='pearson')  ## corelation coefficient = 0.748777
u_corr_value = u_corr['PM25_gc']['PM25_obs']
print(u_corr_value.round(2))
u_text = 'spatial corelation coefficient = ' + str(u_corr_value.round(2))

#### plotting
fig, ax = plt.subplots(1,1,figsize=(12,9))
u_data = u_df_merge_v_gb.copy()
ax.scatter(u_data['PM25_gc'], u_data['PM25_obs'], s=25)
ax.set_xlabel('Modelled Concentration ('+'\u03BCg/m\u00b3'+')',fontsize=14)
ax.set_ylabel('Observed Concentration ('+'\u03BCg/m\u00b3'+')',fontsize=14)
ax.set_xlim(0, 200)
ax.set_ylim(0, 200)
ax.set_title('Modelled Concentration -- Observed Concentration, China', fontweight='regular',fontsize=20)
ax.text(0.9, 0.9, u_text, horizontalalignment='right',verticalalignment='top',fontsize=18,color='black',transform=ax.transAxes)
plt.savefig(fg_dir_output_fig+u_filename+'.png',dpi=150,bbox_inches='tight', format='png')
plt.savefig(fg_dir_output_fig+u_filename+'.svg',dpi=150,bbox_inches='tight', format='svg')
plt.savefig(fg_dir_output_fig+u_filename+'.pdf',dpi=150,bbox_inches='tight', format='pdf')
plt.savefig(fg_dir_output_fig+u_filename+'.eps',dpi=150,bbox_inches='tight', format='eps')

print('Done!')
## End of program ##
