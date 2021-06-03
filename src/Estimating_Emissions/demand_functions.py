#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 10:09:25 2018

This function is used with household_demand_main.py

@author: earao
"""

import pandas as pd
import numpy as np
import io_functions as io
import os
df = pd.DataFrame

def make_footprint(S,U,Y,nrg,allyears):
    footprint = np.zeros(shape = [10,len(allyears)])
    count = 0
    for yr in allyears:
        Z = io.make_Z_from_S_U(S[yr],U[yr])
        bigY = np.zeros(shape = [np.size(Y['1997'],0)*2,np.size(Y['1997'],1)])
        bigY[np.size(Y['1997'],0):np.size(Y['1997'],0)*2,0:8] = Y[yr]
        x = io.make_x(Z,bigY)
        L = io.make_L(Z,x)
        bignrg = np.zeros(shape = [np.size(Y['1997'],0)*2,1])
        bignrg[0:np.size(Y['1997'],0),:] = nrg[yr]
        e = np.sum(bignrg,1)/x
     
        temp = np.dot(np.dot(np.diag(e),L),np.diag(np.sum(bigY[:,0:7],1)))
        
        for a in range(0,4):
            footprint[a,count] = np.sum(temp[a*106:(a+1)*106,:])
        count = count+1
    return footprint

def make_Yhh_112(Y_d,years,meta):
    
    total_Yhh_112 = {}
    col =  Y_d[years[0]].columns[0:36]
    idx =  Y_d[years[0]].index[0:112]
    for yr in years:
        temp = np.zeros(shape = [112,36])
        
        for r in range(0,meta['reg']['len']):
            temp  = temp + Y_d[yr].iloc[r*112:(r+1)*112,0:36].values
            
        total_Yhh_112[yr] = df(temp, index =idx, columns =col)
    
    return total_Yhh_112

def make_defra_foot(S,U,Y,stressor,years):
    defra_foot = {}
    for yr in years:
        Z = io.make_Z_from_S_U(S[yr],U[yr])
        bigY = np.zeros(shape = [np.size(Y['1997'],0)*2,np.size(Y['1997'],1)])
        bigY[np.size(Y['1997'],0):np.size(Y['1997'],0)*2,0:8] = Y[yr]
        x = io.make_x(Z,bigY)
        L = io.make_L(Z,x)
        bigstressor = np.zeros(shape = [np.size(Y['1997'],0)*2,1])
        bigstressor[0:np.size(Y['1997'],0),:] = stressor[yr]
        e = np.sum(bigstressor,1)/x     
        hhold = np.dot(np.dot(np.diag(e),L),np.diag(bigY[:,0]))
        npish = np.dot(np.dot(np.diag(e),L),np.diag(bigY[:,1]))
        cgovr = np.dot(np.dot(np.diag(e),L),np.diag(bigY[:,2]))
        lgovr = np.dot(np.dot(np.diag(e),L),np.diag(bigY[:,3]))
        gfcap = np.dot(np.dot(np.diag(e),L),np.diag(bigY[:,4]))
        valua = np.dot(np.dot(np.diag(e),L),np.diag(bigY[:,5]))
        chinv = np.dot(np.dot(np.diag(e),L),np.diag(bigY[:,6]))
        temp = np.zeros(shape = [106,49])
        temp[:,0] = np.sum(hhold[0:106,424:530],0)+np.sum(hhold[0:106,530:636],0)+np.sum(hhold[0:106,636:742],0)+np.sum(hhold[0:106,742:848],0)
        temp[:,1] = np.sum(npish[0:106,424:530],0)+np.sum(npish[0:106,530:636],0)+np.sum(npish[0:106,636:742],0)+np.sum(npish[0:106,742:848],0)
        temp[:,2] = np.sum(cgovr[0:106,424:530],0)+np.sum(cgovr[0:106,530:636],0)+np.sum(cgovr[0:106,636:742],0)+np.sum(cgovr[0:106,742:848],0)
        temp[:,3] = np.sum(lgovr[0:106,424:530],0)+np.sum(lgovr[0:106,530:636],0)+np.sum(lgovr[0:106,636:742],0)+np.sum(lgovr[0:106,742:848],0)
        temp[:,4] = np.sum(gfcap[0:106,424:530],0)+np.sum(gfcap[0:106,530:636],0)+np.sum(gfcap[0:106,636:742],0)+np.sum(gfcap[0:106,742:848],0)
        temp[:,5] = np.sum(valua[0:106,424:530],0)+np.sum(valua[0:106,530:636],0)+np.sum(valua[0:106,636:742],0)+np.sum(valua[0:106,742:848],0)
        temp[:,6] = np.sum(chinv[0:106,424:530],0)+np.sum(chinv[0:106,530:636],0)+np.sum(chinv[0:106,636:742],0)+np.sum(chinv[0:106,742:848],0)
        temp[:,7] = np.sum(hhold[106:212,424:530],0)
        temp[:,8] = np.sum(npish[106:212,424:530],0)
        temp[:,9] = np.sum(cgovr[106:212,424:530],0)
        temp[:,10] = np.sum(lgovr[106:212,424:530],0)
        temp[:,11] = np.sum(gfcap[106:212,424:530],0)
        temp[:,12] = np.sum(valua[106:212,424:530],0)
        temp[:,13] = np.sum(chinv[106:212,424:530],0)
        temp[:,14] = np.sum(hhold[212:318,424:530],0)
        temp[:,15] = np.sum(npish[212:318,424:530],0)
        temp[:,16] = np.sum(cgovr[212:318,424:530],0)
        temp[:,17] = np.sum(lgovr[212:318,424:530],0)
        temp[:,18] = np.sum(gfcap[212:318,424:530],0)
        temp[:,19] = np.sum(valua[212:318,424:530],0)
        temp[:,20] = np.sum(chinv[212:318,424:530],0)
        temp[:,21] = np.sum(hhold[318:424,424:530],0)
        temp[:,22] = np.sum(npish[318:424,424:530],0)
        temp[:,23] = np.sum(cgovr[318:424,424:530],0)
        temp[:,24] = np.sum(lgovr[318:424,424:530],0)
        temp[:,25] = np.sum(gfcap[318:424,424:530],0)
        temp[:,26] = np.sum(valua[318:424,424:530],0)
        temp[:,27] = np.sum(chinv[318:424,424:530],0)
        temp[:,28] = np.sum(hhold[106:212,530:636],0)+np.sum(hhold[106:212,636:742],0)+np.sum(hhold[106:212,742:848],0)
        temp[:,29] = np.sum(npish[106:212,530:636],0)+np.sum(npish[106:212,636:742],0)+np.sum(npish[106:212,742:848],0)
        temp[:,30] = np.sum(cgovr[106:212,530:636],0)+np.sum(cgovr[106:212,636:742],0)+np.sum(cgovr[106:212,742:848],0)
        temp[:,31] = np.sum(lgovr[106:212,530:636],0)+np.sum(lgovr[106:212,636:742],0)+np.sum(lgovr[106:212,742:848],0)
        temp[:,32] = np.sum(gfcap[106:212,530:636],0)+np.sum(gfcap[106:212,636:742],0)+np.sum(gfcap[106:212,742:848],0)
        temp[:,33] = np.sum(valua[106:212,530:636],0)+np.sum(valua[106:212,636:742],0)+np.sum(valua[106:212,742:848],0)
        temp[:,34] = np.sum(chinv[106:212,530:636],0)+np.sum(chinv[106:212,636:742],0)+np.sum(chinv[106:212,742:848],0)
        temp[:,35] = np.sum(hhold[212:318,530:636],0)+np.sum(hhold[212:318,636:742],0)+np.sum(hhold[212:318,742:848],0)
        temp[:,36] = np.sum(npish[212:318,530:636],0)+np.sum(npish[212:318,636:742],0)+np.sum(npish[212:318,742:848],0)
        temp[:,37] = np.sum(cgovr[212:318,530:636],0)+np.sum(cgovr[212:318,636:742],0)+np.sum(cgovr[212:318,742:848],0)
        temp[:,38] = np.sum(lgovr[212:318,530:636],0)+np.sum(lgovr[212:318,636:742],0)+np.sum(lgovr[212:318,742:848],0)
        temp[:,39] = np.sum(gfcap[212:318,530:636],0)+np.sum(gfcap[212:318,636:742],0)+np.sum(gfcap[212:318,742:848],0)
        temp[:,40] = np.sum(valua[212:318,530:636],0)+np.sum(valua[212:318,636:742],0)+np.sum(valua[212:318,742:848],0)
        temp[:,41] = np.sum(chinv[212:318,530:636],0)+np.sum(chinv[212:318,636:742],0)+np.sum(chinv[212:318,742:848],0)
        temp[:,42] = np.sum(hhold[318:424,530:636],0)+np.sum(hhold[318:424,636:742],0)+np.sum(hhold[318:424,742:848],0)
        temp[:,43] = np.sum(npish[318:424,530:636],0)+np.sum(npish[318:424,636:742],0)+np.sum(npish[318:424,742:848],0)
        temp[:,44] = np.sum(cgovr[318:424,530:636],0)+np.sum(cgovr[318:424,636:742],0)+np.sum(cgovr[318:424,742:848],0)
        temp[:,45] = np.sum(lgovr[318:424,530:636],0)+np.sum(lgovr[318:424,636:742],0)+np.sum(lgovr[318:424,742:848],0)
        temp[:,46] = np.sum(gfcap[318:424,530:636],0)+np.sum(gfcap[318:424,636:742],0)+np.sum(gfcap[318:424,742:848],0)
        temp[:,47] = np.sum(valua[318:424,530:636],0)+np.sum(valua[318:424,636:742],0)+np.sum(valua[318:424,742:848],0)
        temp[:,48] = np.sum(chinv[318:424,530:636],0)+np.sum(chinv[318:424,636:742],0)+np.sum(chinv[318:424,742:848],0)
   
        defra_foot[yr] = temp   
    return defra_foot


def make_hhfootprint(S,U,Y,stressor,allyears,meta):
    
    footprint = np.zeros(shape = [meta['reg']['len'],len(allyears)])
    count = 0
    for yr in allyears:
        Z = io.make_Z_from_S_U(S[yr],U[yr])
        bigY = np.zeros(shape = [np.size(Y[yr],0)*2,np.size(Y[yr],1)])
        bigY[np.size(Y[yr],0):np.size(Y[yr],0)*2,:] = Y[yr]
        x = io.make_x(Z,bigY)
        L = io.make_L(Z,x)
        bigstressor = np.zeros(shape = [np.size(Y[yr],0)*2,1])
        bigstressor[0:np.size(Y[yr],0),:] = stressor[yr]
        e = np.sum(bigstressor,1)/x
     
        temp = np.dot(np.dot(np.diag(e),L),np.diag(np.sum(bigY[:,0:36],1)))
        
        for a in range(0,meta['reg']['len']):
            footprint[a,count] = np.sum(temp[a*106:(a+1)*106,:])
        count = count+1
    
    return footprint

def make_simonrobertsdata(S,U,Y,stressor,allyears,meta):
    
    data = np.zeros(shape = [meta['use_dd']['len_col'],len(allyears)+1])
    count = 0
    for yr in allyears:
        Z = io.make_Z_from_S_U(S[yr],U[yr])
        bigY = np.zeros(shape = [np.size(Y[yr],0)*2,np.size(Y[yr],1)])
        bigY[np.size(Y[yr],0):np.size(Y[yr],0)*2,:] = Y[yr]
        x = io.make_x(Z,bigY)
        L = io.make_L(Z,x)
        bigstressor = np.zeros(shape = [np.size(Y[yr],0)*2,1])
        bigstressor[0:np.size(Y[yr],0),:] = stressor[yr]
        e = np.sum(bigstressor,1)/x
     
        temp = np.dot(np.dot(np.diag(e),L),np.diag(np.sum(bigY[:,0:7],1)))
        
        for a in range(0,meta['use_dd']['len_col']):
            temp2 = 0
            for b in range(1,meta['reg']['len']):
                temp2 = temp2 + np.sum(temp[b*meta['use_dd']['len_col']+a,424:848])
            
            data[a,count] = temp2
        count = count+1
    
    return data

def makeSDA(S,U,Y,nrg,allyears):
    
    yr0 = '2005'
    Z0 = io.make_Z_from_S_U(S[yr0],U[yr0])
    bigY0 = np.zeros(shape = [2120,8])
    bigY0[1060:2120,0:8] = Y[yr0]
    bigYhh0 = bigY0[:,0]
    totalY0 = np.sum(np.sum(bigY0[:,0]))
    propY0 = bigY0[:,0]/totalY0
    x0 = io.make_x(Z0,bigY0)
    L0 = io.make_L(Z0,x0)
    bignrg0 = np.zeros(shape = [2120,1])
    bignrg0[0:1060,:] = nrg[yr0]
    e0 = np.sum(bignrg0,1)/x0
    count = 0
    temp = np.zeros(shape = [12,3])
    temp2 = np.zeros(shape = [12,3])
    for yr in allyears:
        yr1 = yr
        Z1 = io.make_Z_from_S_U(S[yr1],U[yr1])
        bigY1 = np.zeros(shape = [2120,8])
        bigY1[1060:2120,0:8] = Y[yr1]
        bigYhh1 = bigY1[:,0]
        totalY1 = np.sum(np.sum(bigY1[:,0]))
        propY1 = bigY1[:,0]/totalY1
        x1 = io.make_x(Z1,bigY1)
        L1 = io.make_L(Z1,x1)
        bignrg1 = np.zeros(shape = [2120,1])
        bignrg1[0:1060,:] = nrg[yr1]
        e1 = np.sum(bignrg1,1)/x1
 
        foot_0 = np.dot(e0,L0)
        foot_0 = np.dot(foot_0,bigYhh0)

        foot_1 = np.dot(e1,L1)
        foot_1 = np.dot(foot_1,bigYhh1)
        
        foot_2 = np.dot(e0,L0)
        foot_2 = np.dot(foot_2,propY0)
        foot_2 = np.dot(foot_2,totalY0)

        foot_3 = np.dot(e1,L1)
        foot_3 = np.dot(foot_3,propY1)
        foot_3 = np.dot(foot_3,totalY1)

        sda_0 = {}
        sda_0[0] = e0
        sda_0[1] = L0
        sda_0[2] = bigYhh0
            
        sda_1 = {}
        sda_1[0] = e1
        sda_1[1] = L1
        sda_1[2] = bigYhh1
        
        sda_2 = {}
        sda_2[0] = np.dot(e0,L0)
        sda_2[1] = propY0
        sda_2[2] = totalY0
            
        sda_3 = {}
        sda_3[0] = np.dot(e1,L1)
        sda_3[1] = propY1
        sda_3[2] = totalY1
          
        result = io.sda(sda_1,sda_0)
          
        temp[count,:] = result[6,1:4]

        result2 = io.sda(sda_3,sda_2)
          
        temp2[count,:] = result2[6,1:4]
        count = count+1               
    
    return (temp,temp2)

def make_Yhh_106(Y_d,years,meta):
    
    total_Yhh_106 = {}
    col =  Y_d[years[0]].columns[0:36]
    idx =  Y_d[years[0]].index[0:106]
    for yr in years:
        temp = np.zeros(shape = [106,36])
        
        for r in range(0,meta['reg']['len']):
            temp  = temp + Y_d[yr].iloc[r*106:(r+1)*106,0:36].values
            
        total_Yhh_106[yr] = df(temp, index =idx, columns =col)
    
    return total_Yhh_106


def make_oa_exp_136(oa_exp_tot,conc,tax,cc_deflators,total_Yhh_106,years):

    oa_exp_136 = {}
    
    for yr in years:
        temp = df.dot(oa_exp_tot[yr],conc)
        temp2 = df.dot(temp,np.diag(tax))
        temp3 = df.dot(temp2,np.diag(cc_deflators.loc[int(yr)]))*52
        prop = np.sum(total_Yhh_106[yr]*1000000,0)/np.sum(np.sum(temp3))
        temp4 = temp3*prop
        oa_exp_136[yr] = df(temp4)
        oa_exp_136[yr].columns = conc.columns
    
    return oa_exp_136

def make_oa_exp_136_nodef(oa_exp_tot,conc,tax,total_Yhh_106,years):

    oa_exp_136 = {}
    
    for yr in years:
        temp = df.dot(oa_exp_tot[yr],conc)
        temp2 = df.dot(temp,np.diag(tax))
        temp3 = temp2*52
        prop = np.sum(np.sum(total_Yhh_106[yr]*1000000,0)/np.sum(np.sum(temp3)))
        temp4 = temp3*prop
        oa_exp_136[yr] = df(temp4)
        oa_exp_136[yr].columns = conc.columns
    
    return oa_exp_136


def make_LCF_136(LCFspendtot,tax,cc_deflators,total_Yhh_106,years):

    lcf_136 = {}
    
    for yr in years:
        temp = np.dot(np.diag(tax),LCFspendtot[yr])
        temp2 = np.dot(np.diag(cc_deflators.loc[int(yr)]),temp)*52
        prop = np.sum(total_Yhh_106[yr]*1000000,0)/np.sum(np.sum(temp2))
        temp3 = temp2*prop
        lcf_136[yr] = df(temp3, index = LCFspendtot[yr].index, columns = LCFspendtot[yr].columns)
    
    return lcf_136


def make_y_hh_wide(total_Yhh_106,oa_exp_136,to_balance,years):
    
    yhh_wide= {}
    
    temp2 = np.zeros(shape = [106,136,6])
    count = 0
    for yr in years:
        print(yr)
        true_row_sum = total_Yhh_106[yr]*1000000
        true_col_sum = np.sum(oa_exp_136[yr],0)
        true_row_sum[true_row_sum==0] = 0.000000001
        true_col_sum[true_col_sum==0] = 0.000000001       
        temp = io.ras(true_row_sum,true_col_sum.values,to_balance.values)
        temp2[:,:,count] = temp
        yhh_wide[yr] = df(temp2[:,:,count])
        count = count+1
        
    return yhh_wide

def make_y_hh_wide2(total_Yhh_106,oa_exp_136,years,concs_dict2):
    
    yhh_wide = {}
    temp = np.zeros(shape = [106,136])
    countstart = 0
    countend = 0
    col = []
    for yr in years:
        tot_136 = np.sum(oa_exp_136[yr])
        for a in range(1,34):
            print(a)
            tot = np.dot(tot_136,concs_dict2[str(a) + 'a'])
            countend = len(tot)+countstart
            num = np.dot(concs_dict2[str(a)],np.diag(tot))
            den = np.transpose(np.tile(np.sum(num,1),(len(tot),1)))
            prop = np.divide(num,den)
            prop = np.nan_to_num(prop, copy=True)
            print(countstart)
            print(countend)
            temp[:,countstart:countend] = np.dot(np.diag(total_Yhh_106[yr].iloc[:,a-1]),prop) 
            col[countstart:countend] = concs_dict2[str(a) + 'a'].columns
            countstart = countend
        yhh_wide[yr] = df(temp, columns = col)
            
    return yhh_wide


def make_y_hh_wideLCF(total_Yhh_106,lcf_136,to_balance,years):
    
    yhh_wide= {}
    
    temp2 = np.zeros(shape = [106,136,len(years)])
    count = 0
    for yr in years:
        print(yr)
        true_row_sum = total_Yhh_106[yr]*1000000
        true_col_sum = np.sum(lcf_136[yr],1)
        true_row_sum[true_row_sum==0] = 0.000000001
        true_col_sum[true_col_sum==0] = 0.000000001       
        temp = io.ras(true_row_sum,true_col_sum.values,to_balance.values)
        temp2[:,:,count] = temp
        yhh_wide[yr] = df(temp2[:,:,count])
        count = count+1
        
    return yhh_wide

def make_yhh_prop(yhh,Y,regions,total_Yhh_106):
    
    yhh_prop = np.zeros(shape=(len(Y)))
    
    for r in range(0,regions):
        yhh_prop[r*106:(r+1)*106] = np.divide(Y[r*106:(r+1)*106],total_Yhh_106)
        yhh_prop[r*106+78] = 0
        
    return yhh_prop

def make_y_hh_prop2(Y,total_Yhh_106,meta,years):
    
    yhh_prop = {}
    
    for yr in years:
        temp = np.zeros(shape=(len(Y[yr])))
    
        for r in range(0,meta['reg']['len']):
            temp[r*106:(r+1)*106] = np.divide(np.sum(Y[yr].iloc[r*106:(r+1)*106,0:36],1),np.sum(total_Yhh_106[yr],1))
            np.nan_to_num(temp, copy = False)
        
        yhh_prop[yr] = temp

        
    return yhh_prop


def make_new_Y(Y,yhh_prop,yhh_wide,meta,years):
    
    newY = {}
    col = []
    
    for yr in years:
        temp = np.zeros(shape=[len(Y[yr]),143])
        for r in range(0,meta['reg']['len']):
            temp[r*106:(r+1)*106,0:136] = np.dot(np.diag(yhh_prop[yr][r*106:(r+1)*106]),yhh_wide[yr])
        temp[:,136:143] = Y[yr].iloc[:,36:43]
        col[0:136] = yhh_wide[yr].columns
        col[136:143] = Y[yr].iloc[:,36:43].columns
        newY[yr] = df(temp, index = Y[yr].index, columns = col)
    
    return newY
    
def make_exp_mult(S_d,U_d,Y_d,nrg,years,yhh_prop,yhh_wide,oa_exp_136):
  #  e = {}
    nrg_CC_mult = {}
    file = '/Users/earao/Source Data/IEA/direct_from_ons.xlsx'
    direct = pd.read_excel(file, sheet_name='direct')
    oa_exp = {}
    foots = np.zeros(shape=[6,1])   
    count = 0
    eL = {}
   # L = {}
    nrg_prod_mult=np.zeros(shape=[136,106,len(years)]) 
    for yr in years:
        
        Z = io.make_Z_from_S_U(S_d[yr],U_d[yr])
        bigY = np.zeros(shape = [2120,8])
        bigY[1060:2120,0:8] = Y_d[yr]
        x = io.make_x(Z,bigY)
        L = io.make_L(Z,x)
        bignrg = np.zeros(shape = [2120,1])
        bignrg[0:1060,:] = nrg[yr]
        e = np.sum(bignrg,1)/x
        eL[yr] = np.dot(e,L)
        
        tempyprop = np.zeros(shape = (len(Z)))
        tempyprop[len(S_d[yr]):] = yhh_prop[yr]
        temp_nrg_prod_mult = np.zeros(shape=[106])
        nrg_prod_big = np.multiply(eL[yr],tempyprop)
        for a in range(0,10):
            temp_nrg_prod_mult = temp_nrg_prod_mult + nrg_prod_big[(a*106)+1060:((a+1)*106)+1060]
        
        nrg_prod_mult[:,:,count] = np.tile(temp_nrg_prod_mult,[136,1])
        
        foot = np.multiply(np.transpose(nrg_prod_mult[:,:,count]),yhh_wide[yr])
        foot = np.nan_to_num(foot)
        foot = np.sum(foot,0)+direct.loc[:,int(yr)]
        foots[count,0] = np.sum(foot,0)/1000000
        
        nrg_CC_mult[yr] =np.divide(foot,np.sum(yhh_wide[yr],0))/1000000
        
        np.nan_to_num(nrg_CC_mult[yr], copy = False) 
    
        temp = np.divide(np.sum(yhh_wide[yr],0),np.sum(oa_exp_136[yr],0))    
        oa_exp[yr] = df(np.dot(oa_exp_136[yr],np.diag(temp)), index = oa_exp_136[yr].index, columns = oa_exp_136[yr].columns)
    
        np.nan_to_num(oa_exp[yr], copy = False)
        count = count+1
    return (oa_exp,nrg_CC_mult)    
 
def make_oa_exp(yhh_wide,oa_exp_136,years):   
    
    oa_exp = {}
    
    for yr in years:
        temp = np.divide(np.sum(yhh_wide[yr],0),np.sum(oa_exp_136[yr],0))    
        oa_exp[yr] = df(np.dot(oa_exp_136[yr],np.diag(temp)), index = oa_exp_136[yr].index, columns = oa_exp_136[yr].columns)
    
        np.nan_to_num(oa_exp[yr], copy = False)

    return oa_exp 

def make_ghg_mult(L,eghg,uk_ghg_direct,years,yhh_prop,yhh_wide,meta):
    ghg_CC_mult = {}
     
    for yr in years:
        eL = np.dot(eghg,L)
        
        tempyprop = np.zeros(shape = (len(L)))
        tempyprop[1590:3180] = yhh_prop[yr]
        
        temp_ghg_prod_mult = np.zeros(shape=[106])
        ghg_prod_big = np.multiply(eL,tempyprop)
        
        for a in range(0,meta['reg']['len']):
            temp_ghg_prod_mult = temp_ghg_prod_mult + ghg_prod_big[(a*106)+1590:((a+1)*106)+1590]
        
        ghg_prod_mult = np.tile(temp_ghg_prod_mult,[136,1])
               
        ghgfoot = np.multiply(np.transpose(ghg_prod_mult),yhh_wide[yr])
        ghgfoot = np.nan_to_num(ghgfoot)
        ghgfoot = np.sum(ghgfoot,0)
        ghgfoot[62] = ghgfoot[62] +uk_ghg_direct[yr].iloc[0]
        ghgfoot[80] = ghgfoot[80] +uk_ghg_direct[yr].iloc[1]
        ghgfoots = np.sum(ghgfoot,0)
        
        ghg_CC_mult[yr] =np.divide(ghgfoot,np.sum(yhh_wide[yr],0))
        
        np.nan_to_num(ghg_CC_mult[yr], copy = False)
        
    return ghg_CC_mult

def make_mat_mult(L,emat,years,yhh_prop,yhh_wide,meta):
    mat_CC_mult = {}
     
    mat_prod_mult=np.zeros(shape=[136,106,len(years)]) 
    
    eL = np.dot(emat,L)
        
    tempyprop = np.zeros(shape = (len(L)))
    tempyprop[1590:3180] = yhh_prop[2016]
        
    temp_mat_prod_mult = np.zeros(shape=[106])
    mat_prod_big = np.multiply(eL,tempyprop)
        
    for a in range(0,meta['reg']['len']):
        temp_mat_prod_mult = temp_mat_prod_mult + mat_prod_big[(a*106)+1590:((a+1)*106)+1590]
        
    mat_prod_mult = np.tile(temp_mat_prod_mult,[136,1])
               
    matfoot = np.multiply(np.transpose(mat_prod_mult),yhh_wide[2016])
    matfoot = np.nan_to_num(matfoot)
    matfoot = np.sum(matfoot,0)
    matfoots = np.sum(matfoot,0)
         
    mat_CC_mult =np.divide(matfoot,np.sum(yhh_wide[2016],0))
        
    np.nan_to_num(mat_CC_mult, copy = False)
    
    return (mat_CC_mult) 

def make_wat_mult(L,ewat,uk_wat_direct,years,yhh_prop,yhh_wide,meta):
    wat_CC_mult = {}
     
    for yr in years:
        eL = np.dot(ewat,L)
        
        tempyprop = np.zeros(shape = (len(L)))
        tempyprop[1590:3180] = yhh_prop[yr]
        
        temp_wat_prod_mult = np.zeros(shape=[106])
        wat_prod_big = np.multiply(eL,tempyprop)
        
        for a in range(0,meta['reg']['len']):
            temp_wat_prod_mult = temp_wat_prod_mult + wat_prod_big[(a*106)+1590:((a+1)*106)+1590]
        
        wat_prod_mult = np.tile(temp_wat_prod_mult,[136,1])
               
        watfoot = np.multiply(np.transpose(wat_prod_mult),yhh_wide[yr])
        watfoot = np.nan_to_num(watfoot)
        watfoot = np.sum(watfoot,0)
        watfoot[60] = watfoot[60] +uk_wat_direct[yr-1997]
        watfoots = np.sum(watfoot,0)
        
        wat_CC_mult[yr] =np.divide(watfoot,np.sum(yhh_wide[yr],0))
        
        np.nan_to_num(wat_CC_mult[yr], copy = False)
        
    return wat_CC_mult

def make_oafoot(oa_pop,oa_exp,ghg_CC_mult,years):
    ghgfoot_oa = {}
    
    for yr in years:
        temp = np.diag(ghg_CC_mult[yr])       
        ghgmult = df(temp,index = oa_exp[yr].columns,columns = oa_exp[yr].columns)
        temp2 = np.dot(oa_exp[yr],ghgmult)  
        ghgfoot_oa[yr] = df(temp2, index = oa_exp[yr].index, columns = oa_exp[yr].columns)
   
    return (ghgfoot_oa)
    
def make_exp_mult_LCF(S_d,U_d,Y_d,nrg,years,yhh_prop,yhh_wide,lcf_136):
  #  e = {}
    nrg_CC_mult = {}
    file = '/Users/earao/Source Data/IEA/direct_from_ons.xlsx'
    direct = pd.read_excel(file, sheet_name='direct')
    lcf_exp = {}
    foots = np.zeros(shape=[len(years),1])   
    count = 0
    eL = {}
   # L = {}
    nrg_prod_mult=np.zeros(shape=[136,106,len(years)]) 
    for yr in years:
        
        Z = io.make_Z_from_S_U(S_d[yr],U_d[yr])
        bigY = np.zeros(shape = [2120,8])
        bigY[1060:2120,0:8] = Y_d[yr]
        x = io.make_x(Z,bigY)
        L = io.make_L(Z,x)
        bignrg = np.zeros(shape = [2120,1])
        bignrg[0:1060,:] = nrg[yr]
        e = np.sum(bignrg,1)/x
        eL[yr] = np.dot(e,L)
        
        tempyprop = np.zeros(shape = (len(Z)))
        tempyprop[len(S_d[yr]):] = yhh_prop[yr]
        temp_nrg_prod_mult = np.zeros(shape=[106])
        nrg_prod_big = np.multiply(eL[yr],tempyprop)
        for a in range(0,10):
            temp_nrg_prod_mult = temp_nrg_prod_mult + nrg_prod_big[(a*106)+1060:((a+1)*106)+1060]
        
        nrg_prod_mult[:,:,count] = np.tile(temp_nrg_prod_mult,[136,1])
        
        foot = np.multiply(np.transpose(nrg_prod_mult[:,:,count]),yhh_wide[yr])
        foot = np.nan_to_num(foot)
        foot = np.sum(foot,0)+(direct.loc[:,int(yr)]*1000000)
        foots[count,0] = np.sum(foot,0)/1000000
        
        nrg_CC_mult[yr] =np.divide(foot,np.sum(yhh_wide[yr],0))/1000000
        
        np.nan_to_num(nrg_CC_mult[yr], copy = False) 
    
        temp = np.divide(np.sum(yhh_wide[yr],0),np.sum(lcf_136[yr],1))    
        lcf_exp[yr] = df(np.dot(np.diag(temp),lcf_136[yr]), index = lcf_136[yr].index, columns = lcf_136[yr].columns)
    
        np.nan_to_num(lcf_exp[yr], copy = False)
        count = count+1
    return (lcf_exp,nrg_CC_mult)    

def makeLCFSDA(lcf_exp,LCFpopdata,nrg_CC_mult,years):

    yr0 = '2003'
    nrg0 = nrg_CC_mult['2003']
    ypop300 = LCFpopdata['2003'].iloc[5,0]*LCFpopdata['2003'].iloc[0,0]
    ypop490 = LCFpopdata['2003'].iloc[5,1]*LCFpopdata['2003'].iloc[0,1]
    ypop640 = LCFpopdata['2003'].iloc[5,2]*LCFpopdata['2003'].iloc[0,2]
    ypop740 = LCFpopdata['2003'].iloc[5,3]*LCFpopdata['2003'].iloc[0,3]
    ypop750 = LCFpopdata['2003'].iloc[5,4]*LCFpopdata['2003'].iloc[0,4]
    ytot300 = np.sum(lcf_exp['2003'].iloc[:,0],0)/ypop300
    ytot490 = np.sum(lcf_exp['2003'].iloc[:,1],0)/ypop490
    ytot640 = np.sum(lcf_exp['2003'].iloc[:,2],0)/ypop640
    ytot740 = np.sum(lcf_exp['2003'].iloc[:,3],0)/ypop740
    ytot750 = np.sum(lcf_exp['2003'].iloc[:,4],0)/ypop750
    yprp300 = lcf_exp['2003'].iloc[:,0]/np.sum(lcf_exp['2003'].iloc[:,0],0)
    yprp490 = lcf_exp['2003'].iloc[:,1]/np.sum(lcf_exp['2003'].iloc[:,1],0)
    yprp640 = lcf_exp['2003'].iloc[:,2]/np.sum(lcf_exp['2003'].iloc[:,2],0)
    yprp740 = lcf_exp['2003'].iloc[:,3]/np.sum(lcf_exp['2003'].iloc[:,3],0)
    yprp750 = lcf_exp['2003'].iloc[:,4]/np.sum(lcf_exp['2003'].iloc[:,4],0)
    count = 0
    res30 = np.zeros(shape = [len(years),4])
    res49 = np.zeros(shape = [len(years),4])
    res64 = np.zeros(shape = [len(years),4])
    res74 = np.zeros(shape = [len(years),4])
    res75 = np.zeros(shape = [len(years),4])
    for yr in years:
        yr1 = yr
        
        nrg1 = nrg_CC_mult[yr]
        ypop301 = LCFpopdata[yr].iloc[5,0]*LCFpopdata[yr].iloc[0,0]
        ypop491 = LCFpopdata[yr].iloc[5,1]*LCFpopdata[yr].iloc[0,1]
        ypop641 = LCFpopdata[yr].iloc[5,2]*LCFpopdata[yr].iloc[0,2]
        ypop741 = LCFpopdata[yr].iloc[5,3]*LCFpopdata[yr].iloc[0,3]
        ypop751 = LCFpopdata[yr].iloc[5,4]*LCFpopdata[yr].iloc[0,4]
        ytot301 = np.sum(lcf_exp[yr].iloc[:,0],0)/ypop301
        ytot491 = np.sum(lcf_exp[yr].iloc[:,1],0)/ypop491
        ytot641 = np.sum(lcf_exp[yr].iloc[:,2],0)/ypop641
        ytot741 = np.sum(lcf_exp[yr].iloc[:,3],0)/ypop741
        ytot751 = np.sum(lcf_exp[yr].iloc[:,4],0)/ypop751
        yprp301 = lcf_exp[yr].iloc[:,0]/np.sum(lcf_exp[yr].iloc[:,0],0)
        yprp491 = lcf_exp[yr].iloc[:,1]/np.sum(lcf_exp[yr].iloc[:,1],0)
        yprp641 = lcf_exp[yr].iloc[:,2]/np.sum(lcf_exp[yr].iloc[:,2],0)
        yprp741 = lcf_exp[yr].iloc[:,3]/np.sum(lcf_exp[yr].iloc[:,3],0)
        yprp751 = lcf_exp[yr].iloc[:,4]/np.sum(lcf_exp[yr].iloc[:,4],0)
        
        foot30_0 = np.dot(nrg0,yprp300)
        foot30_0 = np.dot(foot30_0,ypop300)
        foot30_0 = np.dot(foot30_0,ytot300)
        foot30_1 = np.dot(nrg1,yprp301)
        foot30_1 = np.dot(foot30_1,ypop301)
        foot30_1 = np.dot(foot30_1,ytot301)
        
        foot49_0 = np.dot(nrg0,yprp490)
        foot49_0 = np.dot(foot49_0,ypop490)
        foot49_0 = np.dot(foot49_0,ytot490)
        foot49_1 = np.dot(nrg1,yprp491)
        foot49_1 = np.dot(foot49_1,ypop491)
        foot49_1 = np.dot(foot49_1,ytot491)

        foot64_0 = np.dot(nrg0,yprp640)
        foot64_0 = np.dot(foot64_0,ypop640)
        foot64_0 = np.dot(foot64_0,ytot640)
        foot64_1 = np.dot(nrg1,yprp641)
        foot64_1 = np.dot(foot64_1,ypop641)
        foot64_1 = np.dot(foot64_1,ytot641)
        
        foot74_0 = np.dot(nrg0,yprp740)
        foot74_0 = np.dot(foot74_0,ypop740)
        foot74_0 = np.dot(foot74_0,ytot740)
        foot74_1 = np.dot(nrg1,yprp741)
        foot74_1 = np.dot(foot74_1,ypop741)
        foot74_1 = np.dot(foot74_1,ytot741)
        
        foot75_0 = np.dot(nrg0,yprp750)
        foot75_0 = np.dot(foot75_0,ypop750)
        foot75_0 = np.dot(foot75_0,ytot750)
        foot75_1 = np.dot(nrg1,yprp751)
        foot75_1 = np.dot(foot75_1,ypop751)
        foot75_1 = np.dot(foot75_1,ytot751)

        sda_300 = {}
        sda_300[0] = nrg0
        sda_300[1] = yprp300
        sda_300[2] = ypop300
        sda_300[3] = ytot300            
        sda_301 = {}
        sda_301[0] = nrg1
        sda_301[1] = yprp301
        sda_301[2] = ypop301
        sda_301[3] = ytot301
        
        sda_490 = {}
        sda_490[0] = nrg0
        sda_490[1] = yprp490
        sda_490[2] = ypop490
        sda_490[3] = ytot490            
        sda_491 = {}
        sda_491[0] = nrg1
        sda_491[1] = yprp491
        sda_491[2] = ypop491
        sda_491[3] = ytot491
            
        sda_640 = {}
        sda_640[0] = nrg0
        sda_640[1] = yprp640
        sda_640[2] = ypop640
        sda_640[3] = ytot640            
        sda_641 = {}
        sda_641[0] = nrg1
        sda_641[1] = yprp641
        sda_641[2] = ypop641
        sda_641[3] = ytot641
          
        sda_740 = {}
        sda_740[0] = nrg0
        sda_740[1] = yprp740
        sda_740[2] = ypop740
        sda_740[3] = ytot740            
        sda_741 = {}
        sda_741[0] = nrg1
        sda_741[1] = yprp741
        sda_741[2] = ypop741
        sda_741[3] = ytot741
        
        sda_750 = {}
        sda_750[0] = nrg0
        sda_750[1] = yprp750
        sda_750[2] = ypop750
        sda_750[3] = ytot750            
        sda_751 = {}
        sda_751[0] = nrg1
        sda_751[1] = yprp751
        sda_751[2] = ypop751
        sda_751[3] = ytot751
        
        temp30 = io.sda(sda_301,sda_300)          
        res30[count,:] = temp30[24,1:5]

        temp49 = io.sda(sda_491,sda_490)          
        res49[count,:] = temp49[24,1:5]
          
        temp64 = io.sda(sda_641,sda_640)          
        res64[count,:] = temp64[24,1:5]

        temp74 = io.sda(sda_741,sda_740)          
        res74[count,:] = temp74[24,1:5]

        temp75 = io.sda(sda_751,sda_750)          
        res75[count,:] = temp75[24,1:5] 
        
        count = count+1             
    
    return (res30,res49,res64,res74,res75)


def make_deciles(oa_pop1,oa_exp1,lad):
    
    deciles = {}
    
    for r in range(0,len(lad)):    
        print(lad[0][r])
        
        pop = oa_pop1[oa_pop1.LAD==lad[0][r]].Pop
        
        exp_oa = oa_exp1[oa_exp1.LAD==lad[0][r]]
        
        exp_oa = exp_oa.iloc[:,0:136]
         
        exp_pp_oa = df.dot(df(np.diag(1/pop),columns = exp_oa.index),exp_oa)
        exp_pp_oa.index = exp_oa.index
        
        total = np.sum(exp_pp_oa,axis=1)
       
        order = total.argsort().argsort()
        
        rankeddata = np.zeros(shape=(len(order),138))
        
        for o in range(0,len(order)):
            for p in range(0,len(order)):        
                if order.iloc[p] == o:
                    rankeddata[o,0] = pop.iloc[p]
                    rankeddata[o,1] = total.iloc[p]
                    rankeddata[o,2:138] = exp_pp_oa.iloc[p,0:136]
        
        temppop = 0
        count = 0
        prop = np.zeros(shape=(11,len(order)))    
        for p in range(0,len(order)):
            temppop = rankeddata[p,0] + temppop
            prop[count,p] = 1
            if temppop > np.sum(pop)/10: 
                temppop = temppop-rankeddata[p,0] 
                prop[count,p] = (np.sum(pop)/10-temppop)/rankeddata[p,0]
                count = count+1
                prop[count,p] = 1-prop[count-1,p]
                temppop = temppop+rankeddata[p,0]-np.sum(pop)/10
        
        rankeddatatot = np.multiply(rankeddata[:,1:138],np.transpose(np.tile(rankeddata[:,0],(137,1))))
        decilecols = exp_oa.columns.values.tolist()
        decilecols.insert(0,'Pop')
        decilecols.insert(1,'Total')
        tempdecile = np.zeros(shape=(11,138))
        tempdecile[0:11,0] = np.sum(pop)/10
        tempdecile[0:11,1:138] = np.dot(prop,rankeddatatot)/(np.sum(pop)/10)
        deciles[lad[0][r]] = df(tempdecile[0:10,:], columns = decilecols)
        
    return deciles
    