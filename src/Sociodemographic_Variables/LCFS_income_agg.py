#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  12 11:21:43 2021

Find income for LSOA/MSOA using LCFS

@author: lenakilian
"""

import OAC_census_functions as oac
import LCFS_aggregation_sociodem as lcfs_cy


wd = "/Users/lenakilian/Documents/Ausbildung/UoLeeds/PhD/Analysis/Predicting_Emissions"
geog = 'MSOA'
first_year = 2007
last_year = 2017
combine_years = 1

sociodem_lcfs_combined = lcfs_cy.import_socoidem_vars(first_year, last_year, combine_years, wd)

to_keep = ['weight', 'no people', 'GOR modified','OA class 1D', 'OAC_Supergroup', 'OAC_Group', 'OAC_Subgroup', 'Income anonymised', 'Income tax']
sociodem_lcfs_combined = {year : sociodem_lcfs_combined[year][to_keep] for year in list(sociodem_lcfs_combined.keys())}

sociodem_full_index, sociodem_oac = lcfs_cy.attach_oac_grouping(sociodem_lcfs_combined, wd)
# import OAC data adjusted to mid-year populations
oac_all = oac.get_oac_census(list(sociodem_lcfs_combined.keys()), wd)

OA_inc_detailed = lcfs_cy.detailed_oac_aggregation(sociodem_full_index, oac_all, sociodem_oac)
OA_inc_detailed = {year : OA_inc_detailed[year].loc[:, :'Income tax'] for year in list(sociodem_lcfs_combined.keys())}
# Aggregate to LSOA and MSOA level
geog_inc_detailed = lcfs_cy.geog_aggregation(OA_inc_detailed, oac_all, list(OA_inc_detailed.keys()), geog)

for year in list(geog_inc_detailed.keys()):
    fname = "r'" + wd + "/data/processed/LCFS/Income/UK_income_" + geog + "_" + str(year) + ".csv'"
    geog_inc_detailed[year].to_csv(eval(fname))

