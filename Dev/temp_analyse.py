#!/usr/bin/python
# -*- coding: UTF-8 -*-
# MEFA: Meterological Event Frequency Analysis Software
# Ver. 1.9.7
# Jérémy Mayoraz pour GéoVal
# Sion, Août 2018

import datetime
from collections import OrderedDict

from utilities import date_beetween, make_period_list

# check if year not yet in event and creates data for it
def check_new_year(year, events, min, max, periods=False):
    if year not in events:
        new_period=OrderedDict()
        for temp in range(min, max+1):
            new_max=OrderedDict()
            if periods:
                for key in periods:
                    new_max[key]={"pos":0, "neg":0, "total":0}
                new_max["new_event"]=False
            else:
                new_max={"pos":0, "neg":0, "total":0, "during_event":False}
            new_period[temp]=new_max
        events[year]=new_period
    return events

# returns the daily average of the data as a dictionnary of type: {day: value}
def daily_average(datas):
    days=OrderedDict()
    for data in datas:
        date=data["date"].date()
        if date not in days:
            days[date]={"temp":0, "numb_of_val":0}
        days[date]["temp"]+=data["temp"]
        days[date]["numb_of_val"]+=1
    for day in days:
        days[day]["temp"]=days[day]["temp"]/days[day]["numb_of_val"]
    return days

# build text for typical format
def build_text(res, T_min, T_max, period_list=[""]):
    text="\t"
    period_text=""
    for i in range(T_min, T_max+1):
        text+=str(i)+"\t"*(len(period_list)*3+1)
    for period in period_list:
        period_text+=str(period)+"\t"*3
    text+="\n\t"+(period_text+"\t")*(T_max-T_min+1)
    text+="\n\t"+("pos\tneg\ttot\t"*len(period_list)+"\t")*(T_max-T_min+1)
    for year in res:
        text+="\n"+str(year)
        for temp in res[year]:
            text+="\t"
            if period_list==[""]:
                for data in ["pos","neg","total"]:
                    text+=str(res[year][temp][data])+"\t"
            else:
                for period in period_list:
                    for data in ["pos","neg","total"]:
                        text+=str(res[year][temp][period][data])+"\t"
    return text

# check if events starts for typical format
def check_event(event_year, d_temp, period_list, date, time_max_event, with_max, per_event):
    # loop for temperature limit
    for temp in event_year:
        new_event=False
        case=event_year[temp]
        # new event
        if not case["new_event"] and abs(d_temp)>=temp:
            for key in period_list:
                if date_beetween(date, period_list[key][0], period_list[key][1]):
                    case["new_event"]={"last": date, "period":key, "max":d_temp}
                    if not per_event:
                        new_event=key
                    break

        if case["new_event"] or new_event:
            #update maximum value and last event date
            if abs(d_temp)>abs(case["new_event"]["max"]):
                case["new_event"]["max"]=d_temp
            if abs(d_temp)>=temp:
                case["new_event"]["last"]=date

            #end and contabilise event
            if new_event or date-case["new_event"]["last"]>=time_max_event:
                if not with_max or int(abs(case["new_event"]["max"]))<temp+1:
                    if not new_event:
                        new_event=case["new_event"]["period"]
                    if case["new_event"]["max"]>0:
                        event_year[temp][new_event]["pos"]+=1
                    else:
                        event_year[temp][new_event]["neg"]+=1
                    event_year[temp][new_event]["total"]+=1
                case["new_event"]=False

    return event_year

#same as check event but for once it is out of the main loop: close last events
def check_event_last(events, with_max):
    for year in events:
        for temp in events[year]:
            case=events[year][temp]
            if case["new_event"]:
                if not with_max or abs(case["new_event"]["max"])<temp+1:
                    period=case["new_event"]["period"]
                    if case["new_event"]["max"]>0:
                        case[period]["pos"]+=1
                    else:
                        case[period]["neg"]+=1
                    case[period]["total"]+=1
            #removes all unnecessary data
            case.pop("new_event", None)
    return events

#######################################################################################
########################## Clean Daily Average ########################################
# daily average and text making
def clean_daily_average(datas, show_info=False):
    days=daily_average(datas)
    text="Day\t\tTemp\tRain\n"
    n=len(datas)
    incr=0
    count=0
    #text making
    for day in days:
        if show_info:
            count+=1
            if count/n>=incr:
                print("  > Analysing data  {:.0f}%".format(incr*100), end="\r")
                incr+=0.01
        text+="{}\t{:.3f}\n".format(day,days[day]["temp"])
    if show_info:
        print("  > Analysing data  {:.0f}%".format(100))
    return text


#######################################################################################
########################## DIFF TIME ##################################################
# Difference of temp with delta_t hours after, min/max: range for delta_T,
# time_max_event: time after which a new event is counted
def diff_time(datas, delta_t, time_max_event, period, min, max, with_max, show_info=False):
    period_list=make_period_list(period)
    event_list=OrderedDict()

    n=len(datas)
    incr=0

    #main analyse loop
    for i in range(n):
        if show_info:
            if i/n>=incr:
                print("  > Analysing data  {:.0f}%".format(incr*100), end="\r")
                incr+=0.01

        year=datas[i]["date"].year
        event_list=check_new_year(year, event_list, min, max, periods=period_list)

        #finding the temp x hours after
        j=i
        while datas[j]["date"]-datas[i]["date"]<delta_t:
            j+=1

        d_temp=datas[j]["temp"]-datas[i]["temp"]
        event_list[year]=check_event(event_list[year], d_temp, period_list, datas[i]["date"], time_max_event, with_max, True)

        # if j is out of the list => end
        if j>=len(datas)-1:
            break

    event_list=check_event_last(event_list, with_max)

    if show_info:
        print("  > Analysing data  {:.0f}%".format(100))

    return build_text(event_list, min, max, period_list=period_list), event_list


