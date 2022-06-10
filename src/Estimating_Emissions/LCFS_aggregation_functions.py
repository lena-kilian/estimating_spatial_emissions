#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 11:03:48 2020

Functions for LCFS_aggregation.py 

@author: lenakilian
"""


import pandas as pd
import copy as cp
import numpy as np


def check_missing_oac(hhdspend_lcfs, years):
    hhdspend_missingoac = {}; hhdspend_product = {}
    for year in years:
        temp = hhdspend_lcfs[year].loc[:,'1.1.1.1':'12.5.3.5'].apply(lambda x: x / hhdspend_lcfs[year]['no people'])
        temp.columns = pd.MultiIndex.from_arrays([[str(x).split('.')[0] for x in temp.columns.tolist()], [x for x in temp.columns.tolist()]])
        temp = temp.sum(level=0, axis=1)
        temp['Total Expenditure'] = temp.sum(1)
        temp = temp.join(hhdspend_lcfs[year][['weight', 'no people', 'OAC_Supergroup', 'GOR modified']])
        temp['OAC_Supergroup'] = pd.to_numeric(temp['OAC_Supergroup'], errors='coerce')
        temp.loc[temp['OAC_Supergroup'].isna() == True, 'OAC_Supergroup'] = 0
        temp['Missing OAC'] = False; temp.loc[temp['OAC_Supergroup'] == 0, 'Missing OAC'] = True
        hhdspend_missingoac[year] = temp
    
        hhdspend_product[year] = pd.DataFrame(columns=['Missing OAC', 'GOR modified', 'Expenditure', 'Product Type'])
        idx = [str(x) for x in range(1, 13)] + ['weight', 'no people']
        for j in idx:
            temp = hhdspend_missingoac[year][[j, 'Missing OAC', 'GOR modified']].rename(columns={j:'Expenditure'})
            temp['Product Type'] = j
            hhdspend_product[year] = hhdspend_product[year].merge(temp, on=['Missing OAC', 'GOR modified', 'Expenditure', 'Product Type'], how='outer')
    return(hhdspend_missingoac, hhdspend_product)

#count OAC Subgroups in LCFS
def count_oac(hhdspend_lcfs, all_oac, years):
    full_index_lookup = {}; full_index = {}
    for year in years:
        subgroup_totals = hhdspend_lcfs[year][['GOR modified', 'OAC_Subgroup']]
        subgroup_totals.columns = ['GOR', 'Subgroup']
        subgroup_totals['count'] = 1
        subgroup_totals = subgroup_totals.groupby(['GOR', 'Subgroup']).sum()
        # merge the two, use UK OA index, fill with LCFS count
        if year < 2014:
            oac_year = '2001'
        else:
            oac_year = '2011'
        count_oac = all_oac[oac_year][['GOR', 'Subgroup']]
        count_oac = count_oac.drop_duplicates().set_index(['GOR', 'Subgroup']).join(subgroup_totals).fillna(0).reset_index()
        count_oac['Supergroup'] = [x[0] for x in count_oac['Subgroup']]; count_oac['Group'] = [x[:-1] for x in count_oac['Subgroup']]
        count_oac = count_oac.set_index(['GOR', 'Supergroup', 'Group', 'Subgroup'])

        full_index_lookup[year] = {}
        temp = count_oac; temp['OAC'] = [str(x[0]) + '_' + x[3] for x in count_oac.index.tolist()]
        full_index_lookup[year]['Subgroup_pass'] = temp.loc[temp['count'] >= 10]
    
        temp = temp.loc[temp['count'] < 10].drop_duplicates()
        OACs = temp.reset_index().groupby(['GOR', 'Supergroup', 'Group'])['OAC'].apply(', '.join); OACs.columns = ['OAC']
        temp = temp.sum(level=['GOR', 'Supergroup', 'Group'])[['count']].join(OACs).drop_duplicates()
        full_index_lookup[year]['Group_pass'] = temp.loc[temp['count'] >= 10]
        full_index_lookup[year]['Group_pass'] = full_index_lookup[year]['Group_pass'].join(full_index_lookup[year]['Group_pass']['OAC'].str.split(', ', expand = True))
    
        temp = temp.loc[temp['count'] < 10].drop_duplicates()
        OACs = temp.reset_index().groupby(['GOR', 'Supergroup'])['OAC'].apply(', '.join); OACs.columns = ['OAC']
        temp = temp.sum(level=['GOR', 'Supergroup'])[['count']].join(OACs).drop_duplicates()
        full_index_lookup[year]['Supergroup_pass'] = temp.loc[temp['count'] >= 10]
        full_index_lookup[year]['Supergroup_pass'] = full_index_lookup[year]['Supergroup_pass'].join(full_index_lookup[year]['Supergroup_pass']['OAC'].str.split(', ', expand = True))
        
        temp = temp.loc[temp['count'] < 10]
        OACs = temp.reset_index().groupby(['Supergroup'])['OAC'].apply(', '.join); OACs.columns = ['OAC']
        temp = temp.sum(level=['Supergroup'])[['count']].join(OACs).drop_duplicates()
        full_index_lookup[year]['Supergroup_UK_pass'] = temp.loc[temp['count'] >= 10].drop_duplicates()
        full_index_lookup[year]['Supergroup_UK_pass'] = full_index_lookup[year]['Supergroup_UK_pass']
        
        full_index_lookup[year]['Supergroup_UK_fail'] = temp.loc[temp['count'] < 10].drop_duplicates()
        full_index_lookup[year]['Supergroup_UK_fail'] = full_index_lookup[year]['Supergroup_UK_fail'].drop_duplicates()
        
        # extract those with enough data for full_index
        check = full_index_lookup[year]['Subgroup_pass'].reset_index().drop(['Supergroup', 'Group'], axis=1).rename(columns={'Subgroup':'OAC_label'})[['GOR', 'OAC_label', 'count', 'OAC']]
        if len(full_index_lookup[year]['Group_pass']) > 0:
            temp = full_index_lookup[year]['Group_pass'].reset_index().drop(['Supergroup'], axis=1).rename(columns={'Group':'OAC_label'})
            check = check.append(temp[['GOR', 'OAC_label', 'count', 'OAC']])
        if len(full_index_lookup[year]['Supergroup_pass']) > 0:
            temp = full_index_lookup[year]['Supergroup_pass'].reset_index().rename(columns={'Supergroup':'OAC_label'})
            check = check.append(temp[['GOR', 'OAC_label', 'count', 'OAC']])
        if len(full_index_lookup[year]['Supergroup_UK_pass']) > 0:
            temp = full_index_lookup[year]['Supergroup_UK_pass'].reset_index().rename(columns={'Supergroup':'OAC_label'}); temp['GOR'] = 0
            check = check.append(temp[['GOR', 'OAC_label', 'count', 'OAC']])
        if len(full_index_lookup[year]['Supergroup_UK_fail']) > 0:
            temp = full_index_lookup[year]['Supergroup_UK_fail'].reset_index().drop('Supergroup', axis=1); temp['GOR'] = 0; temp['OAC_label'] = '0' 
            check = check.append(temp[['GOR', 'OAC_label', 'count', 'OAC']])
            
        check.index = list(range(len(check)))

        idx = pd.DataFrame(check['OAC'].str.split(',', expand=True).stack()).dropna(how='all').droplevel(level=1).join(check)
        idx['GOR modified'] = [x.split('_')[0].replace(' ', '') for x in idx[0]]
        idx['OAC_Subgroup'] = [x.split('_')[1].replace(' ', '') for x in idx[0]]
        idx = idx.drop('OAC', axis=1).rename(columns={'OAC_label':'OAC'})
        
        full_index[year] = idx.rename(columns={0:'GOR_OAC'}).set_index(['GOR modified', 'OAC_Subgroup'])
    
    return(full_index_lookup, full_index)

# attach expenditures to OAC classifications made
def attach_exp(hhdspend_lcfs, full_index, years):
    full_exp = {}
    for year in years:
        # calculate per capita expenditure
        check = hhdspend_lcfs[year].reset_index()
        check['GOR modified'] = check['GOR modified'].astype(str)
        check = check.set_index(['GOR modified', 'OAC_Subgroup'])[['case', 'no people', 'weight']].join(full_index[year]).reset_index().set_index('case')
        check['pop'] = check['weight'] * check['no people']

        exp = hhdspend_lcfs[year].loc[:, '1.1.1.1':]

        check = check[['GOR modified', 'OAC', 'GOR', 'pop', 'weight', 'no people']].join(exp)
        
        full_exp[year] = check.reset_index().drop_duplicates().set_index('case')
    return(full_exp)

def agg_groups(hhdspend_lcfs, full_exp, years):
    hhdspend_full_index = {}; hhdspend_oac = {}
    for year in years:
        # save all OAC levels
        hhdspend_oac[year] = {}
        spend = hhdspend_lcfs[year]  
        spend['pop'] = spend['no people'] * spend['weight']
        spend.loc[:, '1.1.1.1':'12.5.3.5'] = spend.loc[:, '1.1.1.1':'12.5.3.5'].apply(lambda x: x * spend['weight'])
        for region in ['GOR', 'no_GOR']:
            hhdspend_oac[year][region] = {}
            for level in ['Supergroup', 'Group', 'Subgroup']:
                if region == 'GOR':
                    group = ['GOR modified', 'OAC_' + level]
                else:
                    group = ['OAC_' + level]
                spend.loc[spend['OAC_' + level].isna() == True, 'OAC_' + level] = '0'
                spend['OAC_' + level] = spend['OAC_' + level].astype(str)
                temp = spend.groupby(group).sum()
                temp.loc[:, '1.1.1.1':'12.5.3.5'] = temp.loc[:, '1.1.1.1':'12.5.3.5'].apply(lambda x: x/temp['pop'])
                hhdspend_oac[year][region][level] = temp
        # for detailed OACxLCFS
        spend = full_exp[year]
        spend.loc[:, '1.1.1.1':'14.8'] = spend.loc[:, '1.1.1.1':'14.8'].apply(lambda x: x*spend['weight'])
        spend['count'] = 1
        spend = spend.fillna(0).drop('GOR modified', axis=1).rename(columns={'GOR':'GOR modified'}).groupby(['GOR modified', 'OAC']).sum()
        spend.loc[:, '1.1.1.1':'14.8'] = spend.loc[:, '1.1.1.1':'14.8'].apply(lambda x: x/spend['pop'])
        hhdspend_full_index[year] = spend.drop(['weight', 'no people'], axis=1)
    return(hhdspend_full_index, hhdspend_oac)


def detailed_oac_aggregation(hhdspend_full_index, oac_all, hhdspend_oac):
    OA_exp_detailed = {}
    for year in list(hhdspend_full_index.keys()): 
        OAC_detailed = hhdspend_full_index[year].loc[hhdspend_full_index[year]['count'] >= 10].reset_index()
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
                
            OA_list = temp[var].loc[temp[var]['1.1.1.1'].isna() == True].reset_index()['OA_Code'].to_list()
            temp[var] = temp[var].loc[temp[var]['1.1.1.1'].isna() == False]
  
        if len(OA_list) > 0:    
            oac_var = oac_temp.loc[oac_temp['OA_Code'].isin(OA_list) == True]
            oac_var['OAC'] = oac_var['OAC_Supergroup'].str.upper()
            
            temp_exp = hhdspend_oac[year]['no_GOR']['Supergroup'].loc[:, '1.1.1.1':].reset_index()\
                .rename(columns={'OAC_Supergroup':'OAC'})
                
            temp['UK_all'] = oac_var[['OA_Code', 'GOR modified', 'OAC', 'population']]\
                .merge(temp_exp.drop('pop', axis=1), on=['OAC'], how='left')\
                    .set_index(['OA_Code', 'GOR modified', 'OAC'])

        OA_exp_detailed[year] = temp['OAC_Subgroup'].append(temp['OAC_Group']).append(temp['OAC_Supergroup'])\
            .append(temp['UK_all'])
    return(OA_exp_detailed)


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
        
        temp.loc[:,'1.1.1.1':'12.5.3.5'] = temp.loc[:,'1.1.1.1':'12.5.3.5'].apply(lambda x: x * temp['population'])
    
        new_ghg_detailed[year] = temp.groupby(geog_var).sum()
        new_ghg_detailed[year].loc[:,'1.1.1.1':'12.5.3.5'] = new_ghg_detailed[year].loc[:,'1.1.1.1':'12.5.3.5']\
            .apply(lambda x: x / new_ghg_detailed[year]['population'])
    return(new_ghg_detailed)

'''
# agregate expenditure by differen groups
def agg_groups(full_exp, years):
    hhdspend_full_index = {}; hhdspend_oac = {}
    for year in years:
        hhdspend_oac[year] = {}
        # calculate per capita expenditure
        spend = full_exp[year]
        # change NAs, so that these don't get removed by aggregation (needed for accurate emission and population estimatesn)
        spend.loc[spend['OAC'].isna() == True, 'OAC'] = 'other'
        spend.loc[spend['GOR modified'].isna() == True, 'GOR modified'] = 'other'
        spend['pop'] = spend['no people'] * spend['weight']
        spend.loc[:, '1.1.1.1':'12.5.3.5'] = spend.loc[:, '1.1.1.1':'12.5.3.5'].apply(lambda x: x * spend['weight'])
        spend['count'] = 1
        idx = spend.loc[:, '1.1.1.1':'12.5.3.5'].columns.tolist() + ['pop', 'GOR modified', 'count']
        # for OAC with and without regions
        for region in ['GOR', 'no_GOR']:
            hhdspend_oac[year][region] = {}
            for level in ['Supergroup', 'Group', 'Subgroup']:
                if region == 'GOR':
                    group = ['GOR modified', 'OAC_' + level]
                else:
                    group = ['OAC_' + level]
                temp = spend[idx + ['OAC_' + level]].groupby(group).sum()
                temp.loc[:, '1.1.1.1':'12.5.3.5'] = temp.loc[:, '1.1.1.1':'12.5.3.5'].apply(lambda x: x/temp['pop'])
                hhdspend_oac[year][region][level] = temp
        # for detailed OACxLCFS
        temp = spend[idx + ['OAC']].groupby(['GOR modified', 'OAC']).sum()
        temp.loc[:, '1.1.1.1':'12.5.3.5'] = temp.loc[:, '1.1.1.1':'12.5.3.5'].apply(lambda x: x/temp['pop'])
        hhdspend_full_index[year] = temp
        
    return(hhdspend_full_index, hhdspend_oac)
'''