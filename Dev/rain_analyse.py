#!/usr/bin/python
# -*- coding: UTF-8 -*-
# MEFA: Meterological Event Frequency Analysis Software
# Ver. 1.9.7
# Jérémy Mayoraz pour GéoVal
# Sion, Août 2018

import datetime
from collections import OrderedDict

from utilities import date_beetween, make_period_list

# Rain Cumul: steps goes from min_step to max_step with increment of 1 hour,
# min_rain is how much the cumul must be to count as event
def rain_cumul(datas, min_step, max_step, min_time_beetween_event, min_rain, period, per_event, show_info=False):
    # init data
    min_time_beetween_event=datetime.timedelta(minutes=min_time_beetween_event)
    min_step=max(datetime.timedelta(hours=min_step), datas[1]["date"]-datas[0]["date"])
    max_step=datetime.timedelta(hours=max_step+1)

    period_list=make_period_list(period)

    step=datetime.timedelta(hours=1)
    events=OrderedDict()
    first_date=datetime.datetime.max
    n=len(datas)
    incr=0
    #main analyse loop
    for i in range(n):
        if show_info:
            if i/n>=incr:
                print("  > Analysing data   {:.0f}%".format(incr*100), end="\r")
                incr+=0.01
        #finds first date to prevent exeption
        if datas[i]["date"]<first_date:
            first_date=datas[i]["date"]

        year=datas[i]["date"].year
        #make new year
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
        #finds cumul of the last x hours
        while datas[j]["date"]>first_date and datas[i]["date"]-datas[j]["date"]<max_step:
            cumul+=datas[j]["rain"]
            # reached a wanted delta_t
            if datas[i]["date"]-datas[j]["date"]>=delta_t:
                case=events[year][delta_t]
                #new event
                if cumul>=min_rain and not case["during_event"]:
                    for period in period_list:
                        if date_beetween(datas[i]["date"], period_list[period][0], period_list[period][1]):
                            case[period]+=1
                            if per_event:
                                case["last"]=datas[i]["date"]
                                case["during_event"]=True

                elif case["during_event"] and per_event:
                    #end event
                    if cumul<min_rain:
                        if datas[i]["date"]-case["last"]>min_time_beetween_event:
                            case["during_event"]=False
                    #update last event date
                    elif cumul>=min_rain:
                        case["last"]=datas[i]["date"]
                #increment to next step
                delta_t+=step
            j-=1

    if show_info:
        print("  > Analysing data  {:.0f}%".format(100))

    #make text
    text="Time Span: (Hours)\t"
    #time span
    for year in events:
        for delta_t in events[year]:
            text+=str(delta_t.total_seconds()//3600)+"\t"*len(period_list)
        break
    text+="\n\t"
    #period
    for year in events:
        for delta_t in events[year]:
            for period in period_list:
                text+="\t"+period
        break
    #year and data
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



#RAIN EVENT: Event happens when the rain value is greater than zero (when it starts to rain)
#            Event stops when it comes back down to zero for more than "cooldown" period
#            Event only counts if cumul is grater than "min_cumul"
#            Second part of result:
#            Total cumul, max intensity, duration and average intensity are mesured (classed by step_...)
#            The "portion" percentage biggest event are taken and classed by year
def rain_event(datas, period, cooldown=10, max_scale=1, cumul_scale=5, intensity_scale=1, min_cumul=1, portion=0.25):
    #add new data type (intensity, cumul, ...) in events
    def add_data(event_year, data_type, data, maxes):
        if data not in event_year[data_type]:
            event_year[data_type][data]=0
        event_year[data_type][data]+=1
        maxes[data_type]=max(data, maxes[data_type])

    cooldown=datetime.timedelta(minutes=cooldown)

    #make period list
    period_list=make_period_list(period)
    #add a way to count the number of events in a certain period
    for period in period_list:
        period_list[period].append(0)

    events=OrderedDict()
    for period in period_list:
        events[period]=OrderedDict()

    #global max for all the parameters
    maxes={"duration":0, "max":0, "cumul":0, "intensity":0}

    during_event=False
    count=0

    #main loop
    for data in datas:
        rain=data["rain"]
        date=data["date"]
        #begin or continue event
        if rain>0:
            #new event
            if not during_event:
                maxi, cumul, start, last = rain, rain, date, date
                during_event=True
                year=date.year
                for period in period_list:
                    if date_beetween(start, period_list[period][0], period_list[period][1]):
                        if year not in events[period]:
                            events[period][year]={"total":0, "duration":{}, "max":{}, "cumul":{}, "intensity":{}}
                        break
            #if during event: update maxes
            else:
                maxi=max(maxi, rain)
                cumul+=rain
                last=date
        #end event
        elif rain==0 and during_event and date-last>=cooldown:
            if cumul>min_cumul:
                period_list[period][2]+=1
                year=start.year
                events[period][year]["total"]+=1
                duration=((date-start)-cooldown).total_seconds()/3600+1
                add_data(events[period][year], "duration", int(duration), maxes)
                add_data(events[period][year], "max", int(maxi//max_scale+1), maxes)
                add_data(events[period][year], "cumul", int(cumul//cumul_scale+1), maxes)
                add_data(events[period][year], "intensity", int((cumul/duration)//intensity_scale+1), maxes)
            during_event=False

    #close last event
    if during_event:
        if cumul>min_cumul:
            period_list[period][2]+=1
            year=start.year
            events[period][year]["total"]+=1
            duration=((date-start)-cooldown).total_seconds()/3600+1
            add_data(events[period][year], "duration", int(duration), maxes)
            add_data(events[period][year], "max", int(maxi//max_scale+1), maxes)
            add_data(events[period][year], "cumul", int(cumul//cumul_scale+1), maxes)
            add_data(events[period][year], "intensity", int((cumul/duration)//intensity_scale+1), maxes)

    #text first part
    text="cooldown: {} h, max scale: {} mm, cumul scale: {} mm, intensity scale: {} mm/h\n".format(cooldown, max_scale, cumul_scale, intensity_scale)
    maxes_list=OrderedDict()
    for period in period_list:
        maxes_list[period]={"max":[], "cumul":[], "intensity":[]}
    for period in period_list:

        text+="\n\n"+str(period)+":\n"
        for year in events[period]:
            for data in events[period][year]:
                text+="\t"+str(data)+" "
                if data!="total":
                    for i in range(1, maxes[data]+1):
                        text+=str(i)+" "
                text+="\t"
            break

        for year in events[period]:
            text+="\n"+str(year)+":"
            for data in events[period][year]:
                text+="\t\t"
                if data=="total":
                    text+=str(events[period][year]["total"])
                else:
                    for i in range(1, maxes[data]+1):
                        if i in events[period][year][data]:
                            value=events[period][year][data][i]
                            if data in maxes_list[period]:
                                for j in range(value):
                                    maxes_list[period][data].append({"value":i, "year":year})

                        else:
                            value=0
                        text+=" "+str(value)

    #text second part
    #data handling
    text_list=OrderedDict()
    for period in maxes_list:
        for i in maxes_list[period]:
            if i not in text_list:
                text_list[i]=OrderedDict()
                for year in events[period]:
                    text_list[i][year]=OrderedDict()
            while len(maxes_list[period][i])>period_list[period][2]*portion:
                mini=min([j["value"] for j in maxes_list[period][i]])
                for j in maxes_list[period][i]:
                    if j["value"]==mini:
                        maxes_list[period][i].remove(j)

            for year in events[period]:
                year_total=0
                for j in maxes_list[period][i]:
                    if year==j["year"]:
                        year_total+=1
                text_list[i][year][period]=year_total/len(maxes_list[period][i])*100

    #text print
    text+="\n\n{:.2f}% of the biggest events\n".format(portion*100)
    for i in text_list:
        text+="\n"+str(i)+"\n"
        first=True
        for year in text_list[i]:
            for period in period_list:
                text+="\t"+str(period)
            break
        for year in text_list[i]:
            text+="\n"+str(year)
            for period in text_list[i][year]:
                text+="\t{:.1f}%".format(text_list[i][year][period])
    return text


#RAIN MAX: Event starts if rain value is grater than "Rmin", from this point, event counts in certain categorie depending on its value
#          Categories goes from "Rmin" to the biggest value, with step every "increment"
#          "portion" percent biggest events are taken out, and sorted by year
def rain_max(datas, period, Rmin, per_event, with_max, increment=1, portion=0.25, show_info=True):
    period_list=make_period_list(period)
    events=OrderedDict()
    min_rain=[]
    during_event=False
    event_list=OrderedDict()

    #make period list
    for period in period_list:
        events[period]=OrderedDict()
        event_list[period]=[]

    n=len(datas)
    incr=0
    count=0

    #main loop
    for data in datas:
        count+=1
        if show_info:
            if count/n>=incr:
                print("  > Analysing data   {:.0f}%".format(incr*100), end="\r")
                incr+=0.01
        i=Rmin
        year=data["date"].year

        #new event
        if not during_event:
            while i<=data["rain"]:
                if data["rain"]<Rmin:
                    break
                elif data["rain"]>=i and (not with_max or (with_max and data["rain"]<i+increment)):
                    during_event=True
                    for period in period_list:
                        if date_beetween(data["date"], period_list[period][0], period_list[period][1]):
                            if year not in events[period]:
                                events[period][year]={}
                            if i not in min_rain:
                                min_rain.append(i)
                            if i not in events[period][year]:
                                events[period][year][i]={"total":0, "during_event":False}
                            if not events[period][year][i]["during_event"]:
                                events[period][year][i]["total"]+=1
                                events[period][year][i]["during_event"]=True
                                last_year=year
                                event_list[period].append({"total":i, "year":year})
                            break
                    if with_max:
                        break
                i+=increment

        #end event
        if during_event:
            if data["rain"]==0 and per_event:
                during_event=False
                for i in events[period][last_year]:
                    events[period][last_year][i]["during_event"]=False
            elif not per_event:
                during_event=False
                for i in events[period][last_year]:
                    if data["rain"]<i:
                        events[period][last_year][i]["during_event"]=False

    #text part 1: normal result
    text=""
    min_rain=sorted(min_rain)
    for period in events:
        text+="\n"+str(period)+"\t"
        for i in min_rain:
            text+=str(i)+"\t"
        for year in events[period]:
            text+="\n"+str(year)+"\t"
            for i in min_rain:
                if i in events[period][year]:
                    text+=str(events[period][year][i]["total"])
                text+="\t"

    text_list=OrderedDict()
    text+="\n\n{:.2f}% of the biggest event\n".format(portion*100)
    period_max=OrderedDict()

    #text part 2: percentage of biggest event
    for period in event_list:
        text+="\t"+str(period)
        period_max[period]=len(event_list[period])*portion
        event_list[period]=sorted(event_list[period], key=lambda k: k["total"])
        for i in range(int(len(event_list[period])-period_max[period])):
            event_list[period].pop(0)

        for i in event_list[period]:
            if i["year"] not in text_list:
                text_list[i["year"]]=OrderedDict()
                for p in period_list:
                    text_list[i["year"]][p]=0
            text_list[i["year"]][period]+=1
    #text part 2 printing
    for year in sorted(text_list):
        text+="\n"+str(year)+"\t"
        for period in text_list[year]:
            text+="{:.1f}%\t".format(text_list[year][period]/period_max[period]*100)
    return text


#Rain Days Over Lim: Counts for each year how many cumuls are over a limit
#                    Limits are the value of the list "limits"
def rain_days_over_lim(datas, limits, period):

    period_list=make_period_list(period)
    limits=sorted(limits)

    events=OrderedDict()
    #main loop
    for data in datas:
        year=data["date"].year
        #new year
        if year not in events:
            events[year]=OrderedDict()
            for lim in limits:
                events[year][lim]=OrderedDict()
                for period in period_list:
                    events[year][lim][period]=0
        #new event
        for lim in limits:
            if data["rain"]>=lim:
                for period in period_list:
                    if date_beetween(data["date"], period_list[period][0], period_list[period][1]):
                        events[year][lim][period]+=1
                        break

    #text printing
    text="\t"
    for year in events:
        for lim in events[year]:
            text+=str(lim)+"\t"*len(period_list)
        text+="\n\t"
        for lim in events[year]:
            for period in events[year][lim]:
                text+=str(period)+"\t"
        break
    for year in events:
        text+="\n"+str(year)
        for lim in events[year]:
            for period in events[year][lim]:
                text+="\t"+str(events[year][lim][period])

    return text


# -------> ADD HERE NEW TEMPERATURE ANALYSE <--------------
