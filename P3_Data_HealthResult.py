## Data_HealthResult.py
## estimate health impact


import pandas as pd
import numpy as np
import xarray as xr
import math

## estimate health impact: GEMM model, cause-specific mortality ----------------------------------------------------------------------------

def cal_health_GEMM(u_df_gc_pop,u_df_rate_cause,u_cause,u_para_cause,u_cm_conc,u_cm_pop,u_cm_baseline_mort,u_cm_baseline_mort_upper,u_cm_baseline_mort_lower): #using
    
    ## merge population, pm, baseline mortality
    u_df0 = u_df_gc_pop.copy()
    u_df0 = u_df0.merge(u_df_rate_cause,how='left',left_on='code_country',right_on='CIESINCODE_GPW')
    
    ## add health para
    u_RR         = 'RR'
    u_RR_upper   = u_RR + '_upper'
    u_RR_lower   = u_RR + '_lower'
    u_mort       = 'Mortality'
    u_mort_upper = u_mort + '_upper'
    u_mort_lower = u_mort + '_lower'
    
    u_theta     = fg_health[u_para_cause][0]
    u_theta_std = fg_health[u_para_cause][1]
    u_alpha     = fg_health[u_para_cause][2]
    u_mu        = fg_health[u_para_cause][3]
    u_nu        = fg_health[u_para_cause][4]
    
    u_df0['cause']     = u_cause
    u_df0['theta']     = u_theta
    u_df0['theta_std'] = u_theta_std
    u_df0['alpha']     = u_alpha
    u_df0['mu']        = u_mu
    u_df0['nu']        = u_nu
    
    ## calculate hazard ratio
    u_df0['z']         = u_df0[u_cm_conc].apply(lambda x: 0 if x<=2.4 else x-2.4)
    u_df0[u_RR]        = u_df0['z'].apply(lambda x: math.exp(u_theta*np.log(x/u_alpha+1)/(1+math.exp(-(x-u_mu)/u_nu))))
    u_df0[u_RR_upper]  = u_df0['z'].apply(lambda x: math.exp((u_theta+u_theta_std)*np.log(x/u_alpha+1)/(1+math.exp(-(x-u_mu)/u_nu))))
    u_df0[u_RR_lower]  = u_df0['z'].apply(lambda x: math.exp((u_theta-u_theta_std)*np.log(x/u_alpha+1)/(1+math.exp(-(x-u_mu)/u_nu))))

    ## calculate mortality
    u_df0[u_mort]      =u_df0[u_cm_pop]/100000 * u_df0[u_cm_baseline_mort] * (1-1/u_df0[u_RR])
    u_df0[u_mort_upper]=u_df0[u_cm_pop]/100000 * u_df0[u_cm_baseline_mort] * (1-1/u_df0[u_RR_upper])
    u_df0[u_mort_lower]=u_df0[u_cm_pop]/100000 * u_df0[u_cm_baseline_mort] * (1-1/u_df0[u_RR_lower])

    print(u_cause, u_df0[u_cm_pop].sum(), u_df0[u_mort].sum(), u_df0[u_mort_upper].sum(), u_df0[u_mort_lower].sum())
    return u_df0


## directory for health results (0.5x0.5 lat-lon)
dir_health_data = './ResultData/HealthResult/'
dir_pop_pm      = './ResultData/PopulationPM/'
dir_mort_base   = './InputData/BaselineMortality/'

file_mort_base_pre  = 'Location_MortailityRate_25plus_'
file_pop_pm_pre     = 'pop_YAVG_Conc_PM25_'


## para setting and estimation

list_scenario = ['BL_ID','BL_I','BL_D','BL_NoShip','S1N0_ID','S2N0_ID','S1N1_ID']

list_cause = ['GEMM_NCD','GEMM_LRI']
dict_cause = {'CAUSE'   :['para_cause'  , 'rate_cause', 'filename_output_cause'],
              'GEMM_NCD':['GEMM_NCD_LRI', 'NCD'       , 'GEMM_NCD'],
              'GEMM_LRI':['GEMM_NCD_LRI', 'LRI'       , 'GEMM_LRI']
             }

