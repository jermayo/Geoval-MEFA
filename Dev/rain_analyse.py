#!/usr/bin/python
# -*- coding: UTF-8 -*-
# MEFA: Meterological Event Frequency Analysis Software
# Ver. 1.9.6
# Jérémy Mayoraz pour GéoVal
# Sion, Août 2018

import datetime
from collections import OrderedDict

from temp_analyse import date_beetween, make_period_list


#######################################################################################
########################## RAIN CUMUL #################################################

def rain_cumul(datas, min_step, max_step, min_time_beetween_event, min_rain, period, per_event, show_info=False):
    min_time_beetween_event=datetime.timedelta(minutes=min_time_beetween_event)
    min_step=max(datetime.timedelta(hours=min_step), datas[1]["date"]-datas[0]["date"])
    max_step=datetime.timedelta(hours=max_step+1)

    period_list=make_period_list(period)

    step=datetime.timedelta(hours=1)
    events=OrderedDict()
    first_date=datetime.datetime.max
    n=len(datas)
    incr=0
    for i in range(n):
        if show_info:
            if i/n>=incr:
                print("  > Analysing data   {:.0f}%".format(incr*100), end="\r")
                incr+=0.01
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
            if datas[i]["date"]-datas[j]["date"]>=delta_t:
                case=events[year][delta_t]
                if cumul>=min_rain and not case["during_event"]:
                    for period in period_list:
                        if date_beetween(datas[i]["date"], period_list[period][0], period_list[period][1]):
                            case[period]+=1
                            if per_event:
                                case["last"]=datas[i]["date"]
                                case["during_event"]=True
                elif case["during_event"] and per_event:
                    if cumul<min_rain:
                        if datas[i]["date"]-case["last"]>min_time_beetween_event:
                            case["during_event"]=False
                    elif cumul>=min_rain:
                        case["last"]=datas[i]["date"]
                delta_t+=step
            j-=1

    if show_info:
        print("  > Analysing data  {:.0f}%".format(100))
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




def rain_event(datas, period, cooldown=10, max_scale=1, cumul_scale=5, intensity_scale=1, min_cumul=1, portion=0.25):
    def add_data(event_year, data_type, data, maxes):
        if data not in event_year[data_type]:
            event_year[data_type][data]=0
        event_year[data_type][data]+=1
        maxes[data_type]=max(data, maxes[data_type])

    cooldown=datetime.timedelta(minutes=cooldown)

    period_list=make_period_list(period)
    for period in period_list:
        period_list[period].append(0)

    events=OrderedDict()
    for period in period_list:
        events[period]=OrderedDict()
    maxes={"duration":0, "max":0, "cumul":0, "intensity":0}

    during_event=False
    count=0

    for data in datas:
        rain=data["rain"]
        date=data["date"]
        if rain>0:
            if not during_event:
                maxi, cumul, start, last = rain, rain, date, date
                during_event=True
                year=date.year
                for period in period_list:
                    if date_beetween(start, period_list[period][0], period_list[period][1]):
                        if year not in events[period]:
                            events[period][year]={"total":0, "duration":{}, "max":{}, "cumul":{}, "intensity":{}}
                        break
            else:
                maxi=max(maxi, rain)
                cumul+=rain
                last=date

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


def rain_max(datas, period, Rmin, per_event, increment=1, portion=0.25):
    period_list=make_period_list(period)
    events=OrderedDict()
    min_rain=[]
    during_event=False
    event_list=OrderedDict()

    for period in period_list:
        events[period]=OrderedDict()
        event_list[period]=[]
    for data in datas:
        i=Rmin
        year=data["date"].year

        while i:
            if data["rain"]<Rmin:
                break
            elif data["rain"]>=i and data["rain"]<i+increment:
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
                break
            i+=increment

        if data["rain"]==0 and during_event and per_event:
            during_event=False
            for i in events[period][last_year]:
                events[period][last_year][i]["during_event"]=False

        elif not per_event and during_event:
            for i in events[period][last_year]:
                if data["rain"]<i:
                    events[period][last_year][i]["during_event"]=False

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
    for period in event_list:
        text+="\t"+str(period)
        period_max[period]=len(event_list[period])*portion
        while len(event_list[period])>period_max[period]:
            mini=min([i["total"] for i in event_list[period]])
            for i in event_list[period]:
                if mini==i["total"]:
                    event_list[period].remove(i)
                    break
        for i in event_list[period]:
            if i["year"] not in text_list:
                text_list[i["year"]]=OrderedDict()
                for p in period_list:
                    text_list[i["year"]][p]=0
            text_list[i["year"]][period]+=1

    for year in sorted(text_list):
        text+="\n"+str(year)+"\t"
        for period in text_list[year]:
            text+="{:.1f}%\t".format(text_list[year][period]/period_max[period]*100)
    return text
