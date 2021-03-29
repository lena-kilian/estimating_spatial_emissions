#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 15:59:34 2021

@author: lenakilian
"""

import spatial_expenditure_main_function as spatial_expenditure
import LCFS_aggregation_combined_years as lcfs_cy
import estimate_emissions_main_function as estimate_emissions

wd = '/Users/lenakilian/Documents/Ausbildung/UoLeeds/PhD/Analysis/Predicting_Emissions'
geog = 'MSOA'
combine_years = 2

for geog in ['MSOA', 'LSOA']:
    for years in [[2007, 2012], [2014, 2017]]:
        first_year = years[0]
        last_year = years[1]

######################
# estimate emissions #
######################

        geog_exp_detailed = spatial_expenditure.estimate_emissions(geog, first_year, last_year, combine_years, wd)
        # save expenditure
        lcfs_cy.save_geog_expenditure(geog, geog_exp_detailed, wd)

######################
# estimate emissions #
######################

        pc_ghg = estimate_emissions.make_area_footprint(geog, first_year, last_year, wd)
        # Save MSOA or LSOA level GHG emissions
        estimate_emissions.save_footprint_data(pc_ghg, wd, 'MSOA')
