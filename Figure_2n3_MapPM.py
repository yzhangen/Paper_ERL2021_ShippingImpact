## annual average global plots

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


def plot_global_conc_log (u_scenario, u_dict_title, u_dir_input,u_dir_output):
    
    u_pl               = 'PM25'
    u_fig_num          = u_dict_title[u_scenario][0]  # Figure#
    u_title            = u_dict_title[u_scenario][1]  # figure title
    u_cmap             = 'afmhot_r'                   # color
    u_cbar_unit        = '\u03BCg/m\u00b3'            # ug/m3
    u_cbar_extend      = 'both'
    u_cbar_vmin        = 0.01
    u_cbar_vmax        = 10
    u_text_res         = 'Resolution: 2 degree x 2.5 degree lat-lon'

    u_filename_pre     = 'YAVG_Conc_PM25_'    
    u_file_input       = u_dir_input  + u_filename_pre + u_scenario + '_2x25'
    u_file_output      = u_dir_output + u_fig_num + '_' + u_filename_pre + u_scenario + '_2x25'
    print(u_file_input)
    
    u_data_xr          = xr.open_dataset(u_file_input + '.nc')
    u_data_xr          = u_data_xr.where((u_data_xr[u_pl]>=u_cbar_vmin))
    u_data_xr          = u_data_xr.fillna(u_cbar_vmin)
    u_data             = u_data_xr[u_pl]
    
        
    fig, ax = plt.subplots(figsize=(12,16))
    ax = plt.axes(projection=ccrs.PlateCarree())
    fig_data = u_data.plot.pcolormesh(ax=ax,  cmap=u_cmap, add_colorbar=False, norm=colors.LogNorm(vmin=u_cbar_vmin, vmax=u_cbar_vmax),
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
    
    plt.savefig(u_file_output+'.png',dpi=150,bbox_inches='tight', format='png')
    plt.savefig(u_file_output+'.svg',dpi=150,bbox_inches='tight', format='svg')
    plt.savefig(u_file_output+'.pdf',dpi=150,bbox_inches='tight', format='pdf')
    plt.savefig(u_file_output+'.eps',dpi=150,bbox_inches='tight', format='eps')

    u_data_xr.close()
    print(u_file_output)
    return



fg_dir_pm_annual_fig   = './Figure/'
fg_dir_pm_annual_data  = './ResultData/GEOSChemAnnualPM/'


fg_title_pre  = 'Global PM' + '\u2082' + '\u002E' + '\u2085' + ' Concentration'
fg_dict_title = {'scenario'      :['Figure_Num', 'title'],
                'BL_ID_BL_D'     :['Figure_2a', fg_title_pre+' attributed to International Vessels\n Baseline Scenario'],
                'BL_ID_BL_I'     :['Figure_2b', fg_title_pre+' attributed to Domestic Vessels\n Baseline Scenario'],
                'BL_ID_S1N0_ID'  :['Figure_3a', fg_title_pre+' reduction due to 0.5% Sulphur Cap\n International and Domestic Vessels'],
                'S1N0_ID_S2N0_ID':['Figure_3b', fg_title_pre+' reduction due to Post-2020 0.1% Sulphur Cap\n International and Domestic Vessels'],
                'S1N0_ID_S1N1_ID':['Figure_3c', fg_title_pre+' reduction due to Post-2020 Tier III NOx Standard\n International and Domestic Vessels']
               }


list_scenario = ['BL_ID_BL_D', 'BL_ID_BL_I', 'BL_ID_S1N0_ID', 'S1N0_ID_S2N0_ID', 'S1N0_ID_S1N1_ID']
for scenario in list_scenario:
    plot_global_conc_log(scenario, fg_dict_title, fg_dir_pm_annual_data,fg_dir_pm_annual_fig)

