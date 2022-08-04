#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 11:30:59 2021

@author: lenakilian
"""

import numpy as np
import pandas as pd
df = pd.DataFrame

def import_lcfs_income(year, dvhh_file, dvper_file):
    
    idx = {}; idx['person'] = {}; idx['hhld'] = {}

    idx['person']['to_keep'] = ['person', 'a012p', 'a013p']
    idx['person']['new_name'] = ['person_no', 'ethnicity_hrp', 'ethnicity partner hrp', 'income tax']
    idx['person']['dict'] = dict(zip(idx['person']['to_keep'], idx['person']['new_name']))

    idx['hhld']['to_keep'] = ['weighta', 'p396p', 'sexhrp']
    idx['hhld']['new_name'] = ['weight', 'age HRP', 'sex HRP']
    idx['hhld']['dict'] = dict(zip(idx['hhld']['to_keep'], idx['hhld']['new_name']))
    
    dvhh = pd.read_csv(eval(dvhh_file), sep='\t', index_col=0)
    dvper = pd.read_csv(eval(dvper_file), sep='\t', index_col=0)
    
    dvhh.columns = dvhh.columns.str.lower()
    dvper.columns = dvper.columns.str.lower()
     
    person_data = dvper[idx['person']['to_keep']].rename(columns=idx['person']['dict'])
    person_data['income tax'] = np.zeros(shape=np.size(dvper,0))
    
    useful_data = dvhh[idx['hhld']['to_keep']].rename(columns=idx['hhld']['dict'])
    
    temp = useful_data.join(person_data, how = 'inner')
    temp = temp.apply(lambda x: pd.to_numeric(x, errors='coerce')).fillna(0)
    
    useful_data['ethnicity HRP'] = temp.groupby(level=0)['ethnicity_hrp'].sum()
    useful_data['no people'] = dvhh['a049']
    useful_data['type of hhold'] = dvhh['a062']
    useful_data['category of dwelling'] = dvhh['a116']
    useful_data['tenure type'] = dvhh['a122']
    useful_data['GOR modified'] = dvhh['gorx']
    useful_data['OA class 1D'] =  np.zeros(shape=len(dvhh))
    # OAC data only available from 2007
    if year > 2006: 
        useful_data['OAC_Supergroup'] = dvhh['oac1d']
        useful_data['OAC_Group'] = dvhh['oac2d']
        useful_data['OAC_Subgroup'] = dvhh['oac3d']
    useful_data['Income anonymised'] = dvhh['incanon']
    useful_data['Income tax'] = temp.groupby(level=0)['income tax'].sum()
    useful_data['Socio-ec HRP'] = dvhh['a091']
    
    return(useful_data)


#count OAC Subgroups in LCFS
def count_oac(sociodem_lcfs, all_oac, years):
    full_index_lookup = {}; full_index = {}
    for year in years:
        subgroup_totals = sociodem_lcfs[year][['GOR modified', 'OAC_Subgroup']]
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
        temp = temp.sum(level=['GOR', 'Supergroup', 'Group']).join(OACs).drop_duplicates()
        full_index_lookup[year]['Group_pass'] = temp.loc[temp['count'] >= 10]
        full_index_lookup[year]['Group_pass'] = full_index_lookup[year]['Group_pass'].join(full_index_lookup[year]['Group_pass']['OAC'].str.split(', ', expand = True))
    
        temp = temp.loc[temp['count'] < 10].drop_duplicates()
        OACs = temp.reset_index().groupby(['GOR', 'Supergroup'])['OAC'].apply(', '.join); OACs.columns = ['OAC']
        temp = temp.sum(level=['GOR', 'Supergroup']).join(OACs).drop_duplicates()
        full_index_lookup[year]['Supergroup_pass'] = temp.loc[temp['count'] >= 10]
        full_index_lookup[year]['Supergroup_pass'] = full_index_lookup[year]['Supergroup_pass'].join(full_index_lookup[year]['Supergroup_pass']['OAC'].str.split(', ', expand = True))
        
        temp = temp.loc[temp['count'] < 10]
        OACs = temp.reset_index().groupby(['Supergroup'])['OAC'].apply(', '.join); OACs.columns = ['OAC']
        temp = temp.sum(level=['Supergroup']).join(OACs).drop_duplicates()
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
def attach_exp(sociodem_lcfs, full_index, years):
    full_exp = {}
    for year in years:
        # calculate per capita expenditure
        check = sociodem_lcfs[year].reset_index()
        check['GOR modified'] = check['GOR modified'].astype(str)
        check = check.set_index(['GOR modified', 'OAC_Subgroup'])[['case', 'no people', 'weight']].join(full_index[year]).reset_index().set_index('case')
        check['pop'] = check['weight'] * check['no people']

        exp = sociodem_lcfs[year].loc[:, 'Income anonymised':'Income tax']

        check = check[['GOR modified', 'OAC', 'GOR', 'pop', 'weight', 'no people']].join(exp)
        
        full_exp[year] = check
    return(full_exp)

def agg_groups(sociodem_lcfs, full_exp, years):
    sociodem_full_index = {}; sociodem_oac = {}
    for year in years:
        # save all OAC levels
        sociodem_oac[year] = {}
        income = sociodem_lcfs[year]  
        income['pop'] = income['no people'] * income['weight']
        income.loc[:, 'Income anonymised':'Income tax'] = income.loc[:, 'Income anonymised':'Income tax'].apply(lambda x: x * income['weight'])
        for region in ['GOR', 'no_GOR']:
            sociodem_oac[year][region] = {}
            for level in ['Supergroup', 'Group', 'Subgroup']:
                if region == 'GOR':
                    group = ['GOR modified', 'OAC_' + level]
                else:
                    group = ['OAC_' + level]
                income.loc[income['OAC_' + level].isna() == True, 'OAC_' + level] = '0'
                income['OAC_' + level] = income['OAC_' + level].astype(str)
                temp = income.groupby(group).sum()
                temp.loc[:, 'Income anonymised':'Income tax'] = temp.loc[:, 'Income anonymised':'Income tax'].apply(lambda x: x/temp['pop'])
                sociodem_oac[year][region][level] = temp
        # for detailed OACxLCFS
        income = full_exp[year]
        income.loc[:, 'Income anonymised':'Income tax'] = income.loc[:, 'Income anonymised':'Income tax'].apply(lambda x: x*income['weight'])
        income['count'] = 1
        income = income.fillna(0).drop('GOR modified', axis=1).rename(columns={'GOR':'GOR modified'}).groupby(['GOR modified', 'OAC']).sum()
        income.loc[:, 'Income anonymised':'Income tax'] = income.loc[:, 'Income anonymised':'Income tax'].apply(lambda x: x/income['pop'])
        sociodem_full_index[year] = income.drop(['weight', 'no people'], axis=1)
    return(sociodem_full_index, sociodem_oac)