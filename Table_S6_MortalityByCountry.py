## Table S6, health by country


import os
import glob
import pandas as pd
import numpy as np
import gc


def mortality_combine_ncd_lri(sc, u_dir_data): ## calculate total mortality of NCD + LRI
    
    cms_stat = ['Mortality','Mortality_upper','Mortality_lower']
    cms_gb   = ['location_name_GBD']

    df_ncd = pd.read_csv(u_dir_data+'gb_location_Mortality_PM25_GEMM_NCD_'+sc+'.csv')[cms_gb+cms_stat]
    df_lri = pd.read_csv(u_dir_data+'gb_location_Mortality_PM25_GEMM_LRI_'+sc+'.csv')[cms_gb+cms_stat]

    for i in cms_stat:
        df_ncd = df_ncd.rename(columns={i: i+'_'+sc+'_NCD'})
        df_lri = df_lri.rename(columns={i: i+'_'+sc+'_LRI'})

    df_sc = df_ncd.merge(df_lri,how='left',on=cms_gb)

    for i in cms_stat:
        df_sc[i+'_'+sc] = df_sc[i+'_'+sc+'_NCD'] + df_sc[i+'_'+sc+'_LRI']
        
    df_sc = df_sc[cms_gb+['Mortality'+'_'+sc,'Mortality_upper'+'_'+sc,'Mortality_lower'+'_'+sc]]
        
    return df_sc


def mortality_gemm_diff(df, sc1, sc2, sc_diff, u_dir_data): ## calculate difference between simulations

    cms_stat = ['Mortality','Mortality_upper','Mortality_lower']
    cms_gb   = ['location_name_GBD']

    for i in cms_stat:
        df[i+'_'+sc_diff] = df[i+'_'+sc1] - df[i+'_'+sc2]
        
    return df


## I/O
dir_health_data  = './ResultData/HealthResult/'
dir_health_table = './Table/'
cms_stat = ['Mortality','Mortality_upper','Mortality_lower']


## calculate NCD + LRI
BL_I = mortality_combine_ncd_lri('BL_I', dir_health_data)
BL_D = mortality_combine_ncd_lri('BL_D', dir_health_data)
BL_ID = mortality_combine_ncd_lri('BL_ID', dir_health_data)
S1N0_ID = mortality_combine_ncd_lri('S1N0_ID', dir_health_data)
S2N0_ID = mortality_combine_ncd_lri('S2N0_ID', dir_health_data)
S1N1_ID = mortality_combine_ncd_lri('S1N1_ID', dir_health_data)

cm_loc = ['location_name_GBD']
df_sc_combine = BL_I.merge(BL_D,how='left',on=cm_loc).merge(BL_ID,how='left',on=cm_loc).merge(S1N0_ID,how='left',on=cm_loc).merge(S2N0_ID,how='left',on=cm_loc).merge(S1N1_ID,how='left',on=cm_loc)
print(df_sc_combine)


## calculate difference between simulations
dict_scenario_diff = {'scenario'          : ['scenario_1', 'scenario_2', 'diff'], 
                      'BL_ID_BL_I'        : ['BL_ID'     , 'BL_I'      , 'BL_ID_BL_I'], 
                      'BL_ID_BL_D'        : ['BL_ID'     , 'BL_D'      , 'BL_ID_BL_D'], 
                      'BL_ID_S1N0_ID'     : ['BL_ID'     , 'S1N0_ID'   , 'BL_ID_S1N0_ID'],
                      'S1N0_ID_S2N0_ID'   : ['S1N0_ID'   , 'S2N0_ID'   , 'S1N0_ID_S2N0_ID'],
                      'S1N0_ID_S1N1_ID'   : ['S1N0_ID'   , 'S1N1_ID'   , 'S1N0_ID_S1N1_ID']
                     }

list_diff_scenario = ['BL_ID_BL_I','BL_ID_BL_D','BL_ID_S1N0_ID','S1N0_ID_S2N0_ID','S1N0_ID_S1N1_ID']
for diff_sc in list_diff_scenario:
    sc1 = dict_scenario_diff[diff_sc][0]
    sc2 = dict_scenario_diff[diff_sc][1]
    sc_diff = dict_scenario_diff[diff_sc][2]
    df_sc_combine = mortality_gemm_diff(df_sc_combine, sc1, sc2, sc_diff, dir_health_data)


cms_stat = ['Mortality','Mortality_upper','Mortality_lower']
for i in cms_stat:
    df_sc_combine[i+'_BL_total'] = df_sc_combine[i+'_BL_ID_BL_I']+df_sc_combine[i+'_BL_ID_BL_D']
    

df_sc_combine = df_sc_combine.sort_values(['Mortality_BL_total'],ascending=False)
df_sc_combine['DV_rate'] = df_sc_combine['Mortality_BL_ID_BL_I']/df_sc_combine['Mortality_BL_total']
df_sc_combine['IV_rate'] = df_sc_combine['Mortality_BL_ID_BL_D']/df_sc_combine['Mortality_BL_total']

df_sc_combine.to_csv(dir_health_data+'gb_location_Mortality_PM25_GEMM_NCD_LRI_all.csv')


## output

df = df_sc_combine[['location_name_GBD', 'Mortality_BL_total', 'DV_rate','IV_rate',
                    'Mortality_BL_ID_S1N0_ID','Mortality_S1N0_ID_S2N0_ID','Mortality_S1N0_ID_S1N1_ID']]

cms_loc  = ['location_name_GBD']
cms_stat = ['Mortality_BL_total',
            'Mortality_BL_ID_S1N0_ID','Mortality_S1N0_ID_S2N0_ID','Mortality_S1N0_ID_S1N1_ID']
cms_rate = ['DV_rate','IV_rate']

#### format of data presentation
for i in cms_stat:
    df[i] = df[i].mask(df[i]<0,0)
    df[i] = df[i].apply(lambda x: '%.3g' %(x))  ## 3 sinificant number

for j in cms_rate:
    df[j] = df[j].mask(df[j]<0,0)    
    df[j] = df[j].apply(lambda x: "{:.0f}%".format(x*100)) ## %, no digit
    

df.to_csv(dir_health_table+'Table_S6_Mortality_ByCountry.csv', index=False)