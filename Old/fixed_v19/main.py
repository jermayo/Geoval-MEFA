#!/usr/bin/python
# -*- coding: UTF-8 -*-
# MEFA: Meterological Event Frequency Analysis Software
# Ver. 1.8.1
# Jérémy Mayoraz pour GéoVal
# Sion, Août 2018

import sys
import tkinter as tk
from tkinter import messagebox
import datetime
from calendar import monthrange
from collections import OrderedDict

import temp_analyse as ta
import rain_analyse as ra
import plot

#######################################################################################
#                  Classes and general functions                                      #
#######################################################################################
#Global variables of the programme
class GlobalVariables():
    def __init__(self, default=0):
        self.temp_datas=None
        self.rain_datas=None
        self.read_log=None
        self.temp_col=False
        self.rain_col=False

        self.date_format_list=['%Y-%m-%d-%H-%M', '%d/%m/%Y', '%Y-%m-%d']
        self.column_name_list=[["STA", "JAHR", "MO", "TG", "HH", "MM"], ["Date", "Rain", "Temp"], ["Day", "Temp", "Rain"]]
        self.column_format_list=[["Station", "Year", "Month", "Day", "Hour", "Minutes"], ["Date", "Rain", "Temp"], ["Date", "Temp", "Rain"]]

        self.date_format=self.date_format_list[default]
        self.column_format=self.column_format_list[default]
        self.column_name=self.column_name_list[default]
        self.auto_mode=[True, False, False][default]
        self.rain_keyword="Niederschlag"
        self.temp_keyword="Lufttemperatur"


#Creation of data from input, returns a list of the datas (dictionnary)
#and if the data is good (True) not (False)
def create_data(line, column, complete_date):
    def get(elem):
        for i in range(0,len(column)):
            if column[i]["val"]==elem:
                return line[i]
        return None

    try:
        if complete_date:
            date_val=get("Date")
        else:
            date_val=get("Year")+"-"+get("Month")+"-"+get("Day")
            date_val+="-"+get("Hour")+"-"+get("Minutes")
        rain_data={"date":datetime.datetime.strptime(date_val, GV.date_format)}
        temp_data={"date":datetime.datetime.strptime(date_val, GV.date_format)}

        rain_data["rain"]=eval(get("Rain"))
        temp_data["temp"]=eval(get("Temp"))

        return_temp, return_rain=True, True
        if abs(rain_data["rain"])>=RAIN_LIMIT:
            return_rain=False
        if abs(temp_data["temp"])>TEMP_LIMIT:
            return_temp=False
        return temp_data, rain_data, return_temp, return_rain
    except:
        return False, False, "Data could not be retrieved", False


#File Reading and Writting
def read_file(file_name, temp_col, rain_col, file_encoding="UTF-8", show_info=False):
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

    if file_name=="Hello There!":
        messagebox.showinfo("","General Kenobi, you're a bold one.")

    for i in range(0, len(GV.column_format)):
        column.append({"pos":i, "name":GV.column_name[i], "val":GV.column_format[i]})
        if not GV.auto_mode:
            if GV.column_format[i]=="Rain":
                rain_col=GV.column_name[i]
            elif GV.column_format[i]=="Temp":
                temp_col=GV.column_name[i]
        if GV.column_format[i]=="Date":
            complete_date=True
    try:
        file=open(file_name, 'r', encoding=file_encoding)
        file_lines=file.readlines()
        file.close()
    except FileNotFoundError:
        return False, False, False, "File not found (Err. 404)"

    if show_info:
        show_info=1
        len_file_lines=len(file_lines)
        state=0
    flag_1=False
    for comp_line in file_lines:
        line=comp_line.split()
        #Main data input
        if flag_1 and line!=[]:
            new_temp_data, new_rain_data, temp_flag, rain_flag = create_data(line, column, complete_date)
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

        #Get startitng point
        elif get_start(line, column):
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
        elif len(line)>1 and GV.auto_mode:
            if line[1][0:5]==GV.rain_keyword[0:5]:
                rain_col=line[0]
            elif line[1][0:5]==GV.temp_keyword[0:5]:
                temp_col=line[0]

        if show_info:
            if show_info/len_file_lines>state:
                print("  > Opening file     {:.0f}%".format(state*100), end="\r")
                state+=0.01
            show_info+=1
    if show_info:
        print("  > Opening file    {:.0f}%".format(100))
    if len(temp_datas)+len(rain_datas)==0:
        return False, False, False, "Data could not be retrieved"
    log="{} temperature values with {} bad values ({:.1f}%) (taken out)\n".format(len(temp_datas), bad_temp_data, bad_temp_data/len(temp_datas)*100)
    log+="{} rain values with {} bad values ({:.1f}%) (taken out)\n".format(len(rain_datas), bad_rain_data, bad_rain_data/len(rain_datas)*100)

    return temp_datas, rain_datas, log, None


