#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 2021

Aggregating expenditure groups for LCFS by OAC x Region Profiles & UK Supergroups

@author: lenakilian
"""

import pandas as pd
import LCFS_import_raw_data as lcfs_import
import LCFS_aggregation_functions as lcfs_agg
import copy as cp
import pickle


# import LCFS data and adjust flights and rent
def import_expenditure(first_year, last_year, combined_years, working_directory):
    
    if (first_year < 2007) | (last_year > 2018):
        print('Error: Please select year values between 2007-2018 (incl.)')
    elif first_year > last_year:
        print('Error: first_year > last_year')
    else:    
        pass
    if combined_years < 1:
        print('Error: Please choose a value of 1 or greater for combined_years')
    else:    
        pass
        
    all_years = list(range(2007, 2019))
    lcf_years = dict(zip(all_years, ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015-2016', '2016-2017', '2017-2018', '2018-2019']))
    
    years = list(range(first_year, last_year + 1))
    
    # create data directory from working directory
    data_directory = working_directory + "/data/"
    
    # load LFC data
    hhdspend_lcfs = {}
        
    for year in years:
        file_dvhh = "r'" + data_directory + "raw/LCFS/" + lcf_years[year] + '/tab/' + lcf_years[year] + "_dvhh_ukanon.tab'"
        file_dvper = "r'" + data_directory + "raw/LCFS/" + str(lcf_years[year]) + '/tab/' + str(lcf_years[year]) + "_dvper_ukanon.tab'"
        hhdspend_lcfs[year] = lcfs_import.import_lcfs(year, file_dvhh, file_dvper).drop_duplicates()
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
        hhdspend_lcfs[year]['7.3.4.1'] = flights[str(year)]['Domestic'] / flights[str(year)]['Domestic'].sum() * hhdspend_lcfs[year]['7.3.4.1'].sum()
        hhdspend_lcfs[year]['7.3.4.2'] = flights[str(year)]['International'] / flights[str(year)]['International'].sum() * hhdspend_lcfs[year]['7.3.4.2'].sum()
        # rent
        rent[str(year)] = rent[str(year)].set_index('case')
        hhdspend_lcfs[year]['4.1.1'] = rent[str(year)]['4.1.1_proxy']
        hhdspend_lcfs[year]['4.1.2'] = rent[str(year)]['4.1.2_proxy']

    # merge years
    hhdspend_lcfs_combined = {}
    if (last_year - first_year) % combined_years == 0:
        end = last_year + 1
    else:
        end = last_year
    years_combined = list(range(first_year, end, combined_years))
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
                else:
                    pass
                # continue appending years
                temp = cp.copy(hhdspend_lcfs[year + i])
                temp.index = [str(year + i) + '-' + str(x) for x in temp.index]
                hhdspend_lcfs_combined[year] = hhdspend_lcfs_combined[year].append(temp)
        hhdspend_lcfs_combined[year].index = hhdspend_lcfs_combined[year].index.rename('case')
        
    return(hhdspend_lcfs_combined)


def get_year_combinations(first_year, last_year, combine_years):
    year_combinations = {}
    
    check_years = []
    for item in list(range(first_year, last_year, combine_years)):
        if item <= 2013:
            check_years.append(item)
    start_year_2013 = min(check_years, key=lambda x:abs(x-2013))
    end_year_2013 = start_year_2013 + combine_years - 1
        
    year_combinations['2013_boundary'] = [start_year_2013, end_year_2013]
    
    if last_year > end_year_2013:
        year_combinations['higher'] = [first_year, start_year_2013 - 1]

    if first_year < start_year_2013:
        year_combinations['lower'] = [end_year_2013 + 1, last_year]
            
    return(year_combinations)


def mean_spend_2013_bounday(exp_by_year, wd):
    
    lookup = pd.read_csv(eval("r'" + wd + "/data/raw/Geography/Conversion_Lookups/UK_full_lookup_2001_to_2011.csv'"))
    lookup_msoa = lookup[['MSOA01CD', 'MSOA11CD']].drop_duplicates()
            
    new_exp_2013 = pd.DataFrame()
    for year in list(exp_by_year.keys()):
        # import ghg and income
        if year > 2013:
            exp_by_year[year] = exp_by_year[year].join(lookup_msoa.set_index('MSOA11CD')).set_index('MSOA01CD').mean(axis=0, level='MSOA01CD')
        exp_by_year[year]['year'] = year
        new_exp_2013 = new_exp_2013.append(exp_by_year[year])
            
    new_exp_2013 = new_exp_2013.mean(axis=0, level='MSOA01CD').drop('year', axis=1)
            
    return(new_exp_2013)



def winsorise(hhdspend_lcfs_combined, sd_limit):
    new_hhspend_all = {}
    
    for year in list(hhdspend_lcfs_combined.keys()):
        keep = hhdspend_lcfs_combined[year].loc[:,'1.1.1.1':'12.5.3.5'].columns.tolist()
        means = pd.DataFrame(hhdspend_lcfs_combined[year][keep].mean())
        sd = pd.DataFrame(hhdspend_lcfs_combined[year][keep].std())

        new_hhspend = hhdspend_lcfs_combined[year][keep].T
        new_hhspend['sd'] = sd; new_hhspend['mean'] = means

        new_hhspend.columns = pd.MultiIndex.from_arrays([['og' for x in new_hhspend.columns[:-2]] + ['summary', 'summary'], new_hhspend.columns.tolist()])
        new_hhspend = new_hhspend.droplevel(axis=1, level=0)

        for item in new_hhspend.columns[:-2]:
            new_hhspend.loc[new_hhspend[item] > new_hhspend['mean'] + (sd_limit * new_hhspend['sd']), item] = new_hhspend['mean'] + (sd_limit * new_hhspend['sd'])
            new_hhspend.loc[new_hhspend[item] < new_hhspend['mean'] - (sd_limit * new_hhspend['sd']), item] = new_hhspend['mean'] - (sd_limit * new_hhspend['sd'])
    
        new_hhspend_all[year] = hhdspend_lcfs_combined[year].drop(keep, axis=1).join(new_hhspend.T, how='left')
        new_hhspend_all[year] = new_hhspend_all[year][hhdspend_lcfs_combined[year].columns.tolist()]
    
    return(new_hhspend_all)

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
    
    data_directory = working_directory + "/data/"
    
    # adjust household energy use
    geog_energy = pd.read_excel(eval("r'" + data_directory + "processed/LCFS/Gas_Electricity/" + geog + "_adjusted.xlsx'"), sheet_name=None, index_col=0)
    
    for i in range(2):
        name = ['Electricity', 'Gas'][i]; code = '4.4.' + str(i+1)
        for year in list(geog_exp_detailed.keys()):
            new_geog = geog_exp_detailed[year][[code]].join(geog_energy[str(year)][[name]])
            new_geog[name] = new_geog[name].fillna(value=new_geog[name].median())
            new_geog[code] = new_geog[name] / new_geog[name].sum() * new_geog[code].sum()
            new_geog = new_geog.mean(axis=0, level=0)
        
            geog_exp_detailed[year][code] = new_geog[code]
            
            
        
    return(geog_exp_detailed)    


def transport_adjust_lad_based(geog, geog_exp_detailed, working_directory, sd_limit):
    years_combined = list(geog_exp_detailed.keys())
    data_directory = working_directory + "/data"
    
    # adjust household energy use
    geog_petrol = pd.read_csv(eval("r'" + data_directory + "/processed/LCFS/Controls/LAD_road_use.csv'")).rename(columns={'geog11CD': geog + '11CD'})
    geog_petrol = geog_petrol.loc[(geog_petrol['geog'] == geog)].drop(['geog'], axis=1).set_index([geog + '11CD', 'LAD17CD'])

    if len(years_combined) > 1:
        difference = years_combined[1] - years_combined[0]
    else:
        difference = 1
    for year in years_combined:
        year_list = [year + i for i in range(difference)]
        temp_geog = pd.DataFrame(columns = geog_petrol.columns)
        for temp_year in year_list:
            temp_geog = temp_geog.append(geog_petrol.loc[geog_petrol['year'] == temp_year])
        temp_geog = temp_geog.sum(axis=0, level=0)
        temp_geog.index = pd.MultiIndex.from_tuples(temp_geog.index)
        temp_geog['LAD17CD'] = [x[1] for x in temp_geog.index]
        temp_geog = temp_geog.droplevel(axis=0, level=1)
        temp_geog = temp_geog[['LAD17CD']].reset_index().merge(temp_geog.groupby('LAD17CD').sum()[['petrol_geog', 'diesel_geog', 'other_geog']].reset_index(), on='LAD17CD').set_index('index')
        temp_geog = temp_geog.reset_index().groupby('index').head(1).set_index('index')
        
        for i in range(3):
            code = ['7.2.2.1', '7.2.2.2', '7.2.2.3'][i]
            oil = ['petrol', 'diesel', 'other'][i] + '_geog'
            
            new_geog = geog_exp_detailed[year][[code, 'population']].join(temp_geog[[oil, 'LAD17CD']].loc[geog_exp_detailed[year].index], how='left')
            new_geog[oil] = new_geog[oil].fillna(value=new_geog[oil].median())
            new_geog['code_geog'] = new_geog[code] *new_geog['population']
            new_geog['oil_adjusted'] = new_geog[oil]/(new_geog[[oil]].drop_duplicates().sum()[oil]) * new_geog['code_geog'].sum()
            new_geog.index.name = 'MSOA'
            new_geog = new_geog.reset_index().merge(new_geog.groupby('LAD17CD').sum()[['code_geog']].reset_index().rename(columns={'code_geog':'code_lad'}), on='LAD17CD').set_index('MSOA')

            new_geog[code + '_new'] = ((new_geog['code_geog'] / new_geog['code_lad']) * new_geog['oil_adjusted']) / new_geog['population']
            # winsorise
            mean = new_geog[code + '_new'].mean(); sd = new_geog[code + '_new'].std()
            new_geog.loc[new_geog[code + '_new'] > mean + sd_limit * sd, code + '_new'] =  mean + sd_limit * sd
            new_geog.loc[new_geog[code + '_new'] < mean - sd_limit * sd, code + '_new'] =  mean - sd_limit * sd
            
            geog_exp_detailed[year][code] = new_geog[code + '_new']
            
    return(geog_exp_detailed)


def transport_adjust_50_50(geog, geog_exp_detailed, working_directory, sd_limit):
    years_combined = list(geog_exp_detailed.keys())
    data_directory = working_directory + "/data"
    
    # adjust household energy use
    geog_petrol = pd.read_csv(eval("r'" + data_directory + "/processed/LCFS/Controls/LAD_road_use.csv'")).rename(columns={'geog11CD': geog + '11CD'})
    geog_petrol = geog_petrol.loc[(geog_petrol['geog'] == geog)].drop(['geog'], axis=1).set_index([geog + '11CD', 'LAD17CD'])

    if len(years_combined) > 1:
        difference = years_combined[1] - years_combined[0]
    else:
        difference = 1
    for year in years_combined:
        year_list = [year + i for i in range(difference)]
        temp_geog = pd.DataFrame(columns = geog_petrol.columns)
        for temp_year in year_list:
            temp_geog = temp_geog.append(geog_petrol.loc[geog_petrol['year'] == temp_year])
        temp_geog = temp_geog.sum(axis=0, level=0)
        temp_geog.index = pd.MultiIndex.from_tuples(temp_geog.index)
        temp_geog['LAD17CD'] = [x[1] for x in temp_geog.index]
        temp_geog = temp_geog.droplevel(axis=0, level=1)
        temp_geog = temp_geog[['LAD17CD']].reset_index().merge(temp_geog.groupby('LAD17CD').sum()[['petrol_geog', 'diesel_geog', 'other_geog']].reset_index(), on='LAD17CD').set_index('index')
        temp_geog = temp_geog.reset_index().groupby('index').head(1).set_index('index')
        
        for i in range(3):
            code = ['7.2.2.1', '7.2.2.2', '7.2.2.3'][i]
            oil = ['petrol', 'diesel', 'other'][i] + '_geog'
            
            new_geog = geog_exp_detailed[year][[code, 'population']].join(temp_geog[[oil, 'LAD17CD']].loc[geog_exp_detailed[year].index], how='left')
            new_geog[oil] = new_geog[oil].fillna(value=new_geog[oil].median())
            new_geog['code_geog'] = new_geog[code] * new_geog['population']
            new_geog.index.name = 'MSOA'
            new_geog = new_geog.reset_index().merge(new_geog.groupby('LAD17CD').sum()[['population']].reset_index().rename(columns={'population':'pop_lad'}), on='LAD17CD').set_index('MSOA')
            new_geog['oil_geog'] = new_geog[oil]/new_geog['pop_lad'] * new_geog['population']
            new_geog['oil_adjusted'] = new_geog['oil_geog'] / new_geog['oil_geog'].sum() * new_geog['code_geog'].sum()
            

            new_geog[code + '_new'] = ((new_geog['code_geog'] / 2) + (new_geog['oil_adjusted']/2)) / new_geog['population']
            
            # winsorise
            mean = new_geog[code + '_new'].mean(); sd = new_geog[code + '_new'].std()
            new_geog.loc[new_geog[code + '_new'] > mean + sd_limit * sd, code + '_new'] =  mean + sd_limit * sd
            new_geog.loc[new_geog[code + '_new'] < mean - sd_limit * sd, code + '_new'] =  mean - sd_limit * sd
        
            geog_exp_detailed[year][code] = new_geog[code + '_new']
            
    return(geog_exp_detailed)
    
    

# save expenditure
def save_geog_expenditure(geog, geog_exp_detailed, working_directory):  
    data_directory = working_directory + "/data/"        
    # save expenditure profiles
    pickle.dump(geog_exp_detailed, open(eval("r'" + data_directory + "processed/LCFS/lcfsXoac/" + geog + "_expenditure.p'"), 'wb'))
    
    #for year in list(geog_exp_detailed.keys()):
    #    geog_exp_detailed[year].to_csv(eval("r'" + data_directory + "processed/LCFS/lcfsXoac/" + geog + "_expenditure_" + str(year) + '-' + str(year+1) + ".csv'"))