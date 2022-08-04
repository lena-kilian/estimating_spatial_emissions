#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 09:19:27 2022

@author: lenakilian
"""

import LCFS_aggregation_combined_years as lcfs_cy
import copy as cp
import pandas as pd
import pickle
import LCFS_functions as lcfs
import demand_functions as dm
import numpy as np

wd = '/Users/lenakilian/Documents/Ausbildung/UoLeeds/PhD/Analysis'
geog = 'MSOA'
sd_limit = 3.5
oac_level = 'Group'

first_year = 2013
last_year = 2018
years = range(first_year, last_year+1)

# main function to run all above
combine_years = 1
hhdspend = lcfs_cy.import_expenditure(first_year, last_year, combine_years, wd)
hhdspend = lcfs_cy.winsorise(hhdspend, sd_limit)

pop = {}
for year in years:
    hhdspend[year] = hhdspend[year].fillna(0)
    hhdspend[year]['population'] = hhdspend[year]['weight'] * hhdspend[year]['no people']
    hhdspend[year].loc[:,'1.1.1.1':'12.5.3.5'] = hhdspend[year].loc[:,'1.1.1.1':'12.5.3.5']\
        .apply(lambda x: x * hhdspend[year]['weight'])
    hhdspend[year] = hhdspend[year].groupby('OAC_' + oac_level).sum()
    
    pop[year] = hhdspend[year][['population']]

    hhdspend[year] = hhdspend[year].loc[:,'1.1.1.1':'12.5.3.5']
    
    # cannot replace gas and electricity without spatial factor
    
#######################
# Calculate emissions #
#######################

# load meta data from [UKMRIO]
meta = pickle.load(open(eval("r'" + wd + "/data/raw/UKMRIO_2021/meta.p'"), "rb" ))
        
# load and clean up concs to make it usable
# these translate IO data sectors to LCFS products/services
concs_dict = pd.read_excel(eval("r'" + wd + "/data/raw/Concordances/COICOP_LCF_concs_2021.xlsx'"), sheet_name=None, index_col=0)
concs_dict2 = pd.read_excel(eval("r'" + wd + "/data/raw/Concordances/ONS_to_COICOP_LCF_concs_2021.xlsx'"), sheet_name=None, index_col=0)

#######################
# aggregate emissions #
#######################

# Load UKMRIO and calculate means for UKMRIO data
ukmrio = {}; #means = {}
for data in ['ghg', 'uk_ghg_direct', 'S', 'U', 'Y']:
    ukmrio[data] = pickle.load(open(eval("r'" + wd + "/data/raw/UKMRIO_2021/" + data + ".p'"), "rb" ))

ukmrio['Y'] = lcfs.convert36to33(ukmrio['Y'], concs_dict2, years)

total_Yhh_112 = dm.make_Yhh_112(ukmrio['Y'], years, meta)
    
coicop_exp_tot = lcfs.expected_totals(hhdspend, list(hhdspend.keys()), concs_dict2, total_Yhh_112)

yhh_wide = lcfs.make_y_hh_307(ukmrio['Y'], coicop_exp_tot, list(hhdspend.keys()), concs_dict2, meta)
newY = lcfs.make_new_Y(ukmrio['Y'], yhh_wide, meta, list(hhdspend.keys()))

ylcf_props = lcfs.make_ylcf_props(hhdspend, list(hhdspend.keys()))

COICOP_ghg = lcfs.makefoot(ukmrio['S'], ukmrio['U'], newY, ukmrio['ghg'], list(hhdspend.keys()))

Total_ghg = {}; PC_ghg = {}
for year in list(hhdspend.keys()):
    COICOP_ghg[year][160] += ukmrio['uk_ghg_direct'][year][1]
    COICOP_ghg[year][101] += ukmrio['uk_ghg_direct'][year][0]
    
    # this gives GHG emissions for the groups, break down to per capita emissions
    temp = np.dot(ylcf_props[year], np.diag(COICOP_ghg[year]))
    Total_ghg[year] = pd.DataFrame(temp, index=hhdspend[year].index, columns=hhdspend[year].columns)
    Total_ghg[year] = Total_ghg[year].join(pop[year])
    PC_ghg[year] = cp.copy(Total_ghg[year])
    PC_ghg[year].iloc[:,:-1] = PC_ghg[year].iloc[:,:-1].apply(lambda x: x/PC_ghg[year]['population'])
   
##################
# save emissions #
##################

for year in list(hhdspend.keys()):
    PC_ghg[year].to_csv(eval("r'" + wd + "/data/processed/GHG_Estimates/OAC_" + oac_level + '_' + str(year) + ".csv'"))
    print("Saved: " + wd + "/data/processed/GHG_Estimates/OAC_" + oac_level + '_' + str(year) + ".csv'")
