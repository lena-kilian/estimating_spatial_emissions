#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 2021

Aggregating expenditure groups for LCFS by OAC x Region Profiles & UK Supergroups

@author: lenakilian
"""

import pandas as pd
import LCFS_functions as lcfs
import LCFS_aggregation_functions as lcfs_agg

results_filepath = 'Results/lcfs_results/'
lcfs_filepath = 'LCFS/'


gor_lookup = pd.read_excel('LCFS/2016-2017/mrdoc/excel/8351_volume_f_derived_variables_201617_final.xls', sheet_name='Part 4').iloc[920:932, 1:3]
gor_lookup.columns=['GOR_name', 'GOR modified']


lcf_years = ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015-2016', '2016-2017', '2017-2018']
years = [int(year[:4]) for year in lcf_years]

# load LFC data
hhdspend_lcfs = {}

for year in lcf_years:
    file_dvhh = lcfs_filepath + year + '/tab/' + year + '_dvhh_ukanon.tab'
    file_dvper = lcfs_filepath + year + '/tab/' + year + '_dvper_ukanon.tab'
    first_year = eval(year[:4])
    hhdspend_lcfs[first_year] = lcfs.import_lcfs(first_year, file_dvhh, file_dvper).drop_duplicates()
    for col in ['GOR modified', 'OAC_Supergroup', 'OAC_Group', 'OAC_Subgroup']:
        hhdspend_lcfs[first_year][col] = hhdspend_lcfs[first_year][col].astype(str).str.upper().str.replace(' ', '')
        hhdspend_lcfs[first_year].loc[hhdspend_lcfs[first_year][col].str.len() < 1, col] = '0'
    hhdspend_lcfs[first_year]['GOR modified'] = hhdspend_lcfs[first_year]['GOR modified'].astype(int)

    
# LCFS with physical units
flights = pd.read_excel('LCFS/Controls/flights.xlsx', sheet_name=None)
rent = pd.read_excel('LCFS/Controls/rent.xlsx', sheet_name=None)


for year in years:
    # flights
    flights[str(year)] = flights[str(year)].set_index('case')
    hhdspend_lcfs[year]['7.3.4.1'] = flights[str(year)]['Domestic']
    hhdspend_lcfs[year]['7.3.4.2'] = flights[str(year)]['International']
    # rent
    rent[str(year)] = rent[str(year)].set_index('case')
    hhdspend_lcfs[year]['4.1.1'] = rent[str(year)]['4.1.1_proxy']
    hhdspend_lcfs[year]['4.1.2'] = rent[str(year)]['4.1.2_proxy']

# check missing OAC distribution
hhdspend_missingoac, hhdspend_product = lcfs_agg.check_missing_oac(hhdspend_lcfs, years)


# check totals per group
# these are all OAs in the UK
all_oac = pd.read_excel('Output Area Classification/OACxRegion.xlsx', sheet_name=None)
for year in ['2001', '2011']:
    all_oac[year]['GOR'] = all_oac[year]['GOR modified']
    all_oac[year]['Supergroup'] = all_oac[year]['Supergroup'].astype(str)
    

# count OAC Subgroups in LCFS
full_index_lookup, full_index = lcfs_agg.count_oac(hhdspend_lcfs, all_oac, years)

[full_index[year].to_csv('LCFS/lcfsXoac/Index/oac_gor_index_' + str(year) + '.csv') for year in list(full_index.keys())]

# Attach OAC expenditure to index
full_exp = lcfs_agg.attach_exp(hhdspend_lcfs, full_index, years)


#  Aggregate expenditure
hhdspend_full_index, hhdspend_oac = lcfs_agg.agg_groups(hhdspend_lcfs,full_exp, years)

# save expenditure profiles
[hhdspend_full_index[year].to_csv(lcfs_filepath + 'lcfsXoac/detailed_groups_' + str(year) + '.csv') for year in years]

for region in ['GOR', 'no_GOR']:
    for level in ['Supergroup', 'Group', 'Subgroup']:
        for year in years:
            filename = str(year) + '_' + level + '_' + region
            hhdspend_oac[year][region][level].to_csv(lcfs_filepath + 'lcfsXoac/' + filename + '.csv')