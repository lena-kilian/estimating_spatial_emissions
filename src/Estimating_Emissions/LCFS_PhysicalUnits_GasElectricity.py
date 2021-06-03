#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 16:53:55 2021

@author: lenakilian
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy as cp

data_dir = r'/Users/lenakilian/Documents/Ausbildung/UoLeeds/PhD/Analysis/data/'


first_year = 2007
last_year = 2016
combined_years = 2


def get_energy_msoa():

    #MSOA
    msoa_consumption = {year:pd.DataFrame(columns=['MSOA', 'Electricity', 'Gas', 'Region', 'LAD']) for year in range(2007, 2020)}
    #2007
    temp = {}
    regions =  ['EastEngland', 'EastMidlands', 'London', 'NorthEast', 'NorthWest', 'Scotland', 
                'SouthEast', 'SouthWest', 'Wales', 'WestMidlands', 'YorkshireHumber']
    for region in regions:
        name = data_dir + 'processed/LCFS/Gas_Electricity/Original_Data/MSOA/2007_MSOA_gas&elec_' + region + '.xls'
        temp[region] = pd.read_excel(name, header=9, sheet_name=None)
        for lad in list(temp[region].keys())[1:]:
            temp[region][lad] = temp[region][lad][['Unnamed: 1', 'Average consumption per meter', 'Unnamed: 26']]
            temp[region][lad] = temp[region][lad].dropna(how='any').iloc[1:, :]
            temp[region][lad].columns = ['MSOA', 'Electricity', 'Gas']
            temp[region][lad]['Region'] = list(temp[region].keys())[0]
            temp[region][lad]['LAD'] = lad
            msoa_consumption[2007] = msoa_consumption[2007].append(temp[region][lad])
        
    # 2008
    msoa_gas_2008 = pd.read_excel(data_dir + 'processed/LCFS/Gas_Electricity/Original_Data/MSOA/2008_MSOA_gas_GB.xls', header=7, sheet_name=None)
    msoa_elec_2008 = pd.read_excel(data_dir + 'processed/LCFS/Gas_Electricity/Original_Data/MSOA/2008_MSOA_elec_GB.xls', header=12, sheet_name=None)

    temp = {}
    for region in list(msoa_gas_2008.keys())[1:]:
        temp_gas = msoa_gas_2008[region][['LA name', 'MLSOA Code', 'Average consumption']].dropna(how='any')
        temp_gas.columns = ['LAD', 'MSOA', 'Gas']
        temp_gas['Region'] = region
        temp[region.lower().replace(' ', '')] = temp_gas
    for region in list(msoa_elec_2008.keys())[1:]:
        temp_elec = msoa_elec_2008[region][['MLSOA code', 'Average ordinary consumption']].dropna(how='any')
        temp_elec.columns = ['MSOA', 'Electricity']
        temp_gas = temp[region.lower().replace(' ', '')]
        msoa_consumption[2008] = msoa_consumption[2008].append(temp_gas.merge(temp_elec, on='MSOA'))
    
    # 2009
    msoa_gas_2009 = pd.read_excel(data_dir + 'processed/LCFS/Gas_Electricity/Original_Data/MSOA/2009_MSOA_gas_GB.xls', sheet_name=None)
    msoa_elec_2009 = pd.read_csv(data_dir + 'processed/LCFS/Gas_Electricity/Original_Data/MSOA/2009_MSOA_elec_GB.csv')

    temp = pd.DataFrame(columns=['MSOA', 'Gas', 'Region', 'LAD'])
    for region in list(msoa_gas_2008.keys())[1:]:
        temp_gas = msoa_gas_2008[region][['LA name', 'MLSOA Code', 'Average consumption']].dropna(how='any')
        temp_gas.columns = ['LAD', 'MSOA', 'Gas']
        temp_gas['Region'] = region
        temp = temp.append(temp_gas)

    msoa_elec_2009 = msoa_elec_2009[['mlsoa', 'av_consumption_dom']]; msoa_elec_2009.columns = ['MSOA', 'Electricity']
    msoa_consumption[2009] = temp_gas.merge(msoa_elec_2009, on='MSOA')
 
    # 2010 - 2019
    msoa_gas_201019 = pd.read_excel(data_dir + 'processed/LCFS/Gas_Electricity/Original_Data/MSOA/2010-19_MSOA_gas_GB.xlsx', header=1, sheet_name=None)
    msoa_elec_201019 = pd.read_excel(data_dir + 'processed/LCFS/Gas_Electricity/Original_Data/MSOA/2010-19_MSOA_elec_GB.xlsx', header=1, sheet_name=None)

    for year in range(2010, 2020):
        if year == 2019:
            msoa_year = str(year)
        else:
            msoa_year = str(year) + 'r'
        temp_gas = msoa_gas_201019[msoa_year][['Local Authority Name', 'Middle Layer Super Output Area (MSOA) Code', 'Mean consumption (kWh per meter)']].dropna(how='any')
        temp_gas.columns = ['LAD', 'MSOA', 'Gas']
        temp_gas['Region'] = np.nan
        temp_elec = msoa_elec_201019[msoa_year][['Middle Layer Super Output Area (MSOA) Code', ' Mean consumption (kWh per meter) ']].dropna(how='any')
        temp_elec.columns = ['MSOA', 'Electricity']
        msoa_consumption[year] = msoa_consumption[year].append(temp_gas.merge(temp_elec, on='MSOA'))
    
    for year in list(msoa_consumption.keys()):
        msoa_consumption[year] = msoa_consumption[year].drop_duplicates()

    return(msoa_consumption)
        

