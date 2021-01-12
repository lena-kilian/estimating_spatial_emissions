#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  12 11:21:43 2021

Find income for LSOA/MSOA using LCFS

@author: lenakilian
"""

import pandas as pd
#import seaborn as sns
#import matplotlib.pyplot as plt
import LCFS_sociodem_functions as lcfs_sd
import copy as cp

results_filepath = 'Results/lcfs_results/'
lcf_filepath = 'LCFS/'

years = list(range(2001,2018))
years_07 = list(range(2007,2018))

gor_lookup = pd.read_excel('LCFS/2016-2017/mrdoc/excel/8351_volume_f_derived_variables_201617_final.xls', sheet_name='Part 4').iloc[920:932, 1:3]
gor_lookup.columns=['GOR_name', 'GOR modified']

# load LFC data
sociodem_lcfs = {}
lcf_years = [#'2002-2003', '2003-2004', '2004-2005', '2005-2006', '2006', 
             '2007', '2008', '2009', '2010', 
             '2011', '2012', '2013', '2014', '2015-2016', '2016-2017', '2017-2018']

for year in lcf_years:
    file_dvhh = lcf_filepath + year + '/tab/' + year + '_dvhh_ukanon.tab'
    file_dvper = lcf_filepath + year + '/tab/' + year + '_dvper_ukanon.tab'
    first_year = eval(year[:4])
    sociodem_lcfs[first_year] = lcfs_sd.import_lcfs_income(first_year, file_dvhh, file_dvper).drop_duplicates()
    for col in ['GOR modified', 'OAC_Supergroup', 'OAC_Group', 'OAC_Subgroup']:
        sociodem_lcfs[first_year][col] = sociodem_lcfs[first_year][col].astype(str).str.upper().str.replace(' ', '')
        sociodem_lcfs[first_year].loc[sociodem_lcfs[first_year][col].str.len() < 1, col] = '0'
    sociodem_lcfs[first_year]['GOR modified'] = sociodem_lcfs[first_year]['GOR modified'].astype(int)
    


## CONTINUE 

# check missing OAC distribution
hhdspend_missingoac, hhdspend_product = lcfs_agg.check_missing_oac(hhdspend_lcfs, years_07)


# check totals per group
# these are all OAs in the UK
all_oac = pd.read_excel('Output Area Classification/OACxRegion.xlsx', sheet_name=None)
for year in ['2001', '2011']:
    all_oac[year]['GOR'] = all_oac[year]['GOR modified']
    all_oac[year]['Supergroup'] = all_oac[year]['Supergroup'].astype(str)
    

# count OAC Subgroups in LCFS
full_index_lookup, full_index = lcfs_agg.count_oac(hhdspend_lcfs, all_oac, years_07)

# Attach OAC expenditure to index
full_exp = lcfs_agg.attach_exp(hhdspend_lcfs, full_index, years_07)
full_exp_c = lcfs_agg.attach_exp(hhdspend_lcfs_c, full_index, [2014, 2015, 2016])


#  Aggregate expenditure
hhdspend_full_index, hhdspend_oac = lcfs_agg.agg_groups(hhdspend_lcfs,full_exp, years_07)
hhdspend_full_index_c, hhdspend_oac_c = lcfs_agg.agg_groups(hhdspend_lcfs, full_exp_c, [2014, 2015, 2016])


# save expenditure profiles
[hhdspend_full_index[year].to_csv(lcf_filepath + 'lcfsXoac/detailed_groups_' + str(year) + '.csv') for year in years_07]
[hhdspend_full_index_c[year].to_csv(lcf_filepath + 'lcfsXoac/detailed_groups_controls_' + str(year) + '.csv') for year in [2014, 2015, 2016]]

for region in ['GOR', 'no_GOR']:
    for level in ['Supergroup', 'Group', 'Subgroup']:
        for year in [2014, 2015, 2016]:
            filename = str(year) + '_' + level + '_' + region
            hhdspend_oac_c[year][region][level].to_csv(lcf_filepath + 'lcfsXoac/' + filename + '_controls.csv')
        for year in years_07:
            filename = str(year) + '_' + level + '_' + region
            hhdspend_oac[year][region][level].to_csv(lcf_filepath + 'lcfsXoac/' + filename + '.csv')