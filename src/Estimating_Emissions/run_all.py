#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 15:59:34 2021

@author: lenakilian
"""

import spatial_expenditure_main_function as spatial_expenditure
import LCFS_aggregation_combined_years as lcfs_cy
import estimate_emissions_main_function_2021 as estimate_emissions


wd = '/Users/lenakilian/Documents/Ausbildung/UoLeeds/PhD/Analysis'
geog = 'MSOA'
combine_years = 2
sd_limit = 3.5

first_year = 2015
last_year = 2016


# cannot combine 2013 and 2014 - so have to take mean here!

for geog in ['MSOA']:#, 'LSOA']:
#########################
# aggregate expenditure #
#########################
    
    # aggregate expenditure for years if boundary crosses 20013 and 2014 
    if first_year <= 2013 and last_year >= 2013 and 2014 not in list(range(first_year, last_year, combine_years)) and combine_years > 1:
        print('Using mean expenditure for 2013 2014 OAC boundary crossing')
        
        geog_exp_detailed = {}; temp_exp = {}
        
        year_combinations = lcfs_cy.get_year_combinations(first_year, last_year, combine_years)
            
        if len(list(year_combinations.keys())) > 1:
            
            items = list(year_combinations.keys())
            items.remove('2013_boundary')
            
            for item in items:
                start_year = year_combinations[item][0]
                end_year = year_combinations[item][1]
    
                temp_exp = spatial_expenditure.estimate_expenditure(geog, start_year, end_year, combine_years, wd, sd_limit)
                
                for year in list(temp_exp.keys()):
                    geog_exp_detailed[year] = temp_exp[year]
        
        # OAC change after 2013, so need to combine datasets differently
        exp_by_year = spatial_expenditure.estimate_expenditure(geog, year_combinations['2013_boundary'][0], year_combinations['2013_boundary'][1], 1, wd, sd_limit)
        exp_mean_2013 = lcfs_cy.mean_spend_2013_bounday(exp_by_year, wd)
        
        geog_exp_detailed[year_combinations['2013_boundary'][0]] = exp_mean_2013
     
                 
    # aggregate expenditure for years if boundary does NOT cross 2013 and 2014 
    else:
        print('Using aggregated expenditure from OAC')
        geog_exp_detailed = spatial_expenditure.estimate_expenditure(geog, first_year, last_year, combine_years, wd, sd_limit)
        
    # save expenditure
    lcfs_cy.save_geog_expenditure(geog, geog_exp_detailed, wd)

######################
# estimate emissions #
######################

    pc_ghg = estimate_emissions.make_area_footprint(geog, first_year, last_year, wd)
    # Save MSOA or LSOA level GHG emissions
    estimate_emissions.save_footprint_data(pc_ghg, wd, geog)