def file_write(file_name, res, log):
    try:
        file=open(file_name, "w")
        file.write("\t\t\t\t\t{}\n".format(datetime.datetime.now().strftime('%Y-%m-%d')))
        file.write("Result of analyse of data: ")
        file.write(log+"\n")
        file.write(res)
        file.close()
        return True
    except FileNotFoundError:
        return False

#######################################################################################
#                             GUI                                                     #
#######################################################################################
class Window():
    def __init__(self):
        #Main window
        self.w=tk.Tk()
        self.w.title("Meteorological Event Frequency Analysis")
        #self.w.tk.call('wm', 'iconphoto', self.w._w, tk.PhotoImage(file='icone.png'))
        #StringVar and IntVar()
        self.analyse_type = tk.StringVar(self.w)
        self.analyse_type.set(ANALYSE_TYPE[0])
        self.output_toggle = tk.IntVar()
        self.output_toggle.set(1)
        self.plot_toggle = tk.IntVar()
        self.plot_toggle.set(1)
        self.save_plot_toggle=tk.IntVar()
        self.save_plot_toggle.set(0)
        self.file_name="..."
        self.auto_step=tk.IntVar()
        self.auto_step.set(0)
        self.max_limit=tk.IntVar()
        self.max_limit.set(0)
        self.daily_av=tk.IntVar()
        self.daily_av.set(0)
        self.period=tk.IntVar()
        self.period.set(1)
        self.analy_type=tk.IntVar()
        self.analy_type.set(1)

        self.w_list=[]

        tk.Label(self.w, text="File Name:").grid(row=1,column=0)
        self.E_file = tk.Entry(self.w)
        self.E_file.insert(0, DEFAULT_FILE_NAME)
        self.E_file.grid(row=1,column=1)
        self.B_open = tk.Button(self.w, text="Open", command=self.open_file)
        self.B_open.grid(row=1,column=2)

        self.B_exit = tk.Button(self.w, text="Change Load Param", command=self.change_load)
        self.B_exit.grid(row=5, column=3, sticky=tk.SW)
        self.B_exit = tk.Button(self.w, text="Exit", command=self.exit)
        self.B_exit.grid(row=5, column=4, sticky=tk.SW)

        self.L_file=tk.Label(self.w, text=self.file_name)

        self.result_frame=tk.LabelFrame(self.w, text="Results")
        self.res_text=tk.Label(self.result_frame, justify=tk.LEFT)
        self.res_text.grid()
        self.result_frame.grid(row=4,column=3, columnspan=3)
        self.result_frame.grid_remove()

        self.L_anayse=tk.Label(self.w, text = "")
        self.L_anayse.grid(row=4,column=3)

        self.tweak_frame = tk.LabelFrame(self.w, text="Tweaks")
        self.L_info=tk.Label(self.w, justify=tk.LEFT, relief=tk.RIDGE, padx=5, pady=5)

    def init_analyse_option(self):
        for child in self.tweak_frame.winfo_children():
            child.destroy()

        output_frame = tk.LabelFrame(self.w, text="Output")
        self.CB_output = tk.Checkbutton(output_frame, variable=self.output_toggle, text="Output file")
        self.CB_output.grid(row=1,column=1)
        tk.Label(output_frame, text="File Name:").grid(row=2,column=1)
        self.E_output = tk.Entry(output_frame)
        self.E_output.insert(0,"output.txt")
        self.E_output.grid(row=2,column=2)
        self.CB_plot = tk.Checkbutton(output_frame, variable=self.plot_toggle, text="Plot graph")
        self.CB_plot.grid(row=3,column=1)
        self.CB_plot = tk.Checkbutton(output_frame, variable=self.save_plot_toggle, text="Save Plot")
        self.CB_plot.grid(row=3,column=2)
        output_frame.grid(row=1,rowspan=2, column=3, stick=tk.W)


        tk.Label(self.w, text="Analyse type:").grid(row=3,column=0)
        self.analyse_type.set(ANALYSE_TYPE[0])
        self.O_analyse=tk.OptionMenu(self.w, self.analyse_type, *ANALYSE_TYPE_GUI, command=self.change_analyse)
        self.O_analyse.grid(row=3,column=1)


        self.B_open = tk.Button(self.w, text="Analyse", command=self.analyse)
        self.B_open.grid(row=3,column=2)

        self.tweak_frame.grid(row=4,column=0, rowspan=2, columnspan=3, sticky=tk.N)
        self.L_info.grid(row=7,column=0, rowspan=2, columnspan=4, sticky=tk.NW)

        self.change_analyse("Data_Cleaning")

    def open_file(self):
        plot.destroy()
        old_text=self.file_name
        self.L_file.config(text = "Loading File...")
        self.L_file.grid(row=2,column=0,columnspan=2)
        self.L_file.update_idletasks()
        self.load_begin()

        self.file_name=self.E_file.get()
        temp_datas, rain_datas, read_log, message=read_file(self.file_name, GV.temp_col, GV.rain_col, file_encoding=FILE_ENCODING)
        self.load_end()
        if read_log:
            GV.temp_datas, GV.rain_datas, GV.read_log = temp_datas, rain_datas, read_log
            self.init_analyse_option()
            self.L_file.config(text = "File '{}' loaded".format(self.file_name))
            messagebox.showinfo("Done", "File loaded: \n"+GV.read_log)
        else:
            messagebox.showerror("Error", message)
            self.L_file.config(text = old_text)

    def find_min_max(self, w_single, w_min, w_max):
        if self.auto_step.get():
            min=int(self.w_list[w_min].get())
            max=int(self.w_list[w_max].get())
            max_limit=self.max_limit.get()
        else:
            min=int(self.w_list[w_single].get())
            max=min
            max_limit=False
        if min>max:
            messagebox.showerror("Error", "Minimal value greater than maximal.\n(You fool)")
            return False
        return True, min, max, max_limit

    def analyse(self):

        analyse=self.analyse_type.get()
        self.result_frame.grid_remove()
        self.L_anayse.config(text="Analysing data ...")
        self.L_anayse.update_idletasks()
        self.load_begin()

        plot_depth=False
        title=analyse+": "
        if analyse=="Data_Cleaning":
            if self.daily_av.get():
                text=ta.clean_daily_average(GV.temp_datas, GV.rain_analyse)
            else:
                text=""
                temp, rain=GV.temp_datas, GV.rain_analyse
                t,r=0,0
                for l in range(max(len(temp), len(rain))):
                    if t>=len(temp) or temp[t]["date"]>rain[r]["date"]:
                        text+="\n"+str(rain[r]["date"])+"\t \t"+str(rain[r]["rain"])
                        r+=1
                    elif r>=len(rain) or temp[t]["date"]<rain[r]["date"]:
                        text+="\n"+str(temp[t]["date"])+"\t"+str(temp[t]["temp"])+"\t "
                        t+=1
                    elif temp[l]["date"]==rain[t]["date"]:
                        text+="\n"+str(rain[r]["date"])+"\t"+str(temp[t]["temp"])+"\t"+str(rain[r]["rain"])
                        r+=1
                        t+=1

        elif analyse=="Difference_Time":
            plot_depth=4
            delta_t=datetime.timedelta(hours=int(self.Sb_tweak2.get()))
            time_max_event=datetime.timedelta(hours=int(self.Sb_tweak3.get()))
            period=self.period.get()
            go, T_min, T_max, max_limit=self.find_min_max(1, 3, 5)
            title+="delta t: {}, event time max: {}, from: {}°C to: {}°C".format(delta_t, time_max_event, T_min, T_max)
            if max_limit:
                title+=" with max limit"
            #title+="\n"
            if go:
                text, data=ta.diff_time(GV.temp_datas, delta_t, time_max_event, period, T_min, T_max, max_limit)


        elif analyse=="Temp_Average":
            plot_depth=3
            period_type=self.analy_type.get()
            go, T_min, T_max, max_limit=self.find_min_max(0, 2, 4)
            title+="from: {}°C to: {}°C".format(T_min, T_max)
            if period_type:
                title+=", per event"
            else:
                title+=", day to day"
            if go:
                text, data=ta.temp_average(GV.temp_datas, period_type, T_min, T_max, max_limit)

        elif analyse=="Day_To_Span_Average":
            plot_depth=4
            span=int(self.Sb_tweak1.get())
            days=int(self.Sb_tweak2.get())
            analy_type=self.analy_type.get()
            period=self.period.get()
            go, T_min, T_max, max_limit=self.find_min_max(1, 3, 5)
            title+="span: {} days, min time beet. events: {} days,  from: {}°C to: {}°C".format(span, days, T_min, T_max)
            if max_limit:
                title+=" with max limit"
            if analy_type:
                title+=", per event"
            else:
                title+=", day to day"
            if go:
                text, data=ta.day_to_span_av(GV.temp_datas, span, T_min, T_max, max_limit, analy_type, days, period)

        elif analyse=="Rain_Cumul":
            plot_depth=3
            min_rain=int(self.w_list[4].get())
            min_time_beetween_event=int(self.w_list[5].get())
            period=self.period.get()
            per_event=self.analy_type.get()
            go, T_min, T_max, max_limit=self.find_min_max(None, 1, 3)
            if go:
                text, data=ra.rain_cumul(GV.rain_datas, T_min, T_max, min_time_beetween_event, min_rain, period, per_event)

        res_text=title+"\n"+text
        if self.output_toggle.get():
            if not file_write(self.E_output.get(),res_text, GV.read_log):
                messagebox.showerror("Error", "File not found (404)")
                self.load_end()
                return

        self.L_anayse.config(text="")
        if len(res_text)>1000:
            res_text="Data too big, see file\n"
        self.res_text.config(text=res_text)
        self.res_text.grid()
        self.result_frame.grid()

        self.load_end()

        if self.plot_toggle.get() and plot_depth:
            for i in range(TAKE_OUT_FIRST):
                data.pop(min([i for i in data]))
            for i in range(TAKE_OUT_LAST):
                data.pop(max([i for i in data]))
            if not plot.plot_data(data, plot_depth, title, self.save_plot_toggle.get()):
                messagebox.showwarning("Warning", "Cannot plot with only one year.")


    def change_analyse(self, value):
        for child in self.tweak_frame.winfo_children():
            child.destroy()
        self.auto_step.set(0)
        row=1

        if value=="Data_Cleaning":
            self.daily_av.set(0)
            tk.Checkbutton(self.tweak_frame, variable=self.daily_av, text="Daily Average").grid(row=row, column=2)
            self.L_info.config(text=CLEANING_INFO)

        if value=="Difference_Time":
            self.period.set(1)

            tk.Checkbutton(self.tweak_frame, variable=self.auto_step, text="Ranged Auto Min", command=self.toggle_auto_min).grid(row=row, column=1)
            row+=1
            self.toggle_auto_min()
            row+=1
            tk.Label(self.tweak_frame, text="Time Diff:").grid(row=row,column=1)
            self.Sb_tweak2=tk.Spinbox(self.tweak_frame, from_=24, to_=1000, justify=tk.RIGHT, width=3, increment=24)
            self.Sb_tweak2.grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="Hours").grid(row=row,column=3)
            row+=1
            tk.Label(self.tweak_frame, text="Max Event Time:").grid(row=row,column=1)
            self.Sb_tweak3=tk.Spinbox(self.tweak_frame, from_=0, to_=1000, justify=tk.RIGHT, width=3)
            self.Sb_tweak3.delete(0,tk.END)
            self.Sb_tweak3.insert(0,24)
            self.Sb_tweak3.grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="Hours").grid(row=row,column=3)
            row+=1
            tk.Label(self.tweak_frame, text="Period:").grid(row=1, column=7)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="All Year", value=1).grid(row=2, column=7, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Season", value=2).grid(row=3, column=7, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Month", value=3).grid(row=4, column=7, sticky=tk.W)

            tk.Label(self.tweak_frame, text="(Season: Winter (Dec, Jan, Feb), and so on...)").grid(row=5, column=1, columnspan=3)

            self.L_info.config(text=DIFF_TIME_INFO+AUTO_RANGE_INFO+WITH_MAX_INFO)

        elif value=="Temp_Average":
            self.analy_type.set(0)
            tk.Checkbutton(self.tweak_frame, variable=self.auto_step, text="Ranged Auto Min", command=self.toggle_auto_min3).grid(row=row, column=1)
            row+=1
            tk.Label(self.tweak_frame, text="Delta Temp: ").grid(row=row, column=1)
            self.toggle_auto_min3()
            tk.Label(self.tweak_frame, text="°C").grid(row=row,column=6)
            row+=1
            tk.Label(self.tweak_frame, text="Type:").grid(row=row, column=1)
            tk.Radiobutton(self.tweak_frame, var=self.analy_type, text="Day to day", value=0).grid(row=row, column=2, sticky=tk.W, columnspan=10)
            tk.Radiobutton(self.tweak_frame, var=self.analy_type, text="Per event", value=1).grid(row=row+1, column=2, sticky=tk.W, columnspan=10)

            self.L_info.config(text=TEMP_AVERAGE_INFO+AUTO_RANGE_INFO)

        elif value=="Day_To_Span_Average":
            self.analy_type.set(0)
            self.period.set(1)
            tk.Checkbutton(self.tweak_frame, variable=self.auto_step, text="Ranged Auto Min", command=self.toggle_auto_min4).grid(row=row, column=1,columnspan=2)
            tk.Label(self.tweak_frame, text="Type:").grid(row=row, column=9)
            row+=1
            tk.Label(self.tweak_frame, text="Span:").grid(row=row,column=1)
            self.Sb_tweak1=tk.Spinbox(self.tweak_frame, from_=0, to_=1000, justify=tk.RIGHT, width=3)
            self.Sb_tweak1.delete(0,tk.END)
            self.Sb_tweak1.insert(0,30)
            self.Sb_tweak1.grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="Days").grid(row=row, column=3)
            tk.Radiobutton(self.tweak_frame, var=self.analy_type, text="Day to day", value=0).grid(row=row, column=9, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.analy_type, text="Per event", value=1).grid(row=row+1, column=9, sticky=tk.W)
            row+=1
            self.toggle_auto_min4()
            row+=1
            tk.Label(self.tweak_frame, text="Min time beet. events:").grid(row=row,column=1)
            self.Sb_tweak2=tk.Spinbox(self.tweak_frame, from_=0, to_=10000, justify=tk.RIGHT, width=3)
            self.Sb_tweak2.delete(0,tk.END)
            self.Sb_tweak2.insert(0,2)
            self.Sb_tweak2.grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="Days").grid(row=row,column=3)
            tk.Label(self.tweak_frame, text="Period:").grid(row=1, column=8)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="All Year", value=1).grid(row=2, column=8, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Season", value=2).grid(row=3, column=8, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Month", value=3).grid(row=4, column=8, sticky=tk.W)

            self.L_info.config(text=DAY_TO_SPAN_INFO+AUTO_RANGE_INFO+WITH_MAX_INFO)

        elif value=="Rain_Cumul":
            self.period.set(1)
            self.analy_type.set(0)
            tk.Label(self.tweak_frame, text="Step:").grid(row=row,column=1)
            for w in self.w_list:
                w.destroy()
            self.w_list=[]

            self.auto_step.set(1)
            self.create_range(row, 2, 6, 24)
            row+=1
            tk.Label(self.tweak_frame, text="Min Rain: ").grid(row=row,column=1)
            self.w_list.append(tk.Spinbox(self.tweak_frame, from_=0, to_=1000, justify=tk.RIGHT, width=3))
            self.w_list[-1].delete(0,tk.END)
            self.w_list[-1].insert(0,6)
            self.w_list[-1].grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="mm/time").grid(row=row,column=3)
            row+=1
            tk.Label(self.tweak_frame, text="Min time beet. events:").grid(row=row,column=1)
            self.w_list.append(tk.Spinbox(self.tweak_frame, from_=0, to_=10000, justify=tk.RIGHT, width=3))
            self.w_list[-1].delete(0,tk.END)
            self.w_list[-1].insert(0,15)
            self.w_list[-1].grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="Min").grid(row=row,column=3)

            tk.Label(self.tweak_frame, text="Period:").grid(row=1, column=8)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="All Year", value=1).grid(row=2, column=8, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Season", value=2).grid(row=3, column=8, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Month", value=3).grid(row=4, column=8, sticky=tk.W)

            tk.Radiobutton(self.tweak_frame, var=self.analy_type, text="Day to day", value=0).grid(row=2, column=9, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.analy_type, text="Per event", value=1).grid(row=3, column=9, sticky=tk.W)

            self.L_info.config(text=RAIN_CUMUL_INFO)


    def load_begin(self):
        load_w_width=230
        load_w_height=60
        x=self.w.winfo_x()+int(self.w.winfo_width()/2-load_w_width/2)
        y=self.w.winfo_y()+int(self.w.winfo_height()/2-load_w_height/2)

        self.w.config(cursor="watch")

        self.load_w=tk.Toplevel()
        self.load_w.title("Loading...")
        self.load_w.geometry('%dx%d+%d+%d' % (load_w_width, load_w_height, x, y))
        tk.Label(self.load_w, text="Loading, please wait...\n(This can take a few minutes)").pack()

        self.w.update()
        self.load_w.update()
        self.load_w.tkraise(self.w)
        #self.load_w.grab_set()

    def load_end(self):
        self.w.config(cursor="")
        self.load_w.destroy()

    def toggle_auto_min(self):
        row=1
        self.max_limit.set(0)
        for widget in self.w_list:
            widget.destroy()
        self.w_list=[]
        if self.auto_step.get():
            self.w_list.append(tk.Checkbutton(self.tweak_frame, text="With Max", variable=self.max_limit))
            self.w_list[-1].grid(row=row, column=2, columnspan=4)
            row+=1
            self.w_list.append(tk.Label(self.tweak_frame, text="Delta Temp:"))
            self.w_list[-1].grid(row=row,column=1)
            self.create_range(row, 2, 5, 20)
            self.w_list.append(tk.Label(self.tweak_frame, text="°C"))
            self.w_list[-1].grid(row=row,column=6)
        else:
            row+=1
            self.w_list.append(tk.Label(self.tweak_frame, text="Delta Temp:"))
            self.w_list[-1].grid(row=row,column=1)
            self.w_list.append(tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3))
            self.w_list[-1].delete(0,tk.END)
            self.w_list[-1].insert(0,10)
            self.w_list[-1].grid(row=row,column=2)
            self.w_list.append(tk.Label(self.tweak_frame, text="°C"))
            self.w_list[-1].grid(row=row,column=3)

    def toggle_auto_min2(self):
        row=3
        for widget in self.w_list:
            widget.destroy()
        self.w_list=[]
        self.w_list.append(tk.Label(self.tweak_frame, text="Min Rain:"))
        self.w_list[-1].grid(row=row,column=1)
        if self.auto_step.get():
            self.create_range(row, 2, 1, 15)
            self.w_list.append(tk.Label(self.tweak_frame, text="mm/time"))
            self.w_list[-1].grid(row=row,column=6)
        else:
            self.w_list.append(tk.Spinbox(self.tweak_frame, from_=0, to_=1000000, justify=tk.RIGHT, width=3))
            self.w_list[-1].delete(0,tk.END)
            self.w_list[-1].insert(0,5)
            self.w_list[-1].grid(row=row,column=2)
            self.w_list.append(tk.Label(self.tweak_frame, text="mm/time"))
            self.w_list[-1].grid(row=row,column=3)

    def toggle_auto_min3(self):
        row=1
        self.max_limit.set(0)
        for widget in self.w_list:
            widget.destroy()
        self.w_list=[]
        if self.auto_step.get():
            self.w_list.append(tk.Checkbutton(self.tweak_frame, text="With Max", variable=self.max_limit))
            self.w_list[-1].grid(row=row, column=2, columnspan=4)
            row+=1
            self.create_range(row, 2, 5, 10)

        else:
            row+=1
            self.w_list.append(tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3))
            self.w_list[-1].delete(0,tk.END)
            self.w_list[-1].insert(0,8)
            self.w_list[-1].grid(row=row,column=2)

    def toggle_auto_min4(self):
        row=2
        self.max_limit.set(0)
        for widget in self.w_list:
            widget.destroy()
        self.w_list=[]
        if self.auto_step.get():
            self.w_list.append(tk.Checkbutton(self.tweak_frame, text="With Max", variable=self.max_limit))
            self.w_list[-1].grid(row=row-1, column=3, columnspan=4)
            row+=1
            self.w_list.append(tk.Label(self.tweak_frame, text="Delta Temp:"))
            self.w_list[-1].grid(row=row,column=1)
            self.create_range(row, 2, 2, 15)
        else:
            row+=1
            self.w_list.append(tk.Label(self.tweak_frame, text="Delta Temp:"))
            self.w_list[-1].grid(row=row,column=1)
            self.w_list.append(tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3))
            self.w_list[-1].delete(0,tk.END)
            self.w_list[-1].insert(0,8)
            self.w_list[-1].grid(row=row,column=2)

    def create_range(self, row, first_column, default_min, default_max):
        self.w_list.append(tk.Label(self.tweak_frame, text="From:"))
        self.w_list[-1].grid(row=row,column=first_column)
        self.w_list.append(tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3))
        self.w_list[-1].delete(0,tk.END)
        self.w_list[-1].insert(0,default_min)
        self.w_list[-1].grid(row=row,column=first_column+1)
        self.w_list.append(tk.Label(self.tweak_frame, text="To:"))
        self.w_list[-1].grid(row=row,column=first_column+2)
        self.w_list.append(tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3))
        self.w_list[-1].delete(0,tk.END)
        self.w_list[-1].insert(0,default_max)
        self.w_list[-1].grid(row=row,column=first_column+3)


    def change_load(self):
        self.auto_mode=tk.IntVar()
        self.auto_mode.set(GV.auto_mode)
        self.date_format=tk.StringVar()
        self.date_format.set(GV.date_format)
        self.col_name=tk.StringVar()
        self.col_name.set(GV.column_name)
        self.col_format=tk.StringVar()
        self.col_format.set(GV.column_format)

        #x=self.w.winfo_x()+int(self.w.winfo_width()/2-change_load_w_width/2)
        #y=self.w.winfo_y()+int(self.w.winfo_height()/2-change_load_w_height/2)

        self.change_w=tk.Toplevel()
        self.change_w.title("Change Loading Parameters")
        #self.change_w.geometry('%dx%d+%d+%d' % (change_load_w_width, change_load_w_height, x, y))

        tk.Label(self.change_w, text="Date format: ").grid(column=0, row=0)
        tk.OptionMenu(self.change_w, self.date_format, *GV.date_format_list).grid(column=1, row=0)
        tk.Label(self.change_w, text="Column Names: ").grid(column=0, row=1)
        tk.OptionMenu(self.change_w, self.col_name, *GV.column_name_list).grid(column=1, row=1)
        tk.Label(self.change_w, text="Column Format: ").grid(column=0, row=2)
        tk.OptionMenu(self.change_w, self.col_format, *GV.column_format_list).grid(column=1, row=2)
        tk.Checkbutton(self.change_w, variable=self.auto_mode, text="Auto detection mode", command=self.auto_mode_true).grid(column=1, row=3)
        tk.Button(self.change_w, text="Save", command=self.end_change_load).grid(column=1, row=6)

        self.auto_mode_true()
        self.w.update()
        self.change_w.update()
        self.change_w.tkraise(self.w)

    def auto_mode_true(self):
        if self.auto_mode.get():
            self.auto_mode_l=[]
            self.auto_mode_l.append(tk.Label(self.change_w, text="Rain Keyword: "))
            self.auto_mode_l[-1].grid(row=4, column=0)
            self.auto_mode_l.append(tk.Entry(self.change_w))
            self.auto_mode_l[-1].insert(0, GV.rain_keyword)
            self.auto_mode_l[-1].grid(row=4, column=1)
            self.auto_mode_l.append(tk.Label(self.change_w, text="Temp Keyword: "))
            self.auto_mode_l[-1].grid(row=5, column=0)
            self.auto_mode_l.append(tk.Entry(self.change_w))
            self.auto_mode_l[-1].insert(0, GV.temp_keyword)
            self.auto_mode_l[-1].grid(row=5, column=1)
        else:
            for widget in self.auto_mode_l:
                widget.destroy()

    def end_change_load(self):
        def make_list(string):
            list=[]
            for i in string.split("'"):
                if "(" not in i and ")" not in i and "," not in i:
                    list.append(i)
            return list

        GV.auto_mode=self.auto_mode.get()
        GV.date_format=self.date_format.get()
        GV.column_format=make_list(self.col_format.get())
        GV.column_name=make_list(self.col_name.get())
        if self.auto_mode.get():
            GV.rain_keyword=self.auto_mode_l[1].get()
            GV.temp_keyword=self.auto_mode_l[3].get()
        self.change_w.destroy()

    def exit(self):
        plot.destroy()
        self.w.destroy()

