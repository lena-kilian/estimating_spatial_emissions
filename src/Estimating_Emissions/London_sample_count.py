#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 2021

Aggregating expenditure groups for LCFS by OAC x Region Profiles & UK Supergroups

@author: lenakilian
"""

import LCFS_aggregation_functions as lcfs_agg
import OAC_census_functions as oac
import LCFS_aggregation_combined_years as lcfs_cy
import copy as cp
import pandas as pd
import LCFS_PhysicalUnits_GasElectricity as energy
import matplotlib.pyplot as plt
import seaborn as sns



wd = '/Users/lenakilian/Documents/Ausbildung/UoLeeds/PhD/Analysis'
geog = 'MSOA'
combine_years = 2
sd_limit = 3.5

# set font globally
plt.rcParams.update({'font.family':'Times New Roman'})

first_year = 2015
last_year = 2016

hhdspend_lcfs_combined = lcfs_cy.import_expenditure(first_year, last_year, combine_years, wd)
hhdspend_lcfs_combined = lcfs_cy.winsorise(hhdspend_lcfs_combined, sd_limit)
        
hhdspend_full_index, hhdspend_oac = lcfs_cy.attach_oac_grouping(hhdspend_lcfs_combined, wd)
# import OAC data adjusted to mid-year populations
oac_all = oac.get_oac_census(list(hhdspend_lcfs_combined.keys()), wd)


all_oac = pd.read_excel(wd + '/data/raw/Geography/Output_Area_Classification/OACxRegion.xlsx', sheet_name=None)
for year in ['2001', '2011']:
    all_oac[year]['GOR'] = all_oac[year]['GOR modified']
    all_oac[year]['Supergroup'] = all_oac[year]['Supergroup'].astype(str)

full_index_lookup, full_index = lcfs_agg.count_oac(hhdspend_lcfs_combined, all_oac, [2015])

check = full_index[2015].reset_index()
check = check.loc[check['GOR modified'] == '7']

oac_london = oac_all[2015].loc[oac_all[2015]['GOR modified'] == 7]
oac_london['OAC_Subgroup'] = oac_london['OAC_Subgroup'].str.upper()
check = check.merge(oac_london, on='OAC_Subgroup', how='right')
        
# extract London and count cample when converting to MSOA
London_count = check[['OAC', 'GOR', 'MSOA11CD', 'count']].drop_duplicates().groupby('MSOA11CD').sum()[['count']]
London_pop = oac_all[2015].loc[oac_all[2015]['GOR modified'] == 7].groupby('MSOA11CD').sum()[['population']]

London_count_pop = London_pop.join(London_count)
London_count_pop['count/pop'] = London_count_pop['count'] / London_count_pop['population']
London_count_pop['pop/count'] = London_count_pop['population'] / London_count_pop['count']

London_count_pop.columns = ['Population by MSOA', 'Number of Unique Observations by MSOA',
                            'Ration of Number of Unique Observations to Population by MSOA',
                            'Ration of Population to Number of Unique Observations by MSOA']

for item in London_count_pop.columns:
    fig, ax = plt.subplots(figsize=(15,7))
    sns.histplot(ax=ax, data=London_count_pop, x=item, color='#D3D3D3')
    plt.savefig(wd + '/Spatial_Emissions/outputs/Graphs/London_sample_count_' + item + '.png', bbox_inches='tight', dpi=300)
    plt.show()


