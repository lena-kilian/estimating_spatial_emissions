#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Tue May  5 14:19:05 2020

Functions to attach the LCFS to carbon emissions, adapted by Lena Kilian from code by Anne Owen

@author: earao and lenakilian

Data sources:
    
GHG by industry data:
https://www.gov.uk/government/statistics/uks-carbon-footprint

Direct emissions data:
https://www.ons.gov.uk/economy/environmentalaccounts/datasets/ukenvironmentalaccountsatmosphericemissionsgreenhousegasemissionsbyeconomicsectorandgasunitedkingdom

UKMRIO model:
via the University of Leeds
'''


import pandas as pd
import numpy as np
import pickle
import functions_2001_2017_LCFS as lcfs
import demand_functions as dm

df = pd.DataFrame

io_filepath = 'IO data/2020/'
lcf_filepath = 'LCFS/'
concs_filepath = 'Concordances/'

years = list(range(2001,2018))

# load IO and ghg data
meta = pickle.load(open(io_filepath + "meta.p", "rb" ))
ghg = pickle.load(open(io_filepath + "ghg.p", "rb" ))
uk_ghg_direct = pickle.load(open(io_filepath + "uk_ghg_direct.p", "rb" ))
S = pickle.load(open(io_filepath + "S.p", "rb" )) # supply table
U = pickle.load(open(io_filepath + "U.p", "rb" )) # use table
Y = pickle.load(open(io_filepath + "Y.p", "rb" )) # final deman table
Z = {year : lcfs.calc_Z(S[year], U[year]) for year in years} # make Z from supply and use tables

# load LFCS data
hhdspend_lcfs = {}
lcf_years = ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015-2016', '2016-2017', '2017-2018']
years = [int(year[:4]) for year in lcf_years]


# use total UK, to ensure number of people in each household type are taken into account
hhdspend_uk = {}
for year in years:
    temp = hhdspend_lcfs[year].loc[:,'1.1.1.1':'12.5.3.5']
    hhdspend_uk[year] = temp.apply(lambda x: x * hhdspend_lcfs[year]['weight'])

# load and clean up concs to make it usable
concordances = pd.read_excel(io_filepath + 'ONS_to_COICOP_LCF_concs.xlsx', sheet_name=None) 
concordances = {item : concordances[item].set_index('Unnamed: 0') for item in concordances.keys()}

# aggregate Y from 43 to 40 sectors
for year in years:
    temp = np.dot(Y[year], concordances['C43_to_C40'])
    Y[year] = df(temp, index = Y[year].index, columns = concordances['C43_to_C40'].columns)

# sort out exactly what this is later!! --> reduces regions, but how?!
total_Yhh_106 = dm.make_Yhh_106(Y, years, meta)


coicop_exp_tot = {year : lcfs.expected_totals(hhdspend_uk[year], total_Yhh_106[year], concordances) for year in years}


yhh_wide = lcfs.make_y_hh_307(Y, coicop_exp_tot, years, concordances, meta)
    
newY = lcfs.make_new_Y(Y, yhh_wide, meta, years)

COICOP_ghg = lcfs.makefoot(S, U, newY, ghg, years)

for year in years:
    COICOP_ghg[year][160] = COICOP_ghg[year][160]+uk_ghg_direct[year][1]
    COICOP_ghg[year][101] = COICOP_ghg[year][101]+uk_ghg_direct[year][0]
    
emission_factors = {year : COICOP_ghg[year] / (hhdspend_uk[year].sum()) for year in years}