#######################################################################################
###################### NO GUI #########################################################

def analyse_from_prompt(argv, output_file):
    print("  > Opening file ...", end="\r")
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

    if period_list==[]:
        print("  > Error: No period given")
        return

    temp_datas, rain_datas, read_log, message=read_file(DEFAULT_FILE_NAME, False, False, file_encoding=FILE_ENCODING, show_info=True)
    if message:
        print(message)
        return



    plot_depth=False
    title=analyse_type+": "

    first=True
    for period in period_list:
        print("  > Analysis for period: "+str(["Year", "Season", "Month"][period-1]))
        print("  > Analysing data ...", end="\r")
        if analyse_type=="Data_Cleaning" and first:
            if "-da" in argv:
                text=ta.clean_daily_average(temp_datas, rain_datas, show_info=True)
            else:
                text=""
                temp, rain=temp_datas, rain_datas
                t,r=0,0
                for l in range(max(len(temp), len(rain))):
                    if t>=len(temp) or temp[t]["date"]>rain[r]["date"]:
                        text+="\n"+str(rain[r]["date"])+"\t \t"+str(rain[r]["rain"])
                        r+=1
                    elif r>=len(rain) or temp[t]["date"]<rain[r]["date"]:
                        text+="\n"+str(temp[t]["date"])+"\t"+str(temp[t]["temp"])+"\t "
                        t+=1
                    elif temp[l]["date"]==rain[t]["date"]:
                        text+="\n"+str(rain[r]["date"])+"\t"+str(temp[t]["temp"])+"\t"+str(rain[r]["rain"])
                        r+=1
                        t+=1

        elif analyse_type=="Difference_Time":
            plot_depth=4
            delta_t=datetime.timedelta(hours=24)
            time_max_event=datetime.timedelta(hours=24)
            T_min, T_max=2, 8
            title+="delta t: {}, event time max: {}, from: {}°C to: {}°C".format(delta_t, time_max_event, T_min, T_max)
            if with_max:
                title+=" with max limit"
            text, data=ta.diff_time(temp_datas, delta_t, time_max_event, period, T_min, T_max, with_max, show_info=True)


        elif analyse_type=="Temp_Average" and first:
            plot_depth=3
            T_min, T_max= 5, 10
            title+="from: {}°C to: {}°C".format(T_min, T_max)
            if with_max:
                title+=" with max limit"
            if per_event:
                title+=", per event"
            else:
                title+=", day to day"
            text, data=ta.temp_average(temp_datas, per_event, T_min, T_max, with_max, show_info=True)

        elif analyse_type=="Day_To_Span_Average":
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
            plot_depth=3
            min_rain=6
            min_time_beetween_event=15
            T_min, T_max = 6, 24
            text, data=ra.rain_cumul(rain_datas, T_min, T_max, min_time_beetween_event, min_rain, period, per_event, show_info=True)

        elif analyse_type=="Rain_Event":
            plot_depth=0
            text=ra.rain_event(rain_datas, period, portion=0.5)

        elif analyse_type=="Rain_Max":
            plot_depth=0
            text=ra.rain_max(rain_datas, period, 1, per_event, increment=0.5)

        res_text=title+"\n"+text
        if "-of" in argv or output_file!="output.txt":
            if not file_write(output_file, res_text, read_log):
                print("  > Error: File not found (404)")
                return
            else:
                print("  > See file "+output_file)

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



