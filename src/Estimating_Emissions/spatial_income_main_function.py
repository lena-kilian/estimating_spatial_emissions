#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 24 2021

Aggregating income groups for LCFS by OAC x Region Profiles & UK Supergroups

@author: lenakilian
"""

import LCFS_aggregation_functions as lcfs_agg
import OAC_census_functions as oac
import LCFS_aggregation_combined_years as lcfs_cy
import copy as cp
import pandas as pd
import LCFS_PhysicalUnits_GasElectricity as energy

# main function to run all above
def estimate_income(geog, first_year, last_year, combine_years, wd, sd_limit):
    hhdincome_lcfs_combined = lcfs_cy.import_expenditure(first_year, last_year, combine_years, wd)
    hhdincome_lcfs_combined = lcfs_cy.winsorise(hhdincome_lcfs_combined, sd_limit)
    
    
    # extract full index -> lcfs to OAC x GOR
    years_combined = list(hhdincome_lcfs_combined.keys())
    data_directory = wd + "/data/"
    
    # check totals per group
    # these are all OAs in the UK
    all_oac = pd.read_excel(eval("r'" + data_directory + "raw/Geography/Output_Area_Classification/OACxRegion.xlsx'"), sheet_name=None)
    for year in ['2001', '2011']:
        all_oac[year]['GOR'] = all_oac[year]['GOR modified']
        all_oac[year]['Supergroup'] = all_oac[year]['Supergroup'].astype(str)
    
    # count OAC Subgroups in LCFS
    full_index_lookup, full_index = lcfs_agg.count_oac(hhdincome_lcfs_combined, all_oac, years_combined)
        
    [full_index[year].to_csv(eval("r'" + data_directory + 'processed/LCFS/lcfsXoac/Index/oac_gor_index_' + str(year) + ".csv'")) for year in list(full_index.keys())]

    # Attach OAC expenditure to index
    full_inc = {}
    for year in list(hhdincome_lcfs_combined.keys()):
        # calculate per capita expenditure
        check = hhdincome_lcfs_combined[year].reset_index()
        check['GOR modified'] = check['GOR modified'].astype(str)
        check = check.set_index(['GOR modified', 'OAC_Subgroup'])[['case', 'no people', 'weight']].join(full_index[year]).reset_index().set_index('case')
        check['pop'] = check['weight'] * check['no people']

        check = check[['GOR modified', 'OAC', 'GOR', 'pop', 'weight', 'no people']].join(hhdincome_lcfs_combined[year][['Income anonymised']])
        
        full_inc[year] = check.reset_index().drop_duplicates().set_index('case')
    
    # Aggregate groups from surveys
    hhdincome_full_index = {}; hhdincome_oac = {}
    for year in list(hhdincome_lcfs_combined.keys()):
        # save all OAC levels
        hhdincome_oac[year] = {}
        income = hhdincome_lcfs_combined[year]  
        income['pop'] = income['no people'] * income['weight']
        income['Income anonymised'] = income['Income anonymised'].apply(lambda x: x * income['weight'])
        for region in ['GOR', 'no_GOR']:
            hhdincome_oac[year][region] = {}
            for level in ['Supergroup', 'Group', 'Subgroup']:
                if region == 'GOR':
                    group = ['GOR modified', 'OAC_' + level]
                else:
                    group = ['OAC_' + level]
                income.loc[income['OAC_' + level].isna() == True, 'OAC_' + level] = '0'
                income['OAC_' + level] = income['OAC_' + level].astype(str)
                temp = income.groupby(group).sum()
                temp['Income anonymised'] = temp['Income anonymised'].apply(lambda x: x / temp['pop'])
                hhdincome_oac[year][region][level] = temp
        # for detailed OACxLCFS
        income = full_inc[year]
        income['Income anonymised'] = income['Income anonymised'].apply(lambda x: x * income['weight'])
        income['count'] = 1
        income = income.fillna(0).drop('GOR modified', axis=1).rename(columns={'GOR':'GOR modified'}).groupby(['GOR modified', 'OAC']).sum()
        income['Income anonymised'] = income['Income anonymised'].apply(lambda x: x / income['pop'])
        hhdincome_full_index[year] = income.drop(['weight', 'no people'], axis=1)

    # import OAC data adjusted to mid-year populations
    oac_all = oac.get_oac_census(list(hhdincome_lcfs_combined.keys()), wd)
    
    OA_inc_detailed = {}
    for year in list(hhdincome_full_index.keys()): 
        OAC_detailed = hhdincome_full_index[year].loc[hhdincome_full_index[year]['count'] >= 10].reset_index()[['GOR modified', 'OAC', 'pop', 'count', 'Income anonymised']]
        OAC_detailed['OAC'] = OAC_detailed['OAC'].str.upper()
        #OAC_detailed = OAC_detailed.set_index(['GOR modified', 'OAC'])
    
        oac_temp = oac_all[year].drop_duplicates().rename(columns={'OA01CD':'OA_Code', 'OA11CD':'OA_Code'})[
            ['OA_Code', 'GOR modified', 'OAC_Supergroup', 'OAC_Group', 'OAC_Subgroup', 'population']]
        #pop = oac_temp[['OA_Code', 'population']]
    
        temp = {}; OA_list = oac_temp['OA_Code'].to_list()
        for var in ['OAC_Subgroup', 'OAC_Group', 'OAC_Supergroup']:
            oac_var = oac_temp.loc[oac_temp['OA_Code'].isin(OA_list) == True]
            oac_var['OAC'] = oac_var[var].str.upper()
            
            temp[var] = oac_var[['OA_Code', 'GOR modified', 'OAC', 'population']].merge(OAC_detailed.drop('pop', axis=1), on=['GOR modified', 'OAC'], how='left').set_index(['OA_Code', 'GOR modified', 'OAC'])
                
            OA_list = temp[var].loc[temp[var]['Income anonymised'].isna() == True].reset_index()['OA_Code'].to_list()
            temp[var] = temp[var].loc[temp[var]['Income anonymised'].isna() == False]
  
        if len(OA_list) > 0:    
            oac_var = oac_temp.loc[oac_temp['OA_Code'].isin(OA_list) == True]
            oac_var['OAC'] = oac_var['OAC_Supergroup'].str.upper()
            
            temp_inc = hhdincome_oac[year]['no_GOR']['Supergroup'][['Income anonymised', 'pop']].reset_index().rename(columns={'OAC_Supergroup':'OAC'})
                
            temp['UK_all'] = oac_var[['OA_Code', 'GOR modified', 'OAC', 'population']].merge(temp_inc.drop('pop', axis=1), on=['OAC'], how='left').set_index(['OA_Code', 'GOR modified', 'OAC'])

        OA_inc_detailed[year] = temp['OAC_Subgroup'].append(temp['OAC_Group']).append(temp['OAC_Supergroup']).append(temp['UK_all'])
    OA_inc_detailed = {year : OA_inc_detailed[year][['Income anonymised', 'population']] for year in list(hhdincome_lcfs_combined.keys())}
    # Aggregate to LSOA and MSOA level
    new_inc_detailed = {}
    for year in list(OA_inc_detailed.keys()):
        if year > 2013:
            oac_year = 2011
        else:
            oac_year = 2001

        geog_var = geog + str(oac_year)[2:] + 'CD'
        
        geog_lookup = oac_all['oa_' + str(oac_year)].rename(columns={'OA_SA':'OA_Code'})[['OA_Code', geog_var, 'population']]\
            .drop_duplicates().set_index('OA_Code')

        temp = pd.DataFrame(OA_inc_detailed[year].droplevel(['GOR modified', 'OAC']))
        temp = temp.join(geog_lookup)
        temp = temp.set_index([geog_var], append=True)
        
        temp['Income anonymised'] = temp['Income anonymised'].apply(lambda x: x * temp['population'])
    
        new_inc_detailed[year] = temp.groupby(geog_var).sum()
        new_inc_detailed[year]['Income anonymised'] = new_inc_detailed[year]['Income anonymised'].apply(lambda x: x / new_inc_detailed[year]['population'])   
    
