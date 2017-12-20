#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 13:27:42 2017

@author: qiaoshiji
"""

import numpy as np, pandas as pd
path="/Users/qiaoshiji/Downloads/santa/"

print('load data')
child_prefs = pd.read_csv(path+'child_wishlist.csv', header=None).values[:,1:]
gift_prefs = pd.read_csv(path+'gift_goodkids.csv', header=None).values[:,1:]

n_children = 1000000 # n children to give
n_gift_type = 1000 # n types of gifts available
n_gift_quantity = 1000 # each type of gifts are limited to this quantity
n_child_pref = 10 # number of gifts a child ranks
n_gift_pref = 1000 # number of children a gift ranks
twins = 4000
ratio_gift_happiness = 2
ratio_child_happiness = 2

print('combine all nontrivial child-gift pairs and assign happiness on them.')
df_santa = pd.DataFrame({
    'gift':np.repeat(np.arange(n_gift_type), n_gift_pref) ,
    'child':gift_prefs.flatten(),
    'santa_happ':np.tile(np.linspace(n_gift_pref, 1, n_gift_pref) * 2+1, (n_gift_type, 1)).flatten()})

df_child = pd.DataFrame({
    'child':np.repeat(np.arange(n_children), n_child_pref),
    'gift': child_prefs.flatten(),
    'child_happ': np.tile(np.linspace(n_child_pref, 1, n_child_pref) * 2+1, (n_children, 1)).flatten()})

df = df_child.merge(df_santa, on=['child', 'gift'], how='outer')

df['child_happ'] = df.child_happ.fillna(0)
df['santa_happ'] = df.santa_happ.fillna(0)

max_child_happ = 2 * n_child_pref
max_gift_happ  = 2 * n_gift_pref

df['happiness']  = df.child_happ / max_child_happ + df.santa_happ / max_gift_happ    

print('split singles and twins, and take care of twins')
df_twins = df[df.child < twins].reset_index(drop=True)
df_twins['child_t'] = df_twins.child.apply(lambda x: x + 1 if x//2*2==x else x - 1)  # other me

# add happiness of the other's choice
df_tmp = df_twins[['child_t', 'gift']].merge(df_twins[['child', 'gift', 'child_happ']], left_on=['child_t', 'gift'], right_on=['child', 'gift'], how='left')
df_twins['child_happ_t'] = df_tmp.child_happ.fillna(0)

df_tmp = df_twins[['child_t', 'gift']].merge(df_santa, left_on=['child_t', 'gift'], right_on=['child', 'gift'], how='left')
df_twins['santa_happ_t'] = df_tmp.santa_happ.fillna(0)

df_twins['happiness'] = (df_twins.child_happ + df_twins.child_happ_t) / max_child_happ + (df_twins.santa_happ + df_twins.santa_happ_t) / max_gift_happ 

# remove other me 
ii = df_twins.child > df_twins.child_t
df_twins.loc[ii, 'child'] = df_twins.child_t[ii]

df_twins = df_twins[['child', 'gift', 'happiness']].copy()
df_twins=df_twins.drop_duplicates()
df_twins['n'] = 2

print('merge singles and twins')
df1 = df[['child', 'gift', 'happiness']][df.child >= twins].reset_index(drop=True)
df1['n'] = 1

df_dist = pd.concat([df_twins, df1], ignore_index=True)
twins_zero=pd.DataFrame()
tzc=[]
tzg=[]
for i in range(0,4000,2):
    for j in range(1000):
        tzc.append(i)
        tzg.append(j)
twins_zero['child']=tzc
twins_zero['gift']=tzg
twins_zero['happiness']=0.0

df_dist=pd.concat([df_dist,twins_zero])
df_dist=df_dist.groupby(['child','gift'],as_index=False).happiness.max()

df_dist.sort_values(by='happiness', ascending=False, inplace=True)
df_dist.reset_index(drop=True, inplace=True)
#df_dist.to_csv(path+'score_df.csv',index=False)

opt_df=df_dist[:]
gift_list=opt_df.gift.values
child_list=opt_df.child.values
happiness_list=opt_df.happiness.values



sources=[]
for i in range(len(gift_list)):
    if i%1000000==0:
        print i
    sources.append("gift"+str(gift_list[i]) +"child"+str(child_list[i]))


const1={}
val1={}
const2={}

#
#for gift in set(gift_list):
#    a = opt_df[opt_df.gift==gift][['child']]
#    const1[gift]=a.child.values
#    val1[gift]=[1+(i<4000) for i in a.child.values]

for i in range(len(gift_list)):
    if i%1000000==0:
        print i
    if gift_list[i] not in const1:
        const1[gift_list[i]]=[]
        val1[gift_list[i]]=[]
    const1[gift_list[i]].append(i)
    if child_list[i]<4000:
        val1[gift_list[i]].append(2)
    else:
        val1[gift_list[i]].append(1)

#for child in set(child_list):
#    if child%10000==0:
#        print child
#    a = opt_df[opt_df.child==child][['gift']]
#    const2[child]=a.gift.values
#    
for i in range(len(gift_list)):
    if i%1000000==0:
        print i
    if child_list[i] not in const2:
        const2[child_list[i]]=[]
    const2[child_list[i]].append(i)
    



import cplex

model=cplex.Cplex()
model.objective.set_sense(model.objective.sense.maximize)
print "set var"
model.variables.add(obj=happiness_list,names=sources,types=["B"]*len(sources))

#for i in range(len(gift_list)):
#    if i%100000==0:
#        print i
#    model.variables.add(names = ["gift"+str(gift_list[i]) +"child"+str(child_list[i])],
#                                     obj   = [happiness_list[i]])#score_list[i]
#    model.variables.set_types("gift"+str(gift_list[i]) +"child"+str(child_list[i]), model.variables.type.binary)

print "set constraints1"
lin_expr1=[]
rhs1=[]
senses1=[]
for gift in const1:
    print gift
    rhs1.append(1000.1)
    senses1.append('L')   
    lin_expr1.append([const1[gift],val1[gift]])


print "set constraints2"
for child in const2:
    lin_expr1.append([const2[child],[1.0]*len(const2[child])])
    if child>=4000:
        rhs1.append(1.1)
        senses1.append('L')
    else:
        rhs1.append(1)
        senses1.append('E')
    


print "step2,take vary long time :"
model.linear_constraints.add(lin_expr=lin_expr1, senses=senses1,
                                rhs=rhs1)

model.parameters.mip.tolerances.mipgap.set(model.parameters.mip.tolerances.mipgap.min())
print "solve"
model.solve()

c=[]
g=[]
for i in range(len(gift_list)):
    if i%1000000==0:
        print i
    if model.solution.get_values(i)==1:
            g.append(gift_list[i])
            c.append(child_list[i])
r=pd.DataFrame()
r['child']=c
r['gift']=g
r.to_csv(path+'result.csv',index=False)

    

#import pulp
#prob = pulp.LpProblem('gift', pulp.LpMaximize)
#
#x= pulp.LpVariable.dicts("x",[(gift_list[i],child_list[i]) for i in range(len(chappiness_list))],0,1,pulp.LpInteger)
#prob+=pulp.lpSum([chappiness_list[i]*x[(gift_list[i],child_list[i])] for i in range(len(chappiness_list))])
#
#
#for gift_id in const1:
#    prob+=pulp.lpSum(x[(gift_id,child_id)] for child_id in const1[gift_id])<=1000,""
#
#for child_id in const2:
#    prob+=pulp.lpSum(x[(gift_id,child_id)] for gift_id in const2[child_id])<=1,""
#
#Solver=pulp.PULP_CBC_CMD(msg=1).solve
##Solver=pulp.COIN_CMD().solve
#Solver(prob)    



