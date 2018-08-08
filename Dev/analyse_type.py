import datetime
from collections import OrderedDict
from calendar import month_abbr

def _date_beetween(date, month_start, month_end):
    if month_start>month_end:
        if not(date.month<month_start and date.month>=month_end):
            return True
    elif date.month>=month_start and date.month<month_end:
        return True
    return False

#######################################################################################
########################## DIFF TIME ##################################################
#Difference of temp with hours before
def diff_time(datas, delta_t, time_max_event, period, T_min, T_max, max_limit):
    def _diff_time(datas, delta_t, min, max, time_max_event, periods, max_limit):
        def add_event(events, new_event, temp):
            year=new_event["last"].year
            period=new_event["period"]
            if new_event["type"]=="+":
                events[year][temp][period]["pos"]+=1
            elif new_event["type"]=="-":
                events[year][temp][period]["neg"]+=1
            events[year][temp][period]["total"]+=1

            return events

        #month_start and month end of type int, month_end NOT included, 13 means decembre included
        event_list=OrderedDict()
        year_list=[]

        for i in range(0,len(datas)):
            year=datas[i]["date"].year
            if year not in year_list:
                year_list.append(year)
                new_period=OrderedDict()
                for temp in range(min, max+1):
                    new_max=OrderedDict()
                    for key in periods:
                        new_max[key]={"pos":0, "neg":0, "total":0}
                    new_max["during_event"]=False
                    new_period[temp]=new_max
                event_list[year]=new_period

            j=i
            while datas[j]["date"]-datas[i]["date"]<delta_t:
                j+=1

            d_temp=datas[j]["temp"]-datas[i]["temp"]
            for temp in event_list[year]:
                case=event_list[year][temp]
                if not case["during_event"] and abs(d_temp)>=temp:
                    case["during_event"]=True
                    event_type="+"
                    if d_temp<0:
                        event_type="-"

                    for key in periods:
                        if _date_beetween(datas[i]["date"], periods[key][0], periods[key][1]):
                            new_event={"last": datas[i]["date"], "type": event_type, "period":key, "max":abs(d_temp)}
                            break

                elif case["during_event"]:
                    if abs(d_temp)>new_event["max"]:
                        new_event["max"]=abs(d_temp)

                    if d_temp>=min:
                        new_event["last"]=datas[i]["date"]

                    elif datas[i]["date"]-new_event["last"]>time_max_event:
                        case["during_event"]=False
                        if max_limit and new_event["max"]<temp+1:
                            event_list=add_event(event_list, new_event, temp)
                        elif not max_limit:
                            event_list=add_event(event_list, new_event, temp)

            if j>=len(datas)-1:
                break

        for temp in event_list[year]:
            case=event_list[year][temp]
            if case["during_event"]:
                if abs(d_temp)>new_event["max"]:
                    new_event["max"]=abs(d_temp)
                if max_limit and new_event["max"]<temp+1:
                    event_list=add_event(event_list, new_event, temp)
                elif not max_limit:
                    event_list=add_event(event_list, new_event, temp)
        return event_list


    if period==1:
        period_list={"Year":[1,13]} #period list from month# to month# NOT INCLUDED, 13 => december included
    elif period==2:
        period_list={"Winter":[12,3],"Spring":[3,6],"Summer":[6,9],"Autumn":[9,12]}
    elif period==3:
        period_list={}
        for i in range(1,13):
            period_list[month_abbr[i]]=[i, i+1]

    res=_diff_time(datas, delta_t, T_min, T_max, time_max_event, period_list, max_limit)

    text="\t"
    period_text=""
    for i in range(T_min, T_max+1):
        text+=str(i)+"\t"*(len(period_list)*3+1)
    for period in period_list:
        period_text+=str(period)+"\t"*3
    text+="\n\t"+(period_text+"\t")*(T_max-T_min)
    text+="\n\t"+("pos\tneg\ttot\t"*len(period_list)+"\t")*(T_max-T_min)
    for year in res:
        text+="\n"+str(year)
        for max in res[year]:
             text+="\t"
             for period in res[year][max]:
                 if period!="during_event":
                     for data in res[year][max][period]:
                         text+=str(res[year][max][period][data])+"\t"

    return text

