#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 09:58:22 2020

@author: lenakilian
"""

import tabula
import pandas as pd
import numpy as np

use_for_io = ['1.1.1.1', '1.1.1.2', '1.1.1.3', '1.1.2', '1.1.3.1', '1.1.3.2', '1.1.4', 
              '1.1.5', '1.1.6', '1.1.7', '1.1.8', '1.1.9', '1.1.10.1', '1.1.10.2', 
              '1.1.10.3', '1.1.10.4', '1.1.11.1', '1.1.11.2', '1.1.11.3', '1.1.12.1', 
              '1.1.12.2', '1.1.12.3', '1.1.13', '1.1.14', '1.1.15.1', '1.1.15.2', '1.1.16', 
              '1.1.17', '1.1.18.1', '1.1.18.2', '1.1.19.1', '1.1.19.2', '1.1.19.3', 
              '1.1.19.4', '1.1.19.5', '1.1.19.6', '1.1.20', '1.1.21', '1.1.22', '1.1.23.1', 
              '1.1.23.2', '1.1.23.3', '1.1.23.4', '1.1.24', '1.1.25', '1.1.26', '1.1.27', 
              '1.1.28.1', '1.1.28.2', '1.1.29', '1.1.30', '1.1.31', '1.1.32', '1.1.33.1', 
              '1.1.33.2', '1.1.33.3', '1.2.1', '1.2.2', '1.2.3', '1.2.4', '1.2.5', '1.2.6', 
              
              '2.1.1', '2.1.2.1', '2.1.2.2', '2.1.2.3', '2.1.3.1', '2.1.3.2', '2.1.4',
              '2.2.1', '2.2.2.1', '2.2.2.2', 
              
              '3.1.1', '3.1.2', '3.1.3', '3.1.4', '3.1.5', '3.1.6', '3.1.7', '3.1.8', 
              '3.1.9.1', '3.1.9.2', '3.1.9.3', '3.1.9.4', '3.1.10', '3.1.11.1', '3.1.11.2', 
              '3.2.1', '3.2.2', '3.2.3', '3.2.4', 
              
              '4.1.1', '4.1.2', '4.2.1', '4.2.2', '4.2.3', '4.2.4', '4.3.1', '4.3.2', 
              '4.3.3', '4.4.1', '4.4.2', '4.4.3.1', '4.4.3.2', '4.4.3.3', 
              
              '5.1.1.1', '5.1.1.2', '5.1.1.3', '5.1.2.1', '5.1.2.2', '5.2.1', '5.2.2', 
              '5.3.1', '5.3.2', '5.3.3', '5.3.4', '5.3.5', '5.3.6', '5.3.7', '5.3.8', 
              '5.3.9', '5.4.1', '5.4.2', '5.4.3', '5.4.4', '5.5.1', '5.5.2', '5.5.3', 
              '5.5.4', '5.5.5', '5.6.1.1', '5.6.1.2', '5.6.2.1', '5.6.2.2', '5.6.2.3', 
              '5.6.2.4', '5.6.3.1', '5.6.3.2', '5.6.3.3', 
              
              '6.1.1.1', '6.1.1.2', '6.1.1.3', '6.1.1.4', '6.1.2.1', '6.1.2.2', '6.2.1.1', 
              '6.2.1.2', '6.2.1.3', '6.2.2', 
              
              '7.1.1.1', '7.1.1.2', '7.1.2.1', '7.1.2.2', '7.1.3.1', '7.1.3.2', '7.1.3.3', 
              '7.2.1.1', '7.2.1.2', '7.2.1.3', '7.2.1.4', '7.2.2.1', '7.2.2.2', '7.2.2.3', 
              '7.2.3.1', '7.2.3.2', '7.2.4.1', '7.2.4.2', '7.2.4.3', '7.2.4.4', '7.2.4.5', 
              '7.3.1.1', '7.3.1.2', '7.3.2.1', '7.3.2.2', '7.3.3.1', '7.3.3.2', '7.3.4.1', 
              '7.3.4.2', '7.3.4.3', '7.3.4.4', '7.3.4.5', '7.3.4.6', '7.3.4.7', '7.3.4.8', 
              
              '8.1', '8.2.1', '8.2.2', '8.2.3', '8.3.1', '8.3.2', '8.3.3', '8.3.4', '8.4', 
              
              '9.1.1.1', '9.1.1.2', '9.1.2.1', '9.1.2.2', '9.1.2.3', '9.1.2.4', '9.1.2.5', 
              '9.1.2.6', '9.1.2.7', '9.1.2.8', '9.1.2.9', '9.1.3.1', '9.1.3.2', '9.1.3.3', 
              '9.2.1', '9.2.2', '9.2.3', '9.2.4', '9.2.5', '9.2.6', '9.2.7', '9.2.8', 
              '9.3.1', '9.3.2.1', '9.3.2.2', '9.3.3', '9.3.4.1', '9.3.4.2', '9.3.4.3', 
              '9.3.4.4', '9.3.5.1', '9.3.5.2', '9.3.5.3', '9.4.1.1', '9.4.1.2', '9.4.1.3', 
              '9.4.1.4', '9.4.1.5', '9.4.2.1', '9.4.2.2', '9.4.2.3', '9.4.3.1', '9.4.3.2', 
              '9.4.3.3', '9.4.3.4', '9.4.3.5', '9.4.3.6', '9.4.4.1', '9.4.4.2', '9.4.4.3', 
              '9.4.5', '9.4.6.1', '9.4.6.2', '9.4.6.3', '9.4.6.4', '9.5.1', '9.5.2', 
              '9.5.3', '9.5.4', '9.5.5', 
              
              '10.1', '10.2', 
              
              '11.1.1', '11.1.2', '11.1.3', '11.1.4.1', '11.1.4.2', '11.1.4.3', '11.1.4.4', 
              '11.1.5', '11.1.6.1', '11.1.6.2', '11.2.1', '11.2.2', '11.2.3', 
              
              '12.1.1', '12.1.2', '12.1.3.1', '12.1.3.2', '12.1.3.3', '12.1.4', '12.1.5.1', 
              '12.1.5.2', '12.1.5.3', '12.2.1.1', '12.2.1.2', '12.2.1.3', '12.2.2.1', 
              '12.2.2.2', '12.2.2.3', '12.3.1.1', '12.3.1.2', '12.3.1.3', '12.3.1.4', 
              '12.4.1.1', '12.4.1.2', '12.4.1.3', '12.4.2', '12.4.3.1', '12.4.3.2', 
              '12.4.4', '12.5.1.1', '12.5.1.2', '12.5.1.3', '12.5.1.4', '12.5.1.5', 
              '12.5.2.1', '12.5.2.2', '12.5.2.3', '12.5.3.1', '12.5.3.2', '12.5.3.3', 
              '12.5.3.4', '12.5.3.5', 
              
              '13.1.1', '13.1.2', '13.1.3', '13.2.1', '13.2.2', '13.2.3', '13.3.1', 
              '13.3.2', '13.4.1.1', '13.4.1.2', '13.4.2.1', '13.4.2.2', '13.4.2.3', 
              '13.4.2.4', '13.4.3.1', '13.4.3.2', 
              
              '14.1.1', '14.1.2', '14.1.3', '14.2', '14.3.1', '14.3.2', '14.3.3', '14.3.4', 
              '14.3.5', '14.3.6', '14.3.7', '14.4.1', '14.4.2', '14.5.1', '14.5.2', 
              '14.5.3', '14.5.4', '14.5.5', '14.5.6', '14.5.7', '14.5.8', '14.6.1', 
              '14.6.2', '14.6.3', '14.7', '14.8']

# import specs documentation

years = ['2001-2002', '2002-2003', '2003-2004', '2004-2005', '2005-2006', '2006', '2007', '2009', '2010', 
         '2013', '2014', '2015-2016', '2016-2017']

# save first 2 as excel --> come in PDF
pages = ['261-277', '203-219']; names = ['4697userguide1.pdf', '5003userguide3.pdf']
for j in range(2):
    file = 'LCFS/'+ years[j] + '/mrdoc/pdf/' + names[j]
    temp = tabula.io.read_pdf(file, pages = pages[j], multiple_tables = True, pandas_options={'header':None})
    
    writer = pd.ExcelWriter('LCFS/'+ years[j] + '/mrdoc/excel/specs.xlsx')
    for i in range(len(temp)):
        temp[i].to_excel(writer, 'Sheet ' + str(i))
    writer.save()

names = ['specs.xlsx', 'specs.xlsx', '5210spec2003-04.xls', '5375tablea1spec2004-05.xls', '5688_specification_family_spending_EFS_2005-06.xls',
         '5986_spec2006_userguide.xls', '6118_spec2007_userguide.xls', '6655spec2009_v2.xls', '6945spec2010.xls', '7702_2013_specification.xls',
         '7992_spec2014.xls', '8210_spec_2015-16.xls', '8351_spec2016-17.xls']
specs = {}
for j in range(len(years)):
    specs[int(years[j][:4])] = pd.read_excel('LCFS/'+ years[j] + '/mrdoc/excel/' + names[j], sheet_name=None, header=None)
    
cleaned_specs = {}
for year in list(specs.keys())[2:]:
    cleaned_specs[year] = {}
    i = 0
    for item in list(specs[year].keys()):
        cleaned_specs[year][item] = specs[year][item]
        if 'Family Spending' in item:
            pass
        elif 'changes' in item:
            pass
        else:
            if 'FS code' in cleaned_specs[year][item].iloc[:, 1].tolist():
                cleaned_specs[year][item] = cleaned_specs[year][item].iloc[:, 1:]
            if 'FS code' in cleaned_specs[year][item].iloc[:, 0].tolist():
                cleaned_specs[year][item] = cleaned_specs[year][item].iloc[:, 1:]
            if 'FS codes' in cleaned_specs[year][item].iloc[:, 0].tolist():
                cleaned_specs[year][item] = cleaned_specs[year][item].iloc[:, 1:]
            cleaned_specs[year][item] = cleaned_specs[year][item].loc[cleaned_specs[year][item].iloc[:, 0] != 'FS code']\
                .dropna(axis=0, how='all').dropna(axis=1, how='all')
            cleaned_specs[year][item] = cleaned_specs[year][item].loc[cleaned_specs[year][item].iloc[:, 0] != 'Variable']
            if 'Alcohol' in item or 'Clothing' in item:
                if len(cleaned_specs[year][item].columns) > 6:
                    cleaned_specs[year][item] = cleaned_specs[year][item].dropna(axis=1, how='all')
                if len(cleaned_specs[year][item].columns) > 6:
                    cleaned_specs[year][item] = cleaned_specs[year][item].iloc[:, :-1]
            else:
                if len(cleaned_specs[year][item].columns) > 6:
                    cleaned_specs[year][item] = cleaned_specs[year][item].iloc[:, :-1]
                if len(cleaned_specs[year][item].columns) > 6:
                    cleaned_specs[year][item] = cleaned_specs[year][item].dropna(axis=1, how='all')
            cleaned_specs[year][item].columns = ['LCFS_1', 'COIPLUS_1', 'Desc_1', 'LCFS_2', 'COIPLUS_2', 'Desc_2']
            cleaned_specs[year][item].loc[cleaned_specs[year][item]['LCFS_1'].str.len() > 90, 'LCFS_1'] = np.nan
            cleaned_specs[year][item] = cleaned_specs[year][item].dropna(how='all')
            for j in range(1, 3):
                cleaned_specs[year][item].loc[
                    cleaned_specs[year][item]['COIPLUS_' + str(j)].str[-1] == '.', 
                    'COIPLUS_' + str(j)] = cleaned_specs[year][item]['COIPLUS_' + str(j)].str[:-1]
            if i == 0:
                cleaned_specs[year]['all'] =  cleaned_specs[year][item]
                i += 1
            else:
                cleaned_specs[year]['all'] = cleaned_specs[year]['all'].append(cleaned_specs[year][item])
                

writer = pd.ExcelWriter('LCFS/lcfs_coiplus_lookup.xlsx')

check_specs = all_specs = {year:cleaned_specs[year]['all'].dropna(how='all') for year in list(specs.keys())[2:]}
new_specs = {}
no_rooms = ['A114', 'a114', 'a114', 'a114', 'a114p', 'a114p', 'a114p', 'a114p', 'a114p', 
            'a114p', 'a114p', 'a114p', 'a114p', 'a114p', 'a114p', 'a114p', 'a114p']
room_dict = dict(zip([int(x[:4]) for x in years], no_rooms))

for year in list(check_specs.keys()):
    check_specs[year].index = list(range(len(check_specs[year])))
    check_specs[year].loc[check_specs[year]['COIPLUS_2'].isnull() == True, 
                          'COIPLUS_2'] = check_specs[year]['COIPLUS_1']
    for i in range(1, 3):
        if i == 1:
            temp = check_specs[year][['LCFS_1', 'LCFS_2', 'COIPLUS_1', 'Desc_1']]
            temp.loc[temp['LCFS_1'].isnull() == True, 'LCFS_1'] = temp['LCFS_2']
        else:
            temp = all_specs[year][['LCFS_2', 'COIPLUS_2', 'Desc_2']]
            temp.index = list(range(len(temp)))
        temp2 = temp['COIPLUS_' + str(i)].tolist(); temp3 = temp['Desc_' + str(i)].tolist()
        for j in range(1, len(temp2)):
            if pd.isnull(temp2[j]) == True:
                temp2[j] = temp2[j-1]; temp3[j] = temp3[j-1]
        temp['COIPLUS_all'] = temp2; temp['Desc_all'] = temp3
        temp = temp[['LCFS_' + str(i), 'COIPLUS_all', 'Desc_all']].apply(lambda x: x.astype(str))
        temp = temp.set_index(['COIPLUS_all', 'Desc_all']).groupby('COIPLUS_all')['LCFS_' + str(i)].transform(lambda x: '+'.join(x)).drop_duplicates()
        temp.columns = 'LCFS'
        if i == 1:
            new_specs[year] = temp
        else:
            new_specs[year] = new_specs[year].append(temp).reset_index()
    new_specs[year].columns = ['COIPLUS', 'Description', 'LCFS_Code']
    new_specs[year]['LCFS_Code'] = [x.replace(' ', '').replace('nan+', '')\
                                    .replace('+nan', '').replace('nan', '')\
                                        .replace('++', '+').replace('+-', '-')\
                                            .replace('-', '-1*')
                                    for x in new_specs[year]['LCFS_Code'].tolist()]
    new_specs[year]['COIPLUS'] = [x.split(' ')[0] for x in new_specs[year]['COIPLUS'].tolist()]
    new_specs[year] = new_specs[year].loc[new_specs[year]['COIPLUS'] != 'nan']
    new_specs[year]['Level_1'] = [pd.to_numeric(x.split('.')[0], errors='coerce') for x in new_specs[year]['COIPLUS'].tolist()]
    for i in range(2, 5):
        temp = []
        for x in new_specs[year]['COIPLUS'].tolist():
            if len(x.split('.')) > i-1:
                temp.append(pd.to_numeric(x.split('.')[i-1], errors='coerce'))
            else:
                temp.append(0)
        new_specs[year]['Level_' + str(i)] = temp
    new_specs[year].loc[new_specs[year]['LCFS_Code'].str[-1] == '+', 
                        'LCFS_Code'] = new_specs[year]['LCFS_Code'].str[:-1]
    new_specs[year] = new_specs[year].set_index(['Level_1', 'Level_2', 'Level_3', 'Level_4']).sort_index().drop_duplicates()
    new_specs[year].loc[new_specs[year]['COIPLUS'] == '4.1.2', 'Description'] = 'Imputed Rent'
    new_specs[year].loc[new_specs[year]['COIPLUS'] == '4.1.2', 'LCFS_Code'] = 'owned_prop*' + room_dict[year]
    new_specs[year] = new_specs[year].loc[new_specs[year]['Description'] != 'nan']
    new_specs[year] = new_specs[year].loc[new_specs[year]['LCFS_Code'] != '']
    new_specs[year]['IO_use'] = False
    new_specs[year].loc[new_specs[year]['COIPLUS'].isin( use_for_io) == True, 'IO_use'] = True
    new_specs[year].loc[new_specs[year][
        'Description'] != 'Stationery, diaries, address books, art materials']
    new_specs[year]['Description'] = new_specs[year]['Description'].str.replace(' and ', ' & ')
    new_specs[year] = new_specs[year].drop_duplicates()
    new_specs[year].to_excel(writer, str(year))
writer.save()

check = new_specs[2003].loc[new_specs[2003]['IO_use'] == True]

# missing
# 8.4 - Internet Subscription Fees - 9.4.3.7 in coiplus

desc_anne_john = pd.read_excel('LCFS/lcfs_desc_anne&john.xlsx', header=None)
desc_anne_john['COICOP'] = [x.split(' ')[0] for x in desc_anne_john[0]]
desc_anne_john['Description_AJ'] = [' '.join(x.split(' ')[1:]) for x in desc_anne_john[0]]
coicop_anne_john = pd.read_excel('LCFS/lcfs_coicop_lookup_anne&john.xlsx', sheet_name=None)
writer = pd.ExcelWriter('LCFS/lcfs_coicop_full_lookup.xlsx')
for year in list(check_specs.keys()):
    temp = new_specs[year].reset_index()
    coicop_anne_john[str(year)] = coicop_anne_john[str(year)].merge(desc_anne_john[['COICOP', 'Description_AJ']], on='COICOP', how='left')
    coicop_anne_john[str(year)]['COIPLUS'] = coicop_anne_john[str(year)]['COICOP']
    coicop_anne_john[str(year)] = coicop_anne_john[str(year)].merge(temp, on='COIPLUS', how='left')
    
    missing = coicop_anne_john[str(year)].loc[coicop_anne_john[str(year)]['LCFS_Code'].isnull() == True][['COICOP', 'LCFS', 'Description_AJ']]
    temp['LCFS_low'] = temp['LCFS_Code'].str.lower()
    missing['LCFS_low'] = missing['LCFS'].str.lower()
    missing = missing.merge(temp, on='LCFS_low', how='left').drop('LCFS_low', axis=1)
    
    coicop_anne_john[str(year)] = coicop_anne_john[str(year)].loc[coicop_anne_john[str(year)]['LCFS_Code'].isnull() == False]
    coicop_anne_john[str(year)] = coicop_anne_john[str(year)].append(missing)
    coicop_anne_john[str(year)] = coicop_anne_john[str(year)][['COICOP', 'COIPLUS', 'LCFS', 'LCFS_Code', 'Description_AJ', 'Description',]]
    coicop_anne_john[str(year)].columns = ['COICOP_AJ', 'COIPLUS_specsdoc', 'LCFS_AJ', 'LCFS_specsdoc', 'Description_AJ', 'Description_specsdoc']
    for i in range(1, 5):
        temp = []
        for x in coicop_anne_john[str(year)]['COICOP_AJ'].tolist():
            if len(x.split('.')) > i-1:
                temp.append(pd.to_numeric(x.split('.')[i-1], errors='coerce'))
            else:
                temp.append(0)
        coicop_anne_john[str(year)]['Level_' + str(i)] = temp
    coicop_anne_john[str(year)] = coicop_anne_john[str(year)].set_index(['Level_1', 'Level_2', 'Level_3', 'Level_4']).sort_index().drop_duplicates()
    coicop_anne_john[str(year)].to_excel(writer, str(year))
writer.save()