#######################################################################################
######################## TEMPE AVERAGE ################################################
#temp average: 1 average done for each day, 2 average over each same day of year, 3 comparaison each day/average of typical day
#per_event: =0 -> day to day, =1 -> per event
def temp_average(datas, per_event, min, max, with_max, period, show_info=False):
    typical_average={}
    days_average={}
    events=OrderedDict()

    period_list=make_period_list(period)

    #init typical days
    for day in range(0,367):
        typical_average[day]={"val":0, "numb_of_val":0}

    for data in datas:
        #daily average
        date=data["date"].date()
        if date not in days_average:
            days_average[date]={"val":0, "numb_of_val":0}
        days_average[date]["val"]+=data["temp"]
        days_average[date]["numb_of_val"]+=1
        #typical temperature
        day_numb=(data["date"]-datetime.datetime(data["date"].year, 1, 1)).days+1
        typical_average[day_numb]["val"]+=data["temp"]
        typical_average[day_numb]["numb_of_val"]+=1
        #building events list
        if data["date"].year not in events:
            events[data["date"].year]=OrderedDict()
            for temp in range(min, max+1):
                events[data["date"].year][temp]=OrderedDict()
                for period in period_list:
                    events[data["date"].year][temp][period]={"pos":0, "neg":0, "total":0, "during_event":False}

    # calculate typical average
    for day in typical_average:
        if typical_average[day]["numb_of_val"]>0:
            typical_average[day]=typical_average[day]["val"]/typical_average[day]["numb_of_val"]
        else:
            typical_average[day]=0
    #calculate daily average
    for day in days_average:
        if days_average[day]["numb_of_val"]>0:
            days_average[day]=days_average[day]["val"]/days_average[day]["numb_of_val"]
        else:
            days_average[day]=0

    n=len(datas)
    incr=0
    count=0
    #main analyse loop
    for day in days_average:
        year=day.year
        if show_info:
            count+=1
            if count/n>=incr:
                print("  > Analysing data  {:.0f}%".format(incr*100), end="\r")
                incr+=0.01

        #find which day of the year it is
        day_numb=(day-(datetime.datetime(year, 1, 1)).date()).days+1
        diff=days_average[day]-typical_average[day_numb]
        #find period
        for period in period_list:
            if date_beetween(day, period_list[period][0], period_list[period][1]):
                for temp in range(min, max+1):
                    case=events[year][temp][period]
                    #new event
                    if abs(diff)>=temp and not case["during_event"]:
                        case["max"]=abs(diff)
                        if per_event:
                            case["during_event"]=True
                        else:
                            if diff>0:
                                case["pos"]+=1
                            else:
                                case["neg"]+=1
                            case["total"]+=1

                    elif case["during_event"]:
                        #update maximum
                        if case["max"]<abs(diff):
                            case["max"]=abs(diff)
                        #end event
                        if abs(diff)<temp:
                            case["during_event"]=False
                            if temp in events[year]:
                                if not with_max or int(abs(case["max"])<temp+1):
                                    if diff>0:
                                        case["pos"]+=1
                                    else:
                                        case["neg"]+=1
                                    case["total"]+=1
                break
    # remove unnecessary data
    for year in events:
        for temp in events[year]:
            for period in period_list:
                events[year][temp][period].pop("during_event", None)
                events[year][temp][period].pop("max", None)

    if show_info:
        print("  > Analysing data  {:.0f}%".format(100))
    return build_text(events, min, max, period_list=period_list), events


#######################################################################################
######################## Day To Span Average ##########################################
#span: span of average (before and after the date), min/max: range for delta_T
#with_max: Bool (with max)

def day_to_span_av(datas, span, min, max, with_max, per_event, days_beet_event, period, show_info=False):
    events=OrderedDict()
    days=daily_average(datas)
    days_beet_event=datetime.timedelta(days=days_beet_event)
    period_list=make_period_list(period)

    n=len(datas)
    incr=0
    count=0
    #main analse loop
    for day in days:
        if show_info:
            count+=1
            if count/n>=incr:
                print("  > Analysing data  {:.0f}%".format(incr*100), end="\r")
                incr+=0.01

        year=day.year
        events=check_new_year(year, events, min, max, periods=period_list)

        average=days[day]["temp"]
        numb_of_value=1

        # finding average of span
        for i in range(1, span): #span in days
            day_before=day-datetime.timedelta(days=i)
            day_after=day+datetime.timedelta(days=i)
            if day_before in days:
                average+=days[day_before]["temp"]
                numb_of_value+=1
            if day_after in days:
                average+=days[day_after]["temp"]
                numb_of_value+=1

        average=average/numb_of_value

        d_temp=days[day]["temp"]-average
        events[year]=check_event(events[year], d_temp, period_list, day, days_beet_event, with_max, per_event)

    if show_info:
        print("  > Analysing data  {:.0f}%".format(100))
    events=check_event_last(events, with_max)

    return build_text(events, min, max, period_list=period_list), events


# -------> ADD HERE NEW TEMPERATURE ANALYSE <--------------
