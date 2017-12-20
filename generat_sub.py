#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 18:55:43 2017

@author: qiaoshiji
"""
import pandas as pd
path="/Users/qiaoshiji/Downloads/santa/"
r=pd.read_csv(path+'result.csv')
r['cnt']=1
r['cnt'][r.child<4000]=2
gift_cnt=r.groupby('gift',as_index=False).cnt.sum()
gift_cnt['left']=1000-gift_cnt.cnt
gift_cnt=gift_cnt[gift_cnt.left!=0]
hg=list(r.child)
children=[i for i in range(0,4000,2)+range(4000,1000000)]
children = list(set(children)^set(hg))
gifts={}
r=r[['gift','child']]
for i in gift_cnt.index:
    gifts[gift_cnt['gift'][i]]=gift_cnt['left'][i]
c=[]
g=[]
for child in children:
    if child<4000:
        for gift in gifts:
            if gifts[gift]>=2:
                c.append(child)
                g.append(gift)
                gifts[gift]-=2
                break
    else:
        for gift in gifts:
            if gifts[gift]>=1:
                c.append(child)
                g.append(gift)
                gifts[gift]-=1
                break
r3=pd.DataFrame()
r3['child']=c
r3['gift']=g
r4=pd.concat([r,r3])
r5=r4[r4.child<4000]
r5.child=r5.child+1
r6=pd.concat([r4,r5])
r6=r6[['child','gift']]
r6=r6.sort_values('child')
r6.columns=['ChildId','GiftId']
r6.to_csv(path+'test.csv',index=False)
#r=pd.concat([r,r3])
#r['cnt']=1
#r['cnt'][r.child<4000]=2
#gift_cnt=r.groupby('gift',as_index=False).cnt.sum()
#gift_cnt['left']=1000-gift_cnt.cnt
#gift_cnt=gift_cnt[gift_cnt.left!=0]
#for i in gifts:
#    a=r[(r.gift==i)&(r.child>4000)]
#    b=df_dist[(df_dist.gift==i)]
#    d=pd.merge(a,b,on=['child'])
#    e=d[d.happiness==d.happiness.min()].reset_index()
#    print e['gift_x'][0],e['child'][0],e['happiness'][0]
    
"""   
429 252374 0.0945
349 975463 0.1045
319 493634 0.1025
802 791064 0.1035
643 465896 0.1005
108 439187 0.1005
396 926169 0.1065

609 453572 0.1125
753 587412 0.1185
851 871536 0.1065
244 243286 0.1115
757 736472 0.1115
438 692880 0.1175
473 970114 0.1255
"""
#r['gift'][r.child==252374]=609
#r['gift'][r.child==975463]=753
#r['gift'][r.child==493634]=851
#r['gift'][r.child==791064]=244
#r['gift'][r.child==465896]=757
#r['gift'][r.child==439187]=438
#r['gift'][r.child==926169]=473