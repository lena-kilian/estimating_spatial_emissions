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
    
    dvhh = pd.read_csv(dvhh_file, sep='\t', index_col=0)
    dvper = pd.read_csv(dvper_file, sep='\t', index_col=0)
    
    dvhh.columns = dvhh.columns.str.lower()
    dvper.columns = dvper.columns.str.lower()
    
    owned_prop = np.zeros(shape = len(dvhh))
    for n in range (1,len(dvhh)):
        if dvhh['a121'].iloc[n] == 5 or dvhh['a121'].iloc[n] == 6 or dvhh['a121'].iloc[n] == 7:
            owned_prop[n] = 1
     
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