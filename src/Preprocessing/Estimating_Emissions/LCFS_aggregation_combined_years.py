#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 2021

Aggregating expenditure groups for LCFS by OAC x Region Profiles & UK Supergroups

@author: lenakilian
"""

import pandas as pd
import LCFS_functions as lcfs
import LCFS_aggregation_functions as lcfs_agg
import copy as cp
import pickle


# import LCFS data and adjust flights and rent
def import_expenditure(first_year, last_year, combined_years, working_directory):
    
    if (first_year < 2007) | (last_year > 2017):
        print('Error: Please select year values between 2007-2017 (incl.)')
        exit()
    elif first_year > last_year:
        print('Error: first_year > last_year')
        exit()
    else:    
        pass
    
    if combined_years < 1:
        print('Error: Please choose a value of 1 or greater for combined_years')
        exit()
    else:    
        pass
        
    all_years = list(range(2007, 2018))
    lcf_years = dict(zip(all_years, ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015-2016', '2016-2017', '2017-2018']))
    
    years = list(range(first_year, last_year + 1))
    
    # create data directory from working directory
    data_directory = working_directory + "/data/"
    
    # load LFC data
    hhdspend_lcfs = {}
        
    for year in years:
        file_dvhh = "r'" + data_directory + "raw/LCFS/" + lcf_years[year] + '/tab/' + lcf_years[year] + "_dvhh_ukanon.tab'"
        file_dvper = "r'" + data_directory + "raw/LCFS/" + str(lcf_years[year]) + '/tab/' + str(lcf_years[year]) + "_dvper_ukanon.tab'"
        hhdspend_lcfs[year] = lcfs.import_lcfs(year, file_dvhh, file_dvper).drop_duplicates()
        for col in ['GOR modified', 'OAC_Supergroup', 'OAC_Group', 'OAC_Subgroup']:
            hhdspend_lcfs[year][col] = hhdspend_lcfs[year][col].astype(str).str.upper().str.replace(' ', '')
            hhdspend_lcfs[year].loc[hhdspend_lcfs[year][col].str.len() < 1, col] = '0'
            hhdspend_lcfs[year]['GOR modified'] = hhdspend_lcfs[year]['GOR modified'].astype(int)

    # LCFS with physical units 
    flights = pd.read_excel(eval("r'" + data_directory + "processed/LCFS/Controls/flights.xlsx'"), sheet_name=None)
    rent = pd.read_excel(eval("r'" + data_directory + "processed/LCFS/Controls/rent.xlsx'"), sheet_name=None)

    for year in years:
        # flights
        flights[str(year)] = flights[str(year)].set_index('case')
        hhdspend_lcfs[year]['7.3.4.1'] = flights[str(year)]['Domestic']
        hhdspend_lcfs[year]['7.3.4.2'] = flights[str(year)]['International']
        # rent
        rent[str(year)] = rent[str(year)].set_index('case')
        hhdspend_lcfs[year]['4.1.1'] = rent[str(year)]['4.1.1_proxy']
        hhdspend_lcfs[year]['4.1.2'] = rent[str(year)]['4.1.2_proxy']

    # merge years
    hhdspend_lcfs_combined = {}
    years_combined = list(range(first_year, last_year, 2))
    for year in years_combined:
        hhdspend_lcfs_combined[year] = cp.copy(hhdspend_lcfs[year])
        hhdspend_lcfs_combined[year].index = [str(year) + '-' + str(x) for x in hhdspend_lcfs_combined[year].index]
        if combined_years > 1:
            year_list = [] # check if boundary between 2013 and 2014 boundary is kept
            for i in range(1, combined_years):
                # check 2013 & 2014 boudary
                year_list.append(year + i)
                if (2013 in year_list) & (2014 in year_list):
                    print('Error: Please separate 2013 and 2014')
                    exit()
                else:
                    pass
                # continue appending years
                temp = cp.copy(hhdspend_lcfs[year + i])
                temp.index = [str(year + i) + '-' + str(x) for x in temp.index]
                hhdspend_lcfs_combined[year] = hhdspend_lcfs_combined[year].append(temp)
        hhdspend_lcfs_combined[year].index = hhdspend_lcfs_combined[year].index.rename('case')
        
    return(hhdspend_lcfs_combined)


# Assign expenditure to OAs
def attach_oac_grouping(hhdspend_lcfs_combined, working_directory):

    years_combined = list(hhdspend_lcfs_combined.keys())
    data_directory = working_directory + "/data/"
    
    # check totals per group
    # these are all OAs in the UK
    all_oac = pd.read_excel(eval("r'" + data_directory + "raw/Geography/Output_Area_Classification/OACxRegion.xlsx'"), sheet_name=None)
    for year in ['2001', '2011']:
        all_oac[year]['GOR'] = all_oac[year]['GOR modified']
        all_oac[year]['Supergroup'] = all_oac[year]['Supergroup'].astype(str)
    
    # count OAC Subgroups in LCFS
    full_index_lookup, full_index = lcfs_agg.count_oac(hhdspend_lcfs_combined, all_oac, years_combined)
        
    [full_index[year].to_csv(eval("r'" + data_directory + 'processed/LCFS/lcfsXoac/Index/oac_gor_index_' + str(year) + ".csv'")) for year in list(full_index.keys())]

    # Attach OAC expenditure to index
    full_exp = lcfs_agg.attach_exp(hhdspend_lcfs_combined, full_index, years_combined)
    
    # Aggregate expenditure
    hhdspend_full_index, hhdspend_oac = lcfs_agg.agg_groups(hhdspend_lcfs_combined, full_exp, years_combined)
        
    return(hhdspend_full_index, hhdspend_oac)


# Replace household energy
def energy_adjust(geog, geog_exp_detailed, working_directory):
    
    years_combined = list(geog_exp_detailed.keys())
    data_directory = working_directory + "/data/"
    
    # adjust household energy use
    geog_energy = pd.read_excel(eval("r'" + data_directory + "processed/LCFS/Gas_Electricity/" + geog + "_adjusted.xlsx'"), sheet_name=None, index_col=0)
    
    if len(years_combined) > 1:
        difference = years_combined[1] - years_combined[0]
    else:
        difference = 0
    for year in years_combined:
        year_list = [year + i for i in range(difference)]
        for i in range(2):
            name = ['Electricity', 'Gas'][i]; code = '4.4.' + str(i+1)
            temp_geog = pd.DataFrame(columns = geog_energy[str(year)].columns)
            for temp_year in year_list:
                temp_geog = temp_geog.append(geog_energy[str(temp_year)].loc[geog_energy[str(temp_year)][name].isna() == False])
                temp_geog = temp_geog[[name]].mean(level=0)
    
            new_geog = geog_exp_detailed[year][[code]].join(temp_geog)
            new_geog[name] = new_geog[name].fillna(value=new_geog[name].median())
            new_geog[code] = new_geog[name] / new_geog[name].sum() * new_geog[code].sum()
        
            geog_exp_detailed[year][code] = new_geog[code]
        
    return(geog_exp_detailed)

# save expenditure
def save_geog_expenditure(geog, geog_exp_detailed, working_directory):  
    data_directory = working_directory + "/data/"        
    # save expenditure profiles
    pickle.dump(geog_exp_detailed, open(eval("r'" + data_directory + "processed/LCFS/lcfsXoac/" + geog + "_expenditure.p'"), 'wb'))
    
    #for year in list(geog_exp_detailed.keys()):
    #    geog_exp_detailed[year].to_csv(eval("r'" + data_directory + "processed/LCFS/lcfsXoac/" + geog + "_expenditure_" + str(year) + '-' + str(year+1) + ".csv'"))