TAKE_OUT_FIRST=2 #Number of years to take out
TAKE_OUT_LAST=1


DEFAULT_FILE_NAME=""
# DEFAULT_FILE_NAME="../test_file/month6.txt"
# DEFAULT_FILE_NAME="../test_file/sion_big.txt"



RAIN_LIMIT=100
TEMP_LIMIT=100


ANALYSE_TYPE = ("Data_Cleaning", "Difference_Time", "Temp_Average", "Day_To_Span_Average", "Rain_Cumul", "Rain_Event", "Rain_Max")
ANALYSE_TYPE_GUI=("Data_Cleaning", "Difference_Time", "Temp_Average", "Day_To_Span_Average", "Rain_Cumul")

FILE_ENCODING="ISO 8859-1"        #Encoding not same on linux and windows (fgs wondows)



CLEANING_INFO=""" Description:
Data Cleaning:
Does what it says. 'Daily Average': Daily average of the temperature and Rain Cumul"""
DIFF_TIME_INFO="""  Description:
Difference over time:
Event starts if the difference beetween a value and the value recorded "Time Diff" before is greater than "Delta Temp".
It ends after "Max event time" so every value greater than "Delta Temp" in that period is not taken into account. The period
allows one to look at the number of event per period of each year. """
TEMP_AVERAGE_INFO="""   Description:
Temperature average:
Event happens if the difference beetween the daily average and the typical average is greater than "Delta Temp".
The typical average is calulated for each day of the year as the average of the daily average of one of the day of the year.
(For exemple: take the daily average of each July 20th every year and make the average of them all, that is the typical daily average)
"Per event" implies that if two consecutive days are events, they only count as one,
whereas "day to day" counts every day that is an event."""
DAY_TO_SPAN_INFO="""    Description:
Day_To_Span_Average:
Event happens if the difference bettween the daily average and the average of 'span' days before and after is greater than 'Delta Temp'.
With 'Day to day': Every day that is over counts, with 'Per Event': Event stops if the daily average gets under 'Delta Temp' for more
than 'Min time beet. events' days."""
RAIN_CUMUL_INFO=""" Description:
Rain cumul:
Events starts when the rain cumul in the last "step" hours is greater than "Min Rain".
The value of "Min Rain" is in mm/"step"
Events stops when the time beetween the next time the cumul is greater than "Min Rain"
and the last time it did is greater than "Min time beet. events"."""
AUTO_RANGE_INFO="""\n\nAuto Range: automaticaly makes the analyses for all values beetween set boundaries"""
WITH_MAX_INFO="""
With 'With max' (only possible for Auto Range), an event is counted ONLY in the temperature corresponding to it's maximal value."""

