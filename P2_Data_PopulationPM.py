## PopulationPM
## generate files combining population and PM data

import numpy as np
import pandas as pd
import xarray as xr
import os


def pop_age_2015(u_dir_output, u_filename_o, file_age, var_age, file_pop, var_pop): ## step1: prepare population data
    
    print(u_dir_output, u_filename_o)
    print(file_age, var_age)
    print(file_pop, var_pop)

    ## grid-based population 2010 --> age structure
    demog = xr.open_dataset(file_age)
    print(demog)

    demog_var = var_age
    pop_all   = demog[demog_var][0]
    pop_0_4   = demog[demog_var][1]
    pop_5_9   = demog[demog_var][2]
    pop_10_14 = demog[demog_var][3]
    pop_15_19 = demog[demog_var][4]
    pop_20_24 = demog[demog_var][5]
    pop_25_29 = demog[demog_var][6]
    pop_30_34 = demog[demog_var][7]
    pop_35_39 = demog[demog_var][8]
    pop_40_44 = demog[demog_var][9]
    pop_45_49 = demog[demog_var][10]
    pop_50_54 = demog[demog_var][11]
    pop_55_59 = demog[demog_var][12]
    pop_60_64 = demog[demog_var][13]
    pop_65    = demog[demog_var][14]
    area_land    = demog[demog_var][18]
    code_country = demog[demog_var][20]

    ## ratio of 25plus in 2010 
    pop_25plus = pop_25_29+pop_30_34+pop_35_39+pop_40_44+pop_45_49+pop_50_54+pop_55_59+pop_60_64+pop_65

    ## grid-based population 2015 --> total population of the year
    pop_count     = xr.open_dataset(file_pop)
    pop_count_var = var_pop
    pop2015       = pop_count[pop_count_var][3]

    ## combine the selected variables
    del code_country['raster']
    code_country.name = 'code_country'

    del pop_all['raster']
    pop_all.name = 'pop2010_all'

    del pop_25plus['raster']
    pop_25plus.name = 'pop2010_25plus'

    del pop2015['raster']
    pop2015.name = 'pop2015_all'

    dr_pop_country = xr.merge([code_country,pop_all,pop_25plus,pop2015])

    ## estimate 25+ population of 2015 
    dr_pop_country['ratio_25plus_2010'] = dr_pop_country['pop2010_25plus']/dr_pop_country['pop2010_all']
    dr_pop_country['pop2015_25plus']    = dr_pop_country['pop2015_all']*dr_pop_country['ratio_25plus_2010']

    ## output to netcdf file
    dr_pop_country.to_netcdf(u_dir_output+u_filename_o+'.nc4',mode='w')

    ## output to csv file
    df_pop_country = dr_pop_country.to_dataframe().reset_index()
    df_pop_country.rename(columns={'latitude':'lat', 'longitude':'lon'}, inplace=True)
    df_pop_country.to_csv(u_dir_output+u_filename_o+'.csv',index=False)

    return


def main_gc_pop(u_df_pop,u_file_pm_i,u_file_pop_pm_o): ## step2: gridded population-PM
    
    ## I/O
    u_file_pm_i_nc = u_file_pm_i+'.nc'
    print(u_file_pm_i_nc)
    
    u_file_pop_pm_o_csv = u_file_pop_pm_o+'.csv'
    print(u_file_pop_pm_o_csv)
#    u_cms_output = ['lat','lon','code_country','pop2015_all','ratio_25plus_2010','pop2015_25plus']
    
    ## combine population data and PM data
    u_xr_pm  = xr.open_dataset(u_file_pm_i_nc)   
    u_df_pm  = u_xr_pm.to_dataframe().reset_index()
    u_df_pop_pm = u_df_pm.merge(u_df_pop,how='left',on=['lat','lon'])

    ## output to csv file
#    u_df_pop_pm = u_df_pop_pm[u_cms_output]
    print(u_df_pop_pm['pop2015_all'].sum())
    print(u_df_pop_pm['pop2015_25plus'].sum())
    print(u_df_pop_pm.columns.tolist())

    u_df_pop_pm.to_csv(u_file_pop_pm_o_csv,index=False)
    
    ## close
    u_xr_pm.close()
    
    return


## ==============================================================================================================================
## Step 1: prepare gwp data -- get population data of 25plus in 2015

## I/O
file_age_2010 = './InputData/Population/gpw_v4_basic_demographic_characteristics_rev11_bt_2010_cntm_30_min.nc'
var_age_2010  = 'Basic Demographic Characteristics, v4.10 (2010): Both, Count, 30 arc-minutes'

file_pop_2015 = './InputData/Population/gpw_v4_population_count_adjusted_to_2015_unwpp_country_totals_rev11_totpop_30_min.nc'
var_pop_2015  = 'UN WPP-Adjusted Population Count, v4.11 (2000, 2005, 2010, 2015, 2020): 30 arc-minutes'

dir_pop_age_data  = './ResultData/PopulationPM/'
filename_pop_age  = 'geo_pop_25plus_ratio_2015'

## processing
pop_age_2015(dir_pop_age_data, filename_pop_age, file_age_2010, var_age_2010, file_pop_2015, var_pop_2015)

print('made pop_age_2015')


## ==============================================================================================================================
## Step 2: combine data of regrided GC concentraiton and GPW population data

## I/O
dir_pop_pm_data = './ResultData/PopulationPM/'
dir_PM_annual_data  = './ResultData/GEOSChemAnnualPM/'
filename_gc_pre = 'YAVG_Conc_PM25'
res = '05x05'

## input pop file
file_pop_df = './ResultData/PopulationPM/geo_pop_25plus_ratio_2015.csv'
df_pop = pd.read_csv(file_pop_df)
print(df_pop.head(5))
print(df_pop['pop2015_all'].sum())
print(df_pop['pop2015_25plus'].sum())

## regrid and combine pop-gc data
list_scenario = ['BL_ID','BL_I','BL_D','BL_NoShip','S1N0_ID','S2N0_ID','S1N1_ID']
for scenario_one in list_scenario:
    file_pm_input      = dir_PM_annual_data+filename_gc_pre+'_'+scenario_one+'_'+res
    file_pop_pm_output = dir_pop_pm_data + 'pop_' + filename_gc_pre+'_'+scenario_one+'_'+res
    main_gc_pop(df_pop,file_pm_input,file_pop_pm_output)


print('Done')

## End of Program ##    