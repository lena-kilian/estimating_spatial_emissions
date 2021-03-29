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

# main function to run all above
def estimate_emissions(geog, first_year, last_year, combine_years, wd):
    hhdspend_lcfs_combined = lcfs_cy.import_expenditure(first_year, last_year, combine_years, wd)
    hhdspend_full_index, hhdspend_oac = lcfs_cy.attach_oac_grouping(hhdspend_lcfs_combined, wd)
    # import OAC data adjusted to mid-year populations
    oac_all = oac.get_oac_census(list(hhdspend_lcfs_combined.keys()), wd)
    OA_exp_detailed = lcfs_agg.detailed_oac_aggregation(hhdspend_full_index, oac_all, hhdspend_oac)
    OA_exp_detailed = {year : OA_exp_detailed[year].loc[:, :'12.5.3.5'] for year in list(hhdspend_lcfs_combined.keys())}
    # Aggregate to LSOA and MSOA level
    geog_exp_detailed = lcfs_agg.geog_aggregation(OA_exp_detailed, oac_all, list(OA_exp_detailed.keys()), geog)
    # Adjust household energy to physical units
    geog_exp_detailed = lcfs_cy.energy_adjust(geog, geog_exp_detailed, wd)
    
    return(geog_exp_detailed)
            

