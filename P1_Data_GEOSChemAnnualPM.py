#### generate (and regrid) annual PM concentration from simulated monthly PM results


import numpy as np
import xarray as xr
import pandas as pd
import xesmf as xe

import os
import io


dir_PM_monthly_data    = './ResultData/GEOSChemMonthlyPM/'
dir_PM_annual_data     = './ResultData/GEOSChemAnnualPM/'

filename_pm_annual_pre = 'YAVG_Conc_PM25_'



#### combine monthly PM results and calculate annual-average PM results (2 degree x 2.5 degree lat-lon)

def cal_annual_avg_multi2one(u_dir_month, u_dir_annual, u_filename_o):
    
    ## I/O
    u_pl = 'PM25'
    fg_file_pre = 'GEOSChem.AerosolMass.'
    fg_time     = '_0000z'
    
    u_dr_pre = u_dir_month+fg_file_pre + '2015*.nc4'
    print(u_dr_pre)
    
    u_file_o_nc = u_dir_annual+u_filename_o+'.nc'
    print(u_file_o_nc)
    
    u_file_o_csv = u_dir_annual+u_filename_o+'.csv'
    print(u_file_o_csv)
    
    ## combine multiple GC result files and calculate annual-average PM
    u_xr_multi = xr.open_mfdataset(u_dr_pre)
    u_xr_avg = u_xr_multi.isel(lev=0).mean(dim='time')
    
    ## output annual-average PM to netcdf file
    u_xr_avg.to_netcdf(u_file_o_nc)
    
    ## output annual-average PM to csv file    
    u_df_avg = u_xr_avg[u_pl].to_dataframe().reset_index()
    u_df_avg.to_csv(u_file_o_csv, index=False)

    ## close    
    u_xr_multi.close()
    u_xr_avg.close()
    
    return


def cal_diff_annual_avg(u_dir_input, u_dir_output, u_filename_main, u_scenario_1, u_scenario_2, u_filename_o):
    
    ## I/O
    u_pl = 'PM25'
    u_dr_1      = u_dir_input  + u_filename_main + u_scenario_1 +'.nc'
    u_dr_2      = u_dir_input  + u_filename_main + u_scenario_2 +'.nc'
    u_file_o_nc = u_dir_output + u_filename_main + u_filename_o +'.nc'
    u_file_o_csv= u_dir_output + u_filename_main + u_filename_o +'.csv'
    print(u_dr_1, u_dr_2, u_file_o_nc, u_file_o_csv)   
    
    ## calculate difference between scenarios
    u_data_1 = xr.open_dataset(u_dr_1)
    u_data_2 = xr.open_dataset(u_dr_2)
    u_data_diff = u_data_1 - u_data_2
    
    ## output to netcdf file
    u_data_diff.to_netcdf(u_file_o_nc)
    
    ## output to csv file
    u_df_data_diff = u_data_diff[u_pl].to_dataframe().reset_index()
    u_df_data_diff.to_csv(u_file_o_csv, index=False)

    ## close
    u_data_1.close()
    u_data_2.close()
    u_data_diff.close()
    
    return


res = '_2x25'

list_scenario = ['BL_ID','BL_I','BL_D','BL_NoShip','S1N0_ID','S2N0_ID','S1N1_ID']
for scenario in list_scenario:
    cal_annual_avg_multi2one(dir_PM_monthly_data+scenario+'/', dir_PM_annual_data, filename_pm_annual_pre+scenario+res)
    

