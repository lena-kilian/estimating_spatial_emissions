#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 14:19:05 2020

Functions to attach the LCFS to carbon emissions, based on code by Anne Owen

@author: lenakilian
"""

import numpy as np
import pandas as pd
import io_functions as io
df = pd.DataFrame
import demand_functions as dm
import copy as cp

def convert36to33(Y,concs_dict2,years):
    
    Y2 = {}
    
    for yr in years:
        temp = np.dot(Y[yr],concs_dict2['C43_to_C40'])
        Y2[yr] = df(temp, index = Y[yr].index, columns = concs_dict2['C43_to_C40'].columns)
    
    return Y2

"""
def make_totals(hhspenddata, years, concs_dict2, total_Yhh_112):
    
    coicop_exp_tot = {}
    
    for yr in years:
        coicop_exp_tot[yr] = np.sum(hhspenddata[yr].loc[:,'1.1.1.1':'12.5.3.5'],0)
    
    coicop_exp_tot2 = {}
    
    for yr in years:
        corrector = np.zeros(shape = 307)
        countstart = 0
        countend = 0
        for numb in range(0,33):
            conc = concs_dict2[str(numb)+'a']
            countend = np.sum(np.sum(conc))+countstart
            lcf_subtotal = np.sum(np.dot(coicop_exp_tot[yr],conc)) #*52/1000)
            required_subtotal = np.sum(total_Yhh_112[yr].iloc[:,numb])
            correction_factor = required_subtotal/lcf_subtotal
            for c in range(countstart,countend):
                corrector[c] = correction_factor
            countstart = countend
        coicop_exp_tot2[yr] = np.dot(coicop_exp_tot[yr],np.diag(corrector))
    
    return coicop_exp_tot2
