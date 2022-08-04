#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 2021

Aggregating expenditure groups for LCFS by OAC x Region Profiles & UK Supergroups

@author: lenakilian
"""

import pandas as pd
import copy as cp
import pickle
import LCFS_sociodem_functions as lcfs_sd


# import LCFS data and adjust flights and rent
def import_socoidem_vars(first_year, last_year, combined_years, working_directory):
    
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
    sociodem_lcfs = {}
    for year in years:
        file_dvhh = "r'" + data_directory + "raw/LCFS/" + lcf_years[year] + "/tab/" + lcf_years[year] + "_dvhh_ukanon.tab'"
        file_dvper = "r'" + data_directory + "raw/LCFS/" + lcf_years[year] + "/tab/" + lcf_years[year] + "_dvper_ukanon.tab'"
        sociodem_lcfs[year] = lcfs_sd.import_lcfs_income(year, file_dvhh, file_dvper).drop_duplicates()
        sociodem_lcfs[year]['Income anonymised'] = sociodem_lcfs[year]['Income anonymised']/sociodem_lcfs[year]['no people']
        for col in ['GOR modified', 'OAC_Supergroup', 'OAC_Group', 'OAC_Subgroup']:
            sociodem_lcfs[year][col] = sociodem_lcfs[year][col].astype(str).str.upper().str.replace(' ', '')
            sociodem_lcfs[year].loc[sociodem_lcfs[year][col].str.len() < 1, col] = '0'
        sociodem_lcfs[year]['GOR modified'] = sociodem_lcfs[year]['GOR modified'].astype(int)

    # merge years
    sociodem_lcfs_combined = {}
    if (last_year - first_year) % combined_years == 0:
        end = last_year + 1
    else:
        end = last_year
    years_combined = list(range(first_year, end, combined_years))
    for year in years_combined:
        sociodem_lcfs_combined[year] = cp.copy(sociodem_lcfs[year])
        sociodem_lcfs_combined[year].index = [str(year) + '-' + str(x) for x in sociodem_lcfs_combined[year].index]
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
                temp = cp.copy(sociodem_lcfs[year + i])
                temp.index = [str(year + i) + '-' + str(x) for x in temp.index]
                sociodem_lcfs_combined[year] = sociodem_lcfs_combined[year].append(temp)
        sociodem_lcfs_combined[year].index = sociodem_lcfs_combined[year].index.rename('case')
    return(sociodem_lcfs_combined)


# Assign expenditure to OAs
def attach_oac_grouping(sociodem_lcfs_combined, working_directory):

    years_combined = list(sociodem_lcfs_combined.keys())
    data_directory = working_directory + "/data/"
    
    # check totals per group
    # these are all OAs in the UK
    all_oac = pd.read_excel(eval("r'" + data_directory + "raw/Geography/Output_Area_Classification/OACxRegion.xlsx'"), sheet_name=None)
    for year in ['2001', '2011']:
        all_oac[year]['GOR'] = all_oac[year]['GOR modified']
        all_oac[year]['Supergroup'] = all_oac[year]['Supergroup'].astype(str)
    
    # count OAC Subgroups in LCFS
    full_index_lookup, full_index = lcfs_sd.count_oac(sociodem_lcfs_combined, all_oac, years_combined)
        
    [full_index[year].to_csv(eval("r'" + data_directory + 'processed/LCFS/lcfsXoac/Index/oac_gor_index_' + str(year) + ".csv'")) for year in list(full_index.keys())]

    # Attach OAC expenditure to index
    full_exp = lcfs_sd.attach_exp(sociodem_lcfs_combined, full_index, years_combined)
    
    # Aggregate expenditure
    sociodem_full_index, sociodem_oac = lcfs_sd.agg_groups(sociodem_lcfs_combined, full_exp, years_combined)
        
    return(sociodem_full_index, sociodem_oac)


def detailed_oac_aggregation(sociodem_full_index, oac_all, sociodem_oac):
    OA_exp_detailed = {}
    for year in list(sociodem_full_index.keys()): 
        OAC_detailed = sociodem_full_index[year].loc[sociodem_full_index[year]['count'] >= 10].reset_index()
        OAC_detailed['OAC'] = OAC_detailed['OAC'].str.upper()
        #OAC_detailed = OAC_detailed.set_index(['GOR modified', 'OAC'])
    
        oac_temp = oac_all[year].drop_duplicates().rename(columns={'OA01CD':'OA_Code', 'OA11CD':'OA_Code'})[
            ['OA_Code', 'GOR modified', 'OAC_Supergroup', 'OAC_Group', 'OAC_Subgroup', 'population']]
        #pop = oac_temp[['OA_Code', 'population']]
    
        temp = {}; OA_list = oac_temp['OA_Code'].to_list()
        for var in ['OAC_Subgroup', 'OAC_Group', 'OAC_Supergroup']:
            oac_var = oac_temp.loc[oac_temp['OA_Code'].isin(OA_list) == True]
            oac_var['OAC'] = oac_var[var].str.upper()
            
            temp[var] = oac_var[['OA_Code', 'GOR modified', 'OAC', 'population']]\
                .merge(OAC_detailed.drop('pop', axis=1), on=['GOR modified', 'OAC'], how='left')\
                    .set_index(['OA_Code', 'GOR modified', 'OAC'])
                
            OA_list = temp[var].loc[temp[var]['Income anonymised'].isna() == True].reset_index()['OA_Code'].to_list()
            temp[var] = temp[var].loc[temp[var]['Income anonymised'].isna() == False]
  
        if len(OA_list) > 0:    
            oac_var = oac_temp.loc[oac_temp['OA_Code'].isin(OA_list) == True]
            oac_var['OAC'] = oac_var['OAC_Supergroup'].str.upper()
            
            temp_exp = sociodem_oac[year]['no_GOR']['Supergroup'].loc[:, 'Income anonymised':].reset_index()\
                .rename(columns={'OAC_Supergroup':'OAC'})
                
            temp['UK_all'] = oac_var[['OA_Code', 'GOR modified', 'OAC', 'population']]\
                .merge(temp_exp.drop('pop', axis=1), on=['OAC'], how='left')\
                    .set_index(['OA_Code', 'GOR modified', 'OAC'])

        OA_exp_detailed[year] = temp['OAC_Subgroup'].append(temp['OAC_Group']).append(temp['OAC_Supergroup'])\
            .append(temp['UK_all'])
    return(OA_exp_detailed)


# aggregate geographies
def geog_aggregation(OA_exp_detailed, oac_all, years, geog_level):
    new_ghg_detailed= {}
    for year in list(OA_exp_detailed.keys()):
        if year > 2013:
            oac_year = 2011
        else:
            oac_year = 2001

        geog_var = geog_level + str(oac_year)[2:] + 'CD'
        
        geog_lookup = oac_all['oa_' + str(oac_year)].rename(columns={'OA_SA':'OA_Code'})[['OA_Code', geog_var]]\
            .drop_duplicates().set_index('OA_Code')

        temp = OA_exp_detailed[year].droplevel(['GOR modified', 'OAC'])
        temp = temp.join(geog_lookup)
        temp = temp.set_index([geog_var], append=True)
        
        temp.loc[:,'Income anonymised':'Income tax'] = temp.loc[:,'Income anonymised':'Income tax'].apply(lambda x: x * temp['population'])
    
        new_ghg_detailed[year] = temp.groupby(geog_var).sum()
        new_ghg_detailed[year].loc[:,'Income anonymised':'Income tax'] = new_ghg_detailed[year].loc[:,'Income anonymised':'Income tax']\
            .apply(lambda x: x / new_ghg_detailed[year]['population'])
    return(new_ghg_detailed)

# save expenditure
def save_geog_expenditure(geog, geog_exp_detailed, working_directory):  
    data_directory = working_directory + "/data/"        
    # save expenditure profiles
    pickle.dump(geog_exp_detailed, open(eval("r'" + data_directory + "processed/LCFS/lcfsXoac/" + geog + "_expenditure.p'"), 'wb'))
    
    #for year in list(geog_exp_detailed.keys()):
    #    geog_exp_detailed[year].to_csv(eval("r'" + data_directory + "processed/LCFS/lcfsXoac/" + geog + "_expenditure_" + str(year) + '-' + str(year+1) + ".csv'"))