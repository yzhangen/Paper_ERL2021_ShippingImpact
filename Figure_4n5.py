## Figure 4, Figure 5 -- unit: mortality per grid

#%matplotlib inline
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import xarray as xr
import xesmf as xe
import matplotlib.colors as colors
import os
import io
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter




## --------- outputs: Health Impact global plots -----------------------------------------------------------------------------

fg_pl        = 'PM25'
fg_pl_title  = 'PM'+'\u2082' + '\u002E' + '\u2085'  # PM2.5
fg_cbar_unit = 'mortalities/' + 'km\u00b2'
fg_text_res  = 'Resolution: 2 degree x 2.5 degree lat-lon'


fg_list_scenario = ['BL_ID_BL_I', 'BL_ID_BL_D', 'BL_ID_S1N0_ID', 'S1N0_ID_S2N0_ID', 'S1N0_ID_S1N1_ID']

fg_list_cause    = ['GEMM_NCD_LRI']  ## combined


fg_dict_para = {'scenario'       :['FigureNum','title', 'sub_title'],
                'BL_ID_BL_I'     :['Figure_4b','Global Mortality affected by outdoor '+fg_pl_title+' associated with Domestic Shipping', 
                                   ', Baseline Scenario'],
                'BL_ID_BL_D'     :['Figure_4a','Global Mortality affected by outdoor '+fg_pl_title+' associated with International Shipping', 
                                   ', Baseline Scenario'],
                'BL_ID_S1N0_ID'  :['Figure_5a','Avoided Mortality associated with '   +fg_pl_title+' reduction due to 2020 Sulphur Cap', 
                                   ', International and Domestic Shipping'],
                'S1N0_ID_S2N0_ID':['Figure_5b','Avoided Mortality associated with '   +fg_pl_title+' reduction due to Post-2020 0.1% Sulphur Cap', 
                                   ', International and Domestic Shipping'],
                'S1N0_ID_S1N1_ID':['Figure_5c','Avoided Mortality associated with '   +fg_pl_title+' reduction due to Post-2020 Tier III NOx Standard',
                                   ', International and Domestic Shipping']               
               }

fg_dict_cause = {'cause'        : ['filename'    , 'fig_title'], 
                 'GEMM_NCD_LRI' : ['GEMM_NCD_LRI', 'GEMM NCD+LRI']
                }



def plot_global_health (u_cause,u_pl,u_scenario,u_dir_input,u_dir_output):
    
    u_filename_main    = 'Mortality_PM25_'+ fg_dict_cause[u_cause][0] + '_' + u_scenario
    u_file_input       = u_dir_input + u_filename_main + '_2x25.nc'
    print(u_file_input)
    u_data_xr          = xr.open_dataset(u_file_input)
    u_data             = u_data_xr['Mortality']
    print(u_data)
    
    u_title            = fg_dict_para[u_scenario][1] + ' \n' + fg_dict_cause[u_cause][1] + fg_dict_para[u_scenario][2] 
    u_cmap             = 'afmhot_r'
    u_cbar_unit        = 'mortality\nper grid'
    u_cbar_extend      = 'max'
    u_cbar_vmin        = 0
    u_cbar_vmax        = 100
    u_text_res         = 'Resolution: 2 degree x 2.5 degree lat-lon'
    u_level            = [1,10,20,30,40,50,100,150,200,250,300,350,400,450,500]

    
    fig, ax = plt.subplots(figsize=(16,12))
    ax = plt.axes(projection=ccrs.PlateCarree())
#    fig_data = u_data.plot.pcolormesh(ax=ax,  cmap=u_cmap, add_colorbar=False, vmin=u_cbar_vmin,vmax=u_cbar_vmax,
#                                            xticks=np.arange(-180, 181,step=60),yticks=np.arange(-90,91,step=30)) #method3
    fig_data = u_data.plot.pcolormesh(ax=ax,  cmap=u_cmap, add_colorbar=False, levels=u_level,
                                            xticks=np.arange(-180, 181,step=60),yticks=np.arange(-90,91,step=30)) #method3
    cax = fig.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])
    cb = plt.colorbar(fig_data, cax=cax, extend=u_cbar_extend)
    cb.ax.set_title(u_cbar_unit,fontsize=14,x=1.0,y=1.01)
    ax.set_title(u_title, fontweight='regular',fontsize=20,loc='center')
    ax.set_xlabel('',fontsize=14)
    ax.set_ylabel('',fontsize=14)
     
    lon_formatter = LongitudeFormatter()
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)

    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.text(0.9, 0.025, u_text_res, horizontalalignment='right',verticalalignment='bottom',fontsize=12,color='gray',transform=ax.transAxes)
    ax.coastlines(color='gray',linewidth=0.5)
    plt.savefig(u_dir_output+fg_dict_para[u_scenario][0]+'_'+u_filename_main+'.png',dpi=150,bbox_inches='tight', format='png')
    plt.savefig(u_dir_output+fg_dict_para[u_scenario][0]+'_'+u_filename_main+'.svg',dpi=150,bbox_inches='tight', format='svg')
    plt.savefig(u_dir_output+fg_dict_para[u_scenario][0]+'_'+u_filename_main+'.pdf',dpi=150,bbox_inches='tight', format='pdf')
    plt.savefig(u_dir_output+fg_dict_para[u_scenario][0]+'_'+u_filename_main+'.eps',dpi=150,bbox_inches='tight', format='eps')

    print(u_dir_output+'_'+fg_dict_para[u_scenario][0]+u_filename_main+'.png')
    return


fg_dir_health_data  = './ResultData/HealthResult/'
fg_dir_health_fig   = './Figure/'

for fg_cause in fg_list_cause:
    for fg_scenario in fg_list_scenario:
        plot_global_health (fg_cause,fg_pl,fg_scenario,fg_dir_health_data,fg_dir_health_fig)