#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:15:25 2021

@author: lenakilian
"""

import pandas as pd

data_directory = "/Users/lenakilian/Documents/Ausbildung/UoLeeds/PhD/Analysis"
output_directory = "/Users/lenakilian/Documents/Ausbildung/UoLeeds/PhD/Analysis/Spatial_Emissions"

lookup = pd.read_csv(eval("r'" + data_directory + "/data/raw/Geography/Conversion_Lookups/UK_full_lookup_2001_to_2011.csv'"))
lookup_msoa = lookup[['MSOA01CD', 'MSOA11CD']].drop_duplicates()

inflation = [1.32, 1.27, 1.28, 1.22, 1.16, 1.12, 1.09, 1.06, 1.05, 1.04, 1.0]  

ghg = {}; data = {}; income = {}
for year in range(2007, 2017, 2):
    for yr in [year, year+1]:
        # import ghg and income
        ghg[yr] = pd.read_csv(eval("r'" + data_directory + "/data/processed/GHG_Estimates/MSOA_" + str(yr) + ".csv'"), index_col=0)
        ghg[yr].index.name = 'MSOA'
        income[yr] = pd.read_csv(eval("r'" + data_directory + "/data/processed/Income/UK_Income_MSOA_" + str(yr) + ".csv'"), index_col=0)
        income[yr]['Income anonymised'] = income[yr]['Income anonymised'] *  inflation[year-2007]

        ghg[yr] = ghg[yr].join(income[yr][['Income anonymised']])
        
        idx = ghg[year].loc[:,'1.1.1.1':'12.5.3.5'].columns.tolist() + ['Income anonymised']
        ghg[yr][idx] = ghg[yr][idx].apply(lambda x: x * ghg[yr]['population'])
    
    if year == 2013:
        ghg[2013] = ghg[2013].join(lookup_msoa.set_index('MSOA01CD'), how='right').set_index('MSOA11CD').mean(axis=0, level=0, skipna=True).fillna(0)
    else:
        pass
    
    name = str(year) + '-' + str(year+1)
    data[name] = pd.DataFrame(columns=ghg[year+1].columns, index = ghg[year+1].index)
    for item in idx:
        temp = ghg[year][[item, 'population']].join(ghg[year + 1][[item, 'population']], lsuffix='_yr1', rsuffix='_yr2')
        temp['total_item'] = temp[item + '_yr1'] + temp[item + '_yr2']
        temp['total_pop'] = temp['population_yr1'] + temp['population_yr2']
        temp['mean_item'] = temp['total_item'] / temp['total_pop']
        data[name][item] = temp['mean_item']
    data[name]['population'] = temp[['population_yr1', 'population_yr2']].mean(1)
    # save output
    data[name].to_csv(eval("r'" + data_directory + "/data/processed/GHG_Estimates/MSOA_mean_" + name + ".csv'"))
