#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 14:19:05 2020

CO2 emissions for OAC groups of different regsion using the LCFS, IO part adapted from code by Anne Owen

@author: lenakilian
"""

'''
NOTES

still missing
- regional prices?
- pre-2007 findings

- missing a few output areas in detailed version
- some extreme results in detalied findints --> trim extrememly high?
'''


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
df = pd.DataFrame
import pickle
import LCFS_functions as lcfs
import demand_functions as dm
import geopandas as gpd
import copy as cp

io_filepath = 'IO data/'
lcf_filepath = 'LCFS/'
concs_filepath = 'Concordances/'
pop_filepath = 'Geography/Census Populations/'
shapes_filepath = 'Geography/Shapefiles/'
lookup_filepath = 'Geography/Conversion Lookups/'
results_filepath = 'Results/lcfs_results/'

years = list(range(2007,2017))

S = pickle.load( open(io_filepath + "S.p", "rb" ) )
U = pickle.load( open(io_filepath + "U.p", "rb" ) )
Y = pickle.load( open(io_filepath + "Y.p", "rb" ) )
meta = pickle.load( open(io_filepath + "meta.p", "rb" ) )
ghg = pickle.load( open(io_filepath + "ghg.p", "rb" ) )
uk_ghg_direct = pickle.load( open(io_filepath + "uk_ghg_direct.p", "rb" ) )

# load LFC data
hhdspend_lcfsXoac = {}; hhdspend_lcfsXoac_detailed = {}
for year in years:
    hhdspend_lcfsXoac[year] = pd.read_csv(lcf_filepath + 'lcfsXoac/data_' + str(year) + '.csv', index_col = [0,1])
    hhdspend_lcfsXoac_detailed[year] = pd.read_csv(lcf_filepath + 'lcfsXoac/detailed_groups_' + str(year) + '.csv', index_col = [0,1])

# use total UK, to ensure number of people in each household type ae taken into account
hhdspend_uk = {}; hhdspend_uk_detailed = {}
for year in years:
    temp = hhdspend_lcfsXoac[year].loc[:,'1.1.1.1':'12.5.3.5']
    hhdspend_uk[year] = temp.apply(lambda x: x * hhdspend_lcfsXoac[year]['pop'])
    hhdspend_uk[year].index = hhdspend_lcfsXoac[year].index
    
    temp = hhdspend_lcfsXoac_detailed[year].loc[:,'1.1.1.1':'12.5.3.5']
    hhdspend_uk_detailed[year] = temp.apply(lambda x: x * hhdspend_lcfsXoac_detailed[year]['pop'])
    hhdspend_uk_detailed[year].index = hhdspend_lcfsXoac_detailed[year].index

# load and clean up concs to make it usable
concs_dict = pd.read_excel(os.path.join(concs_filepath, 'COICOP_LCF_concs.xlsx'), sheet_name=None)
concs_dict2 = pd.read_excel(os.path.join(concs_filepath, 'ONS_to_COICOP_LCF_concs.xlsx'), sheet_name=None)

for item in concs_dict.keys():
    concs_dict[item] = concs_dict[item].set_index('Unnamed: 0') 
    
for item in concs_dict2.keys():
    concs_dict2[item] = concs_dict2[item].set_index('Unnamed: 0')

# use concs
for year in years:
    temp = np.dot(Y[year], concs_dict2['C43_to_C40'])
    Y[year] = df(temp, index = Y[year].index, columns = concs_dict2['C43_to_C40'].columns)

tax = np.multiply(concs_dict['vat'].iloc[:,0],concs_dict['vat'].iloc[:,1])

total_Yhh_106 = dm.make_Yhh_106(Y, years, meta)

coicop_exp_tot = lcfs.expected_totals(hhdspend_uk, years, concs_dict2, total_Yhh_106)
coicop_exp_tot_detailed = lcfs.expected_totals(hhdspend_uk_detailed, years, concs_dict2, total_Yhh_106)


yhh_wide = lcfs.make_y_hh_307(Y, coicop_exp_tot, years, concs_dict2, meta)
yhh_wide_detailed = lcfs.make_y_hh_307(Y, coicop_exp_tot_detailed, years, concs_dict2, meta)
    
#yhh_prop = lcfs.make_y_hh_prop(Y,total_Yhh_106,meta,years)

newY = lcfs.make_new_Y(Y,yhh_wide,meta,years)
newY_detailed = lcfs.make_new_Y(Y, yhh_wide_detailed, meta,years)

ylcf_props = lcfs.make_ylcf_props(hhdspend_uk, years)
ylcf_props_detailed = lcfs.make_ylcf_props(hhdspend_uk_detailed, years)


COICOP_ghg = lcfs.makefoot(S, U, newY, ghg, years)
COICOP_ghg_detailed = lcfs.makefoot(S, U, newY_detailed, ghg, years)

for year in years:
    COICOP_ghg[year][160] += uk_ghg_direct[year][1]
    COICOP_ghg[year][101] += uk_ghg_direct[year][0]
    
    COICOP_ghg_detailed[year][160] += uk_ghg_direct[year][1]
    COICOP_ghg_detailed[year][101] += uk_ghg_direct[year][0]
    
# this gives GHG emissions for the groups, break down to per capita emissions
LCFSxOAC_ghg = {}; PC_ghg = {}; no_gor = {}; LCFSxOAC_ghg_detailed = {}; PC_ghg_detailed = {}
for year in years:
    temp = np.dot(ylcf_props[year], np.diag(COICOP_ghg[year]))
    LCFSxOAC_ghg[year] = df(temp, index=hhdspend_uk[year].index, columns=hhdspend_uk[year].columns)
    PC_ghg[year] = LCFSxOAC_ghg[year].apply(lambda x: x/hhdspend_lcfsXoac[year]['pop'])
    # make check for those with missing OACs --> check that these are random, ie same distribution as others
    no_gor[year] = LCFSxOAC_ghg[year].join(hhdspend_lcfsXoac[year][['pop']]).reset_index()
    no_gor[year]['OAC'] = False; no_gor[year].loc[no_gor[year]['OAC_Supergroup'] > 0, 'OAC'] = True
    no_gor[year] = no_gor[year].set_index(['GOR modified', 'OAC_Supergroup', 'OAC'])
    no_gor[year].columns = pd.MultiIndex.from_arrays([[str(x).split('.')[0] for x in no_gor[year].columns.tolist()], [x for x in no_gor[year].columns.tolist()]])
    no_gor[year] = no_gor[year].sum(level=0, axis=1)
    no_gor[year] = no_gor[year].apply(lambda x: x/no_gor[year]['pop'])
    
    temp = np.dot(ylcf_props_detailed[year], np.diag(COICOP_ghg_detailed[year]))
    LCFSxOAC_ghg_detailed[year] = df(temp, index=hhdspend_uk_detailed[year].index, columns=hhdspend_uk_detailed[year].columns)
    PC_ghg_detailed[year] = LCFSxOAC_ghg_detailed[year].apply(lambda x: x/hhdspend_lcfsXoac_detailed[year]['pop'])


UK_mean = [LCFSxOAC_ghg[year].sum().sum()/sum(hhdspend_lcfsXoac[year]['pop']) for year in years]

plt.scatter(x=years, y=UK_mean); plt.ylim(0, 14)

# combine with OAs (2007-2013, and 2014-2016)
# waiting to hear back from ONS about 2001 data (for 2007-2013)

oac_shp = gpd.read_file('Output Area Classification/OAC Data/2011_OAC.shp').rename(columns={'SPRGRP':'OAC_Supergroup', 'GRP':'OAC_Group', 'SUBGRP':'OAC_Subgroup',})
rgn_lookup = pd.read_csv(lookup_filepath + 'OA11_RGN11_EN_LU.csv')
oac_england = oac_shp.merge(rgn_lookup.rename(columns={'OA11CD':'OA_SA', 'RGN11NM':'GOR_name'}), on ='OA_SA')
oac_scotland = oac_shp.loc[oac_shp['OA_SA'].str[0] == 'S']; oac_scotland['GOR_name'] = 'Scotland'
oac_northernireland = oac_shp.loc[oac_shp['OA_SA'].str[0] == 'N']; oac_northernireland['GOR_name'] = 'Northern Irlenad'
oac_wales = oac_shp.loc[oac_shp['OA_SA'].str[0] == 'W']; oac_wales['GOR_name'] = 'Wales'

oac_all = oac_england.drop('RGN11CD', axis=1).append(oac_scotland).append(oac_wales).append(oac_northernireland)

gor_lookup = pd.read_excel('LCFS/2016-2017/mrdoc/excel/8351_volume_f_derived_variables_201617_final.xls', sheet_name='Part 4').iloc[920:932, 1:3]
gor_lookup.columns=['GOR_name', 'GOR modified']
gor_lookup['GOR_code'] = gor_lookup['GOR_name'].str.lower().replace(' ', '')

keys = []
for item in oac_all['GOR_name'].tolist():
    if item not in keys:
        keys.append(item)
keys.sort()
values = gor_lookup.sort_values('GOR_name')['GOR modified'].tolist()
oac_all['GOR modified'] = oac_all['GOR_name'].replace(dict(zip(keys, values)))

oa_only = oac_all.drop('geometry', axis=1)

# supergroup only
OA_ghg = {}
for year in range(2014, 2017):
    OA_ghg[year] = oac_all.set_index(['GOR modified', 'OAC_Supergroup'])[['geometry']].join(PC_ghg[year])
    OA_ghg[year]['total_co2'] = OA_ghg[year].loc[:,'1.1.1.1':'12.5.3.5'].sum(1)

# detailed oac
Supergroup_list = []; Group_list = []; Subgroup_list = []
for year in years:
    PC_ghg_detailed[year] = PC_ghg_detailed[year].reset_index()
    PC_ghg_detailed[year]['OAC'] = PC_ghg_detailed[year]['OAC'].astype(str)

    PC_ghg_detailed[year] = PC_ghg_detailed[year].set_index(['GOR modified', 'OAC'])


OA_ghg_detailed = {}; oa_ghg = {}
for year in range(2014, 2017):
    oa_ghg[year] = {}
    ghg_data = PC_ghg_detailed[year].reset_index()
    ghg_data['Type'] = np.nan
    ghg_data.loc[ghg_data['OAC'].str.len() == 1, 'Type'] = 'OAC_Supergroup'
    ghg_data.loc[ghg_data['OAC'].str.len() == 2, 'Type'] = 'OAC_Group'
    ghg_data.loc[(ghg_data['OAC'].str.len() == 3) & (ghg_data['OAC'].str[-1].str.isdigit() == True), 'Type'] = 'OAC_Subgroup'
    ghg_data.loc[(ghg_data['GOR modified'] == 0)  & (ghg_data['OAC'].str[-1].str.isdigit() == True), 'Type'] = 'Mean'
    
    test = []
    oa_list = []
    for level in ['OAC_Subgroup', 'OAC_Group', 'OAC_Supergroup']:
        data = oa_only[['OA_SA', 'GOR modified', level]].set_index('OA_SA').drop(oa_list, axis=0).reset_index()
        data['OAC'] = data[level].astype(str).str.upper()
        temp = ghg_data.loc[ghg_data['Type'] == level].drop('Type', axis=1)
        
        data = data.merge(temp, on=['GOR modified', 'OAC'], how ='left').set_index(['GOR modified', 'OAC', 'OA_SA']).drop(level, axis=1).dropna(how='all')
        oa_ghg[year][level] = data
        
        oa_list += data.reset_index()['OA_SA'].tolist()
        
    data = oa_only[['OAC_Supergroup', 'OA_SA']].set_index('OA_SA').drop(oa_list, axis=0).reset_index().rename(columns={'OAC_Supergroup':'OAC'})
    data['OAC'] = data['OAC'].astype(str)
    temp = ghg_data.loc[ghg_data['Type'] == 'Mean'].drop('Type', axis=1)
    data = data.merge(temp, on=['OAC'], how ='left').set_index(['GOR modified', 'OAC', 'OA_SA']).dropna(how='all')
    oa_ghg[year]['Mean'] = data
    
    OA_ghg_detailed[year] = oa_ghg[year]['OAC_Subgroup'].append(oa_ghg[year]['OAC_Group']).append(oa_ghg[year]['OAC_Supergroup']).append(oa_ghg[year]['Mean'])
    OA_ghg_detailed[year]['total_co2'] = OA_ghg_detailed[year].loc[:,'1.1.1.1':'12.5.3.5'].sum(1)
    

# plots - these take a while to run
'''
for year in range(2014, 2017):
    temp = oac_all.set_index('OA_SA')[['geometry']].join(OA_ghg_detailed[year])
    temp.plot(column='total_co2', cmap='viridis', figsize=(20, 35), legend=True)
    plt.savefig(results_filepath + 'visuals/lcfsXoc_detailed_map' + str(year) + '.png', dpi=300)
    
    OA_ghg[year].plot(column='total_co2', cmap='viridis', figsize=(20, 35), legend=True)
    plt.savefig(results_filepath + 'visuals/lcfsXoc_map_' + str(year) + '.png', dpi=300)
'''

'''
ni_lad = pd.read_csv('Geography/Conversion Lookups/SA_to_LAD_NI.csv')
ni_lookup = pd.read_csv('Geography/Conversion Lookups/NorthernIreland_geography_conversion.csv')

ni_lookup = ni_lookup[['SA', 'SOA', 'WARD1992']].dropna(how='all').rename(columns={'SA':'SA2011'})
ni_lookup = ni_lookup.merge(ni_lad, on='SA2011')
ni_lookup.columns = ['OA11CD', 'LSOA11CD', 'MSOA11CD', 'LAD17CD', 'LAD17NM']
ni_lookup['RGN11CD'] = 'NI'; ni_lookup['RGN11NM'] = 'Northern Ireland'

lookup = pd.read_csv('Geography/Conversion Lookups/GB_geography_conversions.csv')
lookup = lookup[['OA11CD', 'LSOA11CD', 'MSOA11CD', 'LAD17CD', 'LAD17NM', 'RGN11CD', 'RGN11NM']].drop_duplicates()
lookup = lookup.append(ni_lookup)

lookup.to_csv('Geography/Conversion Lookups/UK_geography_conversions.csv')
'''

lsoa_lookup = pd.read_csv('Geography/Conversion Lookups/UK_geography_conversions.csv')

# import OA population data
oa_populations = {}
oa_populations['england_wales'] = pd.read_csv(pop_filepath + 'census2011_oa_pop_england_wales.csv').iloc[8:,:]
oa_populations['northern_ireland'] = pd.read_csv(pop_filepath + 'census2011_oa_pop_northern_ireland.csv').iloc[2:,1:3]
oa_populations['scotland'] = pd.read_csv(pop_filepath + 'census2011_oa_pop_scotland.csv').iloc[5:,:2]
for region in ['england_wales', 'northern_ireland', 'scotland']:
    oa_populations[region].columns = ['OA11CD', 'population']
    oa_populations[region] = oa_populations[region].dropna()
    oa_populations[region]['population'] = oa_populations[region]['population'].astype(str).str.replace(',', '').astype(int)
oa_populations['all'] = oa_populations['england_wales'].append(oa_populations['northern_ireland']).append(oa_populations['scotland'])

LSOA_ghg_detailed= {}; MSOA_ghg_detailed = {}
for year in range(2014, 2017):
    temp = cp.copy(OA_ghg_detailed[year])
    temp.index.names = ['GOR modified', 'OAC', 'OA11CD']
    temp = temp.join(oa_populations['all'].set_index('OA11CD'))
    
    temp.to_csv(results_filepath + 'data/OA_ghg_detailed_' + str(year) + '.csv')
    
    temp = temp.join(lsoa_lookup.set_index('OA11CD')[['LSOA11CD', 'MSOA11CD']])
    temp = temp.drop_duplicates().set_index(['LSOA11CD', 'MSOA11CD'], append=True)
    temp.loc[:,'1.1.1.1':'total_co2'] = temp.loc[:,'1.1.1.1':'total_co2'].apply(lambda x: x * temp['population'])
    
    LSOA_ghg_detailed[year] = temp.sum(level='LSOA11CD')
    LSOA_ghg_detailed[year].loc[:,'1.1.1.1':'total_co2'] = LSOA_ghg_detailed[year].loc[:,'1.1.1.1':'total_co2'].apply(lambda x: x / LSOA_ghg_detailed[year]['population'])
    LSOA_ghg_detailed[year].to_csv(results_filepath + 'data/LSOA_ghg_detailed_' + str(year) + '.csv')

    MSOA_ghg_detailed[year] = temp.sum(level='MSOA11CD')
    MSOA_ghg_detailed[year].loc[:,'1.1.1.1':'total_co2'] = MSOA_ghg_detailed[year].loc[:,'1.1.1.1':'total_co2'].apply(lambda x: x / MSOA_ghg_detailed[year]['population'])
    MSOA_ghg_detailed[year].to_csv(results_filepath + 'data/MSOA_ghg_detailed_' + str(year) + '.csv')