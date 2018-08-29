#!/usr/bin/python
# -*- coding: UTF-8 -*-
# MEFA: Meterological Event Frequency Analysis Software
# Ver. 1.9.6
# Jérémy Mayoraz pour GéoVal
# Sion, Août 2018

import sys
import datetime

#my files
import temp_analyse as ta
import rain_analyse as ra
import plot
from gui import Window
from constant import *
import utilities

#######################################################################################
####################### ANALYSES ######################################################
#analyse directly from command line
def analyse_from_prompt(argv, output_file, data_format):
    print("  > Opening file ...", end="\r")
    #get arguments
    analyse_type=argv[2]
    per_event, with_max, save_plot, show_plot= False, False, False, False
    period_list=[]
    if "-pe" in argv:
        per_event=True
    if "-wm" in argv:
        with_max=True
    if "--year" in argv:
        period_list.append(1)
    if "--season" in argv:
        period_list.append(2)
    if "--month" in argv:
        period_list.append(3)
    if "--save-plot" in argv:
        save_plot=True
    if "--show-plot" in argv:
        show_plot=True
    #default period list (only year)
    if period_list==[]:
        period_list=[1]

    #read file with error detection
    temp_datas, rain_datas, read_log, message=utilities.read_file(argv[1], data_format, file_enc=FILE_ENCODING, show_info=True)
    if message:
        print(message)
        return

    plot_depth=False
    title=analyse_type+": "

    first=True
    #if more than one period: many loop

    for period in period_list:
        print("  > Analysis for period: "+str(["Year", "Season", "Month"][period-1]))
        print("  > Analysing data ...", end="\r")
        if analyse_type=="Data_Cleaning" and first:
            #daily average
            if "-da" in argv:
                text=ta.clean_daily_average(temp_datas, rain_datas, show_info=True)
            #just clean data
            else:
                text="date\ttemp\train"
                temp, rain=temp_datas, rain_datas
                t,r=0,0
                for l in range(max(len(temp), len(rain))):
                    if t>=len(temp) or temp[t]["date"]>rain[r]["date"]:
                        text+="\n"+str(rain[r]["date"])+"\t \t"+str(rain[r]["rain"])
                        r+=1
                    elif r>=len(rain) or temp[t]["date"]<rain[r]["date"]:
                        text+="\n"+str(temp[t]["date"])+"\t"+str(temp[t]["temp"])+"\t "
                        t+=1
                    elif temp[t]["date"]==rain[r]["date"]:
                        text+="\n"+str(rain[r]["date"])+"\t"+str(temp[t]["temp"])+"\t"+str(rain[r]["rain"])
                        r+=1
                        t+=1

        elif analyse_type=="Difference_Time":
            #variable init
            plot_depth=4
            delta_t=datetime.timedelta(hours=24)
            time_max_event=datetime.timedelta(hours=24)
            T_min, T_max=2, 8
            title+="delta t: {}, event time max: {}, from: {}°C to: {}°C".format(delta_t, time_max_event, T_min, T_max)
            if with_max:
                title+=" with max limit"
            text, data=ta.diff_time(temp_datas, delta_t, time_max_event, period, T_min, T_max, with_max, show_info=True)


        elif analyse_type=="Temp_Average":
            #variable init
            plot_depth=4
            T_min, T_max= 3, 10
            title+="from: {}°C to: {}°C".format(T_min, T_max)
            if with_max:
                title+=" with max limit"
            if per_event:
                title+=", per event"
            else:
                title+=", day to day"
            text, data=ta.temp_average(temp_datas, per_event, T_min, T_max, with_max, period, show_info=True)

        elif analyse_type=="Day_To_Span_Average":
            #variable init
            plot_depth=4
            span=10
            days=2
            T_min, T_max=2,10
            title+="span: {} days, min time beet. events: {} days,  from: {}°C to: {}°C".format(span, days, T_min, T_max)
            if with_max:
                title+=" with max limit"
            if per_event:
                title+=", per event"
            else:
                title+=", day to day"
            text, data=ta.day_to_span_av(temp_datas, span, T_min, T_max, with_max, per_event, days, period, show_info=True)

        elif analyse_type=="Rain_Cumul":
            #variable init
            plot_depth=3
            min_rain=6
            min_time_beetween_event=15
            T_min, T_max = 6, 24
            text, data=ra.rain_cumul(rain_datas, T_min, T_max, min_time_beetween_event, min_rain, period, per_event, show_info=True)

        #not accessible per GUI
        elif analyse_type=="Rain_Event":
            plot_depth=0
            text=ra.rain_event(rain_datas, period, portion=0.5)

        #not accessible per GUI
        elif analyse_type=="Rain_Max":
            plot_depth=0
            text=ra.rain_max(rain_datas, period, 1, per_event, with_max, increment=0.5)

        res_text=title+"\n"+text
        #output file
        if "-of" in argv or output_file!="output.txt":
            if not utilities.write_file(output_file, res_text, read_log):
                print("  > Error: File not found (404)")
                return
            else:
                print("  > See file "+output_file)

        #plotting
        if (show_plot or save_plot) and plot_depth:
            for i in range(TAKE_OUT_FIRST):
                data.pop(min([i for i in data]))
            for i in range(TAKE_OUT_LAST):
                data.pop(max([i for i in data]))

            if not first:
                plot.destroy()

            if not plot.plot_data(data, plot_depth, title, save_plot, show_plot=show_plot):
                print("  > Warning: Cannot plot with only one year.")
        first=False

    print("  > Analyse ended")


