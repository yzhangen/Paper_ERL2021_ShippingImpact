## Table 1

import pandas as pd
import numpy as np

def table_emission_sum(u_cal, file_input):
    cms_stat = ['CO2','SO2','SO4','NO2','CO','EC','OC','NMVOC','NH3']
    df = pd.read_csv(file_input)
    df = df[cms_stat]
    df_sum = df.sum().reset_index(name=u_cal)
    df_sum[u_cal+'_10^6kg'] = df_sum[u_cal].apply(lambda x: '%.3g' %(x/1000))
    return df_sum


def table_emission_ratio(df):
    df['IV_ratio'] = df['IV']/df['IV+DV']
    df['DV_ratio'] = df['DV']/df['IV+DV']
    df['IV_ratio'] = df['IV_ratio'].apply(lambda x: "{:.1f}%".format(x*100))
    df['DV_ratio'] = df['DV_ratio'].apply(lambda x: "{:.1f}%".format(x*100))
    return df
    

BL_I = table_emission_sum('IV','./ResultData/ShipEmissionAnnual/BL/gb_Latitude_Longitude_2015_I.csv')
BL_D = table_emission_sum('DV','./ResultData/ShipEmissionAnnual/BL/gb_Latitude_Longitude_2015_D.csv')
BL_ID = table_emission_sum('IV+DV', './ResultData/ShipEmissionAnnual/BL/gb_Latitude_Longitude_2015_ID.csv')
BL = BL_ID.merge(BL_I, how='left', on=['index']).merge(BL_D, how='left', on=['index'])
BL = table_emission_ratio(BL)
BL = BL[['index','IV+DV_10^6kg', 'IV_10^6kg', 'IV_ratio', 'DV_10^6kg', 'DV_ratio']]
BL.to_csv('./Table/Table1_Emission_Baseline.csv', index=False)


print(BL_I)
print(BL_D)
print(BL_ID)
print(BL)