"""


def expected_totals(hhspenddata, years, concs_dict2, total_Yhh_106):
    coicop_exp_tot = {}
    for year in years:
        temp = np.sum(hhspenddata[year], 0)

        corrector = np.zeros(shape = 307)
        start = 0
        end = 0
        corrector = []
    
        for i in range(0, 33):
            conc = concs_dict2[str(i) + 'a']
            end = len(conc.columns) + start
            lcf_subtotal = np.sum(np.dot(temp, conc))
            required_subtotal = np.sum(total_Yhh_106[year].iloc[:, i])
            corrector += [required_subtotal/lcf_subtotal for i in range(start, end)]
            start = end
        coicop_exp_tot[year] = np.dot(temp, np.diag(corrector))  
        
    return(coicop_exp_tot)


def make_y_hh_307(Y,coicop_exp_tot,years,concs_dict2,meta):
    
    yhh_wide = {}
    
    for yr in years:
        temp = np.zeros(shape = [meta['fd']['len_idx'],307])
        countstart = 0
        countend = 0
        col = []
        for a in range(0,33):
            conc = np.tile(concs_dict2[str(a)],(meta['reg']['len'],1))
            countend = np.sum(np.sum(concs_dict2[str(a)+'a']))+countstart
            category_total = np.dot(coicop_exp_tot[yr],concs_dict2[str(a)+'a'])
            #test1 = np.dot(np.diag(Y[yr].iloc[:,a]),conc)
            test1 = np.dot(conc,np.diag(category_total))
            #test2 = np.tile(np.dot(Y[yr].iloc[:,a],conc),(1590,1))
            test2 = np.transpose(np.tile(np.dot(conc,category_total),(np.size(conc,1),1)))
            test3 = test1/test2
            test3 = np.nan_to_num(test3, copy=True)
            #num = np.dot(conc,np.diag(category_total))
            #test4 = np.multiply(num,test3)
            test4 = np.dot(np.diag(Y[yr].iloc[:,a]),test3)
            #den = np.dot(np.diag(np.sum(num,1)),concs_dict2[str(a)])
            #prop = np.divide(num,den)
            #prop = np.nan_to_num(prop, copy=True)
            #temp[:,countstart:countend] = (np.dot(np.diag(total_Yhh_106[yr].iloc[:,a]),prop))
            temp[:,countstart:countend] = test4
            col[countstart:countend] = concs_dict2[str(a) + 'a'].columns
            countstart = countend
        yhh_wide[yr] = df(temp, columns = col)
            
    return yhh_wide


def make_y_hh_prop(Y,total_Yhh_106,meta,years):
    
    yhh_prop = {}
    
    for yr in years:
        temp = np.zeros(shape=(len(Y[yr])))
    
        for r in range(0,meta['reg']['len']):
            temp[r*106:(r+1)*106] = np.divide(np.sum(Y[yr].iloc[r*106:(r+1)*106,0:36],1),np.sum(total_Yhh_106[yr],1))
            np.nan_to_num(temp, copy = False)
        
        yhh_prop[yr] = temp

        
    return yhh_prop


def make_new_Y(Y,yhh_wide,meta,years):
    
    newY = {}
    col = []
    
    for yr in years:
        temp = np.zeros(shape=[len(Y[yr]),314])
        temp[:,0:307] = yhh_wide[yr]
        temp[:,307:314] = Y[yr].iloc[:,33:40]
        col[0:307] = yhh_wide[yr].columns
        col[307:314] = Y[yr].iloc[:,33:40].columns
        newY[yr] = df(temp, index = Y[yr].index, columns = col)
    
    return newY


def make_ylcf_props(hhspenddata,years):
    
    ylcf_props = {}
    
    for yr in years:
        totalspend = np.sum(hhspenddata[yr].loc[:,'1.1.1.1':'12.5.3.5'])
        temp = np.divide(hhspenddata[yr].loc[:,'1.1.1.1':'12.5.3.5'],np.tile(totalspend,[len(hhspenddata[yr]),1]))
        np.nan_to_num(temp, copy = False)
        ylcf_props[yr] = df(temp, index = hhspenddata[yr].index)
        
    return ylcf_props


def makefoot(S,U,Y,stressor,years):
    footbyCOICOP = {}
    for yr in years:
        temp = np.zeros(shape = 307)
        Z = io.make_Z_from_S_U(S[yr],U[yr]) 
        bigY = np.zeros(shape = [np.size(Y[yr],0)*2,np.size(Y[yr],1)])
        bigY[np.size(Y[yr],0):np.size(Y[yr],0)*2,0:] = Y[yr]     
        x = io.make_x(Z,bigY)
        L = io.make_L(Z,x)
        bigstressor = np.zeros(shape = [np.size(Y[yr],0)*2,1])
        bigstressor[0:np.size(Y[yr],0),:] = stressor[yr]
        e = np.sum(bigstressor,1)/x
        eL = np.dot(e,L)
        for a in range(0,307):
            temp[a] = np.dot(eL,bigY[:,a])
        footbyCOICOP[yr] = temp  

    return footbyCOICOP


def makelcffootdata(domfootbyLCF_nrg,impfootbyLCF_nrg,hhspenddata,years):
    
    data = {}
    
    for yr in years:
        temp = np.zeros(shape = [len(domfootbyLCF_nrg[yr]),307+307+17])
        cols = ['index','weight','age','sex','ethnicity','number of people','household type','dwelling type','tenure type','GOR','OAC','income','income tax','Soc-ec','no of rooms','cum sum','income rank',]
        temp[:,0] = hhspenddata[yr].index
        temp[:,1:10] = hhspenddata[yr].loc[:,'weight':'GOR modified']
        for a in range(0,len(hhspenddata[yr])):
            if hhspenddata[yr].iloc[a,9] == ' ':
                temp[a,10] = 0
            else:
                temp[a,10] = int(hhspenddata[yr].iloc[a,9])
        temp[:,11:15] = hhspenddata[yr].loc[:,'Income anonymised':'rooms in accommodation']        
        cols[17:324] = hhspenddata[yr].loc[:,'1.1.1.1':'12.5.3.5'].columns
        cols[341:631] = hhspenddata[yr].loc[:,'1.1.1.1':'12.5.3.5'].columns
        temp[:,17:17+307] = domfootbyLCF_nrg[yr][:,0:307]
        temp[:,17+307:17+307+307] = impfootbyLCF_nrg[yr][:,0:307]
        temp2 = df(temp,columns = cols)
        temp3 = temp2.sort_values('income')
        weightsum = np.sum(temp3.loc[:,'weight'])
        weightsum20 = weightsum/20
        temp3.iloc[0,15] = temp3.iloc[0,1]
        for a in range(1,len(domfootbyLCF_nrg[yr])):
            temp3.iloc[a,15] = temp3.iloc[a-1,15] +  temp3.iloc[a,1] 
        a=0 
        for b in range(0,len(domfootbyLCF_nrg[yr])): 
               
            if temp3.iloc[b,15]<(a+1)*weightsum20:
                temp3.iloc[b,16] = a
            else:
                a=a+1    
        temp3.iloc[b,16] = a-1    
        data[yr] = temp3    
        
    return data
    
def lcfs_analysis(exp_data, concs_dict, concs_dict2, og_Y, S, U, meta, ghg, uk_ghg_direct):
    Y = cp.copy(og_Y)
    hhdspend_uk = {}
    for year in list(exp_data.keys()):
        temp = exp_data[year].loc[:,'1.1.1.1':'12.5.3.5']
        hhdspend_uk[year] = temp.apply(lambda x: x * exp_data[year]['pop'])
        hhdspend_uk[year].index = exp_data[year].index

        # use concs
        temp = np.dot(Y[year], concs_dict2['C43_to_C40'])
        Y[year] = df(temp, index = Y[year].index, columns = concs_dict2['C43_to_C40'].columns)

    total_Yhh_106 = dm.make_Yhh_106(Y, list(exp_data.keys()), meta)

    coicop_exp_tot = expected_totals(hhdspend_uk, list(exp_data.keys()), concs_dict2, total_Yhh_106)

    yhh_wide = make_y_hh_307(Y, coicop_exp_tot, list(exp_data.keys()), concs_dict2, meta)
    #yhh_prop = lcfs.make_y_hh_prop(Y,total_Yhh_106,meta,years)
    newY = make_new_Y(Y, yhh_wide, meta, list(exp_data.keys()))
    ylcf_props = make_ylcf_props(hhdspend_uk, list(exp_data.keys()))

    COICOP_ghg = makefoot(S, U, newY, ghg, list(exp_data.keys()))

    LCFSxOAC_ghg = {}; PC_ghg = {}
    for year in list(exp_data.keys()):
        COICOP_ghg[year][160] += uk_ghg_direct[year][1]
        COICOP_ghg[year][101] += uk_ghg_direct[year][0]
    
        # this gives GHG emissions for the groups, break down to per capita emissions
        temp = np.dot(ylcf_props[year], np.diag(COICOP_ghg[year]))
        LCFSxOAC_ghg[year] = df(temp, index=hhdspend_uk[year].index, columns=hhdspend_uk[year].columns)
        PC_ghg[year] = LCFSxOAC_ghg[year].apply(lambda x: x/exp_data[year]['pop'])
    
    return(COICOP_ghg, LCFSxOAC_ghg, PC_ghg)

def no_gor_check(exp_data, LCFSxOAC_ghg):
    no_gor = {}
    for year in list(exp_data.keys()):
        # make check for those with missing OACs --> check that these are random, ie same distribution as others
        no_gor[year] = LCFSxOAC_ghg[year].join(exp_data[year][['pop']]).reset_index()
        no_gor[year]['OAC'] = False; no_gor[year].loc[no_gor[year]['OAC_Supergroup'] > 0, 'OAC'] = True
        no_gor[year] = no_gor[year].set_index(['GOR modified', 'OAC_Supergroup', 'OAC'])
        no_gor[year].columns = pd.MultiIndex.from_arrays([[str(x).split('.')[0] for x in no_gor[year].columns.tolist()], [x for x in no_gor[year].columns.tolist()]])
        no_gor[year] = no_gor[year].sum(level=0, axis=1)
        no_gor[year] = no_gor[year].apply(lambda x: x/no_gor[year]['pop'])
    return(no_gor)

def detailed_oac_aggregation(PC_ghg_detailed, oac, PC_ghg_supergroup):
    OA_ghg_detailed = {}
    for year in list(PC_ghg_detailed.keys()): #list(PC_ghg_detailed.keys()):
        if year < 2013:
            oac_year = oac[2001]
        else:
            oac_year = oac[2011]
        
        ghg_data = PC_ghg_detailed[year].reset_index()
        ghg_data['OAC'] = ghg_data['OAC'].astype(str).str.replace(' ', '').str.upper()
        
        OA_full = oac_year[['OA_SA', 'GOR modified','OAC_Supergroup', 'OAC_Group', 'OAC_Subgroup']]
        for level in ['OAC_Supergroup', 'OAC_Group', 'OAC_Subgroup']:
            OA_full[level] = OA_full[level].astype(str).str.replace(' ', '').str.upper()
        
        for df in [ghg_data, OA_full]:
            df['GOR modified'] = df['GOR modified'].astype(int).astype(str)
        
        # merge by level, to avoid merging one OA with multiple profiles
        level_merge = {}
        for level in ['OAC_Subgroup', 'OAC_Group', 'OAC_Supergroup']:
            temp = ghg_data.rename(columns={'OAC':level})
            level_merge[level] = OA_full.merge(temp, on=['GOR modified', level])
            OA_full = OA_full.loc[OA_full['OA_SA'].isin(level_merge[level]['OA_SA']) == False]        
        
        # combine and add supergroup UK wide level info for missing
        PC_ghg_supergroup[year].index = [str(x) for x in PC_ghg_supergroup[year].index]
        OA_ghg_detailed[year] = OA_full.merge(PC_ghg_supergroup[year].reset_index().rename(columns={'index':'OAC_Supergroup'}), on='OAC_Supergroup') # these are OAs without matching OACs
        for level in ['OAC_Subgroup', 'OAC_Group', 'OAC_Supergroup']:
            OA_ghg_detailed[year] = OA_ghg_detailed[year].append(level_merge[level])

        if year > 2011:
            pop = oac[2011].rename(columns={'POPULATION':'population'})[['OA_SA', 'population']]
            OA_ghg_detailed[year] = OA_ghg_detailed[year].merge(pop, on='OA_SA')

        OA_ghg_detailed[year] = OA_ghg_detailed[year].drop(['OAC_Subgroup', 'OAC_Group', 'OAC_Supergroup'], axis=1).set_index('OA_SA')
    return(OA_ghg_detailed)
    

def geog_aggregation(OA_ghg_detailed, oac_all, years, geog_level):
    new_ghg_detailed= {}
    for year in years:
        if year > 2010:
            oac_year = 2011
        else:
            oac_year = 2001
            
        temp = cp.copy(OA_ghg_detailed[year])
        geog_var = geog_level + str(oac_year)[2:] + 'CD'
        
        lsoa_lookup = oac_all[oac_year]

        temp = temp.join(lsoa_lookup.set_index('OA' + str(oac_year)[2:] + 'CD')[[geog_var]])
        temp = temp.set_index([geog_var], append=True)
        temp = temp.loc[:,'1.1.1.1':'population']
        temp['population'] = temp['population'].astype(int)
        temp.loc[:,'1.1.1.1':'12.5.3.5'] = temp.loc[:,'1.1.1.1':'12.5.3.5'].apply(lambda x: x * temp['population'])
    
        new_ghg_detailed[year] = temp.sum(level=geog_var)
        new_ghg_detailed[year].loc[:,'1.1.1.1':'12.5.3.5'] = new_ghg_detailed[year].loc[:,'1.1.1.1':'12.5.3.5']\
            .apply(lambda x: x / new_ghg_detailed[year]['population'])
    return(new_ghg_detailed)

