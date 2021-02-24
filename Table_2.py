## Table 2

import pandas as pd
import numpy as np

def table_emission_sum(u_cal, file_input):
    cms_stat = ['CO2','SO2','SO4','NO2','CO','EC','OC','NMVOC','NH3']
    df = pd.read_csv(file_input)
    df = df[cms_stat]
    df_sum = df.sum().reset_index(name=u_cal)
    df_sum[u_cal+'_10^6kg'] = df_sum[u_cal].apply(lambda x: '%.3g' %(x/1000))
    return df_sum


def table_emission_scenario(u_scenario):
    df_IV = table_emission_sum(u_scenario+'_IV','./ResultData/ShipEmissionAnnual/'+u_scenario+'/gb_Latitude_Longitude_2015_I.csv')
    df_DV = table_emission_sum(u_scenario+'_DV','./ResultData/ShipEmissionAnnual/'+u_scenario+'/gb_Latitude_Longitude_2015_D.csv')
    df = df_IV.merge(df_DV, how='left', on=['index'])
    df = df[['index', u_scenario+'_IV_10^6kg', u_scenario+'_DV_10^6kg']]
    print(u_scenario, df)
    return df

BL = table_emission_scenario('BL')
S1N0 = table_emission_scenario('S1N0')
S2N0 = table_emission_scenario('S2N0')
S1N1 = table_emission_scenario('S1N1')

df = BL.merge(S1N0, how='left', on='index').merge(S2N0, how='left', on='index').merge(S1N1, how='left', on='index')
print(df)

df.to_csv('./Table/Table2_Emission_Scenarios.csv', index=False)