#######################################################################################
#                            Main programme                                           #
#######################################################################################
output_file="output.txt"
n=len(sys.argv)

d=0
if n>3 and sys.argv[3] in ["0","1","2"]:
    d=int(sys.argv[3])
GV=GlobalVariables(default=d)

flag=False
argument_list=["-h", "-pe", "-wm", "-da", "--year", "--season", "--month", "--show-plot", "--save-plot", "-of"]
for i in sys.argv:
    if i[:4]=="-of=":
        output_file=i[4:]
    elif i[0]=="-" and i not in argument_list:
        print("Error: '{}' not a known argument\nFormat must be:\n".format(i))
        flag=True


if "-h" in sys.argv or (n>1 and sys.argv[1][0]=="-") or (n>2 and sys.argv[2][0]=="-") or flag:
    print("mefa_v19.x FILE_NAME ANALYSE_TYPE [DATA_FORMAT (0,1 or 2)] [-h, -pe, -wm, -da, --year/--season/--month, --show-plot, --save-plot, -of]\n")
    print("ANALYSE_TYPE must be: "+str(ANALYSE_TYPE))
    print("\nArguments:\n-h\t\t\t help\n-pe\t\t\t per event\n-wm\t\t\t with max\n-da\t\t\t daily average\n--year/--season/--month: period (can be more than one)\n--show-plot\t\t show plot\n--save-plot\t\t save plot\n-of\t\t\t output file")
elif n>2:
    DEFAULT_FILE_NAME=sys.argv[1]
    if sys.argv[2] not in ANALYSE_TYPE:
        print("Error: ANALYSE_TYPE must be: "+str(ANALYSE_TYPE))
    else:
        analyse_from_prompt(sys.argv, output_file)
else:
    if n==2:
        DEFAULT_FILE_NAME=sys.argv[1]
    main=Window()
    if n==2:
        main.open_file()
    main.w.mainloop()
