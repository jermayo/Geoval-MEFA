#!/usr/bin/python
# -*- coding: UTF-8 -*-
# MEFA: Meterological Event Frequency Analysis Software
# Ver. 1.8.1
# Jérémy Mayoraz pour GéoVal
# Sion, Août 2018

import datetime
from collections import OrderedDict

from temp_analyse import date_beetween


#######################################################################################
########################## RAIN CUMUL #################################################

def rain_cumul(datas, min_step, max_step, min_time_beetween_event, min_rain, period):
    min_time_beetween_event=datetime.timedelta(minutes=min_time_beetween_event)
    min_step=datetime.timedelta(hours=min_step)
    max_step=datetime.timedelta(hours=max_step+1)

    if period==1:
        period_list={"Year":[1,13]} #period list from month# to month# NOT INCLUDED, 13 => december included
    elif period==2:
        period_list={"Winter":[12,3],"Spring":[3,6],"Summer":[6,9],"Autumn":[9,12]}
    elif period==3:
        period_list={}
        for i in range(1,13):
            period_list[month_abbr[i]]=[i, i+1]

    step=datetime.timedelta(hours=1)
    events=OrderedDict()
    first_date=datetime.datetime.max
    for i in range(len(datas)):
        if datas[i]["date"]<first_date:
            first_date=datas[i]["date"]

        year=datas[i]["date"].year
        if year not in events:
            events[year]=OrderedDict()
            j=i
            delta_t=min_step
            while delta_t<max_step:
                new_period={"during_event":False}
                for period in period_list:
                    new_period[period]=0
                events[year][delta_t]=new_period
                delta_t+=step


        delta_t=min_step
        cumul=0
        j=i
        while datas[j]["date"]>first_date and datas[i]["date"]-datas[j]["date"]<max_step:
            cumul+=datas[j]["rain"]
            if datas[i]["date"]-datas[j]["date"]>delta_t:
                case=events[year][delta_t]
                if cumul>=min_rain and not case["during_event"]:
                    for period in period_list:
                        if date_beetween(datas[i]["date"], period_list[period][0], period_list[period][1]):
                            case[period]+=1
                            case["last"]=datas[i]["date"]
                            case["during_event"]=True
                elif case["during_event"]:
                    if cumul<min_rain:
                        if datas[i]["date"]-case["last"]>min_time_beetween_event:
                            case["during_event"]=False
                    elif cumul>=min_rain:
                        case["last"]=datas[i]["date"]
                delta_t+=step
            j-=1


    text="Time Span: (Hours)\t"
    for year in events:
        for delta_t in events[year]:
            text+=str(delta_t.total_seconds()//3600)+"\t"*len(period_list)
        break
    text+="\n\t"
    for year in events:
        for delta_t in events[year]:
            for period in period_list:
                text+="\t"+period
        break
    for year in events:
        text+="\n"+str(year)+"\t"
        for delta_t in events[year]:
            to_remove=[]
            for elem in events[year][delta_t]:
                if elem in period_list:
                    text+="\t"+str(events[year][delta_t][elem])
                else:
                    to_remove.append(elem)
            for i in to_remove:
                events[year][delta_t].pop(i, None)

    return text, events
