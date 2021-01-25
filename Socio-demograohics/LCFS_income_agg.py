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
#import copy as cp

lcfs_filepath = 'LCFS/'

years = list(range(2001,2018))
years_07 = list(range(2007,2018))

gor_lookup = pd.read_excel('LCFS/2016-2017/mrdoc/excel/8351_volume_f_derived_variables_201617_final.xls', sheet_name='Part 4').iloc[920:932, 1:3]
gor_lookup.columns=['GOR_name', 'GOR modified']

# load LFC data
sociodem_lcfs = {}
lcf_years = ['2007', '2008', '2009', '2010', 
             '2011', '2012', '2013', '2014', '2015-2016', '2016-2017', '2017-2018']
full_index = {}

for year in lcf_years:
    file_dvhh = lcfs_filepath + year + '/tab/' + year + '_dvhh_ukanon.tab'
    file_dvper = lcfs_filepath + year + '/tab/' + year + '_dvper_ukanon.tab'
    first_year = eval(year[:4])
    full_index[first_year] = pd.read_csv('LCFS/lcfsXoac/Index/oac_gor_index_' + str(first_year) + '.csv')
    sociodem_lcfs[first_year] = lcfs_sd.import_lcfs_income(first_year, file_dvhh, file_dvper).drop_duplicates()
    for col in ['GOR modified', 'OAC_Supergroup', 'OAC_Group', 'OAC_Subgroup']:
        sociodem_lcfs[first_year][col] = sociodem_lcfs[first_year][col].astype(str).str.upper().str.replace(' ', '')
        sociodem_lcfs[first_year].loc[sociodem_lcfs[first_year][col].str.len() < 1, col] = '0'
    sociodem_lcfs[first_year]['GOR modified'] = sociodem_lcfs[first_year]['GOR modified'].astype(int)
    sociodem_lcfs[first_year] = sociodem_lcfs[first_year].merge(full_index[first_year], on=['GOR modified', 'OAC_Subgroup'])

for year in years_07:
    sociodem_lcfs[year]['pop'] = sociodem_lcfs[year]['weight'] * sociodem_lcfs[year]['no people']
    sociodem_lcfs[year]['income'] = sociodem_lcfs[year]['Income anonymised'] * sociodem_lcfs[year]['weight']
    sociodem_lcfs[year]['income_a_pc'] = sociodem_lcfs[year]['Income anonymised'] / sociodem_lcfs[year]['no people']
    
income_full_index = {}
for year in years_07:
    income_full_index[year] = sociodem_lcfs[year].groupby(['GOR', 'OAC']).sum()[['pop', 'income']]
    income_full_index[year]['income_pc'] = income_full_index[year]['income'] / income_full_index[year]['pop']

income_supergroup = {}
for year in years_07:
    income_supergroup[year] = sociodem_lcfs[year].groupby(['OAC_Supergroup']).sum()[['pop', 'income']]
    income_supergroup[year]['income_pc'] = income_supergroup[year]['income'] / income_supergroup[year]['pop']

# save expenditure profiles
[income_full_index[year].to_csv(lcfs_filepath + 'Income/detailed_groups_' + str(year) + '.csv') for year in years_07]
[income_supergroup[year].to_csv(lcfs_filepath + 'Income/UK_supergroups_' + str(year) + '.csv') for year in years_07]
