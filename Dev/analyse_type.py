import datetime
from collections import OrderedDict
from calendar import month_abbr

def date_beetween(date, month_start, month_end):
    if month_start>month_end:
        if not(date.month<month_start and date.month>=month_end):
            return True
    elif date.month>=month_start and date.month<month_end:
        return True
    return False

def check_new_year(year, events, min, max, periods=False):
    if year not in events:
        new_period=OrderedDict()
        for temp in range(min, max+1):
            new_max=OrderedDict()
            if periods:
                for key in periods:
                    new_max[key]={"pos":0, "neg":0, "total":0}
                new_max["during_event"]=False
            else:
                new_max={"pos":0, "neg":0, "total":0, "during_event":False}
            new_period[temp]=new_max
        events[year]=new_period
    return events


def daily_average(datas):
    days=OrderedDict()
    for data in datas:
        date=data["date"].date()
        if date not in days:
            days[date]={"temp":0, "rain":0, "numb_of_val":0}
        days[date]["temp"]+=data["temp"]
        days[date]["rain"]+=data["rain"]
        days[date]["numb_of_val"]+=1
    for day in days:
        days[day]["temp"]=days[day]["temp"]/days[day]["numb_of_val"]
    return days

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

#######################################################################################
########################## Clean Daily Average ########################################
def clean_daily_average(datas):
    days=daily_average(datas)
    res_text="Day\t\tTemp\tRain\n"
    for day in days:
        res_text+="{}\t{:.3f}\t{:.3f}\n".format(day,days[day]["temp"],days[day]["rain"])

    return res_text


#######################################################################################
########################## DIFF TIME ##################################################
#Difference of temp with hours before
def diff_time(datas, delta_t, time_max_event, period, min, max, max_limit):
    #month_start and month end of type int, month_end NOT included, 13 means decembre included
    def add_event(events, new_event, temp):
        year=new_event["last"].year
        period=new_event["period"]
        if new_event["type"]=="+":
            events[year][temp][period]["pos"]+=1
        elif new_event["type"]=="-":
            events[year][temp][period]["neg"]+=1
        events[year][temp][period]["total"]+=1

        return events

    if period==1:
        period_list={"Year":[1,13]} #period list from month# to month# NOT INCLUDED, 13 => december included
    elif period==2:
        period_list={"Winter":[12,3],"Spring":[3,6],"Summer":[6,9],"Autumn":[9,12]}
    elif period==3:
        period_list={}
        for i in range(1,13):
            period_list[month_abbr[i]]=[i, i+1]

    event_list=OrderedDict()

    for i in range(0,len(datas)):
        year=datas[i]["date"].year
        event_list=check_new_year(year, event_list, min, max, period_list)

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

                for key in period_list:
                    if date_beetween(datas[i]["date"], period_list[key][0], period_list[key][1]):
                        new_event={"last": datas[i]["date"], "type": event_type, "period":key, "max":abs(d_temp)}
                        break

            elif case["during_event"]:
                if abs(d_temp)>new_event["max"]:
                    new_event["max"]=abs(d_temp)

                if d_temp>=min:
                    new_event["last"]=datas[i]["date"]

                elif datas[i]["date"]-new_event["last"]>time_max_event:
                    case["during_event"]=False
                    if (max_limit and new_event["max"]<temp+1) or not max_limit:
                        event_list=add_event(event_list, new_event, temp)

        if j>=len(datas)-1:
            break

    for temp in event_list[year]:
        case=event_list[year][temp]
        if case["during_event"]:
            if abs(d_temp)>new_event["max"]:
                new_event["max"]=abs(d_temp)
            if (max_limit and new_event["max"]<temp+1) or not max_limit:
                event_list=add_event(event_list, new_event, temp)

    return build_text(event_list, min, max, period_list=period_list)

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

    min_time_beetween_event=datetime.timedelta(hours=min_time_beetween_event)
    step=datetime.timedelta(minutes=step)
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

def temp_average(datas, analy_type, min, max, max_limit):
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
            new_temp={}
            for temp in range(min, max+1):
                new_temp[temp]={"pos":0, "neg":0, "total":0, "during_event":False}
            events[data["date"].year]=new_temp

    for day in typical_average:
        if typical_average[day]["numb_of_val"]>0:
            typical_average[day]=typical_average[day]["val"]/typical_average[day]["numb_of_val"]
            #print(day,typical_average[day])
        else:
            typical_average[day]=0
    for day in days_average:
        if days_average[day]["numb_of_val"]>0:
            days_average[day]=days_average[day]["val"]/days_average[day]["numb_of_val"]
        else:
            days_average[day]=0


    for day in days_average:
        day_numb=(day-(datetime.datetime(day.year, 1, 1)).date()).days+1
        diff=days_average[day]-typical_average[day_numb]
        for temp in range(min, max+1):
            if abs(diff)>temp and not events[day.year][temp]["during_event"]:
                if not max_limit or (max_limit and abs(diff)<temp+1):
                    if diff>0:
                        events[day.year][temp]["pos"]+=1
                    else:
                        events[day.year][temp]["neg"]+=1
                    events[day.year][temp]["total"]+=1

                if analy_type:
                    events[day.year][temp]["during_event"]=True

            elif events[day.year][temp]["during_event"] and abs(diff)<temp:
                events[day.year][temp]["during_event"]=False


    return build_text(events, min, max)

def day_to_span_av(datas, span, min, max, max_limit, analy_type, days_beet_event, period):
    events=OrderedDict()
    days=daily_average(datas)
    days_beet_event=datetime.timedelta(days=days_beet_event)

    if period==1:
        period_list={"Year":[1,13]} #period list from month# to month# NOT INCLUDED, 13 => december included
    elif period==2:
        period_list={"Winter":[12,3],"Spring":[3,6],"Summer":[6,9],"Autumn":[9,12]}
    elif period==3:
        period_list={}
        for i in range(1,13):
            period_list[month_abbr[i]]=[i, i+1]

    for day in days:
        year=day.year
        events=check_new_year(year, events, min, max, periods=period_list)

        average=0
        numb_of_value=0

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
        for min_temp in range(min, max+1):
            if abs(d_temp)>=min_temp and not events[year][min_temp]["during_event"]:
                if not max_limit or (max_limit and abs(d_temp)<min_temp+1):
                    for key in period_list:
                        if date_beetween(day, period_list[key][0], period_list[key][1]):
                            if analy_type:
                                events[year][min_temp]["during_event"]=True
                                events[year][min_temp]["last"]=day
                            if d_temp>0:
                                events[year][min_temp][key]["pos"]+=1
                            elif d_temp<0:
                                events[year][min_temp][key]["neg"]+=1
                            events[year][min_temp][key]["total"]+=1
                            break

            elif events[year][min_temp]["during_event"]:
                if day-events[year][min_temp]["last"]>days_beet_event:
                    events[year][min_temp]["during_event"]=False
                elif abs(d_temp)>=min_temp:
                    events[year][min_temp]["last"]=day

    return build_text(events, min, max, period_list=period_list)