#######################################################################################
########################## RAIN CUMUL #################################################

def rain_cumul(datas, step, min_time_beetween_event, rain_min, rain_max):
    def _rain_cumul(datas, step, min_rain, min_time_beetween_event):
        last_event_date=datetime.datetime.min
        events=[]
        for i in range(0,len(datas)):
            j=i
            sum=0
            while datas[j]["date"]-datas[i]["date"]<step:
                j+=1
                sum+=datas[j]["rain"]
            if sum>min_rain:
                if datas[j]["date"]-last_event_date>min_time_beetween_event:
                    flag=True
                    for event in events:
                        if event["year"]==datas[i]["date"].year:
                            flag=False
                            event["total"]+=1
                            break
                    if flag:
                        events.append({"year":datas[i]["date"].year, "total":1})
                last_event_date=datas[j]["date"]

            if j>=len(datas)-1:
                break
        return events

    text="Min Rain\t"
    res_total=[]
    for i in range(rain_min, rain_max+1):
        res=_rain_cumul(datas, step, i, min_time_beetween_event)
        res_total.append({"min":i, "res":res})

    for i in res_total[0]["res"]:
        text+=str(i["year"])+"\t"
    for res in res_total:
        text+="\n"+str(res["min"])
        for i in res["res"]:
            text+="\t"+str(i["total"])
    return text


#######################################################################################
######################## TEMPE AVERAGE ################################################
#temp average: 1 average done for each day, 2 average over each same day of year, 3 comparaison each day/average of typical day
#analy_type: =0 -> day to day, =1 -> per event

def temp_average(datas, period_type, T_min, T_max):
    def _temp_average(datas, delta_temp, analy_type):
        typical_average={}
        days_average={}
        events={}

        for day in range(0,367):
            typical_average[day]={"val":0, "numb_of_val":0}
        for data in datas:
            date=data["date"].date()
            if date not in days_average:
                days_average[date]={"val":0, "numb_of_val":0}
            days_average[date]["val"]+=data["temp"]
            days_average[date]["numb_of_val"]+=1

            day_numb=(data["date"]-datetime.datetime(data["date"].year, 1, 1)).days+1
            typical_average[day_numb]["val"]+=data["temp"]
            typical_average[day_numb]["numb_of_val"]+=1

            if data["date"].year not in events:
                events[data["date"].year]={"pos":0, "neg":0, "tot":0}

        for day in typical_average:
            if typical_average[day]["numb_of_val"]>0:
                typical_average[day]=typical_average[day]["val"]/typical_average[day]["numb_of_val"]
            else:
                typical_average[day]=0
        for day in days_average:
            if days_average[day]["numb_of_val"]>0:
                days_average[day]=days_average[day]["val"]/days_average[day]["numb_of_val"]
            else:
                days_average[day]=0

        during_event=False
        for day in days_average:
            day_numb=(day-(datetime.datetime(day.year, 1, 1)).date()).days+1
            diff=typical_average[day_numb]-days_average[day]
            if abs(diff)>delta_temp and not during_event:
                if diff>0:
                    events[day.year]["pos"]+=1
                else:
                    events[day.year]["neg"]+=1
                events[day.year]["tot"]+=1

                if analy_type:
                    during_event=True

            elif during_event and abs(diff)<delta_temp:
                during_event=False

        return events


    text="Delta_T\t"
    res={}
    for i in range(T_min, T_max+1):
        text+=str(i)+"\t"*3
    text+="\n"

    for i in range(T_min, T_max+1):
        res[i]=_temp_average(datas, i, period_type)
        for elem in res[i][list(res[i].keys())[0]]:
            text+="\t"+elem

    text+="\n"
    for year in res[list(res.keys())[0]]:
        text+=str(year)
        for i in res:
            for j in res[i]:
                if j==year:
                    for k in res[i][j]:
                        text+="\t"+str(res[i][j][k])
        text+="\n"
    return text
