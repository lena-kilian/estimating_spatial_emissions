#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 2021

CO2 emissions for OAC groups of different regsion using the LCFS, IO part adapted from code by Anne Owen

@author: lenakilian
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import pickle
import LCFS_functions as lcfs
import geopandas as gpd

io_filepath = 'IO data/2020/'
lcf_filepath = 'LCFS/'
concs_filepath = 'Concordances/'
pop_filepath = 'Geography/Census Populations/'
shapes_filepath = 'Geography/Shapefiles/'
lookup_filepath = 'Geography/Conversion Lookups/'

years = list(range(2007,2018))

S = pickle.load(open(io_filepath + "S.p", "rb" ))
U = pickle.load(open(io_filepath + "U.p", "rb" ))
Y = pickle.load(open(io_filepath + "Y.p", "rb" ) )
meta = pickle.load(open(io_filepath + "meta.p", "rb" ))
ghg = pickle.load(open(io_filepath + "ghg.p", "rb" ))
uk_ghg_direct = pickle.load(open(io_filepath + "uk_ghg_direct.p", "rb" ))


# load LFC data
hhdspend_lcfsXoac = {}; hhdspend_supergroup = {}
for year in years:
    hhdspend_lcfsXoac[year] = pd.read_csv(lcf_filepath + 'lcfsXoac/detailed_groups_' + str(year) + '.csv', index_col = [0,1])
    # can change this to group or subgroup level --> check counts
    hhdspend_supergroup[year] = pd.read_csv(lcf_filepath + 'lcfsXoac/' + str(year) + '_Supergroup_no_GOR.csv')
    hhdspend_supergroup[year] = hhdspend_supergroup[year].loc[hhdspend_supergroup[year]['OAC_Supergroup'] != ' '].set_index('OAC_Supergroup')
        
# load and clean up concs to make it usable
concs_dict = pd.read_excel(os.path.join(concs_filepath, 'COICOP_LCF_concs.xlsx'), sheet_name=None)
concs_dict2 = pd.read_excel(os.path.join(concs_filepath, 'ONS_to_COICOP_LCF_concs.xlsx'), sheet_name=None)

for dictionary in ['concs_dict', 'concs_dict2']:
    concs = eval(dictionary)
    for item in concs.keys():
        concs[item] = concs[item].set_index('Unnamed: 0') 
        
lsoa_lookup = pd.read_csv('Geography/Conversion Lookups/UK_geography_conversions.csv')

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

#######################
# aggregate emissions #
#######################

COICOP_ghg, LCFSxOAC_ghg, PC_ghg = lcfs.lcfs_analysis(hhdspend_lcfsXoac, concs_dict, concs_dict2, Y, S, U, meta, ghg, uk_ghg_direct)
COICOP_ghg_detailed, LCFSxOAC_ghg_detailed, PC_ghg_detailed = lcfs.lcfs_analysis(
    hhdspend_lcfsXoac, concs_dict, concs_dict2, Y, S, U, meta, ghg, uk_ghg_direct)
COICOP_ghg_supergroup, supergroup_ghg, PC_ghg_supergroup = lcfs.lcfs_analysis(hhdspend_supergroup, concs_dict, concs_dict2, Y, S, U, meta, ghg, uk_ghg_direct)

UK_mean = [LCFSxOAC_ghg[year].sum().sum()/sum(hhdspend_lcfsXoac[year]['pop']) for year in years]

plt.scatter(x=years, y=UK_mean); plt.ylim(0, 14)

# spatial results
OA_ghg_detailed = lcfs.detailed_oac_aggregation(PC_ghg_detailed, oac_all, PC_ghg_supergroup)
for year in years:
    if year > 2010:
        oac_year = 2011
    else:
        oac_year = 2001
    if 'population' in OA_ghg_detailed[year].columns:
        OA_ghg_detailed[year] = OA_ghg_detailed[year].drop('population', axis=1)
    else:
        pass
    OA_ghg_detailed[year] = OA_ghg_detailed[year].join(oa_populations[oac_year].set_index('OA' + str(oac_year)[2:] + 'CD'))
# aggregatte to different geographies
LSOA_ghg_detailed = lcfs.geog_aggregation(OA_ghg_detailed, oac_all, years, 'LSOA')
MSOA_ghg_detailed = lcfs.geog_aggregation(OA_ghg_detailed, oac_all, years, 'MSOA')

#################
# save datasets #
#################

for area in ['MSOA', 'LSOA', 'OA']:
    for year in years:
        data = eval(area + '_ghg_detailed' + '[' + str(year) + ']')
        results_filepath = 'Estimating_Emissions/Outputs/' + area
        data.to_csv(results_filepath + '/ghg_detailed_' + str(year) + '.csv')