def energy_and_expenditure_msoa(MSOA_exp):
    msoa_consumption = get_energy_msoa()
        
    consumption_mean = {}
    for year in list(MSOA_exp.keys()):
        consumption_mean[year] = cp.copy(msoa_consumption[year])
        if combined_years > 1:
            for i in range(combined_years - 1):
                consumption_mean[year] = consumption_mean[year].append(msoa_consumption[year + i + 1])
        consumption_mean[year] = consumption_mean[year].set_index('MSOA')[['Electricity', 'Gas']].astype(float).mean(axis=0, level=0)
    
 
    MSOA_combined = {}
    for year in list(MSOA_exp.keys()):
        if year < 2011:
            MSOA_combined[year] = MSOA_exp[year][['4.4.2', '4.4.1']]
        else:
            MSOA_combined[year] = MSOA_exp[year][['4.4.2', '4.4.1']]
        MSOA_combined[year] = MSOA_combined[year].join(consumption_mean[year], how='left')
    
    return(MSOA_combined)
     

# LSOA
def energy_and_expenditure_lsoa(LSOA_exp):

    lsoa_consumption = {year:pd.DataFrame(columns=['LSOA', 'MSOA', 'Electricity', 'Gas', 'Region', 'LAD', 'Gas_meters', 'Electricity_meters']) for year in range(2008, 2020)}
    #2008
    lsoa_gas_2008 = pd.read_excel(data_dir + 'processed/LCFS/Gas_Electricity/Original_Data/LSOA/2008_LSOA_gas_EW.xls', header=8, sheet_name=None)
    lsoa_elec_2008 = pd.read_excel(data_dir + 'processed/LCFS/Gas_Electricity/Original_Data/LSOA/2008_LSOA_elec_EW.xls',  header=12, sheet_name=None)

    for region in list(lsoa_gas_2008.keys())[1:]:
        temp_gas = lsoa_gas_2008[region][['LA name', 'MLSOA code', 'LLSOA code', 'Avergage consumption (kWh)', 'Number of meters']].dropna(how='any')
        temp_gas.columns = ['LAD', 'MSOA', 'LSOA', 'Gas', 'Gas_meters']
        temp_gas['Region'] = region
        temp_elec = lsoa_elec_2008[region][['LLSOA code', 'Average ordinary domestic consumption', 'Number of ordinary domestic meters']].dropna(how='any')
        temp_elec.columns = ['LSOA', 'Electricity', 'Electricity_meters']
        lsoa_consumption[2008] = lsoa_consumption[2008].append(temp_gas.merge(temp_elec, on='LSOA'))
    
    # 2009
    lsoa_gas_2009 = pd.read_excel(data_dir + 'processed/LCFS/Gas_Electricity/Original_Data/LSOA/2009_LSOA_gas_EW.xls', header=7, sheet_name=None)
    lsoa_elec_2009 = pd.read_excel(data_dir + 'processed/LCFS/Gas_Electricity/Original_Data/LSOA/2009_LSOA_elec_EW.xls', header=10, sheet_name=None)

    for region in list(lsoa_gas_2009.keys())[1:]:
        temp_gas = lsoa_gas_2009[region][['LA name', 'MLSOA code', 'LLSOA code', 'Average consumption', 'Number of meters']].dropna(how='any')
        temp_gas.columns = ['LAD', 'MSOA', 'LSOA', 'Gas', 'Gas_meters']
        temp_gas['Region'] = region
        temp_elec = lsoa_elec_2009[region.upper()][['LLSOA code', 'Average ordinary consumption', 'Ordinary domestic (MPANs)']].dropna(how='any')
        temp_elec.columns = ['LSOA', 'Electricity', 'Electricity_meters']
        lsoa_consumption[2009] = lsoa_consumption[2009].append(temp_gas.merge(temp_elec, on='LSOA'))

    # 2010 - 2019
    lsoa_gas_201019 = pd.read_excel(data_dir + 'processed/LCFS/Gas_Electricity/Original_Data/LSOA/2010-19_LSOA_gas_GB.xlsx', header=1, sheet_name=None)
    lsoa_elec_201019 = pd.read_excel(data_dir + 'processed/LCFS/Gas_Electricity/Original_Data/LSOA/2010-19_LSOA_elec_GB.xlsx', header=1, sheet_name=None)

    for year in range(2010, 2020):
        if year == 2019:
            lsoa_year = str(year)
        else:
            lsoa_year = str(year) + 'r'
        if year < 2015:
            to_keep = ['Local Authority Name', 'Middle Layer Super Output Area (MSOA) Code', 
                  'Lower Layer Super Output Area (LSOA) Code', 'Number of meters','Mean consumption (kWh per meter)']
        else:
            to_keep = ['Local Authority Name', 'Middle Layer Super Output Area (MSOA) Code', 
                   'Lower Layer Super Output Area (LSOA) Code', 'Number of consuming meters','Mean consumption (kWh per meter)']
        temp_gas = lsoa_gas_201019[lsoa_year][to_keep].dropna(how='any')
        temp_gas.columns = ['LAD', 'MSOA', 'LSOA', 'Gas_meters', 'Gas']
        temp_gas['Region'] = np.nan
        temp_elec = lsoa_elec_201019[lsoa_year][['Lower Layer Super Output Area (LSOA) Code', 
                                             'Mean domestic electricity consumption \n(kWh per meter)',
                                             'Total number of domestic electricity meters']].dropna(how='any')
        temp_elec.columns = ['LSOA', 'Electricity', 'Electricity_meters']
        lsoa_consumption[year] = lsoa_consumption[year].append(temp_gas.merge(temp_elec, on='LSOA'))
    
    for year in list(lsoa_consumption.keys()):
        lsoa_consumption[year] = lsoa_consumption[year].drop_duplicates()
    
    consumption_mean = {}
    for year in list(LSOA_exp.keys()):
        consumption_mean[year] = cp.copy(lsoa_consumption[year])
        if combined_years > 1:
            for i in range(combined_years - 1):
                consumption_mean[year] = consumption_mean[year].append(lsoa_consumption[year + i + 1])
        consumption_mean[year] = consumption_mean[year].groupby('LSOA').mean()
    
    LSOA_combined =  {}
    for year in list(LSOA_exp.keys()):
        LSOA_combined[year] = LSOA_exp[year][['4.4.2', '4.4.1']]
       
        LSOA_combined[year] = LSOA_combined[year].join(consumption_mean[year], how='left')
    

    # fill missing LSOA values by using MSOA values
    msoa_consumption = get_energy_msoa(first_year, last_year, combined_years)

    # get LSOA values from MSOA
    LSOA_from_MSOA = {}
    LSOA_from_MSOA[2007] = LSOA_combined[2008].reset_index()[['index', 'MSOA']].rename(columns={'index':'LSOA'})\
        .merge(msoa_consumption[2007][['Region', 'LAD', 'Gas', 'Electricity']].reset_index().rename(columns={'MSOA01CD':'MSOA'}))
    for year in list(LSOA_combined.keys()):
        temp = msoa_consumption[year][['Gas', 'Electricity']].astype(float).reset_index()
        temp.columns = ['MSOA', 'Gas_fromMSOA', 'Electricity_fromMSOA']
        LSOA_from_MSOA[year] = LSOA_combined[year][['MSOA', 'Gas', 'Electricity']].reset_index()
        LSOA_from_MSOA[year].columns = ['LSOA', 'MSOA', 'Gas', 'Electricity']
        LSOA_from_MSOA[year] =  LSOA_from_MSOA[year].merge(temp, on='MSOA', how='left')
        for item in ['Gas', 'Electricity']:
            temp = LSOA_from_MSOA[year].loc[LSOA_from_MSOA[year][item].isna() == True, item + '_fromMSOA']
            LSOA_from_MSOA[year].loc[LSOA_from_MSOA[year][item].isna() == True, item] = temp
        
        LSOA_combined[year] = LSOA_combined[year].drop(['Gas', 'Electricity'], axis=1).join(LSOA_from_MSOA[year].set_index('LSOA')[['Gas', 'Electricity']])
    LSOA_combined[2007] = LSOA_exp[2007].set_index('LSOA01CD')[['4.4.1', '4.4.2']].join(LSOA_from_MSOA[2007].set_index('LSOA'))
    
    return(LSOA_combined)

    
