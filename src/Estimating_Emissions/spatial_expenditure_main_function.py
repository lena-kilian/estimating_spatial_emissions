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

# main function to run all above
def estimate_expenditure(geog, first_year, last_year, combine_years, wd, sd_limit):
    hhdspend_lcfs_combined = lcfs_cy.import_expenditure(first_year, last_year, combine_years, wd)
    hhdspend_lcfs_combined = lcfs_cy.winsorise(hhdspend_lcfs_combined, sd_limit)
    
    '''
    # extract regional expenditures
    regions = {}
    for year in list(hhdspend_lcfs_combined.keys()):
        regions[year] = cp.copy(hhdspend_lcfs_combined[year])
        regions[year]['population'] = regions[year]['weight'] * regions[year]['no people']
        regions[year].loc[:,'1.1.1.1':'12.5.3.5'] = regions[year].loc[:,'1.1.1.1':'12.5.3.5'].apply(lambda x: x*regions[year]['population'])
        regions[year] = regions[year].groupby('GOR modified').sum()
        regions[year] = regions[year][['population'] + regions[year].loc[:,'1.1.1.1':'12.5.3.5'].columns.tolist()]
    '''
    
    hhdspend_full_index, hhdspend_oac = lcfs_cy.attach_oac_grouping(hhdspend_lcfs_combined, wd)
    # import OAC data adjusted to mid-year populations
    oac_all = oac.get_oac_census(list(hhdspend_lcfs_combined.keys()), wd)
    OA_exp_detailed = lcfs_agg.detailed_oac_aggregation(hhdspend_full_index, oac_all, hhdspend_oac)
    OA_exp_detailed = {year : OA_exp_detailed[year].loc[:, :'12.5.3.5'] for year in list(hhdspend_lcfs_combined.keys())}
    # Aggregate to LSOA and MSOA level
    geog_exp_detailed = lcfs_agg.geog_aggregation(OA_exp_detailed, oac_all, list(OA_exp_detailed.keys()), geog)
    # Adjust household energy to physical units
    energy.get_energy_data(geog_exp_detailed, geog)
    geog_exp_detailed = lcfs_cy.energy_adjust(geog, geog_exp_detailed, wd)
    
    '''
    # adjust to regional expenditure
    new_exp = {}
    for year in list(geog_exp_detailed.keys()):
        if year < 2014:
            lookup = oac_all[year][[geog + '01CD', 'GOR modified']].drop_duplicates().dropna()
        else:
            lookup = oac_all[year][[geog + '11CD', 'GOR modified']].drop_duplicates().dropna()
        lookup.columns = [geog, 'GOR']
        new_exp = pd.DataFrame(columns = geog_exp_detailed[year].columns)
        for reg in regions[year].index:
            areas = lookup.loc[lookup['GOR'] == reg][geog].tolist()
            temp = geog_exp_detailed[year].reindex(index = areas)
            
            temp.loc[:,'1.1.1.1':'12.5.3.5'] = temp.loc[:,'1.1.1.1':'12.5.3.5'].apply(lambda x: x* temp['population'])
            
            for item in temp.loc[:,'1.1.1.1':'12.5.3.5'].columns:
                temp[item] = temp[item] / temp[item].sum() * regions[year].loc[reg, item]
            
            temp.loc[:,'1.1.1.1':'12.5.3.5'] = temp.loc[:,'1.1.1.1':'12.5.3.5'].apply(lambda x: x / temp['population'])
            
            new_exp = new_exp.append(temp)
    '''
    
    return(geog_exp_detailed)
