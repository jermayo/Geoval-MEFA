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

def rain_cumul(datas, step_min, step_max, min_time_beetween_event, min_rain):

    min_time_beetween_event=datetime.timedelta(hours=min_time_beetween_event)
    min_step=datetime.timedelta(hours=min_step)
    max_step=datetime.timedelta(hours=max_step)

    step=datetime.timedelta(hours=1)
    events=OrderedDict()
    first_date=datetime.datetime.max
    for data in datas:
        year=data["date"].year
        if year not in events:
            events[year]=OrderedDict()
            add_year=True

        if data["date"]<first_date:
            first_date=data["date"]

        dt=min_step
        while dt<=max_step:
            if add_year:
                events[year][dt]={"total":0, "during_event"=False}

            cumul=0
            date=data["date"]
            while date>=first_date and data["date"]-date>dt:
                cumul+=data["rain"]
                date-=step

            if cumul>=min_rain and not events[year][dt]["during_event"]:
                events[year][dt]["total"]+=1
                events[year][dt]["last"]=data["date"]
                events[year][dt]["during_event"]=True

            elif events[year][dt]["during_event"]:
                if cumul<min_rain:
                    if data["date"]-events[year][dt]["last"]>min_time_beetween_event:
                        events[year][dt]["during_event"]=False
                elif cumul>=min_rain:
                    events[year][dt]["last"]=data["date"]
            dt+=step
        add_year=False

    text="Time Span:"
    for year in events:
        if not first:
            text+="\n"+str(year)
        for date in events[year]:
            if first:
                text+=date+"\t"
            else:
                text+=events[year][date]+"\t"
            
    return text