# Adjust: As consumption not there for all, only weigh where it is there by consumption
def fill_empty_values(geog_combined):
    for year in list(geog_combined.keys()):
        geog_combined[year]['Missing'] = False
        geog_combined[year].loc[geog_combined[year]['Gas'].isna() == True, 'Missing'] = True
        
        # Use expenditure where missing, weigh expenditure by consumption where there
        for i in range(2):
            item = ['Electricity', 'Gas'][i]
            temp = geog_combined[year].groupby('Missing').sum().loc[False, '4.4.' + str(i+1)]
            geog_combined[year]['4.4.' + str(i+1) + '_w'] = pd.to_numeric(geog_combined[year][item], errors='coerce')
            geog_combined[year]['4.4.' + str(i+1) + '_w'] = geog_combined[year][item] / geog_combined[year][item].sum() * temp
            geog_combined[year].loc[geog_combined[year]['Missing'] == True, '4.4.' + str(i+1) + '_w'] = geog_combined[year].loc[geog_combined[year]['Missing'] == True]['4.4.' + str(i+1)]
        
        # Use mean consumption where missing
        for i in range(2):
            item = ['Electricity', 'Gas'][i]
            temp = geog_combined[year][item].mean()
            geog_combined[year]['4.4.' + str(i+1) + '_m'] = pd.to_numeric(geog_combined[year][item], errors='coerce')
            geog_combined[year].loc[geog_combined[year]['Missing'] == True, '4.4.' + str(i+1) + '_m'] = temp
            geog_combined[year]['4.4.' + str(i+1) + '_check'] = (geog_combined[year]['4.4.' + str(i+1) + '_m'] / 
                                                        geog_combined[year]['4.4.' + str(i+1) + '_m'].sum() *
                                                        geog_combined[year]['4.4.' + str(i+1)].sum())
    return(geog_combined)
            

def save_files(geog, geog_combined):

    writer = pd.ExcelWriter(data_dir + 'processed/LCFS/Gas_Electricity/' + geog + '_adjusted.xlsx')

    for year in list(geog_combined.keys()):
        geog_combined[year].to_excel(writer, sheet_name = str(year))

    writer.save()
    
    
def get_energy_data(geog_exp, geog):
    energy_data = eval("energy_and_expenditure_" + geog.lower() + "(geog_exp)")
    energy_data = fill_empty_values(energy_data)   
    save_files(geog, energy_data)
    
    print('Saved files to folder ' + data_dir + 'processed/LCFS/Gas_Electricity/' + geog + '_adjusted.xlsx')
        
        
        
    