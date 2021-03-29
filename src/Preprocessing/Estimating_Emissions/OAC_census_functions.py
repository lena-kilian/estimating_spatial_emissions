#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 14:57:45 2021

@author: lenakilian
"""

import pandas as pd

def get_oac_census(years_combined, working_directory):

    data_directory = working_directory + "/data/"   
    
    # Get OA data to create profile by OA
    # combine with OAs (2007-2013, and 2014-2016)
    # Region (GOR) lookup
    fname = "r'" + data_directory + "raw/LCFS/2016-2017/mrdoc/excel/8351_volume_f_derived_variables_201617_final.xls'"
    gor_lookup = pd.read_excel(eval(fname), sheet_name='Part 4').iloc[920:932, 1:3]
    gor_lookup.columns=['GOR_name', 'GOR modified']
    gor_lookup['GOR_code'] = gor_lookup['GOR_name'].str.lower().str.replace(' ', '').str[:7]
    
    oac_all = {}
    # 2001 OAC
    oac_2001 = pd.read_csv(eval("r'" + data_directory + "raw/Geography/Conversion_Lookups/UK_full_lookup_2001.csv'")).drop_duplicates()
    oac_2001.loc[oac_2001['RGN01NM'] == 'East', 'RGN01NM'] = 'Eastern'
    oac_2001['GOR_code'] = oac_2001['RGN01NM'].str.lower().str.replace(' ', '').str[:7]
    oac_2001 = oac_2001.merge(gor_lookup, on='GOR_code')
    oac_all['oa_2001'] = oac_2001.drop_duplicates()

    # 2011 OAC
    full_lookup = pd.read_csv(eval("r'" + data_directory + "raw/Geography/Conversion_Lookups/UK_full_lookup_2001_to_2011.csv'"))
    oac_2011 = full_lookup[['OAC11CD', 'OA11CD', 'LSOA11CD', 'MSOA11CD', 'LAD17NM', 'RGN11NM']].drop_duplicates()
    oac_2011.loc[oac_2011['RGN11NM'] == 'East of England', 'RGN11NM'] = 'Eastern'
    oac_2011['GOR_code'] = oac_2011['RGN11NM'].str.lower().str.replace(' ', '').str[:7]
    oac_2011 = oac_2011.merge(gor_lookup, on='GOR_code')
    oac_all['oa_2011'] = oac_2011


    # clean OAC and import OA populations
    oa_populations = {}
    for year_code in ['oa_2001', 'oa_2011']:
        year_end = year_code[-2:]
        
        # tidy OAC
        oac_all[year_code]['OAC_Supergroup'] = oac_all[year_code]['OAC' + year_end + 'CD'].str[0]
        oac_all[year_code]['OAC_Group'] = oac_all[year_code]['OAC' + year_end + 'CD'].str[:2]
        oac_all[year_code]['OAC_Subgroup'] = oac_all[year_code]['OAC' + year_end + 'CD']
        oac_all[year_code]['OA_SA'] = oac_all[year_code]['OA' + year_end + 'CD']
    
        # import populations
        oa_populations[year_code] = pd.read_csv(eval("r'" + data_directory + "raw/Geography/Census_Populations/census20" + year_end + "_pop_uk_oa.csv'"))[
                ['OA' + year_end + 'CD', 'population']]
        oa_populations[year_code]['population'] = oa_populations[year_code]['population'].astype(float)   

    ni_pop_01 = pd.read_csv(eval("r'" + data_directory + "raw/Geography/Census_Populations/census2001_pop_northern_ireland_oa.csv'"), header=5)[['Unnamed: 0', 'All persons']]
    ni_pop_01['Unnamed: 0'] = ni_pop_01['Unnamed: 0'].str.replace(' ', '')
    ni_pop_01 = ni_pop_01.loc[(ni_pop_01['Unnamed: 0'].str.len() == len('95ZZ160009')) & 
                              (ni_pop_01['Unnamed: 0'].str[-1].str.isnumeric() == True)]
    ni_pop_01.columns = ['OA01CD', 'population']

    oa_populations['oa_2001'] = oa_populations['oa_2001'].append(ni_pop_01)


    # import mid year populations
    mid_year_pop = pd.read_csv(eval("r'" + data_directory + "raw/Geography/Census_Populations/mid_year_pop.csv'"), header=7); mid_year_pop.columns = ['year', 'population']
    mid_year_pop = mid_year_pop.set_index('year')

    mid_year_pop_combined = mid_year_pop.loc[years_combined]
    
    if len(years_combined) > 1:
        difference = years_combined[1] - years_combined[0]
        for year in years_combined:
            year_list = [year + i for i in range(difference)]
            temp =  mid_year_pop.loc[year, 'population']
            for i in range(1, difference):
                temp += mid_year_pop.loc[year_list[i], 'population']
            mid_year_pop_combined.loc[year, 'population'] = temp / difference
    else:
        for year in years_combined:
             mid_year_pop_combined.loc[year, 'population'] = mid_year_pop.loc[year, 'population']

    for year in years_combined:
        if year < 2011:
            year_code = 'oa_2001'
        else:
            year_code = 'oa_2011'
        year_end = year_code[-2:] 

        # adjust OA populations to mid-year populations
        oa_populations[year_code]['OA_SA'] = oa_populations[year_code]['OA' + year_end + 'CD']
        oac_all[year] = oac_all[year_code].merge(oa_populations[year_code][['OA_SA', 'population']], on='OA_SA', how='left')
        oac_all[year] = oac_all[year][['MSOA' + year_end + 'CD', 'LSOA' + year_end + 'CD', 'OA' + year_end + 'CD',
                                   'GOR_code', 'GOR_name', 'GOR modified', 'OAC_Supergroup', 'OAC_Group', 'OAC_Subgroup', 'OA_SA', 'population']].drop_duplicates()
        oac_all[year]['population'] = ((oac_all[year]['population']/oac_all[year]['population'].sum()) * mid_year_pop_combined.loc[year, 'population'])

    return(oac_all)