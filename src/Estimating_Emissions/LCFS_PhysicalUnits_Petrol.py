#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 7 15:46:00 2020

This file controls for physical use of petrol at LAD level

@author: Lena Kilian
"""

import pandas as pd
import copy as cp
            
years = list(range(2007, 2018))

working_directory = "/Users/lenakilian/Documents/Ausbildung/UoLeeds/PhD/Analysis"

petrol = pd.read_excel(eval("r'" + working_directory + "/data/raw/Transport/road-transport-fuel-consumption-tables-2005-2018.xlsx'"), header=0, index_col=0, sheet_name=None)
cols = {}
for year in years:
    cols[year] = {}
    for i in range(3):
        cols[year][i] = petrol[str(year)].iloc[i,:].tolist()
        for j in range(1, len(cols[year][i])):
            if pd.isna(cols[year][i][j]) == True:
                cols[year][i][j] = cols[year][i][j-1]
            else:
                pass
    petrol[str(year)].columns = pd.MultiIndex.from_arrays([cols[year][0], cols[year][2], cols[year][1]])
    petrol[year] = petrol[str(year)].dropna(how='any')
    petrol[year] = petrol[year][['Personal']].droplevel(axis=1, level=0).drop(['Motorways', 'Total consumption'], axis=1).sum(axis=1, level=1).drop(['Buses'], axis=1)
    petrol[year]['Total'] = petrol[year].sum(1)
    petrol[year].columns = ['lad', 'diesel', 'petrol', 'motor', 'other']


lookup = pd.read_csv(eval("r'" + working_directory + "/data/raw/Geography/Conversion_Lookups/UK_full_lookup_2001_to_2011.csv'"))
pop_01 = pd.read_csv(eval("r'" + working_directory + "/data/raw/Geography/Census_Populations/census2001_pop_uk_oa.csv'")).set_index('OA01CD')
pop_11 = pd.read_csv(eval("r'" + working_directory + "/data/raw/Geography/Census_Populations/census2011_pop_uk_oa.csv'")).set_index('OA11CD')
mid_year_pop = pd.read_csv(eval("r'" + working_directory + "/data/raw/Geography/Census_Populations/mid_year_pop.csv'"), index_col=0, header=2)

petrol_sublad = {}; all_data = pd.DataFrame(columns=['year', 'petrol_geog', 'diesel_geog', 'other_geog', 'pop', 'geog', 'geog11CD'])
for geog in ['MSOA', 'LSOA']:
    petrol_sublad[geog] = {}
    for year in years:
        if year < 2014:
            pop = cp.copy(pop_01)
            oac_year = '01'
        else:
            pop = cp.copy(pop_11)
            oac_year = '11'
        pop['pop'] = pop['population'] / pop['population'].sum() * int(mid_year_pop.loc[str(year), 'pop'])
        temp = lookup.set_index('OA' + oac_year + 'CD')[[geog + oac_year + 'CD', 'LAD17CD']].join(pop[['pop']])
        geog_pop = pd.DataFrame(temp.groupby(geog + oac_year + 'CD').sum()).join(temp.drop('pop', axis=1).drop_duplicates().set_index([geog + oac_year + 'CD']))
        lad_pop = pd.DataFrame(temp.groupby('LAD17CD').sum()['pop']).reset_index().rename(columns={'pop':'lad_pop'})
        pop = geog_pop.reset_index().merge(lad_pop, on='LAD17CD', how='left')
            
        petrol_sublad[geog][year] = pop.set_index('LAD17CD').join(pd.DataFrame(petrol[year]), how='left')
        for oil in ['diesel', 'petrol', 'other']:
            petrol_sublad[geog][year][oil + '_pc'] = petrol_sublad[geog][year][oil]/ petrol_sublad[geog][year]['lad_pop']
            petrol_sublad[geog][year][oil + '_geog'] = petrol_sublad[geog][year][oil + '_pc'] * petrol_sublad[geog][year]['pop']
        petrol_sublad[geog][year] = petrol_sublad[geog][year].reset_index().rename(columns={'index':'LAD17CD'}).set_index(geog + oac_year + 'CD')[['LAD17CD', 'petrol_geog', 'diesel_geog', 'other_geog', 'pop']]
        
        temp = petrol_sublad[geog][year].reset_index().rename(columns={geog + '11CD':'geog11CD', geog + '01CD':'geog11CD'})
        temp['year'] = year
        temp['geog'] = geog
        all_data = all_data.append(temp)

all_data.to_csv(eval("r'" + working_directory + "/data/processed/LCFS/Controls/LAD_road_use.csv'"))