list_scenario_diff = ['BL_ID_BL_I','BL_ID_BL_D','BL_ID_BL_NoShip','BL_ID_S1N0_ID','S1N0_ID_S2N0_ID','S1N0_ID_S1N1_ID']
dict_scenario_diff = {'scenario'          : ['scenario_1', 'scenario_2', 'filename_o'], 
                      'BL_ID_BL_I'        : ['BL_ID'     , 'BL_I'      , 'BL_ID_BL_I'], 
                      'BL_ID_BL_D'        : ['BL_ID'     , 'BL_D'      , 'BL_ID_BL_D'], 
                      'BL_ID_BL_NoShip'   : ['BL_ID'     , 'BL_NoShip' , 'BL_ID_BL_NoShip'],
                      'BL_I_BL_NoShip'    : ['BL_I'      , 'BL_NoShip' , 'BL_I_BL_NoShip'], 
                      'BL_D_BL_NoShip'    : ['BL_D'      , 'BL_NoShip' , 'BL_D_BL_NoShip'], 
                      'BL_ID_S1N0_ID'     : ['BL_ID'     , 'S1N0_ID'   , 'BL_ID_S1N0_ID'],
                      'S1N0_ID_BL_NoShip' : ['S1N0_ID'   , 'BL_NoShip' , 'S1N0_ID_BL_NoShip'],
                      'S1N0_ID_S2N0_ID'   : ['S1N0_ID'   , 'S2N0_ID'   , 'S1N0_ID_S2N0_ID'],
                      'S1N0_ID_S1N1_ID'   : ['S1N0_ID'   , 'S1N1_ID'   , 'S1N0_ID_S1N1_ID']
                     }

for scenario_diff in list_scenario_diff:
    cal_diff_annual_avg(dir_PM_annual_data, 
                        dir_PM_annual_data, 
                        filename_pm_annual_pre,
                        dict_scenario_diff[scenario_diff][0]+res, 
                        dict_scenario_diff[scenario_diff][1]+res, 
                        dict_scenario_diff[scenario_diff][2]+res)



    
#### regrid annual-average PM from 2 degree x 2.5 degree lat-lon to 0.5 degree x 0.5 degree (to merge with health data in the later process)


def regrid_gc_2x25_05x05(u_filename_main,u_dir_input,u_dir_output):
    
    ## I/O
    u_file_input  = u_dir_input+u_filename_main+'_2x25.nc'
    print(u_file_input)
    
    u_file_output = u_dir_output+u_filename_main+'_05x05.nc'
    print(u_file_output)
    
    ## generate regridder
    lon_05x05      = np.linspace(-179.75, 179.75, 720)
    lat_05x05      = np.linspace(-89.75,89.75,360)
    lon_edge_05x05 = np.linspace(-179.75-0.5/2, 179.75+0.5/2, 721)
    lat_edge_05x05 = np.linspace(-89.75-0.5/2, 89.75+0.5/2, 361).clip(-90, 90)
    high_grid_with_bounds = {'lon': lon_05x05,
                             'lat': lat_05x05,
                             'lon_b': lon_edge_05x05,
                             'lat_b': lat_edge_05x05}

    lon_2x25      = np.linspace(-180.0, 177.5, 144)
    lat_2x25      = np.array([-89.5]+[-90 + 2*x for x in range(90)][1:]+[89.5])
    lon_edge_2x25 = np.linspace(-180.0-2.5/2, 177.5+2.5/2, 145)
    lat_edge_2x25 = np.array([-91 + 2*x for x in range(92)]).clip(-90,90)  # fix half-polar cells
    low_grid_with_bounds = {'lon': lon_2x25,
                            'lat': lat_2x25,
                            'lon_b': lon_edge_2x25,
                            'lat_b': lat_edge_2x25} 

    regridder_conserve = xe.Regridder(low_grid_with_bounds, high_grid_with_bounds, method='conservative')
        
    ## process regridding
    u_xr_gc  = xr.open_dataset(u_file_input)['PM25']
    xr_gc_regrid = regridder_conserve(u_xr_gc)
    
    ## output
    xr_gc_regrid.to_netcdf(u_file_output)
    
    ## close
    u_xr_gc.close()
    
    return



## list of simulations to be regridded
list_scenario = ['BL_ID','BL_I','BL_D','BL_NoShip','S1N0_ID','S2N0_ID','S1N1_ID',
                 'BL_ID_BL_I','BL_ID_BL_D','BL_ID_BL_NoShip',
                 'BL_ID_S1N0_ID','S1N0_ID_S2N0_ID','S1N0_ID_S1N1_ID']

for scenario in list_scenario:
    regrid_gc_2x25_05x05(filename_pm_annual_pre+scenario,dir_PM_annual_data,dir_PM_annual_data)

    
print('Done')
## End of Program ##
    


