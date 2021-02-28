## Table 3, Table S5, Health

import os
import glob
import pandas as pd
import numpy as np
import gc


def f1_filelist_in_folder(u_folder_path,u_extend_name): 
    u_filelist = glob.glob(u_folder_path + u_extend_name)
    u_filelist.sort()
    return u_filelist
    # eg. f1_filelist_in_folder('/.../','*.csv')


def gb_multi2one(u_dir_input,u_dir_output,u_filename_output): ## combine files to one
    print(u_filename_output)
    u_files = glob.glob(u_dir_input)
    u_files.sort()
    print(len(u_files))
    u_n=0
    u_df_m = pd.DataFrame()
    u_file_list = []
    for xy in range(0,len(u_files)):
        u_df_n = pd.read_csv(u_files[xy],index_col=None, header=0, dtype='object')
        u_file_list = [u_df_m,u_df_n]
        u_df_mn = pd.concat(u_file_list, ignore_index=True)
        u_df_m = u_df_mn.copy()               
        u_n+=1
        if u_n<len(u_files):
            collected=gc.collect()
            continue
        else:
            u_df_m.to_csv(u_dir_output+u_filename_output,index=False)
            break
    return


def cal_sc_diff(df, sc1, sc2, sc_diff): ## calculate difference of mortalities between simulations
    df_sc1 = df.query('scenario=="'+sc1+'"')[cms_stat]
    df_sc2 = df.query('scenario=="'+sc2+'"')[cms_stat]
    df_1_2 = pd.concat([df_sc1,df_sc2])
    df_1_2 = df_1_2.diff(periods=-1)
    df_1_2 = df_1_2.head(1)
    print(df_1_2)
    df_1_2['scenario'] = sc_diff
    return df_1_2


## I/O
dir_health_data  = './ResultData/HealthResult/'
dir_health_table = './Table/'
cms_stat = ['Mortality','Mortality_upper','Mortality_lower']


## combine health results from simulations

#### combine multiple files (NCD, LRI) to one
gb_multi2one(dir_health_data+'gb_cause_*.csv',dir_health_table,'Table_S5_statistic_by_cause.csv')

#### calculate sum of mortalities for GEMM NCD+LRI
df1 = pd.read_csv(dir_health_table+'Table_S5_statistic_by_cause.csv')
df1 = df1[['scenario','cause']+cms_stat]
df1_gb = df1.groupby(['scenario']).sum().reset_index()
df1_gb['cause'] = 'GEMM_NCD+LRI'
print(df1_gb)

df2 = pd.concat([df1,df1_gb])
df2 = df2.sort_values(['scenario','cause'])
df2 = df2[['scenario','cause']+cms_stat]

df2_3sf = df2.copy()
for i in cms_stat:
    df2_3sf[i] = df2_3sf[i].apply(lambda x: '%.3g' %(x/1000))

print('df2',df2)
df2_3sf.to_csv('./Table/'+'Table_S5_mortality_by_scenario.csv',index=False)


## difference by scenario

list_diff_scenario = ['BL_ID_BL_I','BL_ID_BL_D','BL_ID_S1N0_ID','S1N0_ID_S2N0_ID','S1N0_ID_S1N1_ID']
dict_scenario_diff = {'simulation'          : ['scenario_1', 'scenario_2', 'cal'], 
                      'BL_ID_BL_I'        : ['BL_ID'     , 'BL_I'      , 'BL_ID_BL_I'], 
                      'BL_ID_BL_D'        : ['BL_ID'     , 'BL_D'      , 'BL_ID_BL_D'], 
                      'BL_ID_S1N0_ID'     : ['BL_ID'     , 'S1N0_ID'   , 'BL_ID_S1N0_ID'],
                      'S1N0_ID_S2N0_ID'   : ['S1N0_ID'   , 'S2N0_ID'   , 'S1N0_ID_S2N0_ID'],
                      'S1N0_ID_S1N1_ID'   : ['S1N0_ID'   , 'S1N1_ID'   , 'S1N0_ID_S1N1_ID']
                     }

df3 = df2.query('cause=="GEMM_NCD+LRI"')

list_df_diff = []
for diff in list_diff_scenario:
    df_diff = cal_sc_diff(df3, dict_scenario_diff[diff][0], dict_scenario_diff[diff][1], dict_scenario_diff[diff][2])
    list_df_diff.append(df_diff)
    
df_diff_all = pd.concat(list_df_diff)
df_diff_all = df_diff_all[['scenario']+cms_stat]

for i in cms_stat:
    df_diff_all[i] = df_diff_all[i].apply(lambda x: '%.3g' %(x))

df_diff_all.to_csv(dir_health_table+'Table_3_statistic_diff_scenarios.csv')
