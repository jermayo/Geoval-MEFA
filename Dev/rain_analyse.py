#!/usr/bin/python
# -*- coding: UTF-8 -*-
# MEFA: Meterological Event Frequency Analysis Software
# Ver. 1.8.1
# Jérémy Mayoraz pour GéoVal
# Sion, Août 2018

import datetime
from collections import OrderedDict
#from calendar import month_abbr


#######################################################################################
########################## RAIN CUMUL #################################################

def rain_cumul(datas, min_step, max_step, min_time_beetween_event, min_rain):

    min_time_beetween_event=datetime.timedelta(minutes=min_time_beetween_event)
    min_step=datetime.timedelta(hours=min_step)
    max_step=datetime.timedelta(hours=max_step)

    step=datetime.timedelta(hours=1)
    events=OrderedDict()
    first_date=datetime.datetime.max
    for i in range(len(datas)):
        year=datas[i]["date"].year
        if year not in events:
            events[year]=OrderedDict()
            add_year=True

        if datas[i]["date"]<first_date:
            first_date=datas[i]["date"]

        dt=min_step
        while dt<=max_step:
            if add_year:
                events[year][dt]={"total":0, "during_event":False}

            cumul=0
            j=i
            while datas[j]["date"]>first_date and datas[i]["date"]-datas[j]["date"]<dt:
                cumul+=datas[j]["rain"]
                j-=1
            if cumul>=min_rain and not events[year][dt]["during_event"]:
                events[year][dt]["total"]+=1
                events[year][dt]["last"]=datas[i]["date"]
                events[year][dt]["during_event"]=True

            elif events[year][dt]["during_event"]:
                if cumul<min_rain:
                    if datas[i]["date"]-events[year][dt]["last"]>min_time_beetween_event:
                        events[year][dt]["during_event"]=False
                elif cumul>=min_rain:
                    events[year][dt]["last"]=datas[i]["date"]
            dt+=step
        add_year=False


    text="Time Span: (Hours)\t"
    for year in events:
        for date in events[year]:
            text+=str(date.total_seconds()//3600)+"\t"
        break
    for year in events:
        text+="\n"+str(year)+"\t"
        for date in events[year]:
            text+="\t"+str(events[year][date]["total"])

    return text, events