fg_health  = {'cause':['theta', 'theta_std', 'alpha', 'mu', 'nu'],
              'GEMM_NCD_LRI':[0.143, 0.01807, 1.6, 15.5, 36.8], 
              }



res = '05x05'
fg_pl   = 'PM25'
cm_conc                = 'PM25'
cm_pop                 = 'pop2015_25plus'
cm_baseline_mort       = 'rate_country_25plus_val'
cm_baseline_mort_upper = 'rate_country_25plus_val_upper'
cm_baseline_mort_lower = 'rate_country_25plus_val_lower'


for u_scenario in list_scenario:
    print(u_scenario)
    u_file_input_gc_pop = dir_pop_pm + file_pop_pm_pre + u_scenario + '_' + res +'.csv'
    df_gc_pop = pd.read_csv(u_file_input_gc_pop)
    
    for u_cause in list_cause:
        u_para_cause            = dict_cause[u_cause][0]
        u_rate_cause            = dict_cause[u_cause][1]
        u_filename_output_cause = dict_cause[u_cause][2]
        
        ## import data of specific-location-cause mortality rate
        u_file_input_cause  = dir_mort_base + file_mort_base_pre + u_rate_cause + '.csv'
        df_rate_cause       = pd.read_csv(u_file_input_cause)
        
        ## calculate health impacts
        df_gc_pop_cause = cal_health_GEMM(df_gc_pop,
                                          df_rate_cause,
                                          u_cause,
                                          u_para_cause,
                                          cm_conc,
                                          cm_pop,
                                          cm_baseline_mort,
                                          cm_baseline_mort_upper,
                                          cm_baseline_mort_lower)
              
        ## outputs        
        u_filename_output  = 'Mortality_' + fg_pl +'_'+ u_filename_output_cause + '_' + u_scenario
        print(u_filename_output)
        
        #### output results to csv file
#        df_gc_pop_cause.to_csv(dir_health_data+u_filename_output+'_'+ res+'.csv',index=False)
        
        #### group by country/region and cause of death, output to csv file
        cms_gb = ['CIESINCODE_GPW','ISOCODE_GPW','Location_GPW',
                  'location_id_GBD','ISOCODE_GBD','Location_GBD','location_name_GBD',
                  'cause_id_GBD','cause_name_GBD','cause']
        cms_stat = ['Mortality','Mortality_upper','Mortality_lower']
        df_gb = df_gc_pop_cause[cms_gb+cms_stat].groupby(cms_gb).sum().reset_index()
        df_gb.to_csv(dir_health_data+'gb_location_'+u_filename_output+'.csv',index=False)
        
        #### output gridded mortality to netcdf file        
        df_mort = df_gc_pop_cause[['lat','lon','Mortality','Mortality_upper','Mortality_lower']].groupby(['lat','lon']).sum()
        xr_mort = xr.Dataset.from_dataframe(df_mort)
        xr_mort.to_netcdf(dir_health_data+u_filename_output+'_'+ res+'.nc', mode='w')



## combined health effects: GEMM NCD+LRI ------------------------------------------------------------------------------------------------


def cal_combined_health_gemm_ncd_lri(u_dir_health_data,u_scenario):
    
    print('cal_combined_health', u_scenario)
    
    u_filename_pre = 'Mortality_PM25_' 
    u_res          = '05x05'
    fg_cm          = ['Mortality']
    
    gemm_ncd     = xr.open_dataset(u_dir_health_data+u_filename_pre+'GEMM_NCD'+'_'+u_scenario+'_'+u_res+'.nc')
    gemm_lri     = xr.open_dataset(u_dir_health_data+u_filename_pre+'GEMM_LRI'+'_'+u_scenario+'_'+u_res+'.nc')
    gemm_ncd_lri = gemm_ncd + gemm_lri

    u_filename_output = u_filename_pre+'GEMM_NCD_LRI'+'_'+u_scenario+'_'+u_res+'.nc'
    gemm_ncd_lri.to_netcdf(u_dir_health_data+u_filename_output, mode='w')

#    print(gemm_ncd[fg_cm].sum())
#    print(gemm_lri[fg_cm].sum())
    print('GEMM NCD+LRI',gemm_ncd_lri[fg_cm].sum().values)
    
    return


print('combined health effects: GEMM NCD+LRI')
dir_health_data = './ResultData/HealthResult/'

