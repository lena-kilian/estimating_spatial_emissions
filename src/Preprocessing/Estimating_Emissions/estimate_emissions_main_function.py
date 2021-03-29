#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 2021

CO2 emissions for MSOAs or LSOAs combining 2 years at a time, IO part adapted from code by Anne Owen

@author: lenakilian
"""

import pandas as pd
import pickle
import LCFS_functions as lcfs
import copy as cp
import numpy as np
import demand_functions as dm

df = pd.DataFrame

def make_area_footprint(geog, first_year, last_year, working_directory):
    
    """
    Claculate consumption-based household GHG emissions for MSOAs or LSOAs from the LCFS (emissios calculated in LCFS_aggregation_combined_years.py) and the UKMRIO 2020
    
    geog = LSOA or MSOA as str
    first_year = first year to calculate footprint as int
    last_year = last year to calculate footprint as int
    working_directory = full working directory as str (without last '/')
    """
    
    # create data directory from working directory
    data_directory = working_directory + "/data/"

#############
# load data #
#############

    # load meta data from UKMRIO
    meta = pickle.load(open(eval("r'" + data_directory + "raw/UKMRIO_2020/meta.p'"), "rb" ))
    # load household spends
    hhdspend = pickle.load(open(eval("r'" + data_directory + "processed/LCFS/lcfsXoac/" + geog + "_expenditure.p'"), "rb" ))
    
    # create year lists
    years = list(hhdspend.keys())
    
    # load populations
    pop = {}
    for year in years:
        hhdspend[year] = hhdspend[year].drop_duplicates()
        pop[year] = hhdspend[year][['population']] / 1000
        hhdspend[year] = hhdspend[year].iloc[:,1:].apply(lambda x: x * hhdspend[year]['population'])

        
    # load and clean up concs to make it usable
    # these translate IO data sectors to LCFS products/services
    #concs_dict = pd.read_excel(eval("r'" + data_directory + "raw/Concordances/COICOP_LCF_concs.xlsx'"), sheet_name=None)
    concs_dict2 = pd.read_excel(eval("r'" + data_directory + "raw/Concordances/ONS_to_COICOP_LCF_concs.xlsx'"), sheet_name=None)

    for dictionary in ['concs_dict2']: #'concs_dict', 
        concs = eval(dictionary)
        for item in concs.keys():
            concs[item] = concs[item].set_index('Unnamed: 0') 

#######################
# aggregate emissions #
#######################

    # get mean from 2 years
    # calculate differnece between years in household data to calculate means for other vairables
    if len(years) > 1:
        difference = years[1] - years[0]
    else:
        difference = 0
    
    # Load UKMRIO and calculate means for UKMRIO data
    ukmrio = {}; means = {}
    for data in ['ghg', 'uk_ghg_direct', 'S', 'U', 'Y']:
        ukmrio[data] = pickle.load(open(eval("r'" + data_directory + "raw/UKMRIO_2020/" + data + ".p'"), "rb" ))
        means[data] = {}
        for year in years:
            temp = [ukmrio[data][year + i] for i in range(difference)]
            means[data][year] = sum(temp) / difference

    for year in list(hhdspend.keys()):
        # use concs
        temp = np.dot(means['Y'][year], concs_dict2['C43_to_C40'])
        means['Y'][year] = df(temp, index = means['Y'][year].index, columns = concs_dict2['C43_to_C40'].columns)

    total_Yhh_106 = dm.make_Yhh_106(means['Y'], list(hhdspend.keys()), meta)

    coicop_exp_tot = lcfs.expected_totals(hhdspend, list(hhdspend.keys()), concs_dict2, total_Yhh_106)

    yhh_wide = lcfs.make_y_hh_307(means['Y'], coicop_exp_tot, list(hhdspend.keys()), concs_dict2, meta)
    newY = lcfs.make_new_Y(means['Y'], yhh_wide, meta, list(hhdspend.keys()))
    ylcf_props = lcfs.make_ylcf_props(hhdspend, list(hhdspend.keys()))

    COICOP_ghg = lcfs.makefoot(means['S'], means['U'], newY, means['ghg'], list(hhdspend.keys()))

    Total_ghg = {}; PC_ghg = {}
    for year in list(hhdspend.keys()):
        COICOP_ghg[year][160] += means['uk_ghg_direct'][year][1]
        COICOP_ghg[year][101] += means['uk_ghg_direct'][year][0]
    
        # this gives GHG emissions for the groups, break down to per capita emissions
        temp = np.dot(ylcf_props[year], np.diag(COICOP_ghg[year]))
        Total_ghg[year] = df(temp, index=hhdspend[year].index, columns=hhdspend[year].columns)
        Total_ghg[year] = Total_ghg[year].join(pop[year])
        PC_ghg[year] = cp.copy(Total_ghg[year])
        PC_ghg[year].iloc[:,:-1] = PC_ghg[year].iloc[:,:-1].apply(lambda x: x/PC_ghg[year]['population'])
    
    return(PC_ghg)


#################
# save datasets #
#################
def save_footprint_data(PC_ghg, working_directory, geog):
    
    """
    Save per capita GHG emissions of UK MSOAs or LSOAs
    
    PC_ghg = per capita emissions of UK MSOAs or LSOAs as dictrionary containing pandas.DataFrame
    working_directory = full working directory as str (without last '/')
    """
    
    data_directory = working_directory + "/data/"
    
    years = list(PC_ghg.keys())
    if len(years) > 1:
        difference = years[1] - years[0]
    else:
        difference = 0
    for year in years:
        if difference > 1:
            year_str = str(year) + '-' + str(year + difference - 1)
        else:
            year_str = str(year)
        PC_ghg[year].to_csv(eval("r'" + data_directory + "processed/GHG_Estimates/" + geog + '_' + year_str + ".csv'"))
        
        print("Saved: " + data_directory + "processed/GHG_Estimates/" + geog + '_' + year_str + ".csv")
            
# code run in run_all.py