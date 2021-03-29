#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 2021

CO2 emissions for OAC groups of different regsion using the LCFS, IO part adapted from code by Anne Owen

@author: lenakilian
"""

import pandas as pd
import matplotlib.pyplot as plt
import copy as cp
import pickle
import LCFS_functions as lcfs
import geopandas as gpd

pop_filepath = 'Geography/Census Populations/'
shapes_filepath = 'Geography/Shapefiles/'
lookup_filepath = 'Geography/Conversion Lookups/'

years = list(range(2007, 2018))

PC_inc_detailed = {}; PC_inc_supergroup = {}
for year in years:
    PC_inc_detailed[year] = pd.read_csv('LCFS/Income/detailed_groups_' + str(year) + '.csv')
    PC_inc_supergroup[year] = pd.read_csv('LCFS/Income/UK_supergroups_' + str(year) + '.csv')
        
# combine with OAs (2007-2013, and 2014-2016)
# Region (GOR) lookup
gor_lookup = pd.read_excel('LCFS/2016-2017/mrdoc/excel/8351_volume_f_derived_variables_201617_final.xls', sheet_name='Part 4').iloc[920:932, 1:3]
gor_lookup.columns=['GOR_name', 'GOR modified']
gor_lookup['GOR_code'] = gor_lookup['GOR_name'].str.lower().str.replace(' ', '').str[:7]

oac_all = {}
# 2001 OAC
oac_2001 = pd.read_csv('Geography/Conversion Lookups/UK_full_lookup_2001.csv').drop_duplicates()
oac_2001.loc[oac_2001['RGN01NM'] == 'East', 'RGN01NM'] = 'Eastern'
oac_2001['GOR_code'] = oac_2001['RGN01NM'].str.lower().str.replace(' ', '').str[:7]
oac_2001 = oac_2001.merge(gor_lookup, on='GOR_code')
oac_all[2001] = oac_2001

# 2011 OAC
full_lookup = pd.read_csv('Geography/Conversion Lookups/UK_full_lookup_2001_to_2011.csv')

oac_2011 = full_lookup[['OAC11CD', 'OA11CD', 'LSOA11CD', 'MSOA11CD', 'LAD17NM', 'RGN11NM']].drop_duplicates()
oac_2011.loc[oac_2011['RGN11NM'] == 'East of England', 'RGN11NM'] = 'Eastern'
oac_2011['GOR_code'] = oac_2011['RGN11NM'].str.lower().str.replace(' ', '').str[:7]
oac_2011 = oac_2011.merge(gor_lookup, on='GOR_code')
oac_all[2011] = oac_2011

for year in [2001, 2011]:
    oac_all[year]['OAC_Supergroup'] = oac_all[year]['OAC' + str(year)[2:] + 'CD'].str[0]
    oac_all[year]['OAC_Group'] = oac_all[year]['OAC' + str(year)[2:] + 'CD'].str[:2]
    oac_all[year]['OAC_Subgroup'] = oac_all[year]['OAC' + str(year)[2:] + 'CD']
    oac_all[year]['OA_SA'] = oac_all[year]['OA' + str(year)[2:] + 'CD']

# import OA population data --> needed to move from LCFS x OAC population representation to census geographies
oa_populations = {}
oa_populations['england_wales'] = pd.read_csv(pop_filepath + 'census2011_pop_england_wales_oa.csv').iloc[8:,:]
oa_populations['northern_ireland'] = pd.read_csv(pop_filepath + 'census2011_pop_northern_ireland_oa.csv').iloc[2:,1:3]
oa_populations['scotland'] = pd.read_csv(pop_filepath + 'census2011_pop_scotland_oa.csv').iloc[5:,:2]
for region in ['england_wales', 'northern_ireland', 'scotland']:
    oa_populations[region].columns = ['OA11CD', 'population']
    oa_populations[region] = oa_populations[region].dropna()
    oa_populations[region]['population'] = oa_populations[region]['population'].astype(str).str.replace(',', '').astype(int)
oa_populations['all'] = oa_populations['england_wales'].append(oa_populations['northern_ireland']).append(oa_populations['scotland'])


oa_populations_01 = {}
oa_populations_01['england_wales'] = pd.read_csv(pop_filepath + 'census2001_pop_england_wales_oa.csv').iloc[8:-5,:]
oa_populations_01['northern_ireland'] = pd.read_csv(pop_filepath + 'census2001_pop_northern_ireland_oa.csv', header=5).iloc[:-3, :2]
oa_populations_01['scotland'] = pd.read_csv('Geography/Conversion Lookups/Scotland_PC_OA_2001.csv')\
    [['2001_OA_CODE', '2001_POPULATION']].groupby('2001_OA_CODE').sum().reset_index()
oa_populations_01['scotland'].columns = ['TAG', 'population']
s_tag = pd.read_csv('Geography/Conversion Lookups/Scotland_OA_conversion_2001-2011_w-Tag.csv')[['TAG', 'OA01CD']].drop_duplicates()
oa_populations_01['scotland'] = oa_populations_01['scotland'].merge(s_tag, on='TAG')
oa_populations_01['scotland'].to_csv(pop_filepath + 'census2001_pop_scotland_oa.csv')
oa_populations_01['scotland'] = oa_populations_01['scotland'][['population', 'OA01CD']]

for region in ['england_wales', 'northern_ireland']:
    oa_populations_01[region].columns = ['OA01CD', 'population']
oa_populations_01['all'] = oa_populations_01['england_wales'].append(oa_populations_01['northern_ireland'])\
    .append(oa_populations_01['scotland'])
    
oa_populations[2011] = oa_populations['all']
oa_populations[2001] = oa_populations_01['all']

for year in [2001, 2011]:
    oa_populations[year]['population'] = oa_populations[year]['population'].astype(float)
    oac_all[year] = oac_all[year].merge(oa_populations[year], on='OA' + str(year)[2:] + 'CD')        

# spatial results
hhdspend_full_index, hhdspend_oac = PC_inc_detailed, PC_inc_supergroup

OA_exp_detailed = {}
for year in list(hhdspend_full_index.keys()): 
    OAC_detailed = hhdspend_full_index[year]
    OAC_detailed['OAC'] = OAC_detailed['OAC'].str.upper()
    OAC_detailed['GOR modified'] = OAC_detailed['GOR']
    
    if year < 2013:
        oac_year = 2001
    else: 
        oac_year = 2011
    
    oac_temp = oac_all[oac_year].drop_duplicates().rename(columns={'OA01CD':'OA_Code', 'OA11CD':'OA_Code'})[
        ['OA_Code', 'GOR modified', 'OAC_Supergroup', 'OAC_Group', 'OAC_Subgroup', 'population']]
    
    temp = {}; OA_list = oac_temp['OA_Code'].to_list()
    for var in ['OAC_Subgroup', 'OAC_Group', 'OAC_Supergroup']:
        oac_var = oac_temp.loc[oac_temp['OA_Code'].isin(OA_list) == True]
        oac_var['OAC'] = oac_var[var].str.upper()
            
        temp[var] = oac_var[['OA_Code', 'GOR modified', 'OAC', 'population']]\
            .merge(OAC_detailed.drop('pop', axis=1), on=['GOR modified', 'OAC'], how='left')\
                .set_index(['OA_Code', 'GOR modified', 'OAC'])
                
        OA_list = temp[var].loc[temp[var]['income'].isna() == True].reset_index()['OA_Code'].to_list()
        temp[var] = temp[var].loc[temp[var]['income'].isna() == False]
  
    if len(OA_list) > 0:    
        oac_var = oac_temp.loc[oac_temp['OA_Code'].isin(OA_list) == True]
        oac_var['OAC'] = oac_var['OAC_Supergroup'].str.upper()
            
        temp_exp = hhdspend_oac[year].rename(columns={'OAC_Supergroup':'OAC'})
        temp_exp['OAC'] = temp_exp['OAC'].astype(str)
                
        temp['UK_all'] = oac_var[['OA_Code', 'GOR modified', 'OAC', 'population']]\
            .merge(temp_exp.drop('pop', axis=1), on=['OAC'], how='left')\
                .set_index(['OA_Code', 'GOR modified', 'OAC'])

    OA_exp_detailed[year] = temp['OAC_Subgroup'].append(temp['OAC_Group']).append(temp['OAC_Supergroup'])\
        .append(temp['UK_all'])

    
# aggregatte to different geographies
#LSOA_ghg_detailed = lcfs.geog_aggregation(OA_ghg_detailed, oac_all, years, 'LSOA')
MSOA_ghg_detailed = {}
for year in years:
    if year < 2013:
        oac_year = 2001
    else: 
        oac_year = 2011
    temp = cp.copy(OA_exp_detailed[year])
    temp.index = [x[0] for x in temp.index.tolist()]
    temp = temp.join(oac_all[oac_year].set_index('OA' + str(oac_year)[2:] + 'CD')[
        ['MSOA' + str(oac_year)[2:] + 'CD']])
    temp['income'] = temp['income_pc'] * temp['population']
    temp = temp[['population', 'income', 'MSOA' + str(oac_year)[2:] + 'CD']].groupby('MSOA' + str(oac_year)[2:] + 'CD').sum()
    temp['income_pc'] = temp['income'] / temp['population']
    MSOA_ghg_detailed[year] = temp
    
#################
# save datasets #
#################

for year in years:
    MSOA_ghg_detailed[year].to_csv('LCFS/Income/Income_MSOA_' + str(year) + '.csv')