#######################################################################################
#                      Global Constant                                                #
#######################################################################################
#Default file name
FILE_NAME=DEFAULT_FILE_NAME
# FILE_NAME="../test_file/month6.txt"
# FILE_NAME="../test_file/sion_big.txt"

#######################################################################################
#                            Main programme                                           #
#######################################################################################
output_file="output.txt"
n=len(sys.argv)

#file format
d=0
if n>3 and sys.argv[3] in ["0","1","2"]:
    d=int(sys.argv[3])

flag=False
argument_list=["-h", "-pe", "-wm", "-da", "--year", "--season", "--month", "--show-plot", "--save-plot", "-of"]
for i in sys.argv:
    #output file name
    if i[:4]=="-of=":
        output_file=i[4:]
    #check of arguments
    elif i[0]=="-" and i not in argument_list:
        print("Error: '{}' not a known argument\nFormat must be:\n".format(i))
        flag=True

#imput help
if "-h" in sys.argv or (n>1 and sys.argv[1][0]=="-") or (n>2 and sys.argv[2][0]=="-") or flag:
    print("mefa_v19.x FILE_NAME ANALYSE_TYPE [DATA_FORMAT (0,1 or 2)] [-h, -pe, -wm, -da, --year/--season/--month, --show-plot, --save-plot, -of]\n")
    print("ANALYSE_TYPE must be: "+str(ANALYSE_TYPE))
    print("\nArguments:\n-h\t\t\t help\n-pe\t\t\t per event\n-wm\t\t\t with max\n-da\t\t\t daily average\n--year/--season/--month: period (can be more than one)\n--show-plot\t\t show plot\n--save-plot\t\t save plot\n-of\t\t\t output file (-of=... to change from default 'output.txt')")

#analyse from command line
elif n>2:
    FILE_NAME=sys.argv[1]
    if sys.argv[2] not in ANALYSE_TYPE:
        print("Error: ANALYSE_TYPE must be: "+str(ANALYSE_TYPE))
    else:
        analyse_from_prompt(sys.argv, output_file, d)

#analyse from GUI
else:
    if n==2:
        FILE_NAME=sys.argv[1]
    main=Window(FILE_NAME, data_format=d)
    if n==2:
        main.open_file()
    main.mainloop()