fg_list_scenario = ['BL_ID','BL_I','BL_D','BL_NoShip','S1N0_ID','S2N0_ID','S1N1_ID']
for scenario in fg_list_scenario:
    cal_combined_health_gemm_ncd_lri(dir_health_data, scenario)

    

## difference of scenarios: GEMM NCD+LRI --------------------------------------------------------------------------------------------
print('difference of scenarios: GEMM NCD+LRI')

dir_health_data = './ResultData/HealthResult/'

fg_pl       = 'PM25'
fg_cm       = 'Mortality'


def cal_diff_health (u_cause, u_scenario_diff, u_scenario_1, u_scenario_2, u_dir_health):
    
    print('cal_diff_health', u_scenario_diff)
    
    u_filename_pre = 'Mortality_PM25_' 
    u_res          = '05x05'
    fg_cm          = ['Mortality']

    dr_1     = xr.open_dataset(u_dir_health+u_filename_pre+u_cause+'_'+u_scenario_1+'_'+u_res+'.nc')
    dr_2     = xr.open_dataset(u_dir_health+u_filename_pre+u_cause+'_'+u_scenario_2+'_'+u_res+'.nc')
    dr_1_2   = dr_1 - dr_2

    u_filename_output = u_filename_pre+u_cause+'_'+u_scenario_diff+'_'+u_res+'.nc'
    dr_1_2.to_netcdf(u_dir_health+u_filename_output, mode='w')
    
#    print(u_scenario_1, dr_1[fg_cm].sum().values)
#    print(u_scenario_2, dr_2[fg_cm].sum().values)
    print(u_scenario_diff, dr_1_2[fg_cm].sum().values)
    return

fg_list_cause    = ['GEMM_NCD_LRI','GEMM_NCD','GEMM_LRI']

fg_list_scenario = [['BL_ID_BL_I'     , 'BL_ID'   , 'BL_I'],
                    ['BL_ID_BL_D'     , 'BL_ID'   , 'BL_D'],
                    ['BL_ID_BL_NoShip', 'BL_ID'   , 'BL_NoShip'], 
                    ['BL_ID_S1N0_ID'  , 'BL_ID'   , 'S1N0_ID'], 
                    ['S1N0_ID_S2N0_ID', 'S1N0_ID' , 'S2N0_ID'], 
                    ['S1N0_ID_S1N1_ID', 'S1N0_ID' , 'S1N1_ID']
                   ]

for cause in fg_list_cause:
    for scenario in fg_list_scenario:
        cal_diff_health (cause, scenario[0], scenario[1], scenario[2], dir_health_data)




## --- regrid Mortality result: 0.5->2x2.5 ---------------------------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import xarray as xr
import xesmf as xe
import matplotlib.colors as colors
import os

import pandas as pd
import math


def regrid_gc_2x25_05x05(u_file_input, u_file_output):
    
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
    
    regridder_conserve = xe.Regridder(high_grid_with_bounds, low_grid_with_bounds, method='conservative')

    print(u_file_input)
    u_xr_health = xr.open_dataset(u_file_input)
    u_xr_health_regrid = regridder_conserve(u_xr_health)
    u_xr_health_regrid = u_xr_health_regrid*20
    print(u_xr_health['Mortality'].sum())
    print(u_xr_health_regrid['Mortality'].sum())
    
    u_xr_health_regrid.to_netcdf(u_file_output)
    u_xr_health.close()
    return


fg_dir_health_fig        = './Figure/'
fg_dir_health_data_2x25  = './ResultData/HealthResult/'
fg_dir_health_data_05x05 = './ResultData/HealthResult/'

list_files = ['BL_ID_BL_D', 'BL_ID_BL_I', 'BL_ID_S1N0_ID', 'S1N0_ID_S2N0_ID', 'S1N0_ID_S1N1_ID']

for i in list_files:
    filename_pre = 'Mortality_PM25_GEMM_NCD_LRI_'
    file_input   = fg_dir_health_data_05x05 + filename_pre + i + '_05x05'+ '.nc'
    file_output  = fg_dir_health_data_2x25  + filename_pre + i + '_2x25' + '.nc'
    xr_health_regrid = regrid_gc_2x25_05x05(file_input, file_output)
