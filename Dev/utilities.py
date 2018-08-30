#!/usr/bin/python
# -*- coding: UTF-8 -*-
# MEFA: Meterological Event Frequency Analysis Software
# Ver. 1.9.7
# Jérémy Mayoraz pour GéoVal
# Sion, Août 2018

import datetime
from calendar import month_abbr

from constant import *

#######################################################################################
######################## FILE HANDLING ################################################
#File Reading and Writting
def read_file(file_name, data_format, file_enc="UTF-8", show_info=False):
    #Creation of data from input, returns a dictionnary of the datas (temp and rain) and if
    #each data is good (True) or not (False)
    def create_data(line, column, complete_date, date_format):
        def get(elem):
            for i in range(0,len(column)):
                if column[i]["val"]==elem:
                    return line[i]
            return None
        try:
            #if complete date, the column is allready the good format
            if complete_date:
                date_val=get("Date")
            else:
                date_val=get("Year")+"-"+get("Month")+"-"+get("Day")
                date_val+="-"+get("Hour")+"-"+get("Minutes")
            rain_data={"date":datetime.datetime.strptime(date_val, date_format)}
            temp_data={"date":datetime.datetime.strptime(date_val, date_format)}

            rain_data["rain"]=eval(get("Rain"))
            temp_data["temp"]=eval(get("Temp"))

            return_temp, return_rain=True, True
            #limit for bad data
            if abs(rain_data["rain"])>=RAIN_LIMIT:
                return_rain=False
            if abs(temp_data["temp"])>TEMP_LIMIT:
                return_temp=False
            return temp_data, rain_data, return_temp, return_rain
        except:
            return False, False, "Data could not be retrieved\nTry changing loading parameters", False

    #get start of data
    def get_start(line, column):
        #Prevent exception
        if line==[]:
            return False
        for i in range(0, min(len(column),len(line))):
            if column[i]["name"]!=line[i]:
                return False
        return True

    temp_datas, rain_datas=[], []
    bad_temp_data, bad_rain_data= 0, 0
    column=[]
    complete_date=False
    temp_col, rain_col=False, False

    #usual format (from cmd)
    if type(data_format)==int:
        col_name=COL_NAMES[data_format]
        col_format=COL_FORMATS[data_format]
        auto_mode=AUTO_MODES[data_format]
        temp_key=TEMP_KEY
        rain_key=RAIN_KEY
        date_format=DATE_FORMATS[data_format]
    #exotic format (from GUI)
    else:
        col_name=data_format["col_name"]
        col_format=data_format["col_form"]
        auto_mode=data_format["auto_mode"]
        temp_key=data_format["temp_key"]
        rain_key=data_format["rain_key"]
        date_format=data_format["date"]

    if len(col_name)!=len(col_format):
        return False, False, False, "Wrong data format: column name and column format not same length"


    #easter egg
    if file_name=="Hello There!":
        return False, False, False, "General Kenobi, you're a bold one!"
    #create column
    for i in range(0, len(col_format)):
        column.append({"pos":i, "name":col_name[i], "val":col_format[i]})
        if not auto_mode:
            if col_format[i]=="Rain":
                rain_col=col_name[i]
            elif col_format[i]=="Temp":
                temp_col=col_name[i]
        if col_format[i]=="Date":
            complete_date=True
    #open file
    try:
        file=open(file_name, 'r', encoding=file_enc)
        file_lines=file.readlines()
        file.close()
    except(FileNotFoundError, IsADirectoryError):
        return False, False, False, "File not found (Err. 404)"

    if show_info:
        show_info=1
        len_file_lines=len(file_lines)
        state=0
    flag_1=False
    #main reading loop
    for comp_line in file_lines:
        line=comp_line.split()
        #Main data input
        if flag_1 and line!=[]:
            new_temp_data, new_rain_data, temp_flag, rain_flag = create_data(line, column, complete_date, date_format)
            if not new_temp_data and not new_rain_data:
                return False, False, False, temp_flag
            if temp_flag:
                temp_datas.append(new_temp_data)
            else:
                bad_temp_data+=1
            if rain_flag:
                rain_datas.append(new_rain_data)
            else:
                bad_rain_data+=1

        #Get starting point
        elif get_start(line, column):
            if auto_mode and not rain_col and not temp_col:
                return False, False, False, "No temperature or rain data detected"
            for i in line:
                if i==rain_col:
                    column.append({"pos":i, "name":rain_col, "val":"Rain"})
                    flag_1=True
                elif i==temp_col:
                    column.append({"pos":i, "name":temp_col, "val":"Temp"})
                    flag_1=True
            if not flag_1:
                return False, False, False, "No temperature or rain data detected"

        #Automatic rain and temp column detection
        elif len(line)>1 and auto_mode:
            if line[1][0:5]==rain_key[0:5]:
                rain_col=line[0]
            elif line[1][0:5]==temp_key[0:5]:
                temp_col=line[0]
        #percentage indicator
        if show_info:
            if show_info/len_file_lines>state:
                print("  > Opening file     {:.0f}%".format(state*100), end="\r")
                state+=0.01
            show_info+=1
    if show_info:
        print("  > Opening file    {:.0f}%".format(100))

    #check that data was found
    if len(temp_datas)+len(rain_datas)==0:
        return False, False, False, "Data could not be retrieved\nTry changing loading parameters"
    log="{} temperature values with {} bad values ({:.1f}%) (taken out)\n".format(len(temp_datas), bad_temp_data, bad_temp_data/len(temp_datas)*100)
    log+="{} rain values with {} bad values ({:.1f}%) (taken out)\n".format(len(rain_datas), bad_rain_data, bad_rain_data/len(rain_datas)*100)

    return temp_datas, rain_datas, log, None

#write a new file
def write_file(file_name, res, log):
    try:
        file=open(file_name, "w")
        file.write("\t\t\t\t\t{}\n".format(datetime.datetime.now().strftime('%Y-%m-%d')))
        file.write("Result of analyse of data: ")
        file.write(log+"\n")
        file.write(res)
        file.close()
        return True
    except (FileNotFoundError, IsADirectoryError):
        return False

#######################################################################################
################# ANALYSES UTILITIES ##################################################

#returns if a date is beetween two months or not
#month_start and month end of type int, month_end NOT included, 13 means decembre included
def date_beetween(date, month_start, month_end):
    if month_start>month_end:
        if not(date.month<month_start and date.month>=month_end):
            return True
    elif date.month>=month_start and date.month<month_end:
        return True
    return False

# makes a lits of the period: 1=all year, 2=seasonal, 3=monthly
def make_period_list(period):
    if period==1:
        return {"Year":[1,13]} #period list from month# to month# NOT INCLUDED, 13 => december included
    elif period==2:
        return {"Winter":[12,3],"Spring":[3,6],"Summer":[6,9],"Autumn":[9,12]}
    elif period==3:
        period_list={}
        for i in range(1,13):
            period_list[month_abbr[i]]=[i, i+1]
        return period_list
